
import os
import json
from pathlib import Path

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .authentication import (
    get_current_user_obj,
    is_admin,
    login_user,
    logout_user,
    generate_csrf_token,
    validate_csrf,
)

# Import config manager
from ..configuration.config_manager import (
    load_config,
    get_ip_whitelist,
    get_server_host,
    get_server_port,
    get_default_language,
    get_default_theme,
)

# Import database init
from ..database.database import init_db

# Import user manager
from ..users.user_manager import (
    get_admin_user_count,
    create_user,
    verify_password,
    get_user_by_username,
    get_user_by_id,
    get_all_users,
    upgrade_user_to_admin,
    downgrade_user_from_admin,
    update_user_settings,
)

# Import i18n loader
from ..gui.i18n import load_languages, get_translation_func


# Set up base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "application"
GUI_DIR = APP_DIR / "gui"
STATIC_DIR = GUI_DIR / "static"
TEMPLATE_DIR = GUI_DIR / "templates"
LANG_DIR = BASE_DIR / "languages"

# Load configuration
CONFIG_PATH = BASE_DIR / "settings.ini"
config = load_config(CONFIG_PATH)

# Load languages
languages = load_languages(LANG_DIR)


def get_t_func(lang: str):
    return get_translation_func(languages, lang)


# Create FastAPI app
app = FastAPI(title="EFMA")


# Session middleware
SECRET_KEY = "efma-secret-key"  # Replace with a securely generated persistent secret
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    same_site="none",
    https_only=True,
)


# CORS (allow local host only by default)
SERVER_PORT = get_server_port(config)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{SERVER_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# IP Whitelist middleware
class IPWhitelistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist):
        super().__init__(app)
        self.whitelist = whitelist

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        if client_ip not in self.whitelist:
            return PlainTextResponse(
                "Forbidden: IP not in whitelist",
                status_code=403,
            )

        return await call_next(request)


whitelist = get_ip_whitelist(config)
app.add_middleware(IPWhitelistMiddleware, whitelist=whitelist)


# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Template rendering
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


# Initialize database
init_db()


# Dependency to get translation function for current user
async def get_translation(request: Request):
    user = request.session.get("user_id")

    if user:
        usr = get_user_by_id(user)
        lang = usr.language if usr else get_default_language(config)
    else:
        lang = get_default_language(config)

    return get_t_func(lang)


# Utility: build context for templates
async def build_context(
    request: Request,
    extra: dict = None,
    error: str | None = None,
):
    t = await get_translation(request)

    lang = request.session.get("lang", get_default_language(config))
    theme = request.session.get("theme", get_default_theme(config))

    user_id = request.session.get("user_id")
    current_user = get_user_by_id(user_id) if user_id else None

    is_authenticated = current_user is not None
    admin_status = current_user.is_admin if current_user else False

    nav_buttons = [
        "nav_chat_sessions",
        "nav_characters",
        "nav_scenarios",
        "nav_locations",
        "nav_assets",
        "nav_game_mechanics",
        "nav_knowledge",
        "nav_addons",
        "nav_ai_settings",
    ]

    context = {
        "request": request,
        "t": t,
        "lang": lang,
        "theme": theme,
        "is_admin": admin_status,
        "csrf_token": request.session.get("csrf_token"),
        "user_icon": current_user.icon_path if current_user else None,
        "languages": {
            k: languages[k]["lang"] for k in languages
        },
        "nav_buttons": nav_buttons,
        "is_authenticated": is_authenticated,
    }

    if extra:
        context.update(extra)

    if error:
        context["error"] = error

    return context


# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    context = await build_context(request)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=context,
    )


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/")

    if get_admin_user_count() == 0:
        return RedirectResponse(url="/setup")

    csrf = generate_csrf_token(request.session)
    context = await build_context(request, {"csrf_token": csrf})

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=context,
    )


@app.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    if get_admin_user_count() == 0:
        return RedirectResponse(url="/setup")

    validate_csrf(request, csrf_token)

    user = get_user_by_username(username)

    if not user or not verify_password(user, password):
        context = await build_context(
            request,
            error="Invalid username or password",
        )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context=context,
        )

    login_user(request, user.id)

    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/login")


@app.get("/setup", response_class=HTMLResponse)
async def setup_get(request: Request):
    if get_admin_user_count() > 0:
        return RedirectResponse(url="/login")

    csrf = generate_csrf_token(request.session)
    context = await build_context(request, {"csrf_token": csrf})

    return templates.TemplateResponse(
        request=request,
        name="setup_admin.html",
        context=context,
    )


@app.post("/setup", response_class=HTMLResponse)
async def setup_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...),
    csrf_token: str = Form(...),
):
    if get_admin_user_count() > 0:
        return RedirectResponse(url="/login", status_code=303)

    validate_csrf(request, csrf_token)

    if password != confirm:
        csrf = generate_csrf_token(request.session)

        context = await build_context(
            request,
            {"csrf_token": csrf},
            error="Passwords do not match",
        )

        return templates.TemplateResponse(
            request=request,
            name="setup_admin.html",
            context=context,
        )

    create_user(username, password, is_admin=True)

    return RedirectResponse(url="/login")


@app.get("/settings", response_class=HTMLResponse)
async def settings_get(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    csrf = generate_csrf_token(request.session)

    user = get_user_by_id(request.session.get("user_id"))

    context = await build_context(
        request,
        {
            "csrf_token": csrf,
            "user_language": user.language,
            "user_theme": user.theme,
        },
    )

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context=context,
    )


@app.post("/settings", response_class=HTMLResponse)
async def settings_post(
    request: Request,
    language: str = Form(...),
    theme: str = Form(...),
    csrf_token: str = Form(...),
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    validate_csrf(request, csrf_token)

    update_user_settings(
        request.session.get("user_id"),
        language=language,
        theme=theme,
    )

    return RedirectResponse(url="/settings", status_code=303)


@app.get("/users", response_class=HTMLResponse)
async def users_get(
    request: Request,
    admin=Depends(is_admin),
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    users = get_all_users()

    context = await build_context(
        request,
        {"users": users},
    )

    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context=context,
    )


@app.post("/users/create", response_class=HTMLResponse)
async def users_create(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_admin: str = Form("false"),
    csrf_token: str = Form(...),
    admin=Depends(is_admin),
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    validate_csrf(request, csrf_token)

    create_user(
        username,
        password,
        is_admin=(is_admin.lower() == "true"),
    )

    return RedirectResponse(url="/users", status_code=303)


# Simple health endpoint for connection status
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


# Create application via function for compatibility with main.py
def create_app():
    return app


# If running directly, start uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "application.backend.server:create_app",
        host=get_server_host(config),
        port=get_server_port(config),
    )

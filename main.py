
#!/usr/bin/env python3
"""
Entry point for Ember ForgeMind Adventures (EFMA).

Supported launch modes:

    python main.py --web
        Starts the FastAPI web server.

    python main.py --desktop
        Starts the FastAPI backend and opens the EFMA
        interface inside a native PySide6 desktop window.

The desktop application uses Qt WebEngine to display the
existing web frontend without opening an external browser.
"""

import argparse
import os
import sys
import threading
import time

import uvicorn

from application.backend.server import create_app
from application.configuration.config_manager import (
    load_config,
    create_default_config,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(BASE_DIR, "settings.ini")

# Ensure required directories exist.
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure configuration file exists.
if not os.path.isfile(CONFIG_PATH):
    create_default_config(CONFIG_PATH)

config = load_config(CONFIG_PATH)

HOST = config.get("SERVER", "host") or "127.0.0.1"
PORT = int(config.get("SERVER", "port") or 8000)

SERVER_STARTUP_TIMEOUT = 30


# ============================================================
# WEB SERVER
# ============================================================

def run_web_server():
    """Start the FastAPI server in web mode."""

    print("Starting EFMA Web Server...")

    app = create_app()

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )


# ============================================================
# DESKTOP APPLICATION
# ============================================================

def run_desktop_application():
    """
    Start the FastAPI backend and display the frontend
    inside a native PySide6 desktop window.
    """

    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtWidgets import QApplication, QMainWindow
        from PySide6.QtWebEngineWidgets import QWebEngineView

    except ImportError as exc:
        print(
            "\nERROR: PySide6 or Qt WebEngine is not installed."
            "\nInstall the required packages using:"
            "\nuv pip install -r requirements.txt\n"
        )
        print(exc)
        return 1

    print("Starting EFMA Desktop Application...")

    # --------------------------------------------------------
    # Create Qt application
    # --------------------------------------------------------

    qt_app = QApplication(sys.argv[:1])
    qt_app.setApplicationName("Ember ForgeMind Adventures")

    # --------------------------------------------------------
    # Start FastAPI in a background thread
    # --------------------------------------------------------

    app = create_app()

    server_config = uvicorn.Config(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
    )

    server = uvicorn.Server(server_config)

    server_thread = threading.Thread(
        target=server.run,
        name="EFMA-Backend",
        daemon=True,
    )

    def stop_server():
        """Request a graceful Uvicorn shutdown."""

        if server_thread.is_alive():
            print("Stopping EFMA Backend...")

            server.should_exit = True

            server_thread.join(timeout=10)

            if server_thread.is_alive():
                print("Backend is taking too long to stop.")
                server.force_exit = True
                server_thread.join(timeout=5)

    # Start backend.
    server_thread.start()

    # --------------------------------------------------------
    # Wait until the backend is ready
    # --------------------------------------------------------

    print("Waiting for EFMA Backend...")

    startup_deadline = time.monotonic() + SERVER_STARTUP_TIMEOUT

    while not server.started:
        if not server_thread.is_alive():
            print("ERROR: EFMA Backend failed to start.")
            return 1

        if time.monotonic() >= startup_deadline:
            print("ERROR: EFMA Backend startup timed out.")
            stop_server()
            return 1

        time.sleep(0.1)

    print("EFMA Backend is ready.")

    # --------------------------------------------------------
    # Determine frontend URL
    # --------------------------------------------------------

    # Wildcard addresses are valid server bind addresses,
    # but must not be used as browser destinations.
    if HOST in ("0.0.0.0", "::", ""):
        display_host = "127.0.0.1"
    elif ":" in HOST and not HOST.startswith("["):
        display_host = f"[{HOST}]"
    else:
        display_host = HOST

    url = f"http://{display_host}:{PORT}"

    print(f"Loading EFMA interface: {url}")

    # --------------------------------------------------------
    # Create native desktop window
    # --------------------------------------------------------

    class EFMAWindow(QMainWindow):

        def __init__(self):
            super().__init__()

            self.setWindowTitle("Ember ForgeMind Adventures")

            self.resize(1400, 900)

            self.browser = QWebEngineView(self)

            self.setCentralWidget(self.browser)

            self.browser.setUrl(QUrl(url))

        def closeEvent(self, event):
            """Stop the backend when the window closes."""

            stop_server()

            event.accept()

    window = EFMAWindow()
    window.show()

    # --------------------------------------------------------
    # Start Qt event loop
    # --------------------------------------------------------

    try:
        exit_code = qt_app.exec()
    finally:
        stop_server()

    print("EFMA Desktop Application closed.")

    return exit_code


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="EFMA Application Launcher"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--web",
        action="store_true",
        help="Start EFMA as a web server",
    )

    group.add_argument(
        "--desktop",
        action="store_true",
        help="Start EFMA as a desktop application",
    )

    args = parser.parse_args()

    if args.web:
        run_web_server()
        return 0

    if args.desktop:
        return run_desktop_application()

    return 0


if __name__ == "__main__":
    sys.exit(main())

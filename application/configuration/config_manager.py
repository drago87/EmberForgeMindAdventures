import configparser
import os
import ast

DEFAULT_CONFIG = """[SERVER]
host = 127.0.0.1
port = 8013

[SECURITY]
# Comma seperated list
ip_whitelist = 127.0.0.1

[GUI]
default_language = en
default_theme = dark
"""


def load_config(path: str) -> configparser.ConfigParser:
    """Load configuration from *path*. If the file does not exist, return an empty parser.
    """
    cfg = configparser.ConfigParser()
    if os.path.isfile(path):
        cfg.read(path)
    return cfg


def create_default_config(path: str) -> None:
    """Create a new configuration file with default values if it does not exist.
    """
    if not os.path.isfile(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG)


def get_ip_whitelist(config):
    ips = config.get(
        "SECURITY",
        "ip_whitelist",
        fallback="127.0.0.1"
    )

    return [
        ip.strip()
        for ip in ips.split(",")
        if ip.strip()
    ]


def get_default_language(cfg: configparser.ConfigParser) -> str:
    return cfg.get("GUI", "default_language", fallback="en")


def get_default_theme(cfg: configparser.ConfigParser) -> str:
    return cfg.get("GUI", "default_theme", fallback="dark")


def get_server_host(cfg: configparser.ConfigParser) -> str:
    return cfg.get("SERVER", "host", fallback="127.0.0.1")


def get_server_port(cfg: configparser.ConfigParser) -> int:
    return int(cfg.get("SERVER", "port", fallback="8000"))

__all__ = [
    "load_config",
    "create_default_config",
    "get_ip_whitelist",
    "get_default_language",
    "get_default_theme",
    "get_server_host",
    "get_server_port",
]

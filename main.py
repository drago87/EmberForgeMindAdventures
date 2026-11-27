#!/usr/bin/env python3
"""Entry point for the Ember ForgeMind Adventures (EFMA) application.

This script starts the backend server and optionally launches a desktop
interface that connects to the local server.  Two command line options
are supported:

  --web    Start only the web server.
  --desktop  Start the web server and automatically open a browser
              window pointing to the local UI.

The script ensures that all required directories and configuration
files exist before starting the server.
"""

import argparse
import os
import sys
import threading
import webbrowser
import time

from application.backend.server import create_app
from application.configuration.config_manager import load_config, create_default_config

# Ensure the data directory exists so the database can be created.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Ensure configuration file exists.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")
if not os.path.isfile(CONFIG_PATH):
    create_default_config(CONFIG_PATH)

config = load_config(CONFIG_PATH)

HOST = config.get("SERVER", "host") or "127.0.0.1"
PORT = int(config.get("SERVER", "port") or 8000)


def run_server():
    app = create_app()
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)


def main():
    parser = argparse.ArgumentParser(description="EFMA application launcher")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--web", action="store_true", help="Run only the web server")
    group.add_argument("--desktop", action="store_true", help="Run the web server and open a desktop browser")
    args = parser.parse_args()

    # Start the server in a background thread so we can launch a browser
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(1)

    if args.desktop:
        url = f"http://{HOST}:{PORT}"
        webbrowser.open(url)

    # Keep the main thread alive while the server thread is running
    try:
        while server_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()

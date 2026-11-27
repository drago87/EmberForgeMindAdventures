# EFMA – Ember ForgeMind Adventures
 
 <p align="center">
  <img src="./icon.png" alt="EFMA - Ember ForgeMind Adventures Logo" width="480">
</p>

**Forge characters. Shape worlds. Create adventures.**

EFMA (Ember ForgeMind Adventures) is an open-source, AI-powered roleplaying and storytelling platform currently under development.

The goal is to create an alternative to [SillyTavern](https://github.com/SillyTavern/SillyTavern), with a stronger focus on RPG-style character management, immersive storytelling, and persistent game worlds.

Rather than treating characters as simple chat profiles, EFMA aims to provide structured RPG-style character sheets, allowing users to manage everything from appearance, personality, and equipment to attributes, skills, relationships, and more.

## Planned Features

- **RPG-style Character Sheets** – Detailed, structured character profiles with customizable sections and attributes.
- **Scenarios & Locations** – Create reusable scenarios and locations, including hierarchical locations with sublocations.
- **Flexible Roleplay Sessions** – Play with multiple characters, designate a player character, and optionally select a scenario and starting location.
- **Persistent Sessions** – Keep track of story progression, character state, inventory, relationships, and other session information.
- **LLM Integration** – Connect to local and remote language models through services such as Ollama, KoboldCpp, and compatible APIs.
- **Multi-user Support** – Give each user their own characters, scenarios, locations, library, settings, and add-ons.
- **Add-on System** – Extend the application with user-specific add-ons that can introduce new features, RPG mechanics, interface components, and content.
- **Desktop & Browser Support** – Run EFMA as a standalone desktop application or access it through a web browser.
- **Import & Export** – Support importing and exporting characters and other content to make it easier to move between platforms.

## Technology

The planned architecture is built around:

- Python and FastAPI for the backend.
- React and TypeScript for the frontend.
- PySide6 and Qt WebEngine for the desktop application.

## Installation
Reccomended way is using [Pinokio](https://pinokio.co/) and using the one-click installer [EFMA](https://github.com/drago87/EFMA)

Manual Installation
The following instructions assume you are on Windows and want to set up the development environment. If you are on macOS or Linux, adjust the commands accordingly.

1. **Python 3.12.x** – EFMA requires Python 3.12. Download and install the latest 3.12.x release from the [official Python website](https://www.python.org/downloads/) and make sure the `python` executable is on your `PATH`.

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS / Linux
   ```

3. **Upgrade pip**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. **Install the core dependencies**
   ```bash
   # PyTorch with CUDA 13.0 support
   pip install torch==2.10.0 -f https://download.pytorch.org/whl/cu130
   pip install torchvision==0.25.0
   pip install torchaudio==2.10.0
   pip install triton-windows

   # SageAttention (pre‑built wheel for Windows)
   pip install https://github.com/woct0rdho/SageAttention/releases/download/v2.2.0-windows.post5/sageattention-2.2.0+cu130torch2.10.0andhigher.post5-cp310-abi3-win_amd64.whl

   # flash‑attn from the ComfyUI wheels
   pip install flash-attn -f https://comfy-org.github.io/wheels
   ```

5. **Additional project‑specific packages** – the project uses FastAPI, uvicorn, Pydantic, SQLAlchemy, etc. Install them via the provided `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application** – you can start the web server directly or use Pinokio:
   ```bash
   # Web server only
   python main.py --web

   # Desktop + web
   python main.py --desktop
   ```

Feel free to tweak the `requirements.txt` or the install script if you want a different CUDA version or a different set of libraries.

- (The installation commands above are tailored for a Windows environment; on Linux/macOS you should adjust the URLs and packages accordingly.)
- If you encounter any missing dependencies, consult the error message and install the missing package with `pip install <package>`.

- **Tip**: For a clean environment, consider using Conda or pyenv to manage multiple Python versions.

- **Note**: The `triton-windows` package is a pre‑built binary for Windows that satisfies Triton’s runtime requirements.

- **Prerequisite**: A recent GPU with CUDA 13.0 support is recommended for the best performance of the torch and flash‑attn wheels.

- The `sageattention` wheel is compiled for CP310‑ABI3; if you use a different Python version you will need a matching wheel.

- For more details on each dependency, refer to the official documentation linked in the respective package URLs.

- Happy hacking!
- SQLite initially, with support for more advanced database setups as the project evolves.
- Pinokio for installation and application launching.

These technologies and implementation details are subject to change during development.

## Project Status

🚧 **UNDER CONSTRUCTION** 🚧

EFMA is currently in the planning and early development stage.

Features listed above represent the project's goals and planned direction. They are not necessarily implemented or available yet.

Expect significant changes as the project develops. Contributions, ideas, and feedback will be welcome as the project progresses.

## Vision

The vision behind EFMA is to create a flexible platform where users can build characters, create stories, explore locations, and experience evolving RPG adventures with the help of AI.

The aim is to go beyond traditional AI chat-based roleplay by combining character creation, RPG mechanics, world-building, and storytelling into one extensible platform.

**Forge characters. Shape worlds. Create adventures.**

# Backend Architecture

This document describes the agreed backend architecture and technical direction for EFMA.

The goal is to build a modular, extensible application with a Python backend that supports both desktop and browser/server operation.

---

## 1. Python's Role in EFMA

Python will be the main application backend.

It will handle:

- Application logic and internal operations.
    
- Communication with different LLM providers.
    
- Character management.
    
- Scenario and location management.
    
- Chat Sessions and persistent game state.
    
- Inventory and equipment management.
    
- RPG mechanics and game logic.
    
- Decision model integration.
    
- Add-on management.
    
- User accounts, authentication and permissions.
    
- Database operations.
    
- Importing and exporting content.
    

Python will not be used to build every screen of the GUI. The frontend will be a separate application layer.

## 2. Desktop Application – PySide6

### Chosen approach

**PySide6 with an embedded web frontend.**

Technologies:

- **PySide6:** Python bindings for Qt.
    
- **Qt WebEngine:** Embeds a browser inside the desktop application.
    
- **QWebEngineView:** Displays the EFMA frontend inside the desktop window.
    

This allows EFMA to have a modern web-based interface while still operating as a desktop application.

The desktop application will essentially be a Python application containing an embedded browser.

## 3. Browser/Server Mode

EFMA should support two execution modes.

### Desktop mode

- Python starts the backend.
    
- PySide6 opens the frontend in its embedded browser.
    
- The frontend communicates with the backend through HTTP APIs.
    

### Server mode

- Python starts the backend.
    
- The backend serves the frontend.
    
- Users access EFMA through an ordinary web browser.
    

### Important architectural decision

Both modes must use the same backend and HTTP API.

There should be no separate implementation of application functionality for desktop and browser/server modes.

For example, creating a character should work through exactly the same API regardless of whether the user is using the desktop application or browser.

## 4. Backend – Python and FastAPI

The proposed backend technology is:

**Python + FastAPI**

FastAPI will provide the HTTP API used by the frontend.

The backend will handle:

- User accounts and authentication.
    
- User permissions and administration.
    
- Character management.
    
- Scenario and location management.
    
- Chat Sessions and game state.
    
- Inventory and equipment.
    
- RPG mechanics.
    
- LLM connections.
    
- Decision model connections.
    
- Add-on management.
    
- Database operations.
    
- Importing and exporting content.
    

### Communication

- HTTP APIs for ordinary application operations.
    
- Server-Sent Events (SSE) for streaming AI responses, at least initially.
    

The frontend should not directly communicate with LLM providers or access the database. These operations should go through the Python backend.

## 5. LLM Integration

EFMA should support multiple LLM backends.

Rather than implementing individual provider connections throughout the application, we will use a **provider/adapter architecture** in Python.

### Potential integrations

|Provider|Purpose|
|---|---|
|Ollama|Local LLM hosting|
|KoboldCpp|Local LLM inference|
|OpenAI-compatible APIs|Compatible local and remote endpoints|
|Other providers|Additional integrations through adapters|

### Common provider interface

The LLM provider architecture should offer a common interface for:

- Sending prompts.
    
- Receiving responses.
    
- Streaming output.
    
- Handling model settings.
    
- Managing provider-specific configuration.
    
- Reporting provider errors and connection status.
    

The RPG engine should not need to know which LLM provider is being used.

Adding a new LLM provider should not require changing the RPG engine.

## 6. Liquid AI – Native Decision Model Support

EFMA should have native support for **Liquid AI decision models**.

Liquid AI decision models are different from ordinary conversational LLMs.

They evaluate information and return structured answers, such as classifications, choices, scores and probabilities, rather than generating conversational text.

### Purpose

Decision models can be used for:

- Determining which character should speak next.
    
- Identifying the intent behind a player's message.
    
- Determining whether an NPC should react to an event.
    
- Selecting appropriate NPC actions.
    
- Classifying messages and events.
    
- Evaluating game situations.
    
- Selecting between predefined outcomes.
    
- Scoring decisions based on defined criteria.
    

The decision model should return structured results that EFMA's Python backend can interpret and act upon.

### 6.1 Local execution

**Liquid AI should run locally using downloaded model files.**

The local implementation must not require a Liquid AI API key or cloud connection.

Users should be able to obtain models in two ways:

**Manual model installation**

1. The user downloads a Liquid AI model independently.
    
2. The user opens AI Settings.
    
3. The user selects the downloaded model file or model directory.
    
4. EFMA validates the model and its compatibility.
    
5. The model becomes available for loading.
    

**Download through EFMA**

1. The user opens the model browser in AI Settings.
    
2. EFMA displays available compatible Liquid AI models.
    
3. The user selects a model and, where applicable, a quantization.
    
4. EFMA downloads the required files.
    
5. The model becomes available for loading.
    

The downloaded model files should remain on the user's computer.

### 6.2 Model management

AI Settings should support:

- Browsing available Liquid AI models.
    
- Downloading models.
    
- Selecting manually downloaded models.
    
- Selecting the active model.
    
- Viewing model information and file locations.
    
- Loading and unloading models.
    
- Displaying model loading errors.
    
- Displaying model compatibility information.
    
- Managing downloaded models.
    

Users should be able to retain multiple downloaded models and switch between them.

### 6.3 CPU and GPU selection

Users must be able to choose where the model runs.

Supported execution options:

- CPU.
    
- GPU.
    

Additional requirements:

- Detect available hardware.
    
- Detect compatible GPU backends.
    
- Allow selection of a specific GPU when multiple GPUs are available.
    
- Allow CPU-only execution.
    
- Check available memory before loading.
    
- Display hardware compatibility information.
    
- Display loading and inference errors.
    
- Never silently switch from GPU to CPU without informing the user.
    

The available execution options will depend on the selected model and inference runtime.

### 6.4 Inference runtimes

EFMA should support compatible local inference runtimes through a runtime abstraction.

Potential runtimes include:

- **Transformers + PyTorch:** Supports direct model loading and device selection, including CPU, CUDA and Apple MPS where supported.
    
- **llama.cpp:** Supports GGUF models and local CPU/GPU inference.
    

The backend should determine which runtime is compatible with the selected model format.

Different runtimes may expose different capabilities. EFMA must not assume that every runtime supports every decision question type.

For example, the documented d1-2B GGUF implementation in llama.cpp supports `noul`, `choice` and `score` questions, while additional capabilities such as multiple-choice classification, extraction and bounding boxes are available through the Transformers implementation.

Runtime capability detection should therefore be part of the integration.

### 6.5 Decision model architecture

Liquid AI should be implemented as a dedicated decision-model subsystem, separate from ordinary LLM providers.

Proposed structure:

```
backend/
└── ai/
    ├── llm/
    │   ├── provider_interface.py
    │   ├── ollama.py
    │   ├── koboldcpp.py
    │   └── openai_compatible.py
    │
    └── decision/
        ├── decision_interface.py
        ├── decision_manager.py
        ├── decision_schemas.py
        │
        └── liquid_ai/
            ├── model_manager.py
            ├── model_loader.py
            ├── hardware_detection.py
            ├── runtime_manager.py
            └── inference.py
```

### 6.6 Decision model interface

The decision interface should support:

- Providing information about the current situation.
    
- Defining one or more questions.
    
- Defining possible answers and evaluation criteria.
    
- Receiving structured answers.
    
- Receiving probabilities and confidence information where supported.
    
- Interpreting confidence levels.
    
- Applying configurable decision thresholds.
    
- Reporting unsupported question types.
    

The RPG engine should communicate with the decision interface rather than directly with Liquid AI.

This makes it possible to introduce additional decision-model providers later.

### 6.7 Example: Selecting the next speaker

Consider a Chat Session containing:

- A player character.
    
- Two NPCs.
    
- A narrator.
    

EFMA could provide the decision model with:

- Current conversation.
    
- Current scene and location.
    
- Characters present.
    
- Character personalities and motivations.
    
- Recent events.
    
- Current game state.
    

It could then ask:

**Which character should speak next?**

Possible answers:

- NPC 1.
    
- NPC 2.
    
- Narrator.
    
- No character should speak yet.
    

The decision model returns probabilities, and the Python backend interprets the result.

The same approach could be used for NPC reactions, event classification and other game-related decisions.

The user must retain the ability to manually select the next speaker. Automatic decisions should not remove manual control.

### 6.8 Decision model configuration

Decision models should be configurable independently of ordinary LLMs.

|Setting|Purpose|
|---|---|
|Provider|Selected decision-model provider|
|Model|Selected decision model|
|Model location|Local model path|
|Runtime|Compatible inference runtime|
|Execution device|CPU or GPU|
|GPU selection|Select a compatible GPU|
|Confidence threshold|Minimum confidence for automatic decisions|
|Fallback behavior|What EFMA does when a decision cannot be made|

---

## 7. Add-on System

EFMA should support user-specific add-ons that can extend application functionality.

Examples:

- New RPG mechanics.
    
- Custom dice systems.
    
- Combat systems.
    
- Character attributes and skills.
    
- AI prompt processors.
    
- Custom integrations.
    
- New functionality in the chat interface.
    

### Extension architecture

The extension architecture should support:

- A manifest describing each add-on.
    
- Defined extension points.
    
- Permission declarations.
    
- Version and compatibility information.
    
- User-specific installation and configuration.
    
- Separate execution environments for executable extensions.
    

### Security decision

Python add-ons must not automatically execute inside the shared application process.

For multi-user server operation, executable add-ons should run in isolated worker processes with controlled API access.

This helps prevent one user's add-on from accessing another user's data.

---

## 8. Database

We propose starting with **SQLite**.

Python will manage database access and application data.

The database needs to support:

- Multiple user accounts.
    
- User-owned characters.
    
- User-owned scenarios and locations.
    
- Chat Sessions and persistent game state.
    
- Libraries and content.
    
- Add-on installations and configuration.
    
- Add-on-specific data.
    
- User settings and preferences.

The different databases

- Chat Sessions (Only the user that owns them)

- Characters (Only the user that owns them)

- Scenarios and Scenario Collections (Only the user that owns them)

- Locations and Location Collections (Only the user that owns them)

- Assets and Asset Collections (Only the user that owns them)

- Game Mechanics and Game Mechanic Collections (Only the user that owns them)

- Knowladge and Knowladge Konnections (Only the user that owns them)

- Users and their passwords (Only admin accounts and the user itself, passwords should still be hidden from admins)

The architecture should allow migration to more advanced database systems later, such as PostgreSQL.

All databases should be encrypted so that only the user that it is bound to can read it.

---

## 9. User Data Structure

User data will be stored inside the `app/` directory, alongside the application files.

The directory will be excluded from Git using `.gitignore`.

### Proposed structure

```
app/
├── requirements.txt
├── .gitignore
│
├── backend/
├── frontend/
│
└── users/
    ├── user1/
    │   ├── settings/
    │   │   └── ai/
    │   ├── characters/
    │   ├── scenarios/
    │   ├── locations/
    │   ├── chat_sessions/
    │   ├── knowledge/
    │   ├── models/
    │   │   └── liquid_ai/
    │   ├── addons/
    │   ├── uploads/
    │   └── ...
    │
    └── user2/
        ├── settings/
        ├── characters/
        ├── scenarios/
        ├── locations/
        ├── chat_sessions/
        ├── knowledge/
        ├── models/
        └── ...
```

The exact user data subdirectories can evolve as EFMA develops.

### Git protection

The `.gitignore` file must include:

```
# User data - never commit
/users/
```

This ensures that user accounts and their content are not accidentally uploaded to GitHub.

Important: `.gitignore` does not automatically untrack files that have already been committed. The users directory must remain untracked from the beginning.

### User data requirements

1. Application updates must never overwrite user data.
    
2. User data must be independent of application source code.
    
3. All database and content paths must be configurable.
    
4. Users must be able to back up and restore their data.
    
5. Each user's data must be isolated from other users.
    
6. Downloaded AI models should not need to be downloaded again after an ordinary application update.
    

---

## 10. User Accounts and Administration

EFMA will support multiple user accounts.

Each account will have its own user data and settings.

### 10.1 Initial administrator creation

When EFMA is started for the first time:

1. Check whether any user accounts exist.
    
2. If no accounts exist, require the creation of an administrator account.
    
3. The first account created becomes the initial administrator.
    
4. Once created, normal login becomes available.
    

### 10.2 Administrator recovery

If accounts exist but none of them has administrator privileges:

1. EFMA detects that no administrator accounts remain.
    
2. It checks whether the request originates from the same computer as the server.
    
3. If access is local, allow the creation of a new administrator account.
    
4. If access is remote, do not allow administrator creation.
    

This prevents remote users from taking over server administration if the existing administrator accounts are removed or demoted.

### 10.3 Security requirements

- Local access verification must happen in the Python backend.
    
- Remote requests must not be treated as local simply because of spoofed forwarding headers.
    
- Administrator creation must be an atomic server-side operation.
    
- Only administrators can manage other users.
    
- User permissions must be enforced by the backend, not just the frontend.
    
- Administrator recovery must not be available to ordinary remote users.
    

### 10.4 User management

Administrator accounts should be able to:

- View existing users.
    
- Create users.
    
- Remove users.
    
- Change user permissions.
    
- Promote users to administrator.
    
- Remove administrator privileges.
    

User-specific settings and content must remain isolated.

---

## 11. Proposed Backend Folder Structure

The following is a conceptual structure for the Python backend.

```
backend/
├── main.py
│
├── api/
│   ├── routes/
│   └── dependencies/
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── events.py
│
├── users/
│   ├── manager.py
│   ├── authentication.py
│   ├── permissions.py
│   └── admin_recovery.py
│
├── characters/
├── scenarios/
├── locations/
├── chat_sessions/
├── inventory/
├── mechanics/
│
├── ai/
│   ├── llm/
│   └── decision/
│
├── addons/
├── database/
├── imports/
└── exports/
```

This structure is a starting proposal. The exact module boundaries can be refined during implementation.

---

## 12. Agreed Technologies and Architecture

|Component|Technology / approach|
|---|---|
|Main backend language|Python|
|Backend framework|FastAPI|
|Desktop application|PySide6|
|Embedded browser|Qt WebEngine|
|Frontend|Separate web frontend|
|Desktop communication|HTTP API|
|Browser communication|HTTP API|
|AI response streaming|SSE initially|
|LLM integration|Provider/adapter architecture|
|Local LLM providers|Ollama, KoboldCpp and compatible APIs|
|Decision models|Dedicated provider architecture|
|Native decision provider|Liquid AI|
|Liquid AI deployment|Local execution|
|Liquid AI model acquisition|Manual download or EFMA download|
|Liquid AI execution|CPU or GPU, user selectable|
|Liquid AI runtimes|Compatible local inference runtimes|
|Database|SQLite initially|
|Add-on execution|Isolated worker processes|
|User management|Multi-user accounts|
|Initial administrator|Required on first startup|
|Administrator recovery|Local server access only|
|User data|Individual directories under `app/users/`|
|Git protection|`/users/` in `.gitignore`|

---

## 13. Overall Architectural Principles

The following principles should guide future EFMA development.

1. **One backend:** Desktop and browser/server modes use the same Python backend.
    
2. **API-based frontend:** The frontend communicates with the backend through HTTP APIs.
    
3. **Provider independence:** The RPG engine should not depend on a specific LLM provider.
    
4. **Separate AI systems:** Conversational LLMs and decision models use separate interfaces.
    
5. **Local Liquid AI:** Liquid AI decision models are downloaded and executed locally.
    
6. **User-controlled hardware:** Users choose CPU or GPU execution for compatible models.
    
7. **Extensibility:** Add-ons can introduce new functionality without modifying the core application.
    
8. **Process isolation:** Executable Python add-ons must run outside the shared application process.
    
9. **User isolation:** Each account has its own settings, content and permissions.
    
10. **Data protection:** User data must never be included in Git commits.
    
11. **Recoverable administration:** Initial administrator creation and local administrator recovery are built into the backend.
    
12. **Future compatibility:** Database, AI providers, runtimes and add-on systems should be replaceable or extendable without redesigning the entire application.
    

**Overall goal:** EFMA should have one modular Python backend responsible for application functionality, game logic, user management and AI integration. The desktop and browser interfaces are two different ways of accessing that same backend.
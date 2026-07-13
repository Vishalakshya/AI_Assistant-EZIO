# EZIO: Developer Onboarding Guide

Welcome to the EZIO development team! EZIO is an advanced AI desktop assistant designed to be highly capable, witty, and deeply integrated with the Windows operating system. 

This guide provides a comprehensive, step-by-step walkthrough for setting up your development environment on Windows 11 (with secondary support for Windows 10). Whether you are a beginner or a seasoned engineer, this document will get you up and running.

---

## 1. COMPLETE SOFTWARE REQUIREMENTS

To develop EZIO locally, your machine must meet the following software requirements.

- **OS**: Windows 11 (Primary) or Windows 10 (Secondary). EZIO relies heavily on Windows APIs and PowerShell.
- **Python (v3.11+)**: Required for the FastAPI backend, AI orchestration, and system manipulation tools.
- **Node.js (v18.x or v20.x LTS)**: Required for the Electron, React, and Vite frontend.
- **Git**: Required for version control and collaborating on the repository.
- **Visual Studio Code (VS Code)**: The officially supported IDE for this project.
- **Visual Studio Build Tools (C++ Desktop Development)**: **CRITICAL.** Many Python libraries EZIO uses (e.g., `psutil` for process management, `pycaw` for audio control) require C++ compilation during `pip install`.
- **PowerShell (v5.1+)**: Pre-installed on Windows. Used heavily by EZIO's backend for system controls (WiFi, Bluetooth).
- **Playwright Dependencies**: Required for Browser Automation. Handled via Python post-installation scripts.

---

## 2. INSTALLATION LINKS

Please install the required software using the official links below.

- **Python**: [Download Python 3.11+](https://www.python.org/downloads/windows/)
  - *Important*: During installation, check the box **"Add Python to PATH"**.
- **Node.js**: [Download Node.js (LTS)](https://nodejs.org/en/download/)
  - We recommend the LTS (Long Term Support) version.
- **Git**: [Download Git for Windows](https://git-scm.com/download/win)
  - Accept the default installation settings.
- **Visual Studio Code**: [Download VS Code](https://code.visualstudio.com/)
- **Visual Studio Build Tools**: [Download Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - *Important*: Run the installer, select the **"Desktop development with C++"** workload, and ensure "Windows 10/11 SDK" is checked on the right panel.

---

## 3. PROJECT CLONING

Once all prerequisites are installed, clone the repository.

```powershell
# Open PowerShell or Git Bash
git clone https://github.com/your-org/ezio-desktop.git
cd ezio-desktop
code .
```

### Branch Strategy & Commits
- The `main` branch is locked. All development happens on `develop` or feature branches.
- **Conventional Commits**: We strictly follow Conventional Commits (e.g., `feat: add volume control`, `fix: memory leak in UI`, `docs: update readme`). 

Recommended Git Config:
```powershell
git config --global core.autocrlf true
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 4. BACKEND ENVIRONMENT SETUP

The backend is built with Python, FastAPI, and SQLite.

### 1. Create and Activate the Virtual Environment
Open a terminal in VS Code (Ctrl+`):
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*Note: If you receive a PowerShell Execution Policy error, run:*
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
EZIO uses Playwright for browser automation. You must download the browser binaries:
```powershell
playwright install
```

### 4. Database Setup (Alembic)
EZIO uses SQLite. We use Alembic to manage database migrations.
```powershell
alembic upgrade head
```

---

## 5. FRONTEND ENVIRONMENT SETUP

The frontend is built with Electron, React, TypeScript, and TailwindCSS, bundled by Vite.

Open a **new** terminal window in VS Code:
```powershell
cd frontend
npm install
```
This command installs all dependencies, including Electron, React, Vite, and Tailwind configuration packages.

---

## 6. ENVIRONMENT VARIABLES

You need to create two `.env` files. **Never commit these files to version control.**

### Backend (`backend/.env`)
Create a file named `.env` in the `backend/` directory:

```env
# API Keys
OPENAI_API_KEY=sk-proj-...

# Application Settings
ENVIRONMENT=development    # 'development' or 'production'
PORT=8000                  # Port for FastAPI to run on
LOG_LEVEL=DEBUG            # Set to INFO in production

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/ezio.db

# Security
ALLOW_DANGEROUS_ACTIONS=false  # Forces confirmation for Tier 3 OS actions
```

### Frontend (`frontend/.env`)
Create a file named `.env` in the `frontend/` directory:

```env
# API Connectivity
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000/ws

# UI Toggles
VITE_ENABLE_DEBUG_PANEL=true
```

---

## 7. OPENAI SETUP

EZIO is powered by GPT-5.5, Whisper, and OpenAI TTS.

1. **Create an Account**: Go to [platform.openai.com](https://platform.openai.com) and create a developer account.
2. **Add Credits**: You must have a funded billing account (Tier 1+) to access the latest GPT models.
3. **Generate API Key**: Navigate to "API Keys" -> "Create new secret key". Name it `EZIO_DEV`.
4. **Copy Key**: Paste it into your `backend/.env` file.

**Cost Optimization Tip**: During heavy UI development, you can mock OpenAI responses in the backend by setting `MOCK_LLM=true` in your `.env` (if supported by the current codebase) to save credits.

---

## 8. DATABASE INITIALIZATION

EZIO relies on SQLite for persistent memory, user preferences, and action logs.

- **File Location**: During development, the database lives at `backend/data/ezio.db`.
- **Migrations**: We use Alembic. If you change a model in `models.py`, generate a migration:
  ```powershell
  alembic revision --autogenerate -m "Add custom_commands table"
  alembic upgrade head
  ```
- **Resetting Database**: To completely wipe memory for testing:
  ```powershell
  alembic downgrade base
  alembic upgrade head
  ```
**Memory Persistence**: EZIO saves "facts" to the `Memories` table asynchronously. FTS5 (Full-Text Search) is used to retrieve context before calling GPT-5.5.

---

## 9. RUNNING THE PROJECT

### Development Mode (Hot Reloading)

You need to run both the backend and frontend simultaneously.

**Terminal 1 (Backend)**:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```powershell
cd frontend
npm run dev
```
*This starts Vite for React hot-reloading and launches the Electron application window.*

### Production Mode

**Backend Build**:
We bundle the backend using PyInstaller to create a standalone executable (no Python required on the host machine).
```powershell
cd backend
pyinstaller --name EZIO_Backend --onefile app/main.py
```

**Frontend Build & Package**:
```powershell
cd frontend
npm run build
npm run package
```
*This produces a final Windows `.exe` installer in the `frontend/dist` directory.*

---

## 10. VS CODE DEBUGGING

We have pre-configured VS Code to attach to both the Python backend and Electron frontend. 
Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "env": { "ENVIRONMENT": "development" }
    },
    {
      "name": "Debug Electron",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "runtimeExecutable": "${workspaceFolder}/frontend/node_modules/.bin/electron.cmd",
      "args": ["."],
      "outputCapture": "std"
    }
  ],
  "compounds": [
    {
      "name": "Debug Full Stack",
      "configurations": ["Debug FastAPI", "Debug Electron"]
    }
  ]
}
```
**Workflow**: Go to the "Run and Debug" tab in VS Code. Select "Debug Full Stack" to launch both environments with active breakpoints!

---

## 11. RECOMMENDED EXTENSIONS

Please install these VS Code extensions to maintain code quality:
1. **Python** (Microsoft): Core language support.
2. **Pylance** (Microsoft): Fast, feature-rich language server for Python.
3. **Ruff**: The extremely fast Python linter and formatter we use.
4. **Prettier**: Code formatter for TypeScript/React.
5. **ESLint**: Linting for the frontend.
6. **Tailwind CSS IntelliSense**: Autocompletion for Tailwind utility classes.
7. **SQLite Viewer**: Allows you to click on `ezio.db` and view tables directly in VS Code.
8. **GitLens**: Essential for understanding Git blame and history.

---

## 12. DEVELOPMENT WORKFLOW

1. **Branch**: `git checkout -b feat/voice-integration`
2. **Code**: Write your feature following architecture principles.
3. **Format**: Ensure Prettier (Frontend) and Ruff (Backend) have run.
4. **Test**: Run unit tests (see below).
5. **Commit**: `git commit -m "feat: add whisper voice integration"`
6. **Push**: `git push origin feat/voice-integration`
7. **Pull Request**: Open a PR to `develop`. Require at least 1 code review from a peer.

---

## 13. TESTING WORKFLOW

### Backend (Python)
We use `pytest` for unit and integration testing.
```powershell
cd backend
pytest -v
pytest --cov=app # For coverage reports
```

### Frontend (React/Electron)
We use `vitest` for React components and `Playwright` for Electron E2E tests.
```powershell
cd frontend
npm run test:unit
```

### Integration (Tool & Memory Testing)
Specific backend integration tests mock the OpenAI API to verify that the Tool Orchestrator correctly parses JSON schemas and handles database insertions safely.

---

## 14. COMMON PROBLEMS & TROUBLESHOOTING

- **`psutil` or `pycaw` fails to install**: You forgot to install the Visual Studio C++ Build Tools. See section 2.
- **PowerShell Execution Policy Error**: When activating `venv`, Windows blocks it. Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` as Administrator.
- **Playwright errors (Browser not found)**: You forgot to run `playwright install` inside your activated virtual environment.
- **`port 8000 is already in use`**: Another process is running. Find it using `netstat -ano | findstr :8000` and kill it using `taskkill /PID <number> /F`.
- **Database Schema Errors (`no such table`)**: You haven't run Alembic migrations. Run `alembic upgrade head` in the backend.
- **Electron opens but is blank**: The React app isn't running or finished building yet. Ensure Vite (`npm run dev`) is running without errors.

---

## 15. CONTRIBUTOR GUIDE

- **Coding Standards**: 
  - Backend: Use Type Hints strictly. Format with `ruff`.
  - Frontend: Use TypeScript interfaces. Format with `Prettier`.
- **Naming Conventions**: 
  - Python: `snake_case` for variables/functions, `PascalCase` for Classes.
  - React: `PascalCase` for components (`ChatBubble.tsx`), `camelCase` for functions/hooks.
- **Architecture Principles**: 
  - **No Logic in UI**: The React app is purely presentational. ALL logic, OS interactions, and AI orchestrations live in Python.
- **Security Requirements**: 
  - Any backend tool that manipulates files, registry, or shuts down apps MUST be flagged as `Tier 3` and invoke the IPC `REQUEST_CONFIRMATION` flow to the frontend. No exceptions.
- **Documentation Standards**: All new backend Tools must include a docstring detailing exactly what it does, as this docstring is parsed into the JSON schema sent to GPT-5.5.

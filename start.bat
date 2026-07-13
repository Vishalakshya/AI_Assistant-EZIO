@echo off
echo Starting EZIO Developer Environment...

REM Check if Ollama is running, if not start it (assuming ollama in PATH)
tasklist /fi "imagename eq ollama.exe" | find /i "ollama.exe" > nul
if errorlevel 1 (
    echo Starting Ollama...
    start "" ollama serve
) else (
    echo Ollama is already running.
)

REM Start Backend
echo Starting Backend...
start "EZIO Backend" cmd /c "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

REM Start Frontend / Electron
echo Starting Frontend & Electron...
start "EZIO Frontend" cmd /c "cd frontend && npm run dev"

echo EZIO successfully launched!

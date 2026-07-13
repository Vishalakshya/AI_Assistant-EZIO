# dev.ps1
Write-Host "Starting EZIO Developer Environment..." -ForegroundColor Cyan

# Check if Ollama is running
$ollamaRunning = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaRunning) {
    Write-Host "Starting Ollama in background..." -ForegroundColor Yellow
    Start-Process -NoNewWindow "ollama" -ArgumentList "serve"
} else {
    Write-Host "Ollama is already running." -ForegroundColor Green
}

# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/c cd backend && venv\Scripts\activate && uvicorn app.main:app --reload" -WindowStyle Normal

# Start Frontend
Write-Host "Starting Frontend (Vite + Electron)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/c cd frontend && npm run dev" -WindowStyle Normal

Write-Host "All processes started!" -ForegroundColor Green

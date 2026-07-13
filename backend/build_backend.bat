@echo off
echo Building EZIO Backend with PyInstaller...

:: We must include the alembic directory and alembic.ini
venv\Scripts\pyinstaller.exe ^
    --name ezio-backend ^
    --onedir ^
    --add-data "alembic.ini;." ^
    --add-data "alembic;alembic" ^
    --hidden-import "app.tools.system.tools" ^
    --hidden-import "app.tools.apps.tools" ^
    --hidden-import "app.tools.browser.tools" ^
    --hidden-import "app.tools.files.tools" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.protocols.websockets" ^
    --hidden-import "uvicorn.protocols.websockets.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "playwright" ^
    --hidden-import "playwright.async_api" ^
    --hidden-import "aiosqlite" ^
    --hidden-import "sqlalchemy.ext.asyncio" ^
    run_app.py

echo Build complete.

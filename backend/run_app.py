import os
import sys
import uvicorn
import logging
from pathlib import Path

# Configure AppData paths before anything else imports
app_data = os.getenv('APPDATA')
if app_data:
    base_dir = Path(app_data) / "EZIO"
else:
    base_dir = Path.home() / ".ezio"

data_dir = base_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True)
db_path = data_dir / "ezio.db"

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"

# PyInstaller creates a temp folder and stores path in _MEIPASS
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

def apply_migrations():
    print("Running DB Migrations...")
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config(os.path.join(bundle_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(bundle_dir, "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")
    print("Migrations complete.")

if __name__ == "__main__":
    apply_migrations()
    
    import app.tools.system.tools
    import app.tools.apps.tools
    import app.tools.browser.tools
    import app.tools.files.tools

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, workers=1)

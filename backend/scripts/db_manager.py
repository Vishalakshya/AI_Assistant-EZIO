import os
import shutil
import argparse
import asyncio
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ezio.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "backups")

def backup_db():
    if not os.path.exists(DB_PATH):
        print(f"[-] Database not found at {DB_PATH}")
        return
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"ezio_backup_{timestamp}.db")
    
    shutil.copy2(DB_PATH, backup_path)
    print(f"[+] Database backed up to {backup_path}")

def reset_db():
    if not os.path.exists(DB_PATH):
        print(f"[-] Database not found at {DB_PATH}")
        return
    
    confirm = input("WARNING: This will delete the database. Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        # Create a backup just in case
        backup_db()
        os.remove(DB_PATH)
        print("[+] Database deleted. Run migrations to initialize a fresh one.")
    else:
        print("[-] Aborted.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EZIO Database Manager")
    parser.add_argument("--backup", action="store_true", help="Backup the SQLite database")
    parser.add_argument("--reset", action="store_true", help="Delete the SQLite database")
    
    args = parser.parse_args()
    
    if args.backup:
        backup_db()
    elif args.reset:
        reset_db()
    else:
        parser.print_help()

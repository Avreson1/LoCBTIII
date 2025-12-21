from backend.database import SessionLocal
from sqlalchemy import text

try:
    db = SessionLocal()
    # Test connection by selecting sqlite_version
    result = db.execute(text("SELECT sqlite_version();"))
    version = result.fetchone()
    print(f"Connection successful. SQLite version: {version[0]}")
    db.close()
except Exception as e:
    print(f"Connection failed: {e}")

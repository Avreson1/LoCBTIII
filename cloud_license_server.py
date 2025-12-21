from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel
import sqlite3
import uuid
import datetime

# --- Configuration ---
# In production on Oracle, use PostgreSQL or a persistent volume for SQLite
DB_FILE = "cloud_licenses.db"
ADMIN_SECRET = "change_this_to_a_complex_secret_key"

app = FastAPI(title="LoCBT Cloud License Authority")

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            client_name TEXT,
            created_at TEXT,
            is_active BOOLEAN DEFAULT 0,
            activated_at TEXT,
            hardware_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Models ---
class LicenseCreate(BaseModel):
    client_name: str

class LicenseVerify(BaseModel):
    key: str
    hardware_id: str

# --- Endpoints ---

@app.post("/generate-key")
def generate_license_key(data: LicenseCreate, x_admin_secret: str = Header(None)):
    """
    Called by your Payment Gateway (e.g., Stripe Webhook) or You manually.
    """
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    key = str(uuid.uuid4()).upper()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO licenses (key, client_name, created_at) VALUES (?, ?, ?)",
              (key, data.client_name, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return {"success": True, "key": key, "client": data.client_name}

@app.post("/verify-activate")
def verify_and_activate(data: LicenseVerify):
    """
    Called by the Local LoCBT App when the user clicks 'Activate'.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Check if key exists
    c.execute("SELECT is_active, hardware_id FROM licenses WHERE key = ?", (data.key,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Invalid License Key")

    is_active, stored_hw_id = row

    # Scenario 1: First time activation
    if not is_active:
        c.execute("UPDATE licenses SET is_active = 1, activated_at = ?, hardware_id = ? WHERE key = ?",
                  (datetime.datetime.now().isoformat(), data.hardware_id, data.key))
        conn.commit()
        conn.close()
        return {"valid": True, "message": "Activation Successful"}

    # Scenario 2: Re-activation (Check Hardware ID lock)
    if stored_hw_id == data.hardware_id:
        conn.close()
        return {"valid": True, "message": "License Valid"}
    else:
        conn.close()
        raise HTTPException(status_code=403, detail="License already verified on a different machine.")

if __name__ == "__main__":
    import uvicorn
    # On Oracle, you'd run this with gunicorn/uvicorn behind Nginx
    uvicorn.run(app, host="0.0.0.0", port=8080)

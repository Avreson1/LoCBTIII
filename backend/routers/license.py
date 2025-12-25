from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import License
from backend.schemas import SuccessResponse
import uuid
import requests
from datetime import datetime
import platform

router = APIRouter()

import os

# Configuration
# Default to localhost, but allow override via environment variable for Production/PythonAnywhere
CLOUD_AUTHORITY_URL = os.getenv("LOCBT_LICENSE_URL", "http://localhost:8080")

@router.post("/payment/mock")
def mock_payment():
    """
    Simulates a payment and returns a valid license key.
    In a real app, this would be a webhook listener for Stripe/PayPal.
    """
    # For the mock, we now need to actually register this key with the Cloud Server
    # so that subsequent activation requests succeed.
    try:
        # Admin secret is hardcoded in cloud_license_server.py for this demo
        headers = {"x-admin-secret": "change_this_to_a_complex_secret_key"}
        payload = {"client_name": "Mock Customer"}
        resp = requests.post(f"{CLOUD_AUTHORITY_URL}/generate-key", json=payload, headers=headers)
        if resp.status_code == 200:
             data = resp.json()
             return {
                "success": True,
                "message": "Payment successful. Key generated on Cloud.",
                "license_key": data['key']
            }
    except Exception as e:
        pass

    # Fallback if cloud server is down (just to keep UI working)
    key = str(uuid.uuid4()).upper()
    return {
        "success": True,
        "message": "Payment successful (Offline Mode).",
        "license_key": key
    }

@router.post("/license/activate", response_model=SuccessResponse)
def activate_license(
    key: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    # 1. Local Check: Is it already active?
    existing = db.query(License).filter(License.key == key).first()
    if existing and existing.is_active:
         return SuccessResponse(success=True, message="License already active locally.")

    # 2. Online Verification
    try:
        hw_id = platform.node() + "-" + platform.machine()
        payload = {"key": key, "hardware_id": hw_id}
        resp = requests.post(f"{CLOUD_AUTHORITY_URL}/verify-activate", json=payload, timeout=5)

        if resp.status_code == 200:
            # Success!
            if not existing:
                new_license = License(
                    key=key,
                    is_active=True,
                    activated_at=datetime.now().isoformat()
                )
                db.add(new_license)
            else:
                existing.is_active = True
                existing.activated_at = datetime.now().isoformat()

            db.commit()
            return SuccessResponse(success=True, message="License activated via Cloud Authority.")

        elif resp.status_code == 403:
            raise HTTPException(status_code=403, detail="License is locked to another machine.")
        elif resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Invalid License Key.")
        else:
            raise HTTPException(status_code=400, detail=f"Activation Failed: {resp.text}")

    except requests.exceptions.ConnectionError:
        # Optional: Allow offline activation code if you implement it
        raise HTTPException(status_code=503, detail="Could not connect to License Server.")

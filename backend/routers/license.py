from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import License
from backend.schemas import SuccessResponse
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/payment/mock")
def mock_payment():
    """
    Simulates a payment and returns a valid license key.
    In a real app, this would be a webhook listener for Stripe/PayPal.
    """
    # Generate a random key
    key = str(uuid.uuid4()).upper()
    return {
        "success": True,
        "message": "Payment successful. Here is your license key.",
        "license_key": key
    }

@router.post("/license/activate", response_model=SuccessResponse)
def activate_license(
    key: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    # Check if key already exists (maybe we pre-generated them?)
    # For this mock, we just trust the key if it looks like a UUID or just insert it as new.
    # To make it slightly more realistic, let's say any key > 10 chars is valid.

    if len(key) < 10:
        raise HTTPException(status_code=400, detail="Invalid license key format.")

    # Check if this specific key is already used/active
    existing = db.query(License).filter(License.key == key).first()
    if existing:
        if existing.is_active:
             return SuccessResponse(success=True, message="License already active.")
        else:
            existing.is_active = True
            existing.activated_at = datetime.now().isoformat()
            db.commit()
            return SuccessResponse(success=True, message="License activated successfully.")

    # Create new active license
    new_license = License(
        key=key,
        is_active=True,
        activated_at=datetime.now().isoformat()
    )
    db.add(new_license)
    db.commit()

    return SuccessResponse(success=True, message="System Activated Successfully!")

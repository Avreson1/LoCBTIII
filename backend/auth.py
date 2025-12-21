from sqlalchemy.orm import Session
from backend.models import Admin
import hashlib

def verify_admin_password(db: Session, username: str, password: str) -> bool:
    # Note: The database has 'admin' as password. In a real app we'd use bcrypt.
    # The existing schema implies plain text or simple hash stored in 'password_hash'.
    # Checking the schema dump: INSERT INTO "admins" VALUES(1,'admin','admin');
    # It seems to be plain text based on the dump. I will treat it as plain text for now
    # to match the existing DB state, but ideally we should hash it.

    user = db.query(Admin).filter(Admin.username == username).first()
    if not user:
        return False

    # If the stored password matches input
    if user.password_hash == password:
        return True

    return False

from fastapi import Header, HTTPException, status

def get_current_admin(authorization: str = Header(None)):
    """
    Validates the admin token.
    For this implementation, we use a simple static token "fake-jwt-token-for-now"
    returned by the login endpoint. In production, use real JWTs.
    """
    if authorization != "Bearer fake-jwt-token-for-now":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

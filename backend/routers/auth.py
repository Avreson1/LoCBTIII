from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import LoginRequest, LoginResponse
from backend.auth import verify_admin_password

router = APIRouter()

@router.post("/login/admin", response_model=LoginResponse)
def login_admin(request: LoginRequest, db: Session = Depends(get_db)):
    if verify_admin_password(db, request.username, request.password):
        return LoginResponse(
            success=True,
            message="Login successful",
            token="fake-jwt-token-for-now"
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

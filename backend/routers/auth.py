from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import LoginRequest, LoginResponse
from backend.auth import verify_admin_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()

@router.post("/login/admin", response_model=LoginResponse)
def login_admin(request: LoginRequest, db: Session = Depends(get_db)):
    if verify_admin_password(db, request.username, request.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username}, expires_delta=access_token_expires
        )
        return LoginResponse(
            success=True,
            message="Login successful",
            token=access_token
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

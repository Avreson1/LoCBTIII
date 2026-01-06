from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.models import Admin

# Configuration
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" # Should be env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    # For now, we are comparing against plain text in DB as per original schema constraint
    # But ideally, we should verify hash.
    # Since existing DB has plain 'admin', we keep plain check for backward compat
    # OR we can just assume the DB stores hashes.
    # Given the previous instruction was to "stick to simple hash", let's assume strict equality for the pre-seeded admin
    # BUT for a security upgrade, we should support hashed.
    # Let's do a hybrid: try verify, if fail, try plain match (legacy).

    if plain_password == hashed_password:
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_admin_password(db: Session, username: str, password: str) -> bool:
    user = db.query(Admin).filter(Admin.username == username).first()
    if not user:
        return False
    if verify_password(password, user.password_hash):
        return True
    return False

def get_current_admin(authorization: str = Header(None)):
    """
    Validates the admin JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username

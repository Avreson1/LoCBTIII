from pydantic import BaseModel
from typing import Optional, List

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

# --- Common Schemas ---
class SuccessResponse(BaseModel):
    success: bool
    message: str

# --- Test Schemas ---
class TestCreate(BaseModel):
    title: str
    duration_minutes: int

class TestResponse(BaseModel):
    id: int
    title: str
    duration_minutes: int
    is_active: bool
    access_key: Optional[str]

    class Config:
        from_attributes = True

# --- Question Schemas ---
class Option(BaseModel):
    label: str
    text: str

class QuestionResponse(BaseModel):
    id: int
    text: str
    options: List[Option] # This will need JSON handling
    # Correct answer not sent to student usually

# --- Student Schemas ---
class StudentLoginRequest(BaseModel):
    student_id: str

class StudentLoginResponse(BaseModel):
    success: bool
    message: str
    student: Optional[dict] = None
    token: Optional[str] = None

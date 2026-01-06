from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Student, Test, Result
from backend.schemas import StudentLoginRequest, StudentLoginResponse, SuccessResponse
from typing import List, Dict, Any
from datetime import datetime
import json

router = APIRouter()

@router.post("/student/login", response_model=StudentLoginResponse)
def student_login(request: StudentLoginRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_id_str == request.student_id).first()
    if not student:
        raise HTTPException(status_code=401, detail="Invalid Student ID")

    return StudentLoginResponse(
        success=True,
        message="Login successful",
        student={"name": student.name, "id": student.id}
    )

@router.get("/student/exam")
def get_exam(db: Session = Depends(get_db)):
    # Get active test
    test = db.query(Test).filter(Test.is_active == True).first()
    if not test:
        raise HTTPException(status_code=404, detail="No active test found")

    # Construct response with questions (hide correct answers)
    questions_data = []
    for q in test.questions:
        # q.options is already a list of dicts or string.
        # Ideally it's stored as JSON. SQLAlchemy might return it as list if type is JSON.
        # But if it's stored as string in older DB, we might need to parse.
        # The new models define it as JSON.

        opts = q.options
        if isinstance(opts, str):
            try:
                opts = json.loads(opts)
            except:
                pass

        questions_data.append({
            "id": q.id,
            "text": q.text,
            "options": opts
        })

    return {
        "test_id": test.id,
        "title": test.title,
        "duration": test.duration_minutes,
        "questions": questions_data
    }

@router.post("/student/submit", response_model=SuccessResponse)
def submit_exam(
    student_id: int = Body(...),
    test_id: int = Body(...),
    answers: Dict[str, str] = Body(...), # QuestionID -> Answer Key (A, B)
    db: Session = Depends(get_db)
):
    # Calculate Score
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    score = 0
    total = 0

    for q in test.questions:
        total += 1
        q_id_str = str(q.id)
        if q_id_str in answers:
            if answers[q_id_str] == q.correct_answer:
                score += 1

    # Save Result
    result = Result(
        test_id=test_id,
        student_id=student_id,
        score=score,
        total_questions=total,
        completed_at=datetime.now().isoformat()
    )
    db.add(result)
    db.commit()

    return SuccessResponse(success=True, message="Exam submitted successfully.")

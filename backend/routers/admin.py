from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import get_current_admin
from typing import List
from backend.models import Test, Question, Student, Result
from backend.schemas import SuccessResponse, TestResponse, TestCreate
from backend.docx_parser import parse_docx_test
import shutil
import os
import uuid
import json
import csv
import io

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/admin/upload-test", response_model=SuccessResponse, dependencies=[Depends(get_current_admin)])
def upload_test(
    file: UploadFile = File(...),
    title: str = "New Test",
    duration: int = 60,
    db: Session = Depends(get_db)
):
    # Save file locally
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse
    try:
        parsed_questions = parse_docx_test(filepath)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not parsed_questions:
        raise HTTPException(status_code=400, detail="No valid questions found in file.")

    # Create Test
    new_test = Test(
        title=title,
        duration_minutes=duration,
        is_active=False
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # Create Questions
    for q in parsed_questions:
        db_q = Question(
            test_id=new_test.id,
            text=q['text'],
            options=q['options'], # SQLAlchemy JSON type handles dict/list
            correct_answer=q['correct_answer']
        )
        db.add(db_q)

    db.commit()

    return SuccessResponse(success=True, message=f"Test '{title}' created with {len(parsed_questions)} questions.")

@router.get("/admin/tests", response_model=List[TestResponse], dependencies=[Depends(get_current_admin)])
def get_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()

@router.post("/admin/tests/{test_id}/publish", response_model=SuccessResponse, dependencies=[Depends(get_current_admin)])
def publish_test(test_id: int, db: Session = Depends(get_db)):
    # Deactivate all tests
    db.query(Test).update({Test.is_active: False})

    # Activate selected test
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    test.is_active = True
    db.commit()
    return SuccessResponse(success=True, message=f"Test '{test.title}' is now active.")

@router.get("/admin/results", dependencies=[Depends(get_current_admin)])
def get_results(db: Session = Depends(get_db)):
    results = db.query(Result).all()
    # Simple list of dicts for now
    data = []
    for r in results:
        data.append({
            "student_name": r.student.name,
            "test_title": r.test.title,
            "score": r.score,
            "total": r.total_questions,
            "date": r.completed_at
        })
    return data

@router.post("/admin/upload-classes", response_model=SuccessResponse, dependencies=[Depends(get_current_admin)])
def upload_classes(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Expect CSV: ID, Name
    content = file.file.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(content))

    count = 0
    for row in csv_reader:
        if len(row) < 2:
            continue
        student_id_str = row[0].strip()
        name = row[1].strip()

        # Check if exists
        existing = db.query(Student).filter(Student.student_id_str == student_id_str).first()
        if not existing:
            new_student = Student(student_id_str=student_id_str, name=name)
            db.add(new_student)
            count += 1

    db.commit()
    return SuccessResponse(success=True, message=f"Imported {count} new students.")

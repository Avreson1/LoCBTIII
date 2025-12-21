from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    logo_url = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=False)
    access_key = Column(String, nullable=True)

    questions = relationship("Question", back_populates="test")
    results = relationship("Result", back_populates="test")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    text = Column(String)
    options = Column(JSON)
    correct_answer = Column(String)

    test = relationship("Test", back_populates="questions")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id_str = Column(String, unique=True, index=True)
    name = Column(String)

    results = relationship("Result", back_populates="student")

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    score = Column(Integer)
    total_questions = Column(Integer)
    completed_at = Column(String)

    test = relationship("Test", back_populates="results")
    student = relationship("Student", back_populates="results")

class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)
    activated_at = Column(String, nullable=True)

from backend.database import SessionLocal
from backend.models import Admin, Test, Question

db = SessionLocal()

# Verify Admin
admin = db.query(Admin).first()
if admin:
    print(f"Admin found: {admin.username}")
else:
    print("No admin found")

# Verify Tests
tests = db.query(Test).all()
print(f"Found {len(tests)} tests")
for t in tests:
    print(f"- Test: {t.title} (Active: {t.is_active})")

# Verify Questions
questions = db.query(Question).filter(Question.test_id == 1).all()
print(f"Found {len(questions)} questions for Test ID 1")

db.close()

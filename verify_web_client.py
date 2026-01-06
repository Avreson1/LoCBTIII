import threading
import time
import os
import sys
import requests
from web_client import app, load_questions

def verify_headless_web():
    print("Verifying Web Client Logic...")

    # 1. Setup Data
    with open("test_questions.csv", "w") as f:
        f.write("question,A,B,C,D,answer\n")
        f.write("Q1,OptA,OptB,OptC,OptD,A\n")

    # Mock globals for the imported app module
    # We need to monkeypatch the file path variable in the module if we can,
    # or just rename our test file to match the expected constant.
    # web_client.QUESTIONS_FILE is a global string, we can't easily change it after import
    # unless we modify the file or reload.
    # Easiest way: just write to 'questions.csv' (backup original if needed).

    if os.path.exists("questions.csv"):
        os.rename("questions.csv", "questions.csv.bak")

    with open("questions.csv", "w") as f:
        f.write("question,A,B,C,D,answer\n")
        f.write("Q1,OptA,OptB,OptC,OptD,A\n")

    load_questions()

    # 2. Test Flask Client
    client = app.test_client()

    # Login Page
    resp = client.get('/')
    assert resp.status_code == 200
    assert b"LoCBT Login" in resp.data
    print("Login Page OK")

    # Start Exam
    resp = client.post('/exam', data={'fullname': 'TestUser', 'regno': '123'})
    assert resp.status_code == 200
    assert b"Q1" in resp.data
    print("Exam Page OK")

    # Submit Exam
    resp = client.post('/submit', data={'fullname': 'TestUser', 'regno': '123', 'q0': 'A'})
    assert resp.status_code == 200
    assert b"1 / 1" in resp.data
    print("Result Page OK")

    # Check CSV Result
    assert os.path.exists("results.csv")
    with open("results.csv", 'r') as f:
        content = f.read()
        assert "TestUser" in content
        assert "100.0" in content
    print("Result CSV OK")

    # Cleanup
    if os.path.exists("questions.csv.bak"):
        os.remove("questions.csv")
        os.rename("questions.csv.bak", "questions.csv")
    else:
        os.remove("questions.csv")

    if os.path.exists("test_questions.csv"):
        os.remove("test_questions.csv")

if __name__ == "__main__":
    verify_headless_web()

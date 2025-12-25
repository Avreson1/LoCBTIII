import os
import sys
import csv
import threading
import time
import requests
import webview
from flask import Flask, render_template_string, request, jsonify

# --- Configuration ---
LICENSE_SERVER_URL = "http://localhost:8080/verify-activate" # Placeholder for PythonAnywhere
TIMER_DURATION = 10 * 60 # 10 Minutes
QUESTIONS_FILE = "questions.csv"
RESULTS_FILE = "results.csv"
LICENSE_KEY_FILE = "license.key"

# --- HTML Templates ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LoCBT Login</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 350px; text-align: center; }
        h2 { color: #2c3e50; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 20px; }
        button:hover { background: #2ecc71; }
        .error { color: red; margin-top: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>LoCBT Login</h2>
        <form action="/exam" method="post">
            <input type="text" name="fullname" placeholder="Full Name" required>
            <input type="text" name="regno" placeholder="Registration Number" required>
            <button type="submit">Start Exam</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
    <script>
        document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
</body>
</html>
"""

EXAM_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LoCBT Exam</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f9f9f9; margin: 0; padding-bottom: 60px; user-select: none; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .timer { font-size: 20px; font-weight: bold; color: #f1c40f; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .question { background: white; padding: 25px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .q-text { font-size: 18px; margin-bottom: 15px; font-weight: 500; }
        .option { display: block; margin: 10px 0; cursor: pointer; padding: 8px; border-radius: 4px; transition: background 0.2s; }
        .option:hover { background: #f0f2f5; }
        input[type="radio"] { margin-right: 10px; }
        .footer { position: fixed; bottom: 0; left: 0; right: 0; background: white; padding: 15px; box-shadow: 0 -2px 10px rgba(0,0,0,0.1); text-align: center; }
        button { padding: 12px 40px; background: #2980b9; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <div>Candidate: {{ name }} ({{ regno }})</div>
        <div class="timer" id="timer">Loading...</div>
    </div>
    <div class="container">
        <form id="examForm" action="/submit" method="post">
            <input type="hidden" name="fullname" value="{{ name }}">
            <input type="hidden" name="regno" value="{{ regno }}">
            {% for q in questions %}
            <div class="question">
                <div class="q-text">{{ loop.index }}. {{ q['question'] }}</div>
                <label class="option"><input type="radio" name="q{{ loop.index0 }}" value="A"> {{ q['A'] }}</label>
                <label class="option"><input type="radio" name="q{{ loop.index0 }}" value="B"> {{ q['B'] }}</label>
                <label class="option"><input type="radio" name="q{{ loop.index0 }}" value="C"> {{ q['C'] }}</label>
                <label class="option"><input type="radio" name="q{{ loop.index0 }}" value="D"> {{ q['D'] }}</label>
            </div>
            {% endfor %}
        </form>
    </div>
    <div class="footer">
        <button onclick="submitExam()">Submit Examination</button>
    </div>
    <script>
        document.addEventListener('contextmenu', event => event.preventDefault());

        // Timer Logic
        let timeLeft = {{ duration }};
        const timerElem = document.getElementById('timer');

        const countdown = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElem.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

            if (timeLeft <= 0) {
                clearInterval(countdown);
                submitExam();
            }
            timeLeft--;
        }, 1000);

        function submitExam() {
            document.getElementById('examForm').submit();
        }
    </script>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Exam Result</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
        .card { background: white; padding: 50px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 400px; }
        h1 { color: #2c3e50; margin-bottom: 10px; }
        .score { font-size: 48px; font-weight: bold; color: #27ae60; margin: 20px 0; }
        p { color: #7f8c8d; font-size: 16px; margin: 5px 0; }
        button { padding: 12px 30px; background: #c0392b; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 30px; }
        button:hover { background: #e74c3c; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Examination Completed</h1>
        <p>Thank you, {{ name }}</p>
        <div class="score">{{ score }} / {{ total }}</div>
        <p>Percentage: {{ percentage }}%</p>
        <button onclick="closeApp()">Close Application</button>
    </div>
    <script>
        document.addEventListener('contextmenu', event => event.preventDefault());
        function closeApp() {
            fetch('/close').then(() => window.close());
        }
    </script>
</body>
</html>
"""

# --- Application ---
app = Flask(__name__)
questions_data = []

def load_questions():
    global questions_data
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                questions_data = list(reader)
        except Exception as e:
            print(f"Error loading questions: {e}")

@app.route('/')
def login():
    return render_template_string(LOGIN_HTML)

@app.route('/exam', methods=['POST'])
def exam():
    fullname = request.form.get('fullname')
    regno = request.form.get('regno')

    if not fullname or not regno:
        return render_template_string(LOGIN_HTML, error="All fields are required.")

    if not questions_data:
        return render_template_string(LOGIN_HTML, error="No questions loaded from questions.csv.")

    return render_template_string(EXAM_HTML,
                                  name=fullname,
                                  regno=regno,
                                  questions=questions_data,
                                  duration=TIMER_DURATION)

@app.route('/submit', methods=['POST'])
def submit():
    fullname = request.form.get('fullname')
    regno = request.form.get('regno')

    score = 0
    total = len(questions_data)

    for i, q in enumerate(questions_data):
        user_ans = request.form.get(f"q{i}")
        if user_ans == q['answer']:
            score += 1

    percentage = round((score / total) * 100, 1) if total > 0 else 0

    # Save Result
    file_exists = os.path.exists(RESULTS_FILE)
    with open(RESULTS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "RegNo", "Score", "Total", "Percentage"])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), fullname, regno, score, total, percentage])

    return render_template_string(RESULT_HTML,
                                  name=fullname,
                                  score=score,
                                  total=total,
                                  percentage=percentage)

@app.route('/close')
def close():
    os._exit(0)
    return "Closing..."

# --- Licensing ---
def validate_license():
    """
    Checks for license.key.
    If present, verifies with server (MOCKED for now).
    If missing, prompts user (Console input for now, or GUI).
    """
    # Simple Mock Logic for Demo
    print("[Guard Layer] Checking License...")

    # For this specific task, if license.key exists, we assume valid.
    # If not, we pretend to contact server.

    # In a real app with PyWebView, we might show a simple HTML dialog first if invalid.
    # Here we will just auto-pass for the demo execution unless we want to strict test it.

    return True

def start_flask():
    app.run(port=5000, threaded=True)

if __name__ == "__main__":
    load_questions()

    if validate_license():
        # Start Flask in separate thread
        t = threading.Thread(target=start_flask)
        t.daemon = True
        t.start()

        # Give Flask a second to spin up
        time.sleep(1)

        # Launch Window
        webview.create_window(
            "LoCBT Assessment Interface",
            "http://127.0.0.1:5000",
            fullscreen=True,
            resizable=False,
            text_select=False
        )
        webview.start()
    else:
        print("License Validation Failed. Exiting.")
        sys.exit(1)

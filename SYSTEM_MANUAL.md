# System Manual & Operations Guide
## Local Wireless CBT Platform

### 1. Overview
This system allows an Administrator to host exams on a local Wi-Fi network. Students connect via browser to take tests. No internet is required.

### 2. Administrator Guide

#### A. Starting the System
1.  Open the project folder.
2.  Run `python run.py`.
3.  Keep the window open.
4.  Navigate to `http://localhost:8000/admin`.
5.  **Default Login:**
    *   **Username:** `admin`
    *   **Password:** `admin`

#### B. Managing Classes (Student Roster)
1.  Go to the **"Manage Classes"** tab.
2.  Create a CSV file with student data (Column A: ID, Column B: Name).
3.  Upload the CSV to create a "Class Profile".
    *   *Note:* Students can only login if their ID matches what you uploaded (unless you allow guest access).

#### C. Creating a Test (Relaxed Format)
Upload a `.docx` file. The system now supports flexible formatting:

**Valid Formats:**
```text
1. What is 2+2?
(A) 3
(B) 4
Ans: B

Q: What is the capital of France?
A. Paris
B. London
Key: A
```

#### D. Publishing
*   Go to **Dashboard**.
*   Click **"Publish"** on the test you want to go live.
*   Only one test can be active at a time.

### 3. Student Guide
1.  Connect to the Exam Wi-Fi.
2.  Open Browser (Chrome/Safari).
3.  Go to the IP address written on the board (e.g., `192.168.1.5:8000`).
4.  Enter your **Student ID**.
5.  Take the test. Do not switch tabs.

### 4. Troubleshooting
*   **"BadZipFile" Error:** The uploaded file is not a valid Word document. Open it in Word and "Save As" a fresh `.docx`.
*   **"No Questions Found":** Check your text format. Ensure answers are clearly marked with `ANSWER:`, `Ans:`, or `Key:`.

# Operational Directives & Standard Operating Procedures (SOP)
## Local Wireless CBT Platform

This document outlines the mandatory directives for Administrators, Proctors, and Content Creators to ensure the smooth operation of the CBT System.

---

### I. Administrator Directives (System Setup)

**Directive 1.1: Network Configuration**
*   The Host Machine (Admin Laptop) **must** be connected to a robust Local Area Network (Wi-Fi Router).
*   **Internet access is NOT required**, but the Wi-Fi signal must be strong enough to support all student devices.
*   The Host Machine should have a static IP address if possible, to prevent disconnection if the router restarts.

**Directive 1.2: Server Initialization**
1.  Open the terminal in the project directory.
2.  Execute `python run.py`.
3.  **DO NOT** close the terminal window. Minimizing is permitted.
4.  Note the **Student URL** displayed in the logs (e.g., `http://192.168.1.5:8000/`). Write this on the classroom whiteboard.

**Directive 1.3: Data Security**
*   The database (`cbt.db`) is stored locally.
*   **Backup Directive:** After every major exam, copy the `cbt.db` file to a secure backup location (USB drive or cloud storage).

---

### II. Test Formulation Directives (Content Creation)

**Directive 2.1: File Format**
*   All tests must be created using Microsoft Word (`.docx`).
*   Images and complex formatting (tables, footnotes) are **currently not supported** and will be ignored.

**Directive 2.2: Strict Syntax Template**
Content creators must adhere to the following syntax **exactly**. Deviations will cause the upload to fail.

*   **Questions:** Must start with `Q:` followed by the text.
*   **Options:** Must start with a capital letter and a dot (e.g., `A.`, `B.`).
*   **Answers:** Must be on a new line starting with `ANSWER:` followed by the correct letter.

**Example:**
```text
Q: What is the boiling point of water?
A. 90 C
B. 100 C
C. 120 C
D. 150 C
ANSWER: B
```

---

### III. Exam Day Protocol (Proctoring)

**Directive 3.1: Pre-Flight Check (15 Minutes Before)**
1.  Start the Server (`python run.py`).
2.  Login to Admin Dashboard (`/admin`).
3.  Verify the correct test is marked **"Active"**.
4.  Connect a test device (phone) to the Wi-Fi and verify the **Student URL** loads the login page.

**Directive 3.2: Student Onboarding**
1.  Instruct students to connect to the Exam Wi-Fi.
2.  Instruct students to open Chrome or Safari.
3.  Instruct students to type the **Student URL** exactly.
4.  Students must enter their unique **Student ID**.

**Directive 3.3: Active Monitoring**
*   Proctors should monitor the "Results" tab in the Admin Dashboard.
*   **Cheating Alert:** The system logs if a student switches tabs. Proctors should walk the room to enforce physical compliance.

---

### IV. Student Code of Conduct (Directives for Candidates)

1.  **Fullscreen Mode:** You are required to keep the browser window maximized.
2.  **No Tab Switching:** Switching to another tab or application will trigger a warning log. Repeated violations may result in disqualification.
3.  **Submission:** You must click "Submit" before the timer reaches 00:00. The system will auto-submit if time expires, but manual submission is safer.
4.  **Do Not Refresh:** Avoid reloading the page unless instructed by a Proctor.

---

### V. Troubleshooting Directives

*   **Issue:** "Connection Refused" on student device.
    *   **Action:** Check if Host Machine firewall is blocking Port 8000. Allow Python through firewall.
    *   **Action:** Ensure student is on the *exact same* Wi-Fi network name (SSID).
*   **Issue:** "No Active Test" error.
    *   **Action:** Admin must go to Dashboard and click "Publish" on the desired test.

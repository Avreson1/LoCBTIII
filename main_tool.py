import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from PIL import Image, ImageTk
import random
import threading
import time
import os
import datetime
import json
import requests
import platform
import uuid

# --- Constants & Config ---
DB_NAME = "results.db"
ADMIN_PIN = "1234" # Hardcoded for this phase
LICENSE_FILE = "license.json"
CLOUD_URL = "http://localhost:8080" # Reference implementation

class LicenseManager:
    """Handles offline license check and online activation."""
    def __init__(self):
        self.key = None
        self.is_active = False
        self.check_local()

    def check_local(self):
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, "r") as f:
                    data = json.load(f)
                    self.key = data.get("key")
                    # In a real app, verify signature/hardware ID match here
                    if data.get("is_active"):
                        self.is_active = True
            except:
                pass

    def activate(self, key):
        """Calls cloud server to activate."""
        try:
            hw_id = platform.node() + "-" + platform.machine()
            payload = {"key": key, "hardware_id": hw_id}
            # Timeout set short for UI responsiveness
            resp = requests.post(f"{CLOUD_URL}/verify-activate", json=payload, timeout=5)

            if resp.status_code == 200:
                self.key = key
                self.is_active = True
                self.save_local()
                return True, "Activation Successful"
            elif resp.status_code == 403:
                return False, "License locked to another machine."
            else:
                return False, "Invalid Key"
        except Exception as e:
            return False, f"Connection Error: {e}"

    def save_local(self):
        with open(LICENSE_FILE, "w") as f:
            json.dump({"key": self.key, "is_active": True, "hw_id": platform.node()}, f)

class DatabaseManager:
    """Handles SQLite connection and result storage."""
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                surname TEXT,
                reg_no TEXT,
                subject TEXT,
                score INTEGER,
                total_questions INTEGER,
                percentage REAL,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_result(self, surname, reg_no, subject, score, total):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        percentage = (score / total) * 100 if total > 0 else 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO results (surname, reg_no, subject, score, total_questions, percentage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (surname, reg_no, subject, score, total, percentage, timestamp))
        conn.commit()
        conn.close()

    def get_all_results(self):
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM results", conn)
        conn.close()
        return df

class QuestionManager:
    """Handles CSV loading and randomization."""
    def __init__(self):
        self.questions = []

    def load_questions(self, filepath):
        try:
            df = pd.read_csv(filepath)
            # Normalize column names
            df.columns = [c.lower().strip() for c in df.columns]
            required_cols = {'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option'}
            if not required_cols.issubset(df.columns):
                raise ValueError(f"Missing columns. Required: {required_cols}")

            # Convert to list of dicts
            self.questions = df.to_dict('records')
            self.randomize()
            return True, f"Loaded {len(self.questions)} questions."
        except Exception as e:
            return False, str(e)

    def randomize(self):
        """Shuffles questions and options."""
        random.shuffle(self.questions)
        for q in self.questions:
            # Shuffle options
            opts = [
                ('A', q['option_a']),
                ('B', q['option_b']),
                ('C', q['option_c']),
                ('D', q['option_d'])
            ]
            correct_val = q[f"option_{q['correct_option'].lower()}"]
            random.shuffle(opts)

            # Re-assign options and find new correct key
            q['shuffled_options'] = opts # List of (Key, Value) tuples like [('A', '4'), ('B', '3')...]
            # Actually, we need to map the new layout to A, B, C, D for the UI
            # But keep track of which one is correct.

            # Let's simplify: Just shuffle the list of answer texts.
            # Then find which one was the original correct answer.
            # Then store the new correct index/key.

            # Correct answer text
            correct_text = str(correct_val)

            # List of option texts
            opt_texts = [str(q['option_a']), str(q['option_b']), str(q['option_c']), str(q['option_d'])]
            random.shuffle(opt_texts)

            q['ui_options'] = {
                'A': opt_texts[0],
                'B': opt_texts[1],
                'C': opt_texts[2],
                'D': opt_texts[3]
            }

            # Find new key for correct text
            for key, val in q['ui_options'].items():
                if val == correct_text:
                    q['new_correct_key'] = key
                    break

class LoCBTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LoCBT Commercial Edition")
        self.geometry("800x600")

        # Managers
        self.db_manager = DatabaseManager()
        self.question_manager = QuestionManager()
        self.license_manager = LicenseManager()

        # State
        self.current_frame = None
        self.student_details = {}

        # Styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)

        # Bindings
        self.bind("<Escape>", self.exit_fullscreen_admin)

        # Check License
        if not self.license_manager.is_active:
             self.show_activation()
        else:
             self.attributes("-fullscreen", True) # Kiosk Mode Only if Licensed
             self.show_login()

    def show_activation(self):
        self.switch_frame(ActivationFrame)

    def exit_fullscreen_admin(self, event=None):
        # Secret admin exit (for development/admin usage)
        # In real kiosk, this might be disabled or password protected
        if messagebox.askyesno("Exit", "Exit Application?"):
            self.destroy()

    def switch_frame(self, frame_class, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.switch_frame(LoginFrame)

    def show_admin(self):
        self.switch_frame(AdminFrame)

    def show_exam(self):
        self.switch_frame(ExamFrame)

# --- Frames ---

class ActivationFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="#333")

        container = tk.Frame(self, bg="white", padx=50, pady=50)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Software Activation", font=("Helvetica", 20, "bold"), bg="white").pack(pady=20)
        tk.Label(container, text="This software is unlicensed.", bg="white", fg="red").pack()
        tk.Label(container, text="Please enter your license key to activate.", bg="white").pack(pady=(0, 20))

        self.key_entry = ttk.Entry(container, width=40)
        self.key_entry.pack(pady=10)

        ttk.Button(container, text="Activate Online", command=self.activate).pack(pady=20)
        tk.Label(container, text="Server: " + CLOUD_URL, font=("Arial", 8), fg="gray", bg="white").pack()

    def activate(self):
        key = self.key_entry.get().strip()
        if not key: return

        success, msg = self.master.license_manager.activate(key)
        if success:
            messagebox.showinfo("Success", "Activation Successful! Restarting...")
            self.master.attributes("-fullscreen", True)
            self.master.show_login()
        else:
            messagebox.showerror("Activation Failed", msg)

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="#f0f0f0")

        container = tk.Frame(self, bg="white", padx=40, pady=40, relief="raised", borderwidth=1)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Student Login", font=("Helvetica", 24, "bold"), bg="white", fg="#333").pack(pady=(0, 20))

        # Inputs
        tk.Label(container, text="Surname:", bg="white").pack(anchor="w")
        self.surname_entry = ttk.Entry(container, width=30)
        self.surname_entry.pack(pady=(0, 10))

        tk.Label(container, text="Registration Number:", bg="white").pack(anchor="w")
        self.reg_entry = ttk.Entry(container, width=30)
        self.reg_entry.pack(pady=(0, 10))

        tk.Label(container, text="Subject:", bg="white").pack(anchor="w")
        self.subject_var = tk.StringVar()
        # Scan directory for CSVs or just hardcode for now
        subjects = [f.replace('.csv', '').title() for f in os.listdir('.') if f.endswith('.csv')]
        if not subjects: subjects = ["No Subjects Found"]
        self.subject_combo = ttk.Combobox(container, textvariable=self.subject_var, values=subjects, state="readonly")
        self.subject_combo.pack(pady=(0, 20))
        if subjects: self.subject_combo.current(0)

        ttk.Button(container, text="Start Exam", command=self.login).pack(fill="x", pady=5)

        # Admin Link
        tk.Button(container, text="Admin Login", command=self.admin_prompt, bg="white", fg="blue", bd=0, cursor="hand2").pack(pady=10)

    def login(self):
        surname = self.surname_entry.get().strip()
        reg = self.reg_entry.get().strip()
        subject = self.subject_var.get()

        if not surname or not reg or not subject:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        csv_file = f"{subject.lower()}.csv"
        if not os.path.exists(csv_file):
            messagebox.showerror("Error", f"Subject file {csv_file} not found.")
            return

        success, msg = self.master.question_manager.load_questions(csv_file)
        if not success:
            messagebox.showerror("Error", msg)
            return

        self.master.student_details = {
            "surname": surname,
            "reg_no": reg,
            "subject": subject
        }
        self.master.show_exam()

    def admin_prompt(self):
        pin = tk.simpledialog.askstring("Admin Login", "Enter Admin PIN:", show="*")
        if pin == ADMIN_PIN:
            self.master.show_admin()
        elif pin is not None:
            messagebox.showerror("Error", "Invalid PIN")

class AdminFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="#e0e0e0")

        header = tk.Frame(self, bg="#333", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Admin Control Panel", fg="white", bg="#333", font=("Helvetica", 18)).pack(side="left", padx=20, pady=10)
        tk.Button(header, text="Logout", command=master.show_login, bg="#555", fg="white").pack(side="right", padx=20)

        content = tk.Frame(self, bg="#e0e0e0")
        content.pack(expand=True, fill="both", padx=50, pady=50)

        # Actions
        btn_frame = tk.Frame(content, bg="#e0e0e0")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="View Results", command=self.view_results).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Export Results to CSV", command=self.export_results).grid(row=0, column=1, padx=10)

        # Results Table
        cols = ("ID", "Surname", "Reg No", "Subject", "Score", "%", "Time")
        self.tree = ttk.Treeview(content, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(expand=True, fill="both")

        self.load_data()

    def load_data(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)

        df = self.master.db_manager.get_all_results()
        if not df.empty:
            for index, row in df.iterrows():
                self.tree.insert("", "end", values=(
                    row['id'], row['surname'], row['reg_no'], row['subject'],
                    f"{row['score']}/{row['total_questions']}", f"{row['percentage']:.1f}", row['timestamp']
                ))

    def view_results(self):
        self.load_data()

    def export_results(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            df = self.master.db_manager.get_all_results()
            df.to_csv(filename, index=False)
            messagebox.showinfo("Success", "Results exported successfully.")

class ExamFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg="white")

        # State
        self.questions = self.master.question_manager.questions
        self.current_idx = 0
        self.answers = {} # {idx: 'A'/'B'...}
        self.time_left = 60 * 10 # 10 Minutes default
        self.running = True

        # Top Bar
        top_bar = tk.Frame(self, bg="#333", height=50)
        top_bar.pack(fill="x")

        details = self.master.student_details
        tk.Label(top_bar, text=f"Student: {details.get('surname', '')} ({details.get('reg_no', '')})",
                 fg="white", bg="#333", font=("Helvetica", 12)).pack(side="left", padx=20)

        self.timer_label = tk.Label(top_bar, text="00:00", fg="yellow", bg="#333", font=("Courier", 16, "bold"))
        self.timer_label.pack(side="right", padx=20)

        # Main Area
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(expand=True, fill="both", padx=50, pady=20)

        self.q_label = tk.Label(self.content_frame, text="", wraplength=700, font=("Helvetica", 16), bg="white", justify="left")
        self.q_label.pack(anchor="w", pady=(0, 20))

        self.img_label = tk.Label(self.content_frame, bg="white")
        self.img_label.pack(pady=10)

        self.var = tk.StringVar()
        self.radios = []
        for i, opt_key in enumerate(['A', 'B', 'C', 'D']):
            r = ttk.Radiobutton(self.content_frame, text="", variable=self.var, value=opt_key, command=self.save_answer)
            r.pack(anchor="w", pady=5)
            self.radios.append(r)

        # Navigation
        nav_frame = tk.Frame(self, bg="white")
        nav_frame.pack(fill="x", padx=50, pady=20)

        ttk.Button(nav_frame, text="Previous", command=self.prev_q).pack(side="left")
        self.next_btn = ttk.Button(nav_frame, text="Next", command=self.next_q)
        self.next_btn.pack(side="right")
        self.submit_btn = ttk.Button(nav_frame, text="Submit Exam", command=self.submit)

        self.load_question()
        self.update_timer()

    def update_timer(self):
        if not self.running: return

        mins, secs = divmod(self.time_left, 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        if self.time_left <= 0:
            self.submit()
        else:
            self.time_left -= 1
            self.after(1000, self.update_timer)

    def load_question(self):
        q = self.questions[self.current_idx]

        # Question Text
        self.q_label.config(text=f"{self.current_idx + 1}. {q['question']}")

        # Image
        if pd.notna(q.get('image_path')) and q.get('image_path'):
            try:
                img_path = q['image_path']
                if os.path.exists(img_path):
                    load = Image.open(img_path)
                    load = load.resize((200, 200), Image.Resampling.LANCZOS)
                    render = ImageTk.PhotoImage(load)
                    self.img_label.config(image=render)
                    self.img_label.image = render
                else:
                    self.img_label.config(image='', text="[Image Not Found]")
            except:
                self.img_label.config(image='')
        else:
            self.img_label.config(image='')

        # Options
        ui_opts = q['ui_options']
        for i, r in enumerate(self.radios):
            key = ['A', 'B', 'C', 'D'][i]
            r.config(text=f"{key}. {ui_opts[key]}")

        # Selection
        self.var.set(self.answers.get(self.current_idx, ""))

        # Buttons
        if self.current_idx == len(self.questions) - 1:
            self.next_btn.pack_forget()
            self.submit_btn.pack(side="right")
        else:
            self.submit_btn.pack_forget()
            self.next_btn.pack(side="right")

    def save_answer(self):
        if self.var.get():
            self.answers[self.current_idx] = self.var.get()

    def next_q(self):
        self.save_answer()
        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self.load_question()

    def prev_q(self):
        self.save_answer()
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_question()

    def submit(self):
        self.running = False
        # Calculate Score
        score = 0
        for idx, ans in self.answers.items():
            q = self.questions[idx]
            # 'ans' is the UI option key (A, B, C, D) selected by user
            # 'new_correct_key' is the Key in 'ui_options' that corresponds to the correct answer text
            if ans == q.get('new_correct_key'):
                score += 1

        # Save Result
        d = self.master.student_details
        self.master.db_manager.save_result(
            d['surname'], d['reg_no'], d['subject'], score, len(self.questions)
        )

        messagebox.showinfo("Submitted", f"Exam Submitted!\nYour Score: {score}/{len(self.questions)}")
        self.master.show_login()

def run():
    app = LoCBTApp()
    app.mainloop()

if __name__ == "__main__":
    run()

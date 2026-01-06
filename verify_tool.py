import threading
import time
import os
import sys

# Since main_tool uses Tkinter mainloop which blocks, we cannot easily automate the GUI interaction
# from a script without a proper GUI testing framework like Selenium or specialized Tkinter test tools.
# However, we can verify that the code *runs* and the classes instantiate correctly.

def verify_headless():
    print("Verifying imports and classes...")
    try:
        from main_tool import DatabaseManager, QuestionManager

        # Test DB
        print("Testing DatabaseManager...")
        db = DatabaseManager("test_results.db")
        db.save_result("TestUser", "REG123", "Maths", 10, 20)
        df = db.get_all_results()
        assert len(df) == 1
        assert df.iloc[0]['surname'] == "TestUser"
        print("DB Test Passed.")

        # Test Questions
        print("Testing QuestionManager...")
        qm = QuestionManager()
        # Create dummy csv
        with open("test_maths.csv", "w") as f:
            f.write("question,option_a,option_b,option_c,option_d,correct_option,image_path\n")
            f.write("Q1,A,B,C,D,A,\n")

        success, msg = qm.load_questions("test_maths.csv")
        assert success
        assert len(qm.questions) == 1
        q = qm.questions[0]
        assert 'ui_options' in q
        assert 'new_correct_key' in q
        print("Question Test Passed.")

        # Cleanup
        os.remove("test_results.db")
        os.remove("test_maths.csv")
        print("Cleanup done.")

    except Exception as e:
        print(f"Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_headless()

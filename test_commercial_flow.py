import requests
import json
import os
import time
import subprocess
import signal

CLOUD_PORT = 8080
APP_PORT = 8000
CLOUD_URL = f"http://localhost:{CLOUD_PORT}"
APP_URL = f"http://localhost:{APP_PORT}/api"

def start_server(script, port, logfile):
    print(f"Starting {script} on port {port}...")
    # Using python to run the script
    # For cloud server: python cloud_license_server.py
    # For app server: python run.py

    # We need to set PORT env var or arguments if the script supports it.
    # cloud_license_server.py has port 8080 hardcoded in main block.
    # run.py has port 8000 hardcoded.

    with open(logfile, "w") as out:
        proc = subprocess.Popen(["python", script], stdout=out, stderr=out)
    return proc

def test_integration():
    print("="*50)
    print("INTEGRATION TEST: LICENSING")
    print("="*50)

    # 1. Cleanup
    if os.path.exists("cbt.db"):
        # We need to clear license table to test fresh activation
        # But we can just rely on mocking the payment/activation flow
        import sqlite3
        conn = sqlite3.connect("cbt.db")
        try:
            conn.execute("DELETE FROM licenses")
            conn.commit()
            print("Cleared local licenses.")
        except:
            pass
        conn.close()

    if os.path.exists("cloud_licenses.db"):
        os.remove("cloud_licenses.db")

    if os.path.exists("license.json"):
        os.remove("license.json")

    # 2. Start Cloud Server
    cloud_proc = start_server("cloud_license_server.py", CLOUD_PORT, "cloud_server.log")
    time.sleep(2) # Wait for startup

    # 3. Start Local Web App
    app_proc = start_server("run.py", APP_PORT, "app_server.log")
    time.sleep(5) # Wait for startup

    try:
        session = requests.Session()

        # 4. Generate Key on Cloud (Simulate Stripe Webhook)
        print("\n[Step 1] Purchasing License on Cloud...")
        headers = {"x-admin-secret": "change_this_to_a_complex_secret_key"}
        payload = {"client_name": "Test Customer"}
        resp = requests.post(f"{CLOUD_URL}/generate-key", json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"FAILED to generate key: {resp.text}")
            return

        license_key = resp.json()['key']
        print(f"Generated Key: {license_key}")

        # 5. Verify App is Locked
        print("\n[Step 2] Verifying App is Locked...")
        resp = session.get(f"{APP_URL}/admin/tests")
        if resp.status_code == 403:
            print("SUCCESS: App returned 403 Forbidden (License Required).")
        else:
            print(f"FAILURE: App returned {resp.status_code}. Expected 403.")

        # 6. Activate App with Key
        print("\n[Step 3] Activating App...")
        payload = {"key": license_key}
        resp = session.post(f"{APP_URL}/license/activate", json=payload)

        if resp.status_code == 200:
            print(f"SUCCESS: Activation Response: {resp.json()['message']}")
        else:
            print(f"FAILURE: Activation Failed: {resp.text}")
            return

        # 7. Verify App is Unlocked
        print("\n[Step 4] Verifying App is Unlocked...")
        # Need auth now (JWT)
        # Login first
        l_resp = session.post(f"{APP_URL}/login/admin", json={"username": "admin", "password": "admin"})
        token = l_resp.json()['token']
        headers = {"Authorization": f"Bearer {token}"}

        resp = session.get(f"{APP_URL}/admin/tests", headers=headers)
        if resp.status_code == 200:
            print("SUCCESS: App returned 200 OK.")
        else:
            print(f"FAILURE: App returned {resp.status_code}. Expected 200.")

        # 8. Test Tkinter Logic (Headless)
        print("\n[Step 5] Testing Tkinter Logic...")
        from main_tool import LicenseManager
        lm = LicenseManager()
        # Should be inactive initially (unless we share same folder and key file?)
        # main_tool uses license.json, web app uses cbt.db. They are separate.
        # So we activate Tkinter app separately using SAME key.

        print("Activating Tkinter App with SAME key...")
        success, msg = lm.activate(license_key)
        # Should FAIL because key is already used?
        # Check cloud_license_server.py logic:
        # "If stored_hw_id == data.hardware_id: return Valid"
        # "Else: return 403"
        # Since we run on same machine, HW ID is same. So it should SUCCEED (Re-install scenario).

        if success:
            print("SUCCESS: Tkinter App Activated (Re-use valid).")
        else:
            print(f"FAILURE: Tkinter App Activation Failed: {msg}")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print("\nStopping Servers...")
        os.kill(cloud_proc.pid, signal.SIGTERM)
        os.kill(app_proc.pid, signal.SIGTERM)

if __name__ == "__main__":
    test_integration()

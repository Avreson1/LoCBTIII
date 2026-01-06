# LoCBT: Deployment & Commercialization Guide

This guide outlines how to transform **LoCBT** from a local project into a distributed commercial software product using **Oracle Cloud** for licensing control.

---

## 1. Architecture Strategy

To commercialize this software, you must separate the **Product** (what you sell) from the **Authority** (what you control).

### A. The Product (Local App)
*   **What it is:** The software running on the School/Admin's laptop.
*   **Components:** Python Backend (`run.py`) + React Frontend.
*   **Role:** Runs the exam **offline** on a local Wi-Fi.
*   **Constraint:** It must "phone home" to your Cloud Server *once* to activate, but then can run offline (validated by a locally stored, signed token).

### B. The Authority (Oracle Cloud)
*   **What it is:** A lightweight server you host online.
*   **Code:** `cloud_license_server.py` (provided in repo).
*   **Role:** Generates license keys, validates purchases, and prevents key sharing (by locking keys to Hardware IDs).

---

## 2. Oracle Cloud Setup (The Authority)

You will host `cloud_license_server.py` on an Oracle Cloud "Always Free" instance.

### Step-by-Step Deployment
1.  **Create Instance:**
    *   Sign up for Oracle Cloud Free Tier.
    *   Create a **Compute VM** (Ubuntu 22.04 or Oracle Linux).
    *   Allow Ingress Traffic on Port 80 (HTTP) and 443 (HTTPS) in the Security List.

2.  **Setup Environment:**
    *   SSH into your VM: `ssh ubuntu@<your-oracle-ip>`
    *   Install Python & Dependencies:
        ```bash
        sudo apt update && sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx
        ```

3.  **Deploy Code:**
    *   Copy `cloud_license_server.py` to the VM.
    *   Run it using a robust server (Gunicorn):
        ```bash
        pip install fastapi uvicorn gunicorn
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker cloud_license_server:app --bind 127.0.0.1:8000 --daemon
        ```

4.  **Expose to Internet (Nginx & SSL):**
    *   Configure Nginx as a Reverse Proxy to forward port 80 -> 8000.
    *   Use `certbot --nginx` to get a free HTTPS certificate.
    *   **Result:** You now have an API at `https://license.yourdomain.com/verify-activate`.

---

## 3. Packaging the Product (for Customers)

You cannot ask customers to "run `npm install`". You must give them a single `.exe` file.

### A. Build the Frontend
1.  Run `cd frontend && npm run build`.
2.  This creates `frontend/dist`. The backend is already configured to serve this folder.

### B. Freeze with PyInstaller
PyInstaller bundles Python and all dependencies into one executable.

1.  **Install:** `pip install pyinstaller`
2.  **Build Command:**
    ```bash
    pyinstaller --name "LoCBT_Pro" \
      --add-data "frontend/dist:frontend/dist" \
      --add-data "cbt.db:." \
      --onefile \
      --windowed \
      run.py
    ```
    *   `--add-data`: Ensures the React files are bundled inside the exe.
    *   `--onefile`: Produces a single `LoCBT_Pro.exe`.
    *   `--windowed`: Hides the black terminal window (optional, but professional).

### C. Code Protection (Obfuscation)
Python code can be reverse-engineered. To protect your licensing logic:
1.  Use **PyArmor** (Commercial tool, recommended) or compile critical modules (like `license_utils.py`) to Cython (`.so` or `.pyd` files) before packaging.
2.  **Critical:** Ensure your `cloud_license_server.py` URL is not easily patchable in the binary.

---

## 4. Sales & Commercialization Workflow

### A. The Purchase Flow
1.  **Website:** You set up a simple landing page (WordPress/Wix/Custom).
2.  **Payment:** User pays via Stripe/PayPal.
3.  **Webhook:** Stripe sends a webhook to your Oracle Server (`POST /generate-key`).
4.  **Delivery:** Your server generates a key and emails it to the customer.

### B. The Activation Flow (In-App)
1.  Customer downloads `LoCBT_Pro.exe`.
2.  On first run, the app sees no license in local DB.
3.  App shows the "License Gate" screen (which we built).
4.  Customer enters the key.
5.  App sends Key + Hardware ID to `https://<your-oracle-ip>/verify-activate`.
6.  Oracle Server checks DB:
    *   If valid & unused: Returns "OK".
    *   If used by *same* Hardware ID: Returns "OK" (Re-install allowed).
    *   If used by *different* Hardware ID: Returns "403 Forbidden".
7.  Local App saves the "Activation Token" locally and unlocks the UI.

---

## 5. Next Steps Checklist

- [ ] **Deploy** `cloud_license_server.py` to Oracle Cloud.
- [ ] **Update** `backend/routers/license.py` in the local app to point to your real Oracle URL instead of `mock_payment`.
- [ ] **Integrate** a hardware ID library (like `machineid` in Python) to prevent users from sharing one key across 50 computers.
- [ ] **Package** the app using PyInstaller.
- [ ] **Sell** your first license!

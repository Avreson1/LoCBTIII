import uvicorn
import socket
import os
import webbrowser
import sys

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    ip = get_ip()
    port = 8000
    
    print("="*50)
    print(f"CBT SERVER STARTED")
    print("="*50)
    print(f"ADMIN URL:   http://{ip}:{port}/admin")
    print(f"STUDENT URL: http://{ip}:{port}/")
    print("-" * 50)
    print(f"Keep this window open while the exam is running.")
    print("="*50)
    
    # Auto-open browser
    try:
        webbrowser.open(f"http://localhost:{port}/")
    except:
        pass

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, log_level="info")

import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("   LoCBT Application Launcher")
    print("=" * 60)
    print("This launcher helps you connect your local LoCBT application")
    print("to your Cloud Licensing Server (e.g., PythonAnywhere).")
    print("-" * 60)

    # 1. Prompt for URL
    print("Enter your Cloud Licensing Server URL.")
    print("Examples:")
    print(" - https://jules.pythonanywhere.com")
    print(" - http://localhost:8080 (for local testing)")
    print("")
    url = input("Server URL [Press Enter for http://localhost:8080]: ").strip()

    if not url:
        url = "http://localhost:8080"

    # Remove trailing slash if present to avoid double slashes
    if url.endswith('/'):
        url = url[:-1]

    print(f"\n✅ Configuration Set: {url}")
    print("🚀 Starting LoCBT Application...\n")

    # 2. Set Environment Variable
    os.environ["LOCBT_LICENSE_URL"] = url

    # 3. Run the App
    try:
        # We use subprocess to run 'run.py' passing the current environment
        # which now includes our new variable.
        subprocess.run([sys.executable, "run.py"], env=os.environ, check=True)
    except KeyboardInterrupt:
        print("\n\nStopped.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Application crashed with error code {e.returncode}")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")

if __name__ == "__main__":
    main()

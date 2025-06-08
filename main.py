import subprocess
import os
import sys
import io

# Path to the project directory and menu.py
project_dir = os.path.dirname(os.path.abspath(__file__))
menu_path = os.path.join(project_dir, "menu.py")

# Set UTF-8 encoding for output of main.py itself
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Copy current environment and add variable for UTF-8 output of the child process
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

try:
    print("Starting menu.py ...\n")

    result = subprocess.run(
        [sys.executable, menu_path],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env
    )

    print("Output of menu.py:\n")
    print(result.stdout)

    if result.stderr:
        print("ERROR: An error occurred...")
        print(result.stderr)

except Exception as e:
    print(f"ERROR: Failed to start menu.py: {e}")

input("\nPress Enter to exit...")

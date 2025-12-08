import os
import subprocess
import sys

WORKER_COUNT = int(os.getenv("PY_WORKER_COUNT", "4"))

# Detect the current python executable (the one running this script)
PYTHON_EXECUTABLE = sys.executable

print(f"🚀 Using Python executable: {PYTHON_EXECUTABLE}")
print(f"🚀 Starting {WORKER_COUNT} Python workers...")

processes = []

for i in range(WORKER_COUNT):
    print(f"👷 Launching worker #{i+1}")
    p = subprocess.Popen([PYTHON_EXECUTABLE, "-m", "app.queues.worker"])
    processes.append(p)

print("All workers started. Press CTRL+C to terminate.")

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all workers...")
    for p in processes:
        p.terminate()

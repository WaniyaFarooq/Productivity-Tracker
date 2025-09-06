import time
import psutil
import win32gui
import win32process
import matplotlib.pyplot as plt
import csv
from collections import defaultdict


def get_active_process_name():
    """Return the process name of the current active window."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return None  # no active window
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except Exception:
        return None


usage_log = defaultdict(float)  # store total seconds
current_app = None
start_time = time.time()

print("Tracking started... Press Ctrl+C to stop.\n")
try:
    while True:
        active_process = get_active_process_name()

        # Skip if no valid process
        if not active_process:
            time.sleep(1)
            continue

        if active_process != current_app:
            # save elapsed time for previous app
            if current_app:
                elapsed = time.time() - start_time
                usage_log[current_app] += elapsed
                print(f"[{time.strftime('%H:%M:%S')}] Switched from {current_app} → {active_process} ({elapsed:.1f}s)")

            # reset timer
            current_app = active_process
            start_time = time.time()

        time.sleep(1)

except KeyboardInterrupt:
    # add final app time before stopping
    if current_app:
        elapsed = time.time() - start_time
        usage_log[current_app] += elapsed
        print(f"Stopped at {current_app}, added {elapsed:.1f}s")

    print("\nTracking stopped.\n")

# --- Save results to CSV ---
with open("usage_log.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Application", "Seconds", "Minutes"])
    for app, seconds in usage_log.items():
        writer.writerow([app, f"{seconds:.1f}", f"{seconds/60:.1f}"])

print("Usage data saved to usage_log.csv\n")

# --- Visualization ---
labels = list(usage_log.keys())
sizes = list(usage_log.values())
sizes_minutes = [s / 60 for s in sizes]

# Pie chart
plt.figure(figsize=(8, 6))
plt.pie(
    sizes_minutes,
    labels=labels,
    autopct=lambda p: f"{p:.1f}% ({p*sum(sizes_minutes)/100:.1f} min)"
)
plt.title("App Usage Distribution (Minutes)")
plt.show()

# Bar chart
plt.figure(figsize=(10, 6))
plt.barh(labels, sizes_minutes)
plt.xlabel("Minutes")
plt.title("App Usage (Minutes)")
plt.tight_layout()
plt.show()

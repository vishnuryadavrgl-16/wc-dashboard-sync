import subprocess
import sys
from datetime import datetime

LOG_PREFIX = "[WC MASTER SYNC]"

# =========================
# MODE
# =========================
MODE = "daily"   # "daily" OR "full_setup"

# =========================
# RUNNER
# =========================
def run_script(script):
    print(f"\n{LOG_PREFIX} Running: {script}")

    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise Exception(f"{script} failed")

    print(f"{LOG_PREFIX} Completed: {script}")

# =========================
# FULL SETUP (ONE TIME)
# =========================
def full_setup():
    print("\n===== FULL SETUP MODE =====\n")

    # ONLY USE IF YOU REALLY NEED RESET STATE
    run_script("upload_order_full.py")
    run_script("upload_engagement_full.py")
    run_script("sync_all_sheets.py")

# =========================
# DAILY PIPELINE (MAIN SYSTEM)
# =========================
def daily_run():
    print("\n===== DAILY MODE =====\n")

    # 1. ORDER SYNC (CUTOVER LOGIC INSIDE SCRIPT)
    run_script("upload_order.py")

    # 2. ENGAGEMENT SYNC (CUTOVER LOGIC INSIDE SCRIPT)
    run_script("upload_engagement.py")

    # 3. ORDER SUMMARY FULL SYNC
    run_script("upload_order_summary_full.py")

    # 4. FINAL SYNC (ALL SHEETS + IMPORT DB)
    run_script("sync_all_sheets.py")

# =========================
# MAIN
# =========================
def main():
    start = datetime.now()

    print(f"\n{LOG_PREFIX} STARTED: {start}")
    print(f"{LOG_PREFIX} MODE = {MODE}")

    try:
        if MODE == "full_setup":
            full_setup()

        elif MODE == "daily":
            daily_run()

        else:
            raise Exception("Invalid MODE")

    except Exception as e:
        print(f"\n{LOG_PREFIX} FAILED: {e}")
        sys.exit(1)

    end = datetime.now()

    print(f"\n{LOG_PREFIX} ENDED: {end}")
    print(f"{LOG_PREFIX} DURATION: {end - start}")


if __name__ == "__main__":
    main()
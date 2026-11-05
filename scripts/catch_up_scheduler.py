"""
Self-Healing & Catch-Up Scheduler Monitor
Tracks daily execution state. If the host machine was asleep, offline, or restarted
during the 7:00 AM window, this module detects the missed run and triggers
immediate catch-up execution.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = BASE_DIR / "data" / "execution_state.json"

def get_state() -> dict:
    if STATE_FILE.is_file():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "last_successful_date": None,
        "last_run_timestamp": None,
        "last_status": "NONE",
        "consecutive_failures": 0
    }

def save_state(status: str, error_msg: str = None):
    today = datetime.now().strftime("%Y-%m-%d")
    now_iso = datetime.now().isoformat()
    state = get_state()
    
    if status == "SUCCESS":
        state["last_successful_date"] = today
        state["consecutive_failures"] = 0
    else:
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        
    state["last_run_timestamp"] = now_iso
    state["last_status"] = status
    if error_msg:
        state["last_error"] = error_msg
        
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def needs_execution() -> bool:
    state = get_state()
    today = datetime.now().strftime("%Y-%m-%d")
    return state.get("last_successful_date") != today

def run_daily_pipeline(is_catchup: bool = False) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    mode_label = "CATCH-UP EXECUTION" if is_catchup else "SCHEDULED 7:00 AM RUN"
    print(f"[{mode_label}] Initiating daily gospel pipeline for {today}...")

    # 1. Run Email & Media Dispatch Script
    send_script = BASE_DIR / "scripts" / "send_viral_fliers_email.py"
    if not send_script.is_file():
        err = f"Script not found: {send_script}"
        print(f"[ERROR] {err}", file=sys.stderr)
        save_state("FAILED", err)
        return False

    try:
        cmd = [sys.executable, str(send_script)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"[PIPELINE SUCCESS] Output:\n{result.stdout}")
        save_state("SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        err = f"Execution failed with code {e.returncode}: {e.stderr}"
        print(f"[PIPELINE ERROR] {err}", file=sys.stderr)
        save_state("FAILED", err)
        return False

def check_and_catch_up():
    if needs_execution():
        print("[MONITOR] Today's briefing has not been executed yet. Running catch-up now...")
        success = run_daily_pipeline(is_catchup=True)
        sys.exit(0 if success else 1)
    else:
        state = get_state()
        print(f"[MONITOR] Today's run is already completed ({state.get('last_successful_date')}). No action needed.")
        sys.exit(0)

if __name__ == "__main__":
    check_and_catch_up()

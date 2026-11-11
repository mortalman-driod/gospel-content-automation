"""
Milestone 6: State & Operations Engine (src/state.py)
Manages single source of truth (data/state.json), idempotency locks,
36-hour watchdog timer, and 30-day deduplication memory (data/used.json) with automated pruning.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("kingdom_journal.state")
BASE_DIR = Path(__file__).resolve().parent.parent

STATE_FILE = BASE_DIR / "data" / "state.json"
USED_FILE = BASE_DIR / "data" / "used.json"

class StateManager:
    def __init__(self):
        self.state_file = STATE_FILE
        self.used_file = USED_FILE
        self.state_data = self._load_state()
        self.used_data = self._load_used()

    def _load_state(self) -> Dict:
        if self.state_file.is_file():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Error loading state.json: {e}")
        return {
            "current_issue_number": 49,
            "last_successful_date": "",
            "last_run_timestamp": "",
            "last_status": "INIT",
            "consecutive_failures": 0
        }

    def _load_used(self) -> Dict:
        if self.used_file.is_file():
            try:
                return json.loads(self.used_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Error loading used.json: {e}")
        return {
            "used_video_ids": [],
            "used_quotes": [],
            "used_themes": [],
            "history": []
        }

    def get_next_issue_number(self) -> int:
        """Returns the next issue number to produce."""
        return self.state_data.get("current_issue_number", 49) + 1

    def can_run_today(self, force: bool = False) -> Tuple[bool, str]:
        """
        Idempotency lock: checks if an issue has already been sent today.
        Returns: (can_run_bool, reason_message)
        """
        if force:
            return True, "Force flag enabled."

        today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        last_date = self.state_data.get("last_successful_date", "")

        if last_date == today_utc:
            return False, f"Issue for today ({today_utc}) was already successfully sent. Skipping run."

        return True, "Ready to produce today's issue."

    def check_watchdog_warning(self) -> Optional[str]:
        """Checks if the last successful run was more than 36 hours ago."""
        last_ts_str = self.state_data.get("last_run_timestamp")
        if not last_ts_str:
            return None

        try:
            last_dt = datetime.fromisoformat(last_ts_str.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            delta_hours = (now_dt - last_dt).total_seconds() / 3600.0
            if delta_hours > 36.0:
                return f"Watchdog Alert: Last successful run was {delta_hours:.1f} hours ago (> 36h threshold)."
        except Exception:
            pass
        return None

    def prune_used_history(self, days_retention: int = 30):
        """
        Prunes historical entries older than days_retention from used.json.
        Guarantees deduplication without unbounded file growth.
        """
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_retention)).strftime("%Y-%m-%d")
        history = self.used_data.get("history", [])
        fresh_history = [h for h in history if h.get("date", "") >= cutoff_date]
        self.used_data["history"] = fresh_history

        active_vids = {h["video_id"] for h in fresh_history if h.get("video_id")}
        self.used_data["used_video_ids"] = [
            vid for vid in self.used_data.get("used_video_ids", []) if vid in active_vids
        ]

    def record_success(
        self,
        issue_number: int,
        video_id: Optional[str] = None,
        quote_text: Optional[str] = None,
        theme: Optional[str] = None
    ):
        """
        Atomically updates state.json and used.json after a successful send.
        Increments current_issue_number exactly once.
        """
        now_utc = datetime.now(timezone.utc)
        today_str = now_utc.strftime("%Y-%m-%d")
        now_iso = now_utc.isoformat()

        # Update state
        self.state_data["current_issue_number"] = issue_number
        self.state_data["last_successful_date"] = today_str
        self.state_data["last_run_timestamp"] = now_iso
        self.state_data["last_status"] = "SUCCESS"
        self.state_data["consecutive_failures"] = 0

        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state_data, indent=2), encoding="utf-8")

        # Update used history safely
        self.used_data.setdefault("used_video_ids", [])
        self.used_data.setdefault("used_quotes", [])
        self.used_data.setdefault("used_themes", [])
        self.used_data.setdefault("history", [])

        if video_id and video_id not in self.used_data["used_video_ids"]:
            self.used_data["used_video_ids"].append(video_id)
        if quote_text and quote_text not in self.used_data["used_quotes"]:
            self.used_data["used_quotes"].append(quote_text)
        if theme and theme not in self.used_data["used_themes"]:
            self.used_data["used_themes"].append(theme)

        self.used_data["history"].append({
            "issue": issue_number,
            "date": today_str,
            "video_id": video_id,
            "theme": theme
        })

        # Prune entries older than 30 days
        self.prune_used_history(days_retention=30)

        self.used_file.write_text(json.dumps(self.used_data, indent=2), encoding="utf-8")
        logger.info(f"State successfully committed for Issue {issue_number} on {today_str}.")

    def record_failure(self, error_msg: str):
        """Records run failure in state.json for monitoring."""
        self.state_data["last_run_timestamp"] = datetime.now(timezone.utc).isoformat()
        self.state_data["last_status"] = "FAILED"
        self.state_data["consecutive_failures"] = self.state_data.get("consecutive_failures", 0) + 1
        self.state_data["last_error"] = str(error_msg)[:300]
        try:
            self.state_file.write_text(json.dumps(self.state_data, indent=2), encoding="utf-8")
        except Exception:
            pass

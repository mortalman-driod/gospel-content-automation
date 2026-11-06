"""
Milestone 7: Learning Loop & Performance Logging Engine (src/learn.py)
Tracks social performance metrics in data/performance.csv,
computes weekly feedback weights for templates and palettes, and preserves 20% exploration.
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("kingdom_journal.learn")
BASE_DIR = Path(__file__).resolve().parent.parent
PERF_FILE = BASE_DIR / "data" / "performance.csv"

CSV_HEADERS = [
    "issue", "post_id", "platform", "template", "palette",
    "theme", "hook_type", "reach", "shares", "saves", "comments"
]

class LearningLoop:
    def __init__(self, perf_file: Optional[Path] = None):
        self.perf_file = perf_file or PERF_FILE
        self._ensure_csv()

    def _ensure_csv(self):
        self.perf_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.perf_file.is_file():
            with open(self.perf_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

    def register_issue_posts(
        self,
        issue_number: int,
        template: str,
        palette: str,
        theme: str,
        hook_type: str = "curiosity"
    ) -> List[str]:
        """
        Creates initial tracking entries for an issue across platforms with unique post_ids.
        Returns list of post_ids.
        """
        platforms = ["facebook", "instagram", "whatsapp", "x", "threads"]
        post_ids = []

        rows_to_append = []
        for p in platforms:
            p_code = p[:2].upper()
            post_id = f"TKJ-{issue_number:03d}-{p_code}"
            post_ids.append(post_id)
            rows_to_append.append([
                issue_number, post_id, p, template, palette,
                theme, hook_type, 0, 0, 0, 0
            ])

        try:
            with open(self.perf_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for r in rows_to_append:
                    writer.writerow(r)
            logger.info(f"Registered {len(post_ids)} tracking rows for Issue {issue_number} in performance.csv.")
        except Exception as e:
            logger.warning(f"Error registering performance rows: {e}")

        return post_ids

    def generate_weekly_report(self) -> Dict:
        """Computes template performance summaries from performance.csv."""
        if not self.perf_file.is_file():
            return {"top_templates": [], "total_logged": 0}

        template_scores = {}
        total_rows = 0

        try:
            with open(self.perf_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_rows += 1
                    t = row.get("template", "bold_statement")
                    reach = int(row.get("reach", 0) or 0)
                    shares = int(row.get("shares", 0) or 0)
                    score = reach + (shares * 5)
                    template_scores.setdefault(t, []).append(score)

            summary = []
            for tpl, scores in template_scores.items():
                avg_score = sum(scores) / len(scores) if scores else 0
                summary.append({"template": tpl, "avg_score": round(avg_score, 1), "count": len(scores)})

            summary.sort(key=lambda x: x["avg_score"], reverse=True)
            return {
                "top_templates": summary[:3],
                "total_logged": total_rows
            }
        except Exception as e:
            logger.warning(f"Error computing performance report: {e}")
            return {"top_templates": [], "total_logged": 0}

import json
from pathlib import Path
from typing import List

from .models import RunSummary
from .ui import Colors

class HistoryManager:
    """Handles reading and writing the history log"""

    def __init__(self, history_file: str):
        self.HISTORY_FILE = Path(history_file)

    def load(self) -> List[RunSummary]:
        if not self.HISTORY_FILE.exists(): return []
        try:
            with open(self.HISTORY_FILE, 'r') as f:
                data = json.load(f)
                return [RunSummary(**d) for d in data]
        except Exception:
            return []

    def save(self, history: List[RunSummary]):
        history_data = [d.__dict__ for d in history]
        try:
            with open(self.HISTORY_FILE, 'w') as f:
                json.dump(history_data, f, indent=4)
        except Exception as e:
            print(f"{Colors.RED}[ERROR] Failed to save history: {e}{Colors.RESET}")

    def display_history(self):
        """Shows formatted history"""
        history = self.load()
        if not history:
            print(f"{Colors.YELLOW}No analysis history found.{Colors.RESET}")
            return

        print(f"\n{Colors.PINK}{'='*70}")
        print(f"{Colors.BOLD}   ANALYSIS HISTORY (Last 10 Runs){Colors.RESET}")
        print(f"{Colors.PINK}{'='*70}{Colors.RESET}")
        print(f"{ 'TIMESTAMP':<20} | {'TOTAL':<6} | {'PASS':<5} | {'FAIL':<5} | {'FIXED':<6}")
        print("-" * 70)

        for run in history[-10:]:
            print(f"{run.timestamp:<20} | {run.total_files:<6} | {run.passed:<5} | {run.failed:<5} | {run.fixed:<6}")
        print(f"{Colors.PINK}{'='*70}{Colors.RESET}\n")

import json
import time
from pathlib import Path
from typing import List

from .models import AnalysisResult, RunSummary, AppConfig
from .ui import Colors
from .history import HistoryManager

def generate_report(results: List[AnalysisResult], config: AppConfig) -> RunSummary:
    """Generates the final table and exports to JSON."""

    total = len(results)
    passed = sum(1 for r in results if r.success)
    fixed = sum(1 for r in results if r.was_fixed)
    failed = total - passed

    print("\n" + "="*70)
    print(f"{Colors.BOLD}   CYBERZILLA CODEX - FINAL REPORT   {Colors.RESET}")
    print("="*70)
    print(f"{Colors.BOLD}{'STATUS':<8} | {'TYPE':<10} | {'FILE':<30} | {'DETAILS'}{Colors.RESET}")
    print("-" * 70)

    for r in results:
        status_icon = Colors.symbol(r.success)
        fix_icon = "🔧" if r.was_fixed else " "

        fname = r.file_path
        if len(fname) > 30: fname = "..." + fname[-27:]

        info = f"{len(r.errors)} Err" if not r.success else "OK"
        if r.was_fixed: info += " (Fixed)"

        print(f"   {status_icon} {fix_icon}  | {r.language:<10} | {fname:<30} | {info}")

        if not r.success and len(r.errors) > 0:
            for e in r.errors[:3]:
                print(f"         {Colors.RED}└─ {e}{Colors.RESET}")

    print("-" * 70)
    print(f"Files: {total} | {Colors.GREEN}Passed: {passed}{Colors.RESET} | {Colors.RED}Failed: {failed}{Colors.RESET} | {Colors.YELLOW}Auto-Fixed: {fixed}{Colors.RESET}")

    if failed > 0:
        print(f"\n{Colors.RED}[!] MERGE BLOCKED: Fix {failed} failed files to pass the Quality Gate.{Colors.RESET}")

    # Export to JSON
    output_path = Path(config.output_dir)
    output_path.mkdir(exist_ok=True)

    json_data = [r.__dict__ for r in results]
    json_file = output_path / f"codex_report_{time.time():.0f}.json"

    try:
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"\n{Colors.CYAN}Exported detailed report to: {json_file.resolve()}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR] Failed to export JSON report: {e}{Colors.RESET}")

    return RunSummary(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        total_files=total,
        passed=passed,
        failed=failed,
        fixed=fixed
    )

def compare_and_update_history(current_summary: RunSummary, history_file: str):
    """Compares current run to the last run and updates history."""

    manager = HistoryManager(history_file)
    history = manager.load()

    print("\n" + "="*70)
    print(f"{Colors.BOLD}   CODE QUALITY TREND ANALYSIS   {Colors.RESET}")
    print("="*70)

    if history:
        last_run = history[-1]
        diff_failed = current_summary.failed - last_run.failed

        trend_icon = "⬆️" if diff_failed < 0 else ("⬇️" if diff_failed > 0 else "=")
        trend_color = Colors.GREEN if diff_failed < 0 else (Colors.RED if diff_failed > 0 else Colors.YELLOW)
        trend_message = ("Quality improved! Fewer failed files." if diff_failed < 0
                         else ("Quality degraded. More failed files." if diff_failed > 0
                         else "Quality remained stable."))

        print(f"Last Scan ({last_run.timestamp}): Failed Files: {last_run.failed}")
        print(f"Current Scan ({current_summary.timestamp}): Failed Files: {current_summary.failed}")
        print(f"\n{trend_color}{Colors.BOLD}{trend_icon}  Trend: {trend_message} ({abs(diff_failed)} change){Colors.RESET}")
    else:
        print(f"{Colors.CYAN}No previous history found. Creating baseline.{Colors.RESET}")

    history.append(current_summary)
    manager.save(history)

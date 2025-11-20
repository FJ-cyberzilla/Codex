
import os
import sys
import argparse
import logging
from pathlib import Path

from .ui import print_banner, print_menu, Colors
from .config import ConfigLoader
from .analyzer import EnterpriseAnalyzer
from .history import HistoryManager
from .reporting import generate_report, compare_and_update_history
from .models import AppConfig

log = logging.getLogger(__name__)

def setup_logging(log_file: str = "codex.log"):
    """Configures logging to file and console."""
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.INFO)

def run_analysis(target_path: str, fix_mode: bool = False, verbose: bool = False) -> bool:
    """Main analysis runner function"""
    try:
        setup_logging()
        config, tool_map = ConfigLoader.load()
        config.fix_mode = fix_mode
        config.verbose = verbose

        analyzer = EnterpriseAnalyzer(config, tool_map)
        results = analyzer.scan_directory(target_path)
        summary = generate_report(results, config)
        compare_and_update_history(summary, config.history_file)

        return summary.failed == 0

    except Exception as e:
        log.error(f"Analysis failed: {e}", exc_info=True)
        print(f"{Colors.RED}[FATAL] Analysis failed: {e}{Colors.RESET}")
        return False

def cleanup_backups(path: str):
    """Deletes any orphaned .codex.bak files left by a crashed run."""
    target = Path(path)
    count = 0
    for root, _, files in os.walk(target):
        for f in files:
            if f.endswith(".codex.bak"):
                try:
                    os.remove(Path(root) / f)
                    count += 1
                except (IOError, OSError) as e:
                    log.error(f"Failed to remove backup file {f}: {e}")
                    print(f"{Colors.RED}[ERROR] Failed to remove backup file {f}: {e}{Colors.RESET}")
    if count > 0:
        print(f"{Colors.YELLOW}[CLEANUP] Removed {count} orphaned backup files.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}[CLEANUP] No orphaned backup files found.{Colors.RESET}")

def show_config_info(config: AppConfig, tool_map: dict):
    """Display current configuration"""
    print(f"\n{Colors.PINK}{'='*70}")
    print(f"{Colors.BOLD}   CURRENT CONFIGURATION{Colors.RESET}")
    print(f"{Colors.PINK}{'='*70}{Colors.RESET}")
    print(f"Max Workers: {config.max_workers}")
    print(f"History File: {config.history_file}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Default Timeout: {config.default_timeout}s")
    print(f"Skip Directories: {', '.join(config.skip_dirs)}")
    print(f"\nSupported Languages: {', '.join(tool_map.keys())}")
    print(f"{Colors.PINK}{'='*70}{Colors.RESET}\n")

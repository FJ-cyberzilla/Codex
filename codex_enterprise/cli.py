
import sys
import argparse

from .main import run_analysis, cleanup_backups, show_config_info
from .ui import print_banner, print_menu, Colors
from .config import ConfigLoader
from .history import HistoryManager


def interactive_mode():
    """Interactive command line interface"""
    print_banner()
    
    while True:
        print_menu()
        choice = input(f"{Colors.CYAN}Select an option [0-5]: {Colors.RESET}").strip()
        
        if choice == '1':
            path = input(f"{Colors.CYAN}Enter path to analyze [.]: {Colors.RESET}").strip() or "."
            run_analysis(path, fix_mode=False, verbose=True)
            
        elif choice == '2':
            path = input(f"{Colors.CYAN}Enter path to analyze [.]: {Colors.RESET}").strip() or "."
            run_analysis(path, fix_mode=True, verbose=True)
            
        elif choice == '3':
            config, _ = ConfigLoader.load()
            HistoryManager(config.history_file).display_history()
            
        elif choice == '4':
            path = input(f"{Colors.CYAN}Enter path to clean [.]: {Colors.RESET}").strip() or "."
            cleanup_backups(path)
            
        elif choice == '5':
            config, tool_map = ConfigLoader.load()
            show_config_info(config, tool_map)
            
        elif choice == '0':
            print(f"{Colors.PINK}Thank you for using Cyberzilla Codex!{Colors.RESET}")
            break
            
        else:
            print(f"{Colors.RED}Invalid option. Please try again.{Colors.RESET}")

def main():
    """Main entry point with CLI argument support"""
    parser = argparse.ArgumentParser(description="Cyberzilla Codex - Enterprise Code Quality Analyzer")
    parser.add_argument("path", nargs="?", default=".", help="Target directory to analyze")
    parser.add_argument("--fix", action="store_true", help="Enable auto-fix mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        success = run_analysis(args.path, args.fix, args.verbose)
        sys.exit(0 if success else 1)


class Colors:
    """Cross-platform ANSI colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PINK = '\033[95m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def symbol(success: bool) -> str:
        return f"{Colors.GREEN}✓{Colors.RESET}" if success else f"{Colors.RED}✗{Colors.RESET}"

def print_banner():
    """Displays the startup banner in pink"""
    banner = f"""{Colors.PINK}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║                                                      ║
║   ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗           ║
║  ██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝           ║
║  ██║     ██║   ██║██║  ██║█████╗   ╚███╔╝            ║
║  ██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗            ║
║  ╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗           ║
║   ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝           ║
║                                                      ║
║          Enterprise Code Analyzer & Quality Gate     ║
║                     Version 6.1.1                    ║
║                                                      ║
║  GitHub: FJ-cyberzilla                               ║
║  Status: Initiated  | Thread-Safe | Auto-Fix Enabled ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)

def print_menu():
    """Interactive menu for user selection"""
    menu = f"""
{Colors.PINK}╔═══════════════════════════════════════╗
║                      MAIN MENU                     ║
╠════════════════════════════════════════════════════╣
║                                                    ║
║  {Colors.CYAN}[1]{Colors.PINK} Analyze Code        ║
║  {Colors.CYAN}[2]{Colors.PINK} Analyze & Auto-Fix  ║
║  {Colors.CYAN}[3]{Colors.PINK} View Analysis       ║
║  {Colors.CYAN}[4]{Colors.PINK} Cleanup Backup      ║
║  {Colors.CYAN}[5]{Colors.PINK} Configuration Info  ║
║  {Colors.CYAN}[0]{Colors.PINK} Exit                ║
║                                                    ║
╚════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(menu)


import os
import shutil
import subprocess
import concurrent.futures
import logging
from pathlib import Path
from typing import List, Tuple

from .models import AppConfig, AnalysisResult
from .concurrency import ConcurrencyManager
from .ui import Colors

log = logging.getLogger(__name__)

class EnterpriseAnalyzer:
    def __init__(self, config: AppConfig, tool_map: dict):
        self.config = config
        self.tool_map = tool_map
        self.concurrency_manager = ConcurrencyManager()

        # Map file extensions to language keys defined in the config
        self.ext_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'javascript',
            '.go': 'go', '.rs': 'rust', '.c': 'c/c++', '.cpp': 'c/c++',
        }

    def _run_tool(self, file_path: Path, tool_config: dict, is_fixer: bool) -> Tuple[int, str, str]:
        """Executes a tool with backup/rollback safety for fixers."""
        cmd = tool_config['command'] + [str(file_path)]
        tool_name = tool_config['tool']
        timeout = tool_config.get('timeout', self.config.default_timeout)

        backup_path = file_path.with_suffix(f"{file_path.suffix}.codex.bak")

        try:
            if not shutil.which(cmd[0]):
                log.warning(f"Tool '{cmd[0]}' not found in system path.")
                return -1, "", f"Tool '{cmd[0]}' not found in system path."

            if is_fixer:
                try:
                    shutil.copyfile(file_path, backup_path)
                except (IOError, OSError) as e:
                    log.error(f"Failed to create backup for {file_path}: {e}")
                    return -3, "", f"Failed to create backup: {e}"

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                encoding='utf-8', errors='replace',
                cwd=file_path.parent
            )

            if is_fixer and result.returncode != 0:
                if backup_path.exists():
                    try:
                        shutil.move(backup_path, file_path)
                    except (IOError, OSError) as e:
                        log.error(f"Failed to restore backup for {file_path}: {e}")
                        return result.returncode, result.stdout, f"Fix failed, but restore also failed: {e}. {result.stderr}"
                    return result.returncode, result.stdout, f"Fix failed; rolled back changes. {result.stderr}"

            if is_fixer and backup_path.exists():
                try:
                    os.remove(backup_path)
                except OSError as e:
                    log.warning(f"Failed to remove backup file {backup_path}: {e}")

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            if is_fixer and backup_path.exists():
                try:
                    shutil.move(backup_path, file_path)
                except (IOError, OSError) as e:
                    log.error(f"Failed to restore backup for {file_path} after timeout: {e}")
                    return -2, "", f"Analysis timed out, but restore failed: {e}."
                return -2, "", f"Analysis timed out after {timeout}s and rolled back."
            return -2, "", f"Analysis timed out after {timeout}s."

        except Exception as e:
            if is_fixer and backup_path.exists():
                try:
                    shutil.move(backup_path, file_path)
                except (IOError, OSError) as e_move:
                    log.error(f"Tool execution failed and restore failed for {file_path}: {e_move}")
                    return -3, "", f"Tool execution failed and restore failed: {e_move}"
            return -3, "", f"Tool execution failed: {e}"

    def process_file(self, file_path: Path) -> AnalysisResult:
        """The core pipeline: Fix (under lock) -> Check -> Result"""
        ext = file_path.suffix
        lang_key = self.ext_map.get(ext)

        if not lang_key or lang_key not in self.tool_map:
            return AnalysisResult(str(file_path), "Unknown", False, ["Unsupported language/extension"], [], False)

        # 1. Fixing Phase (Protected by Lock)
        was_fixed = False
        if self.config.fix_mode:
            file_lock = self.concurrency_manager.get_lock(file_path)
            with file_lock:
                for tool_config in self.tool_map.get(lang_key, []):
                    if tool_config.get('fix') and tool_config.get('command'):
                        if self._run_tool(file_path, tool_config, is_fixer=True)[0] == 0:
                            was_fixed = True
                            break

        # 2. Analysis Phase
        errors, warnings = [], []

        for tool_config in self.tool_map.get(lang_key, []):
            if tool_config.get('check') and tool_config.get('command'):
                tool_name = tool_config['tool']
                code, out, err = self._run_tool(file_path, tool_config, is_fixer=False)

                if code == -1:
                    warnings.append(f"{tool_name} not available. Install it.")
                elif code != 0 or err:
                    output_lines = (out + err).splitlines()

                    if not output_lines:
                        errors.append(f"Exit code {code} from {tool_name}")
                    else:
                        errors.extend([f"[{tool_name}] {line}" for line in output_lines[:5]])

        success = not errors
        return AnalysisResult(str(file_path), lang_key.capitalize(), success, errors, warnings, was_fixed)

    def scan_directory(self, path: str) -> List[AnalysisResult]:
        """Threaded directory scanning and file finding"""
        target = Path(path)
        files_to_scan = []

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in self.config.skip_dirs]
            for f in files:
                if Path(f).suffix in self.ext_map:
                    files_to_scan.append(Path(root) / f)

        print(f"{Colors.CYAN}Found {len(files_to_scan)} files. Starting analysis...{Colors.RESET}")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {executor.submit(self.process_file, f): f for f in files_to_scan}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                if self.config.verbose:
                    status = "✓" if result.success else "✗"
                    print(f"{status} {result.file_path}")
                else:
                    print(".", end="", flush=True)

        print("\n")
        return results
rue, timeout=timeout,
                encoding='utf-8', errors='replace',
                cwd=file_path.parent
            )

            if is_fixer and result.returncode != 0:
                if backup_path.exists():
                    shutil.move(backup_path, file_path)
                    return result.returncode, result.stdout, f"Fix failed; rolled back changes. {result.stderr}"

            if is_fixer and backup_path.exists():
                os.remove(backup_path)

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            if is_fixer and backup_path.exists():
                shutil.move(backup_path, file_path)
                return -2, "", f"Analysis timed out after {timeout}s and rolled back."
            return -2, "", f"Analysis timed out after {timeout}s."

        except Exception as e:
            if is_fixer and backup_path.exists():
                shutil.move(backup_path, file_path)
                return -3, "", f"Tool execution failed and rolled back: {e}"
            return -3, "", f"Tool execution failed: {e}"

    def process_file(self, file_path: Path) -> AnalysisResult:
        """The core pipeline: Fix (under lock) -> Check -> Result"""
        ext = file_path.suffix
        lang_key = self.ext_map.get(ext)

        if not lang_key or lang_key not in self.tool_map:
            return AnalysisResult(str(file_path), "Unknown", False, ["Unsupported language/extension"], [], False)

        # 1. Fixing Phase (Protected by Lock)
        was_fixed = False
        if self.config.fix_mode:
            file_lock = self.concurrency_manager.get_lock(file_path)
            with file_lock:
                for tool_config in self.tool_map.get(lang_key, []):
                    if tool_config.get('fix') and tool_config.get('command'):
                        if self._run_tool(file_path, tool_config, is_fixer=True)[0] == 0:
                            was_fixed = True
                            break

        # 2. Analysis Phase
        errors, warnings = [], []

        for tool_config in self.tool_map.get(lang_key, []):
            if tool_config.get('check') and tool_config.get('command'):
                tool_name = tool_config['tool']
                code, out, err = self._run_tool(file_path, tool_config, is_fixer=False)

                if code == -1:
                    warnings.append(f"{tool_name} not available. Install it.")
                elif code != 0 or err:
                    output_lines = (out + err).splitlines()

                    if not output_lines:
                        errors.append(f"Exit code {code} from {tool_name}")
                    else:
                        errors.extend([f"[{tool_name}] {line}" for line in output_lines[:5]])

        success = not errors
        return AnalysisResult(str(file_path), lang_key.capitalize(), success, errors, warnings, was_fixed)

    def scan_directory(self, path: str) -> List[AnalysisResult]:
        """Threaded directory scanning and file finding"""
        target = Path(path)
        files_to_scan = []

        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in self.config.skip_dirs]
            for f in files:
                if Path(f).suffix in self.ext_map:
                    files_to_scan.append(Path(root) / f)

        print(f"{Colors.CYAN}Found {len(files_to_scan)} files. Starting analysis...{Colors.RESET}")

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {executor.submit(self.process_file, f): f for f in files_to_scan}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                if self.config.verbose:
                    status = "✓" if result.success else "✗"
                    print(f"{status} {result.file_path}")
                else:
                    print(".", end="", flush=True)

        print("\n")
        return results

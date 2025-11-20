
from dataclasses import dataclass, field
from typing import List

@dataclass
class AppConfig:
    """Global Configuration loaded from external file"""
    fix_mode: bool = False
    verbose: bool = False
    max_workers: int = 4
    history_file: str = "codex_history.json"
    output_dir: str = "reports"
    default_timeout: int = 30
    # Common directories to always skip
    DEFAULT_SKIP = {
        'node_modules', 'venv', '.venv', '__pycache__', '.git',
        'build', 'dist', '.ipynb_checkpoints', 'site-packages'
    }
    skip_dirs: set = field(default_factory=set)

@dataclass
class AnalysisResult:
    """Holds the state of a single file analysis for reporting"""
    file_path: str
    language: str
    success: bool
    errors: List[str]
    warnings: List[str]
    was_fixed: bool = False

@dataclass
class RunSummary:
    """Summary of one single run for history tracking"""
    timestamp: str
    total_files: int
    passed: int
    failed: int
    fixed: int

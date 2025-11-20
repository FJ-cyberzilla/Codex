
import threading
from pathlib import Path

class ConcurrencyManager:
    """Manages file locks to prevent race conditions during fixing."""

    def __init__(self):
        self._locks = {}
        self._global_lock = threading.Lock()

    def get_lock(self, file_path: Path) -> threading.Lock:
        """Returns the specific lock for the given file path."""
        abs_path = str(file_path.resolve())
        with self._global_lock:
            if abs_path not in self._locks:
                self._locks[abs_path] = threading.Lock()
            return self._locks[abs_path]

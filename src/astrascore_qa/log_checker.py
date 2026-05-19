from __future__ import annotations

from pathlib import Path


class LogChecker:
    def __init__(self, log_file: str | Path):
        self.log_file = Path(log_file)

    def contains(self, text: str) -> bool:
        if not self.log_file.exists():
            return False
        return text in self.log_file.read_text(encoding="utf-8", errors="ignore")

    def last_lines(self, limit: int = 50) -> list[str]:
        if not self.log_file.exists():
            return []
        lines = self.log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        return lines[-limit:]

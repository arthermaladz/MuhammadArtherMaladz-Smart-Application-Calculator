"""Portable settings and calculation history storage."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


DEFAULT_SETTINGS: dict[str, Any] = {
    "theme": "dark",
    "number_format": "id",
    "decimal_places": 10,
    "angle_unit": "deg",
    "always_on_top": False,
    "window": {"width": 1000, "height": 700},
    "history_limit": 500,
}


def data_directory() -> Path:
    base = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
    return base / "data"


class PortableStorage:
    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or data_directory()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.settings_path = self.directory / "settings.json"
        self.database_path = self.directory / "history.db"
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'standard',
                created_at INTEGER NOT NULL DEFAULT (unixepoch())
            )"""
        )
        self.connection.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at DESC)")
        self.connection.commit()

    def load_settings(self) -> dict[str, Any]:
        if not self.settings_path.exists():
            return DEFAULT_SETTINGS.copy()
        with self.settings_path.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
        settings = DEFAULT_SETTINGS.copy()
        settings.update(loaded)
        return settings

    def save_settings(self, settings: dict[str, Any]) -> None:
        temporary = self.settings_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.settings_path)

    def add_history(self, expression: str, result: str, mode: str, limit: int = 500) -> None:
        self.connection.execute(
            "INSERT INTO history(expression, result, mode) VALUES (?, ?, ?)",
            (expression, result, mode),
        )
        self.connection.execute(
            "DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY created_at DESC, id DESC LIMIT ?)",
            (limit,),
        )
        self.connection.commit()

    def get_history(self, limit: int = 500) -> list[tuple[int, str, str, str]]:
        return self.connection.execute(
            "SELECT id, expression, result, mode FROM history ORDER BY created_at DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def delete_history_item(self, item_id: int) -> None:
        self.connection.execute("DELETE FROM history WHERE id = ?", (item_id,))
        self.connection.commit()

    def clear_history(self) -> None:
        self.connection.execute("DELETE FROM history")
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

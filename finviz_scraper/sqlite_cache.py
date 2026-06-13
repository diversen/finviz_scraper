from __future__ import annotations

import sqlite3
import time
from pathlib import Path


class SqliteCache:
    """Small sqlite-backed string cache used by the scraper."""

    def __init__(self, path: str | Path) -> None:
        self.db_path = self._db_path(path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @staticmethod
    def _db_path(path: str | Path) -> Path:
        cache_path = Path(path)
        if cache_path.suffix:
            return cache_path
        return cache_path / "cache.sqlite3"

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )

    def get(self, key: str) -> str | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM cache WHERE key = ?",
                (str(key),),
            ).fetchone()
        if row is None:
            return None
        return str(row[0])

    def set(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cache (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (str(key), str(value), time.time()),
            )

    def delete(self, key: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (str(key),))

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM cache")

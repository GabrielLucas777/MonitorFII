"""CRUD SQLite — acesso limpo com context managers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from .config import DB_PATH
from .models import Ativo

SCHEMA = """
CREATE TABLE IF NOT EXISTS ativos (
    ticker       TEXT PRIMARY KEY,
    preco        REAL  DEFAULT 0,
    pvp          REAL  DEFAULT 0,
    yield_anual  REAL  DEFAULT 0,
    dividendo    REAL  DEFAULT 0,
    quantidade   INT   DEFAULT 0,
    custo_medio  REAL  DEFAULT 0,
    data_coleta  TEXT
);
"""


@contextmanager
def _conn(path: str | None = None) -> Generator[sqlite3.Connection, None, None]:
    c = sqlite3.connect(path or str(DB_PATH))
    c.row_factory = sqlite3.Row
    try:
        yield c
    finally:
        c.close()


# ────────────── Init / Migrate ──────────────
def init_db(path: str | None = None) -> None:
    with _conn(path) as c:
        c.executescript(SCHEMA)
        cols = {r[1] for r in c.execute("PRAGMA table_info(ativos)").fetchall()}
        for name, ctype in [
            ("preco", "REAL DEFAULT 0"),
            ("pvp", "REAL DEFAULT 0"),
            ("yield_anual", "REAL DEFAULT 0"),
            ("dividendo", "REAL DEFAULT 0"),
            ("quantidade", "INTEGER DEFAULT 0"),
            ("custo_medio", "REAL DEFAULT 0"),
            ("data_coleta", "TEXT"),
        ]:
            if name not in cols:
                c.execute(f"ALTER TABLE ativos ADD COLUMN {name} {ctype}")
        c.commit()


# ────────────── CRUD ──────────────
def upsert(record: Ativo, path: str | None = None) -> None:
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    with _conn(path) as c:
        c.execute(
            """INSERT OR REPLACE INTO ativos
               (ticker, preco, pvp, yield_anual, dividendo, data_coleta)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                record.ticker,
                float(record.preco), float(record.pvp),
                float(record.yield_anual), float(record.dividendo),
                now,
            ),
        )
        c.commit()


def add(ticker: str, path: str | None = None) -> bool:
    with _conn(path) as c:
        c.execute("INSERT OR IGNORE INTO ativos (ticker) VALUES (?)", (ticker.upper(),))
        c.commit()
    return True


def get_all(path: str | None = None) -> list[dict]:
    with _conn(path) as c:
        return [dict(r) for r in c.execute("SELECT * FROM ativos").fetchall()]


def get_one(ticker: str, path: str | None = None) -> dict | None:
    with _conn(path) as c:
        row = c.execute(
            "SELECT * FROM ativos WHERE ticker = ?", (ticker.upper(),)
        ).fetchone()
    return dict(row) if row else None


def delete(ticker: str, path: str | None = None) -> None:
    with _conn(path) as c:
        c.execute("DELETE FROM ativos WHERE ticker = ?", (ticker.upper(),))
        c.commit()


def clear(path: str | None = None) -> None:
    p = path or str(DB_PATH)
    if Path(p).exists():
        os.remove(p)


def summary(path: str | None = None) -> dict:
    rows = get_all(path)
    sync = [r for r in rows if r.get("data_coleta")]
    dy = [r["yield_anual"] for r in rows if r.get("yield_anual", 0) > 0]
    pvp = [r["pvp"] for r in rows if r.get("pvp", 0) > 0]
    return {
        "total": len(rows),
        "synced": len(sync),
        "pending": len(rows) - len(sync),
        "avg_dy": round(sum(dy) / len(dy), 2) if dy else 0,
        "avg_pvp": round(sum(pvp) / len(pvp), 2) if pvp else 0,
    }

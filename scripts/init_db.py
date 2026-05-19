from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "scoring.db"


SCHEMA = """
DROP TABLE IF EXISTS realtime_results;
DROP TABLE IF EXISTS batch_results;
DROP TABLE IF EXISTS model_baseline;

CREATE TABLE realtime_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL UNIQUE,
    customer_id TEXT,
    msisdn TEXT,
    model_code TEXT NOT NULL,
    amount REAL NOT NULL,
    score INTEGER NOT NULL,
    decision TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE batch_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    model_code TEXT NOT NULL,
    amount REAL NOT NULL,
    score INTEGER NOT NULL,
    decision TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_baseline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_code TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    expected_min_score INTEGER NOT NULL,
    expected_max_score INTEGER NOT NULL,
    expected_decision TEXT NOT NULL,
    UNIQUE(model_code, customer_id)
);
"""

BASELINES = [
    ("CREDIT_RISK_V1", "C1001", 620, 760, "APPROVE"),
    ("CREDIT_RISK_V1", "C1002", 500, 650, "REVIEW"),
    ("CREDIT_RISK_V1", "C1003", 300, 520, "REJECT"),
]


def init_database(db_path: str | Path = DEFAULT_DB_PATH) -> Path:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.executemany(
            """
            INSERT INTO model_baseline
            (model_code, customer_id, expected_min_score, expected_max_score, expected_decision)
            VALUES (?, ?, ?, ?, ?)
            """,
            BASELINES,
        )
        connection.commit()
    return db_path


if __name__ == "__main__":
    created = init_database()
    print(f"Database initialized: {created}")

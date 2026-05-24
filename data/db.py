"""
db.py — SQLite persistence layer for scan history.

Architecture reasoning:
  SQLite is perfect here: zero infrastructure, single file, Python stdlib.
  For a prod tool you'd swap to PostgreSQL or TimescaleDB with the same interface.

  Tables:
    scans  — one row per scan session (target, time, summary)
    hosts  — one row per discovered device per scan (foreign key to scans)

  This gives us: scan timeline, per-device history, improvement tracking.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from netwatcher.config import DB_PATH
from utils.logger import get_logger

log = get_logger(__name__)


@contextmanager
def _conn():
    """Context manager that auto-closes the DB connection."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db() -> None:
    """Create tables if they don't exist. Safe to call multiple times."""
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                target      TEXT    NOT NULL,
                started_at  TEXT    NOT NULL,
                host_count  INTEGER DEFAULT 0,
                avg_score   INTEGER DEFAULT 0,
                summary_json TEXT
            );

            CREATE TABLE IF NOT EXISTS hosts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id     INTEGER NOT NULL REFERENCES scans(id),
                ip          TEXT    NOT NULL,
                hostname    TEXT,
                mac         TEXT,
                vendor      TEXT,
                os_guess    TEXT,
                device_type TEXT,
                risk_score  INTEGER,
                risk_level  TEXT,
                issues_json TEXT,
                ports_json  TEXT,
                scanned_at  TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_hosts_scan_id ON hosts(scan_id);
            CREATE INDEX IF NOT EXISTS idx_hosts_ip      ON hosts(ip);
        """)
    log.debug("Database initialized.")


def save_scan(target: str, devices: List, summary: dict) -> int:
    """
    Persist a scan session and all its devices.
    Returns the scan_id for reference.
    """
    init_db()
    now = datetime.now().isoformat(timespec="seconds")

    with _conn() as con:
        cur = con.execute(
            "INSERT INTO scans (target, started_at, host_count, avg_score, summary_json) VALUES (?,?,?,?,?)",
            (
                target,
                now,
                len(devices),
                summary.get("overall_score", 0),
                json.dumps(summary),
            ),
        )
        scan_id = cur.lastrowid

        for d in devices:
            con.execute(
                """INSERT INTO hosts
                   (scan_id, ip, hostname, mac, vendor, os_guess, device_type,
                    risk_score, risk_level, issues_json, ports_json, scanned_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    scan_id,
                    d.ip,
                    d.hostname,
                    d.mac,
                    d.vendor,
                    d.os_guess,
                    d.device_type,
                    d.risk_score,
                    d.risk_level,
                    json.dumps(d.issues),
                    json.dumps([p.__dict__ for p in d.ports]),
                    d.scan_time,
                ),
            )

    log.info(f"Scan saved → id={scan_id}  target={target}  hosts={len(devices)}")
    return scan_id


def get_scan_history(limit: int = 20) -> List[dict]:
    """Return recent scan sessions, newest first."""
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM scans ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_scan_devices(scan_id: int) -> List[dict]:
    """Return all hosts for a specific scan_id."""
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM hosts WHERE scan_id = ? ORDER BY risk_score DESC",
            (scan_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["issues"] = json.loads(d.pop("issues_json", "[]"))
        d["ports"]  = json.loads(d.pop("ports_json", "[]"))
        result.append(d)
    return result

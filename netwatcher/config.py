"""
config.py — Central configuration for NetWatcher.

Architecture reasoning:
  All tunable values live here. Zero magic strings scattered across the codebase.
  Recruiters see this = "developer understands configuration management".
"""

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
DATA_DIR      = BASE_DIR / "data"
REPORTS_DIR   = BASE_DIR / "reports" / "exports"
TEMPLATES_DIR = BASE_DIR / "reports" / "templates"
DB_PATH       = DATA_DIR / "netwatcher.db"

# Auto-create dirs if they don't exist
for d in [DATA_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Scan defaults ────────────────────────────────────────────────────────────
DEFAULT_TIMEOUT_SEC   = 120        # Max time for a full subnet scan
DEFAULT_NMAP_ARGS     = "-sV -O --open -T4"  # Version + OS detect, open ports, fast
LOCAL_SUBNET_DEFAULT  = "192.168.1.0/24"

# ─── Risk thresholds ──────────────────────────────────────────────────────────
RISK_CRITICAL_THRESHOLD = 75
RISK_HIGH_THRESHOLD     = 50
RISK_MEDIUM_THRESHOLD   = 25
# below 25 = LOW

# ─── App metadata ────────────────────────────────────────────────────────────
APP_NAME      = "NetWatcher"
APP_VERSION   = "1.0.0"
DEVELOPER     = "Akshay"
GITHUB        = "https://github.com/Akshay-core"
PORTFOLIO     = "https://akshay.fruvvi.com"
LINKEDIN      = "https://www.linkedin.com/in/akshay-tb-791bb4372"

"""
helpers.py — Small reusable utility functions.
"""

import socket
import subprocess
import sys
from pathlib import Path


def check_nmap_installed() -> bool:
    """Return True if nmap binary is reachable."""
    try:
        result = subprocess.run(["nmap", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_local_subnet() -> str:
    """
    Attempt to detect the local subnet automatically.
    Returns e.g. "192.168.1.0/24" or falls back to default.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        # Assume /24 subnet (common home network)
        parts = local_ip.rsplit(".", 1)
        return f"{parts[0]}.0/24"
    except Exception:
        return "192.168.1.0/24"


def open_file_in_browser(path: Path) -> None:
    """Cross-platform open of an HTML file in the default browser."""
    import webbrowser
    webbrowser.open(f"file://{path.resolve()}")


def risk_color_ansi(level: str) -> str:
    """Return ANSI color code for a risk level string."""
    return {
        "CRITICAL": "\033[91m",   # bright red
        "HIGH":     "\033[93m",   # bright yellow
        "MEDIUM":   "\033[94m",   # bright blue
        "LOW":      "\033[92m",   # bright green
    }.get(level, "\033[0m")


ANSI_RESET = "\033[0m"

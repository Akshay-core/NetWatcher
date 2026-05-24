"""
scanner.py — Network discovery and port scanning layer.

Architecture reasoning:
  This module has ONE job: talk to Nmap and return structured Device objects.
  It knows nothing about risk scoring or reporting — pure separation of concerns.

  Tradeoffs:
    python-nmap vs subprocess: python-nmap gives structured XML parsing for free.
    We catch NmapNotFoundError early so the user gets a clear message, not a traceback.

  Scalability:
    For large subnets, split targets and use ThreadPoolExecutor to scan concurrently.
"""

import socket
from datetime import datetime
from typing import List, Optional

from netwatcher.config import DEFAULT_NMAP_ARGS, DEFAULT_TIMEOUT_SEC
from netwatcher.devices import Device, Port
from utils.logger import get_logger

log = get_logger(__name__)


def _detect_device_type(os_guess: str, ports: List[Port], vendor: str) -> str:
    """Heuristic device-type classifier based on OS, vendor, and open services."""
    os_lower    = os_guess.lower()
    vendor_low  = vendor.lower()
    services    = {p.service.lower() for p in ports}

    if any(k in vendor_low for k in ("cisco", "netgear", "tp-link", "d-link", "asus", "linksys")):
        return "router"
    if "router" in os_lower or "dd-wrt" in os_lower:
        return "router"
    if any(k in os_lower for k in ("android", "ios", "iphone", "ipad")):
        return "mobile"
    if "windows" in os_lower:
        return "windows-pc"
    if "linux" in os_lower:
        if "http" in services or "https" in services:
            return "server"
        return "linux-device"
    if "printer" in os_lower or "hp" in vendor_low:
        return "printer"
    if "camera" in os_lower or "hikvision" in vendor_low or "dahua" in vendor_low:
        return "ip-camera"
    return "unknown"


def scan_network(
    target: str,
    nmap_args: str = DEFAULT_NMAP_ARGS,
    timeout: int   = DEFAULT_TIMEOUT_SEC,
) -> List[Device]:
    """
    Scan `target` (single IP or CIDR range) and return a list of Device objects.

    Args:
        target:    e.g. "192.168.1.0/24" or "192.168.1.1"
        nmap_args: Nmap CLI flags passed directly to the scanner
        timeout:   Max seconds before the scan is killed

    Returns:
        List[Device] — one per live host found

    Raises:
        RuntimeError if nmap is not installed
    """
    try:
        import nmap  # python-nmap
    except ImportError:
        raise RuntimeError("python-nmap is not installed. Run: pip install python-nmap")

    try:
        nm = nmap.PortScanner()
    except nmap.PortScannerError:
        raise RuntimeError(
            "Nmap binary not found. Install it:\n"
            "  Linux/Mac: sudo apt install nmap  OR  brew install nmap\n"
            "  Windows  : https://nmap.org/download.html"
        )

    log.info(f"Starting scan → target={target}  args='{nmap_args}'")

    try:
        nm.scan(hosts=target, arguments=nmap_args, timeout=timeout)
    except Exception as e:
        raise RuntimeError(f"Nmap scan failed: {e}")

    devices: List[Device] = []

    for host in nm.all_hosts():
        if nm[host].state() != "up":
            continue

        # ── Basic host info ─────────────────────────────────────────────────
        hostname = _safe_hostname(host, nm[host].hostname())
        mac      = nm[host]["addresses"].get("mac", "unknown")
        vendor   = nm[host].get("vendor", {}).get(mac, "unknown") if mac != "unknown" else "unknown"
        os_guess = _extract_os(nm[host])

        # ── Parse open ports ────────────────────────────────────────────────
        ports: List[Port] = []
        for proto in nm[host].all_protocols():
            for port_num in sorted(nm[host][proto].keys()):
                pdata   = nm[host][proto][port_num]
                service = pdata.get("name", "unknown")
                version = f"{pdata.get('product', '')} {pdata.get('version', '')}".strip()
                ports.append(Port(
                    number   = port_num,
                    protocol = proto,
                    state    = pdata.get("state", "unknown"),
                    service  = service,
                    version  = version,
                ))

        device_type = _detect_device_type(os_guess, ports, vendor)

        devices.append(Device(
            ip          = host,
            hostname    = hostname,
            mac         = mac,
            vendor      = vendor,
            os_guess    = os_guess,
            device_type = device_type,
            ports       = ports,
            scan_time   = datetime.now().isoformat(timespec="seconds"),
        ))
        log.debug(f"  Found host: {host}  ports={len(ports)}  os={os_guess}")

    log.info(f"Scan complete — {len(devices)} hosts discovered")
    return devices


# ─── Private helpers ──────────────────────────────────────────────────────────

def _safe_hostname(ip: str, nmap_hostname: str) -> str:
    """Return nmap hostname or fallback to reverse DNS, or IP."""
    if nmap_hostname:
        return nmap_hostname
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return ip


def _extract_os(host_data) -> str:
    """Pull best OS guess from nmap osclass/osmatch data."""
    try:
        matches = host_data.get("osmatch", [])
        if matches:
            return matches[0].get("name", "unknown")
    except Exception:
        pass
    return "unknown"

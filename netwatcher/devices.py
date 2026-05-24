"""
devices.py — Typed data model for a discovered network device.

Architecture reasoning:
  A dataclass gives us a clean contract between scanner → analyzer → report.
  No raw dicts passed around — every component knows exactly what shape the data is.
  This is standard production Python practice (replaces Pydantic when keeping deps minimal).
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Port:
    """Represents a single open port and its detected service."""
    number:   int
    protocol: str          # "tcp" | "udp"
    state:    str          # "open" | "filtered"
    service:  str          # e.g. "ssh", "http", "telnet"
    version:  str = ""     # e.g. "OpenSSH 7.4"
    risk_tag: str = "LOW"  # assigned by risk engine


@dataclass
class Device:
    """Complete representation of a network device discovered during a scan."""
    ip:            str
    hostname:      str                  = "unknown"
    mac:           str                  = "unknown"
    vendor:        str                  = "unknown"
    os_guess:      str                  = "unknown"
    device_type:   str                  = "unknown"   # router, server, phone, etc.
    ports:         List[Port]           = field(default_factory=list)
    risk_score:    int                  = 0           # 0–100
    risk_level:    str                  = "LOW"       # LOW | MEDIUM | HIGH | CRITICAL
    issues:        List[str]            = field(default_factory=list)
    recommendations: List[str]         = field(default_factory=list)
    scan_time:     Optional[str]        = None

    @property
    def open_port_count(self) -> int:
        return len(self.ports)

    @property
    def critical_ports(self) -> List[Port]:
        return [p for p in self.ports if p.risk_tag in ("CRITICAL", "HIGH")]

    def to_dict(self) -> dict:
        """Serialize to plain dict for SQLite / Jinja2 rendering."""
        return {
            "ip":              self.ip,
            "hostname":        self.hostname,
            "mac":             self.mac,
            "vendor":          self.vendor,
            "os_guess":        self.os_guess,
            "device_type":     self.device_type,
            "risk_score":      self.risk_score,
            "risk_level":      self.risk_level,
            "issues":          self.issues,
            "recommendations": self.recommendations,
            "scan_time":       self.scan_time,
            "ports": [
                {
                    "number":   p.number,
                    "protocol": p.protocol,
                    "state":    p.state,
                    "service":  p.service,
                    "version":  p.version,
                    "risk_tag": p.risk_tag,
                }
                for p in self.ports
            ],
        }

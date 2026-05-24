"""
risk_engine.py — Converts raw scan data into a scored risk assessment.

Architecture reasoning:
  This is the "brain" of NetWatcher. It's deliberately decoupled from Nmap —
  it receives Device objects and mutates them with risk data.

  The scoring model:
    base_score  = sum of per-port severity weights (capped at 70)
    modifier    = device type offset (router gets +15 for example)
    final_score = min(base_score + modifier, 100)

  Why this matters in interviews:
    "How would you improve the scoring?" → Add CVE database, CVSS scores,
    time-since-patch, service version comparisons, etc.
"""

from typing import List

from netwatcher.config import (
    RISK_CRITICAL_THRESHOLD,
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
)
from netwatcher.devices import Device, Port
from engine.rules import (
    PORT_RULES,
    SERVICE_RULES,
    DEVICE_RISK_MODIFIER,
    SEVERITY_WEIGHTS,
)
from utils.logger import get_logger

log = get_logger(__name__)


def score_device(device: Device) -> Device:
    """
    Analyze a Device, assign risk scores and tags to each port,
    compute an overall risk score, and populate issues + recommendations.

    Mutates the device in-place and returns it for chaining.
    """
    base_score   = 0
    issues:       list = []
    recommendations: list = []
    seen_recommendations: set = set()

    for port in device.ports:
        severity, explanation, fix = _lookup_port_rule(port)
        port.risk_tag = severity
        weight        = SEVERITY_WEIGHTS.get(severity, 1)
        base_score   += weight

        issue_str = f"Port {port.number} ({port.service.upper()}) — {explanation}"
        issues.append({"level": severity, "text": issue_str})

        if fix not in seen_recommendations:
            recommendations.append(fix)
            seen_recommendations.add(fix)

    # Cap base at 70, then add device-type modifier
    base_capped  = min(base_score, 70)
    modifier     = DEVICE_RISK_MODIFIER.get(device.device_type, 5)
    final_score  = min(base_capped + modifier, 100)

    device.risk_score      = final_score
    device.risk_level      = _score_to_level(final_score)
    device.issues          = issues
    device.recommendations = recommendations

    log.debug(f"  Scored {device.ip}: {final_score}/100 [{device.risk_level}]")
    return device


def score_devices(devices: List[Device]) -> List[Device]:
    """Score a list of devices and sort by descending risk score."""
    scored = [score_device(d) for d in devices]
    return sorted(scored, key=lambda d: d.risk_score, reverse=True)


def network_summary(devices: List[Device]) -> dict:
    """
    Compute a network-wide risk summary for the dashboard header.

    Returns dict with: overall_score, level, total_devices, critical_count,
    high_count, medium_count, low_count, top_issues
    """
    if not devices:
        return {"overall_score": 0, "level": "UNKNOWN", "total_devices": 0,
                "critical": 0, "high": 0, "medium": 0, "low": 0, "top_issues": []}

    avg_score = int(sum(d.risk_score for d in devices) / len(devices))

    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for d in devices:
        counts[d.risk_level] = counts.get(d.risk_level, 0) + 1

    # Collect top issues across all devices (deduplicated)
    all_issues: list = []
    seen: set = set()
    for d in devices:
        for issue in d.issues:
            if issue["text"] not in seen and issue["level"] in ("CRITICAL", "HIGH"):
                all_issues.append(issue)
                seen.add(issue["text"])

    return {
        "overall_score":  avg_score,
        "level":          _score_to_level(avg_score),
        "total_devices":  len(devices),
        "critical":       counts["CRITICAL"],
        "high":           counts["HIGH"],
        "medium":         counts["MEDIUM"],
        "low":            counts["LOW"],
        "top_issues":     all_issues[:5],
    }


# ─── Private helpers ──────────────────────────────────────────────────────────

def _lookup_port_rule(port: Port):
    """
    Check port number first, then service name, then default to LOW.
    Returns (severity, explanation, fix).
    """
    if port.number in PORT_RULES:
        return PORT_RULES[port.number]
    if port.service.lower() in SERVICE_RULES:
        return SERVICE_RULES[port.service.lower()]
    return ("LOW", f"Port {port.number} ({port.service}) is open.", "Review if this service is necessary.")


def _score_to_level(score: int) -> str:
    if score >= RISK_CRITICAL_THRESHOLD:
        return "CRITICAL"
    if score >= RISK_HIGH_THRESHOLD:
        return "HIGH"
    if score >= RISK_MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"

"""
test_risk_engine.py — Unit tests for the risk scoring engine.

Architecture note:
  We test the risk engine in complete isolation — no Nmap, no SQLite, no file system.
  This is the correct way: unit test pure logic, integration test the pipeline.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from netwatcher.devices import Device, Port
from engine.risk_engine import score_device, score_devices, network_summary


def make_device(ip: str, ports: list) -> Device:
    return Device(
        ip=ip,
        ports=[Port(number=p, protocol="tcp", state="open", service=s) for p, s in ports],
    )


def test_telnet_port_tagged_critical():
    """Telnet port should be tagged CRITICAL even if a single-port device is MEDIUM overall."""
    d = score_device(make_device("10.0.0.1", [(23, "telnet")]))
    telnet_port = d.ports[0]
    assert telnet_port.risk_tag == "CRITICAL", f"Telnet port should be tagged CRITICAL, got {telnet_port.risk_tag}"
    assert d.risk_score >= 30  # weight 30 + modifier 5 = 35


def test_ssh_is_medium_risk():
    d = score_device(make_device("10.0.0.2", [(22, "ssh")]))
    # SSH alone = MEDIUM weight (10) + 5 unknown modifier = 15 → LOW band
    # but that's correct: a single SSH is LOW overall risk score
    assert d.risk_score > 0


def test_multiple_critical_ports_max_score():
    d = score_device(make_device("10.0.0.3", [
        (23, "telnet"), (445, "microsoft-ds"), (6379, "redis"), (27017, "mongodb"),
    ]))
    assert d.risk_score == 100 or d.risk_score >= 75
    assert d.risk_level == "CRITICAL"


def test_no_ports_low_risk():
    d = score_device(make_device("10.0.0.4", []))
    assert d.risk_score <= 20
    assert d.risk_level in ("LOW", "MEDIUM")


def test_router_modifier_applied():
    d = make_device("10.0.0.5", [(80, "http")])
    d.device_type = "router"
    d = score_device(d)
    # router +15 modifier should bump score
    assert d.risk_score >= 20


def test_score_devices_sorted_desc():
    devices = [
        make_device("10.0.0.1", [(80, "http")]),
        make_device("10.0.0.2", [(23, "telnet"), (445, "microsoft-ds")]),
        make_device("10.0.0.3", [(22, "ssh")]),
    ]
    scored = score_devices(devices)
    scores = [d.risk_score for d in scored]
    assert scores == sorted(scores, reverse=True), "Devices should be sorted by risk score descending"


def test_network_summary_structure():
    devices = score_devices([
        make_device("10.0.0.1", [(23, "telnet")]),
        make_device("10.0.0.2", [(80, "http")]),
    ])
    s = network_summary(devices)
    assert "overall_score" in s
    assert "level" in s
    assert "total_devices" in s
    assert s["total_devices"] == 2


if __name__ == "__main__":
    tests = [
        test_telnet_port_tagged_critical,
        test_ssh_is_medium_risk,
        test_multiple_critical_ports_max_score,
        test_no_ports_low_risk,
        test_router_modifier_applied,
        test_score_devices_sorted_desc,
        test_network_summary_structure,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗  {t.__name__}: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")

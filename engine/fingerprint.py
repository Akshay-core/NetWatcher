"""
fingerprint.py — Enriches Device objects with contextual intelligence.

Architecture reasoning:
  Fingerprinting is separate from scanning and risk scoring.
  It bridges raw nmap data → richer context that the risk engine uses.

  In a production system this would:
    - Query MAC vendor OUI database (IEEE)
    - Cross-reference with Shodan for internet-exposed hosts
    - Match OS version against CVE databases

  Here we implement the offline version cleanly.
"""

from netwatcher.devices import Device
from utils.logger import get_logger

log = get_logger(__name__)

# MAC prefix → vendor mapping (top home-network vendors)
MAC_VENDOR_MAP = {
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Foundation",
    "E4:5F:01": "Raspberry Pi Foundation",
    "18:FE:34": "Espressif (IoT device)",
    "30:AE:A4": "Espressif (IoT device)",
    "3C:61:05": "TP-Link",
    "50:C7:BF": "TP-Link",
    "14:CC:20": "TP-Link",
    "C8:3A:35": "Tenda Networks",
    "00:90:4C": "Epigram (Broadcom chipset)",
    "AC:9E:17": "Huawei",
    "20:0B:C7": "Huawei",
    "D4:6E:0E": "D-Link",
    "1C:7E:E5": "D-Link",
    "00:E0:4C": "Realtek",
    "44:D9:E7": "Netgear",
    "A0:40:A0": "Netgear",
}


def fingerprint_device(device: Device) -> Device:
    """
    Enrich a Device with vendor info and a refined device type if MAC is known.
    Mutates device in-place and returns it.
    """
    mac = device.mac.upper()

    # Try to resolve vendor from MAC OUI (first 3 octets)
    if mac and mac != "UNKNOWN":
        oui = mac[:8]  # e.g. "B8:27:EB"
        matched_vendor = MAC_VENDOR_MAP.get(oui)
        if matched_vendor and device.vendor == "unknown":
            device.vendor = matched_vendor
            log.debug(f"  Fingerprint: {device.ip} → vendor={matched_vendor}")

    # Refine device_type if we now have vendor context
    vendor_low = device.vendor.lower()
    if device.device_type == "unknown":
        if "raspberry" in vendor_low:
            device.device_type = "linux-device"
        elif "espressif" in vendor_low or "iot" in vendor_low:
            device.device_type = "iot-device"
        elif "tp-link" in vendor_low or "netgear" in vendor_low or "d-link" in vendor_low:
            device.device_type = "router"

    return device


def fingerprint_devices(devices):
    """Apply fingerprinting to a list of devices."""
    return [fingerprint_device(d) for d in devices]

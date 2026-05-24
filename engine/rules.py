"""
rules.py — Vulnerability rule definitions for the risk engine.

Architecture reasoning:
  Rules are DATA, not code. Keeping them separate means:
    1. Non-engineers can edit rules without touching logic
    2. In a real product, these come from a database or external feed (NVD, CVE)
    3. Interviewers LOVE this pattern — "rule engine separation"

  Format:
    PORT_RULES   → port number → (severity, explanation, recommendation)
    SERVICE_RULES → service name → (severity, explanation, recommendation)
    DEVICE_RISK_MODIFIER → device type adds a base risk score offset
"""

from typing import Dict, Tuple

# (severity_label, human_explanation, fix_recommendation)
RuleEntry = Tuple[str, str, str]

# ─── Port-based rules ─────────────────────────────────────────────────────────
PORT_RULES: Dict[int, RuleEntry] = {
    21:   ("HIGH",     "FTP port is open. FTP transmits credentials in plaintext.",
                       "Disable FTP. Use SFTP or SCP instead."),
    22:   ("MEDIUM",   "SSH is exposed. Weak or default credentials allow brute-force access.",
                       "Disable password auth; use SSH key pairs. Restrict to known IPs."),
    23:   ("CRITICAL", "Telnet is open. All traffic including passwords is transmitted unencrypted.",
                       "Disable Telnet immediately. Replace with SSH."),
    25:   ("HIGH",     "SMTP relay port open. May be exploited for spam or email spoofing.",
                       "Restrict SMTP relay to authenticated users only."),
    53:   ("MEDIUM",   "DNS port exposed externally. May allow zone transfer or DNS amplification attacks.",
                       "Restrict DNS to internal clients only."),
    80:   ("LOW",      "HTTP web server running. Traffic is unencrypted.",
                       "Migrate to HTTPS. Ensure no admin panels are exposed."),
    110:  ("MEDIUM",   "POP3 mail port open. Credentials sent in cleartext.",
                       "Use POP3S (port 995) with TLS."),
    135:  ("HIGH",     "Windows RPC port open. Common exploitation vector for lateral movement.",
                       "Block from internet. Restrict to internal trusted hosts."),
    139:  ("HIGH",     "NetBIOS session port open. Vulnerable to SMB-related attacks.",
                       "Disable NetBIOS over TCP/IP if not needed."),
    143:  ("MEDIUM",   "IMAP port open in cleartext mode.",
                       "Use IMAPS (port 993) instead."),
    443:  ("LOW",      "HTTPS running. Ensure certificate is valid and TLS 1.2+ enforced.",
                       "Audit TLS configuration with SSL Labs."),
    445:  ("CRITICAL", "SMB port exposed. EternalBlue, WannaCry exploit this vector.",
                       "Block port 445 at firewall. Patch system immediately."),
    3306: ("HIGH",     "MySQL database port exposed to network.",
                       "Bind MySQL to localhost only (bind-address=127.0.0.1)."),
    3389: ("HIGH",     "RDP port open. BlueKeep and credential attacks target this port.",
                       "Disable if not needed. Enable NLA. Use VPN for remote access."),
    5900: ("HIGH",     "VNC remote desktop exposed. Often uses weak or no authentication.",
                       "Disable VNC or restrict to localhost. Use SSH tunneling."),
    6379: ("CRITICAL", "Redis exposed without auth. Attackers can read/write all data.",
                       "Bind Redis to localhost. Enable requirepass in redis.conf."),
    8080: ("LOW",      "Alternative HTTP port running. Check if admin panel is exposed.",
                       "Ensure no development server or admin UI is accessible."),
    8443: ("LOW",      "Alternative HTTPS port. Verify it's intentional.",
                       "Audit what service runs here."),
    9200: ("CRITICAL", "Elasticsearch port exposed. No auth by default — data breach risk.",
                       "Bind to localhost. Enable security features in elasticsearch.yml."),
    27017:("CRITICAL", "MongoDB port exposed. Default install has no authentication.",
                       "Enable MongoDB auth. Bind to 127.0.0.1 only."),
}

# ─── Service-based rules (by service name from nmap) ─────────────────────────
SERVICE_RULES: Dict[str, RuleEntry] = {
    "telnet":     ("CRITICAL", "Telnet service detected. Unencrypted legacy protocol.",
                               "Replace with SSH immediately."),
    "ftp":        ("HIGH",     "FTP service detected. Cleartext credential transmission.",
                               "Switch to SFTP/FTPS."),
    "vnc":        ("HIGH",     "VNC remote access detected.",
                               "Use SSH tunnel for VNC or switch to a VPN."),
    "rdesktop":   ("HIGH",     "RDP service found.",
                               "Restrict RDP behind VPN."),
    "smtp":       ("MEDIUM",   "Mail server exposed.",
                               "Ensure relay is authenticated."),
    "snmp":       ("HIGH",     "SNMP service exposed. Default community strings are guessable.",
                               "Use SNMPv3 with authentication. Change default strings."),
    "http":       ("LOW",      "Unencrypted HTTP service.",
                               "Upgrade to HTTPS."),
    "mysql":      ("HIGH",     "MySQL database exposed on network.",
                               "Bind to localhost."),
    "mongodb":    ("CRITICAL", "MongoDB exposed. No auth by default.",
                               "Enable auth and bind to localhost."),
    "redis":      ("CRITICAL", "Redis exposed without authentication.",
                               "Add requirepass and bind to localhost."),
    "elasticsearch": ("CRITICAL", "Elasticsearch exposed. No auth by default in older versions.",
                                  "Enable X-Pack security."),
}

# ─── Device-type risk modifier (added to base score) ─────────────────────────
DEVICE_RISK_MODIFIER: Dict[str, int] = {
    "router":       +15,   # highest value target on a home network
    "server":       +10,
    "ip-camera":    +10,   # often unpatched firmware
    "printer":      +5,
    "windows-pc":   +5,
    "linux-device": +3,
    "mobile":        0,
    "unknown":       +5,   # unknown = assume worst
}

# ─── Port risk weights (used in numeric score calculation) ────────────────────
SEVERITY_WEIGHTS: Dict[str, int] = {
    "CRITICAL": 30,
    "HIGH":     20,
    "MEDIUM":   10,
    "LOW":       5,
    "INFO":      1,
}

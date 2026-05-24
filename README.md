<div align="center">

<img src="https://raw.githubusercontent.com/Akshay-core/netwatcher/main/assets/banner.png" alt="NetWatcher Banner" width="100%">

# 🛡 NetWatcher
### AI-Powered Home Network Vulnerability Scanner

**Scan your network. Understand your risks. Fix them — even if you're not a tech expert.**

<br>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Nmap](https://img.shields.io/badge/Engine-Nmap-4EAA25?style=for-the-badge)](https://nmap.org)
[![AI](https://img.shields.io/badge/AI-Mistral%207B%20%2B%20Ollama-FF6B35?style=for-the-badge)](https://ollama.ai)
[![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?style=for-the-badge)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[![GitHub](https://img.shields.io/badge/GitHub-Akshay--core-181717?style=flat-square&logo=github)](https://github.com/Akshay-core)
[![Portfolio](https://img.shields.io/badge/Portfolio-akshay.fruvvi.com-0077B5?style=flat-square)](https://akshay.fruvvi.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Akshay-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/akshay-tb-791bb4372)

<br>

> *"Most network scanners just print ports. NetWatcher thinks like a security analyst — it scores risk, simulates attacks, and explains everything in plain English a 14-year-old can understand."*

<br>

---

</div>

## 📖 Table of Contents

- [What Is This?](#-what-is-this)
- [Who Is This For?](#-who-is-this-for)
- [Live Demo](#-live-demo)
- [How It Works](#-how-it-works)
- [Architecture](#-architecture)
- [Feature Breakdown](#-feature-breakdown)
- [AI Engine](#-ai-engine)
- [Quick Start](#-quick-start--one-command-setup)
- [Usage Guide](#-usage-guide)
- [Report Walkthrough](#-report-walkthrough)
- [Risk Scoring Model](#-risk-scoring-model)
- [Attack Simulation Logic](#-attack-simulation-logic)
- [Tech Stack Decisions](#-tech-stack--every-decision-explained)
- [Folder Structure](#-folder-structure)
- [Interview Questions](#-interview-questions-this-generates)
- [Roadmap](#-roadmap)
- [Developer](#-developer)

---

## 🔍 What Is This?

NetWatcher is a **free, offline-first network security auditing tool** that does what paid enterprise scanners do — for your home or lab network, at zero cost.

You run one command. NetWatcher:

1. Discovers every device on your network
2. Identifies what each device is (router, PC, IoT device, camera…)
3. Scans for open ports and dangerous services
4. Scores each device 0–100 for risk
5. Simulates how an attacker would exploit each vulnerability
6. Uses a local AI model to write plain-English explanations
7. Generates a beautiful visual HTML dashboard report — offline, private, no cloud

```
Before NetWatcher:   "Port 23 open"          ← meaningless to most people
After NetWatcher:    "Telnet is open on your router — this is like leaving your
                      front door unlocked with the key taped to it. Disable it
                      in router settings in under 5 minutes."
```

This is what separates a script from a product.

---

## 🎯 Who Is This For?

| Person | Why NetWatcher helps |
|--------|---------------------|
| 🎓 CS / Cybersecurity student | Portfolio project that demonstrates system design, security thinking, and AI integration at once |
| 🏠 Home user | Understand what's exposed on your network without needing security knowledge |
| 🔒 Security hobbyist | Lightweight Nessus alternative for home lab auditing |
| 💼 Internship seeker | Shows recruiters: pipeline architecture, AI integration, product thinking, and security domain knowledge |
| 🧑‍💻 Developer | Learn how real security tools are structured — layers, rules engines, typed data models |

---

## 🎬 Live Demo

```
$ python netwatcher.py scan --local --open

╭──────────────────────────────────────────────────╮
│  🛡  NetWatcher  v1.0.0                          │
│  AI-Powered Network Vulnerability Scanner        │
│  Developer : Akshay  ·  akshay.fruvvi.com        │
╰──────────────────────────────────────────────────╯

Auto-detected local subnet: 192.168.1.0/24

Target: 192.168.1.0/24
⠸ Discovering hosts…
⠸ Fingerprinting devices…
⠸ Running risk analysis…
⠸ Running AI analysis…  (mistral:7b-instruct-q4_K_M)

┌─────────────────┬──────────────────┬────────────┬───────┬────────────┬──────────┐
│ IP              │ Hostname         │ Type       │ Ports │ Risk Score │ Level    │
├─────────────────┼──────────────────┼────────────┼───────┼────────────┼──────────┤
│ 192.168.1.1     │ RTK_GW.bbrouter  │ router     │ 4     │  87/100    │ CRITICAL │
│ 192.168.1.3     │ AKSHAY.bbrouter  │ windows-pc │ 3     │  75/100    │ CRITICAL │
│ 192.168.1.130   │ esp32-iot        │ iot-device │ 2     │  55/100    │ HIGH     │
└─────────────────┴──────────────────┴────────────┴───────┴────────────┴──────────┘

╭──────────────────────────────────────────────────────────────╮
│  NETWORK SECURITY SCORE: 72/100  HIGH RISK                   │
│  Devices: 3  Critical: 2  High: 1  Medium: 0  Low: 0        │
╰──────────────────────────────────────────────────────────────╯

✓ Report saved: reports/exports/netwatcher_report_20240115_143022.html
  Opening in browser…
```

**The HTML report includes:**
- 📊 Risk breakdown donut chart
- 📈 Per-device risk score bar chart  
- 🔴 Color-coded device cards with plain-English AI explanations
- ⚔ Attack simulation flowcharts per vulnerability
- ✅ Step-by-step fix plan with time estimates

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NETWATCHER PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  You type:  python netwatcher.py scan --local
                          │
                          ▼
         ┌────────────────────────────┐
         │   1. NETWORK DISCOVERY     │
         │   scanner.py + Nmap        │
         │                            │
         │   • Pings subnet range     │
         │   • Detects live hosts     │
         │   • Grabs OS fingerprint   │
         │   • Lists all open ports   │
         │   • Reads service banners  │
         └─────────────┬──────────────┘
                       │  List of Device objects
                       ▼
         ┌────────────────────────────┐
         │   2. DEVICE FINGERPRINTING │
         │   engine/fingerprint.py    │
         │                            │
         │   • MAC → vendor lookup    │
         │   • Classifies device type │
         │     (router/PC/IoT/camera) │
         │   • Enriches OS context    │
         └─────────────┬──────────────┘
                       │  Enriched Device objects
                       ▼
         ┌────────────────────────────┐
         │   3. RISK ANALYSIS         │
         │   engine/risk_engine.py    │
         │   engine/rules.py          │
         │                            │
         │   • Port → severity lookup │
         │   • Service → rule match   │
         │   • Score = Σ weights      │
         │     + device modifier      │
         │   • Tags each port         │
         │   • Builds issue list      │
         └─────────────┬──────────────┘
                       │  Scored Device objects (0–100)
                       ▼
         ┌────────────────────────────┐
         │   4. AI ANALYSIS           │
         │   ai/analyzer.py           │
         │   ai/prompts.py            │
         │   ai/ollama_client.py      │
         │                            │
         │   • Compresses scan data   │
         │   • Builds surgical prompt │
         │   • Calls Ollama API       │
         │     (local, private, free) │
         │   • Parses JSON response   │
         │   • Falls back gracefully  │
         └─────────────┬──────────────┘
                       │  AI analysis dict (or fallback)
                       ▼
         ┌────────────────────────────┐
         │   5. PERSISTENCE           │
         │   data/db.py (SQLite)      │
         │                            │
         │   • Saves scan session     │
         │   • Stores all devices     │
         │   • Enables history view   │
         │   • Tracks risk over time  │
         └─────────────┬──────────────┘
                       │  scan_id
                       ▼
         ┌────────────────────────────┐
         │   6. REPORT GENERATION     │
         │   reports/generator.py     │
         │   reports/templates/*.html │
         │                            │
         │   • Jinja2 renders HTML    │
         │   • Chart.js bar + donut   │
         │   • Attack flowcharts      │
         │   • Action plan            │
         │   • Single file output     │
         └─────────────┬──────────────┘
                       │
                       ▼
            📄 netwatcher_report.html
              (self-contained, offline)
```

---

## 🏗 Architecture

### Design Principle: Strict Layer Separation

Every module has **one job** and knows nothing about the layers above or below it. This is the same pattern used in production security tools like Nessus and OpenVAS.

```
┌─────────────────────────────────────────────────────┐
│                    LAYER MAP                        │
├──────────────┬──────────────────────────────────────┤
│ Presentation │ cli.py, reports/                     │
│              │ → Rich terminal UI + HTML dashboard  │
├──────────────┼──────────────────────────────────────┤
│ AI           │ ai/analyzer.py, ai/prompts.py        │
│              │ → Local LLM via Ollama               │
├──────────────┼──────────────────────────────────────┤
│ Analysis     │ engine/risk_engine.py                │
│              │ → Pure scoring logic, no I/O         │
├──────────────┼──────────────────────────────────────┤
│ Rules        │ engine/rules.py                      │
│              │ → Data only, zero logic              │
├──────────────┼──────────────────────────────────────┤
│ Enrichment   │ engine/fingerprint.py                │
│              │ → MAC OUI, device type detection     │
├──────────────┼──────────────────────────────────────┤
│ Discovery    │ netwatcher/scanner.py                │
│              │ → Nmap wrapper, typed output only    │
├──────────────┼──────────────────────────────────────┤
│ Data Model   │ netwatcher/devices.py                │
│              │ → Device + Port dataclasses          │
├──────────────┼──────────────────────────────────────┤
│ Persistence  │ data/db.py                           │
│              │ → SQLite, scan history               │
└──────────────┴──────────────────────────────────────┘
```

**Why this matters:** You can swap Nmap for a different scanner by changing only `scanner.py`. You can swap SQLite for PostgreSQL by changing only `db.py`. You can swap Ollama for OpenAI by changing only `ollama_client.py`. Nothing else needs to touch.

### Data Flow (typed contract between layers)

```
Nmap XML output
      │
      │  scanner.py parses into:
      ▼
  Device(
    ip="192.168.1.1",
    ports=[Port(number=23, service="telnet", risk_tag="?")],
    risk_score=0          ← not set yet
  )
      │
      │  risk_engine.py fills in:
      ▼
  Device(
    ip="192.168.1.1",
    ports=[Port(number=23, service="telnet", risk_tag="CRITICAL")],
    risk_score=87,
    issues=[{"level":"CRITICAL", "text":"Telnet is open..."}],
    recommendations=["Disable Telnet immediately..."]
  )
      │
      │  .to_dict() for Jinja2/SQLite:
      ▼
  Plain dict → template renders → HTML report
```

---

## ✨ Feature Breakdown

### 🧠 Risk Scoring Engine
Not just "port open." Every port is weighted by real-world severity. A Telnet port (23) scores 30 points. SSH (22) scores 10. Device type adds a modifier — routers get +15 because they're the highest-value target on any home network. Final score is 0–100 with four thresholds.

### 🔍 Device Fingerprinting
Uses MAC OUI (the first 3 bytes of a MAC address, which identify the manufacturer) combined with Nmap OS detection to classify every device. Your ESP32 IoT device, Raspberry Pi, HP printer, and Windows laptop each get correctly identified — not labeled "unknown host."

### 📋 Rule-Based Vulnerability Engine
`engine/rules.py` is pure data — a dictionary of port numbers and service names mapped to severity, explanation, and fix. No logic lives there. This is intentional: rules are policy, the engine is mechanism. Adding a new vulnerability means one new dict entry, nothing else.

### 🤖 AI Plain-English Analysis
When Ollama is running, a local Mistral 7B model reads the scan results and writes explanations a non-technical person can act on. No jargon without immediate explanation. Uses everyday analogies. Falls back gracefully if AI is offline.

### ⚔ Attack Simulation Flowcharts
For every CRITICAL or HIGH port, the HTML report shows a 3-step attack simulation: Discovery → Exploit → Prevention. Not theoretical — based on real attack patterns (EternalBlue, BlueKeep, Redis unauthenticated RCE, Telnet interception).

### 🗃 Scan History Timeline
Every scan is saved to a local SQLite database. Run `netwatcher history` to see all previous scans with risk scores. Run the same scan weekly — track whether your network is getting more or less secure over time.

### 📊 Visual HTML Dashboard
Single self-contained HTML file. No server needed. Open it in any browser, share it with anyone. Includes Chart.js donut and bar charts, color-coded device cards, attack flowcharts, and a step-by-step action plan.

---

## 🤖 AI Engine

### Why a local model, not ChatGPT/OpenAI?

Your network scan contains sensitive data — IP addresses, open ports, device names, MAC addresses. Sending that to a cloud API is a privacy and security anti-pattern for a security tool. NetWatcher runs everything locally.

```
Cloud API path:                   NetWatcher path:
  Your scan data                    Your scan data
       │                                  │
       ▼                                  ▼
  OpenAI servers  ← PRIVACY RISK    Ollama (localhost:11434)
  (leaves device)                    (never leaves your machine)
       │                                  │
       ▼                                  ▼
  Analysis                          Analysis
  ❌ Costs money                    ✅ Free
  ❌ Needs internet                 ✅ Fully offline
  ❌ Data exposed                   ✅ Private
```

### Model Selection — Why Mistral 7B Q4_K_M

```
┌─────────────────────────┬──────────┬──────────────┬────────────────┐
│ Model                   │ VRAM     │ JSON Accuracy│ Speed (3050)   │
├─────────────────────────┼──────────┼──────────────┼────────────────┤
│ mistral:7b-q4_K_M  ← ✓ │ ~4.1 GB  │ ★★★★☆       │ ~15 tok/s      │
│ llama3.2:3b             │ ~2.0 GB  │ ★★★☆☆       │ ~35 tok/s      │
│ phi3:mini               │ ~2.3 GB  │ ★★★★☆       │ ~30 tok/s      │
│ llama3.1:8b-q4          │ ~5.0 GB  │ ★★★★★       │ ~10 tok/s      │
└─────────────────────────┴──────────┴──────────────┴────────────────┘
```

Mistral 7B Q4_K_M is chosen because:
- **Fits 4GB VRAM** — RTX 3050 compatible, 35 GPU layers, 1 CPU layer
- **Instruction-tuned** — follows the JSON schema contract reliably
- **Sliding window attention** — handles long scan data without truncation
- **Q4_K_M quantization** — ~1% accuracy loss vs full precision, 3.5x smaller

### Surgical Prompt Engineering

The prompt in `ai/prompts.py` uses 5 techniques that each have measurable effects:

```
┌──────────────────────────────────────────────────────────────────┐
│                     PROMPT ARCHITECTURE                          │
├───────────────────────┬──────────────────────────────────────────┤
│ TECHNIQUE             │ WHAT IT DOES                             │
├───────────────────────┼──────────────────────────────────────────┤
│ 1. Role Anchoring     │ "You are a senior security analyst       │
│                       │  writing for non-technical users"        │
│                       │ → Model draws from security domain       │
│                       │   training, adjusts reading level        │
├───────────────────────┼──────────────────────────────────────────┤
│ 2. Strict JSON Schema │ Output format defined explicitly in      │
│                       │  system prompt with every key named      │
│                       │ → Model "knows" the shape before         │
│                       │   seeing any input data                  │
├───────────────────────┼──────────────────────────────────────────┤
│ 3. Few-Shot Example   │ One worked example shows exact           │
│                       │  tone ("like a postcard anyone           │
│                       │  can read") and structure               │
│                       │ → Teaches style, not just format         │
├───────────────────────┼──────────────────────────────────────────┤
│ 4. Negative Rules     │ "Do NOT add markdown.                    │
│                       │  Do NOT explain outside the JSON."       │
│                       │ → Prevents the #1 failure mode:         │
│                       │   preamble text breaking JSON parse      │
├───────────────────────┼──────────────────────────────────────────┤
│ 5. Context Last       │ Scan data injected at END of prompt      │
│                       │ → Transformer attention is               │
│                       │   recency-biased; most recent           │
│                       │   content gets highest attention         │
└───────────────────────┴──────────────────────────────────────────┘

temperature = 0.0  →  Deterministic output. No creativity needed.
                       Reliability > variety for JSON parsing.
```

### Graceful Fallback

```
  Is Ollama running?
         │
    No ──┼──► Rule-based fallback analysis
         │    (same output shape, auto-generated from rules)
        Yes
         │
  Model installed?
         │
    No ──┼──► Rule-based fallback analysis
         │
        Yes
         │
  JSON parseable?
         │
    No ──┼──► Rule-based fallback analysis (3 recovery attempts first)
         │
        Yes
         │
         ▼
    AI analysis in report
    (badge shows model name)
```

The report always generates. The fallback produces identical structure. The template never crashes because AI is optional.

---

## 🚀 Quick Start — One Command Setup

### Windows

```powershell
# 1. Install Python 3.10+ from https://python.org/downloads (check "Add to PATH")
# 2. Install Nmap from https://nmap.org/download.html
# 3. Open PowerShell and run:

git clone https://github.com/Akshay-core/netwatcher
cd netwatcher
pip install -r requirements.txt
python netwatcher.py check
python netwatcher.py scan --local --open
```

### macOS

```bash
# One-liner prerequisites (requires Homebrew: brew.sh)
brew install python nmap git && \
git clone https://github.com/Akshay-core/netwatcher && \
cd netwatcher && \
pip3 install -r requirements.txt && \
python3 netwatcher.py scan --local --open
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y python3 python3-pip nmap git && \
git clone https://github.com/Akshay-core/netwatcher && \
cd netwatcher && \
pip3 install -r requirements.txt && \
python3 netwatcher.py scan --local --open
```

### Enable AI Analysis (optional, one time)

```bash
# Linux/Mac (auto-install):
bash scripts/setup_ai.sh

# Windows — download installer from:
# https://ollama.ai/download
# Then run:
ollama pull mistral:7b-instruct-q4_K_M

# Verify AI is ready:
python netwatcher.py check
```

> **No Ollama?** The tool works fully without AI. Reports still generate with rule-based analysis. AI adds plain-English explanations on top.

---

## 📋 Usage Guide

### Core Commands

```bash
# Scan your local network (auto-detects subnet)
python netwatcher.py scan --local

# Scan and open the HTML report immediately in browser
python netwatcher.py scan --local --open

# Scan a specific IP range
python netwatcher.py scan --target 192.168.1.0/24

# Scan a single device
python netwatcher.py scan --target 192.168.1.1

# Scan without generating HTML report (terminal only)
python netwatcher.py scan --local --no-report

# Enable verbose debug logging
python netwatcher.py scan --local --verbose
```

### History & Reports

```bash
# View all past scans with risk scores
python netwatcher.py history

# View last 5 scans only
python netwatcher.py history --limit 5

# Open the most recent HTML report in browser
python netwatcher.py report

# Verify environment (nmap, python packages, ollama)
python netwatcher.py check
```

### Command Reference

```
netwatcher scan     Run a network scan
  --local    -l     Auto-detect and scan local subnet
  --target   -t     Specific IP or CIDR range
  --open            Open HTML report in browser after scan
  --no-report       Skip HTML report generation
  --verbose  -v     Show debug logs

netwatcher report   Open most recent report in browser
netwatcher history  Show scan history from database
netwatcher check    Preflight check (nmap, deps, ollama)
```

---

## 📊 Report Walkthrough

The HTML report is divided into 6 sections:

```
┌──────────────────────────────────────────────────────────────────┐
│  SECTION 1: VERDICT BANNER                                       │
│  ─────────────────────────────────────────────────────────────── │
│  Large risk score (0–100), color-coded banner (red/yellow/       │
│  blue/green), AI plain-English summary, model badge             │
├──────────────────────────────────────────────────────────────────┤
│  SECTION 2: STATS ROW                                            │
│  ─────────────────────────────────────────────────────────────── │
│  Four counters: Critical / High / Medium / Low device counts    │
├──────────────────────────────────────────────────────────────────┤
│  SECTION 3: CHARTS                                               │
│  ─────────────────────────────────────────────────────────────── │
│  Left:  Donut chart — risk level breakdown                       │
│  Right: Bar chart — individual device risk scores               │
├──────────────────────────────────────────────────────────────────┤
│  SECTION 4: ATTACK SIMULATION FLOWCHARTS                         │
│  ─────────────────────────────────────────────────────────────── │
│  One card per CRITICAL/HIGH port found:                          │
│    Step 1: Discovery  → how attacker finds this                  │
│    Step 2: Exploit    → what they do with it (plain English)     │
│    Step 3: Prevention → exact fix instruction                    │
├──────────────────────────────────────────────────────────────────┤
│  SECTION 5: FIX PLAN                                             │
│  ─────────────────────────────────────────────────────────────── │
│  Numbered steps from AI analysis, priority-tagged               │
│  (URGENT / SOON / OPTIONAL), with time estimates                │
├──────────────────────────────────────────────────────────────────┤
│  SECTION 6: DEVICE CARDS                                         │
│  ─────────────────────────────────────────────────────────────── │
│  One card per device:                                            │
│    • Risk score bar, level badge, device icon                    │
│    • AI plain-English biggest risk explanation                   │
│    • Open port tags (color-coded by severity)                    │
│    • One-line beginner action                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Risk Scoring Model

### How the Score is Calculated

```
┌─────────────────────────────────────────────────────────────────┐
│  score = min( Σ(port_weights) capped at 70  +  device_modifier, 100 )
└─────────────────────────────────────────────────────────────────┘

Example: Router with Telnet + SMB open

  Port 23  (telnet)       → CRITICAL  → +30
  Port 445 (smb)          → CRITICAL  → +30
  ─────────────────────────────────────────
  Base score              =  60  (capped at 70, so stays 60)
  Device modifier (router)= +15
  ─────────────────────────────────────────
  Final score             =  75  → CRITICAL
```

### Port Severity Weights

```
┌──────────────────────────────────────────────────────────────┐
│ CRITICAL (+30)     HIGH (+20)       MEDIUM (+10)  LOW (+5)   │
│                                                              │
│ 23  Telnet         21  FTP          22  SSH        80  HTTP  │
│ 445 SMB            25  SMTP         53  DNS        443 HTTPS │
│ 6379 Redis         135 Win RPC      110 POP3       8080      │
│ 27017 MongoDB      139 NetBIOS      143 IMAP                 │
│ 9200 Elasticsearch 3306 MySQL                               │
│                    3389 RDP                                  │
│                    5900 VNC                                  │
└──────────────────────────────────────────────────────────────┘
```

### Device Type Modifiers

```
router         +15   (highest-value target on home networks)
server         +10   (multiple services, persistence target)
ip-camera      +10   (often unpatched, used in botnets)
printer        +5    (often forgotten, long-lived on network)
windows-pc     +5    (SMB, RDP attack surface)
linux-device   +3
mobile          0
unknown        +5    (assume worst when can't identify)
```

### Score to Risk Level

```
75 – 100  →  🔴 CRITICAL   (immediate action required)
50 – 74   →  🟡 HIGH       (action within days)
25 – 49   →  🔵 MEDIUM     (address when possible)
 0 – 24   →  🟢 LOW        (monitor, minor improvements)
```

---

## ⚔ Attack Simulation Logic

Each attack flowchart in the report is based on real attack patterns, not made-up scenarios:

```
PORT 23 — TELNET
┌─────────────────────────────────────────────────────────────────┐
│ Discovery:  Attacker scans the internet for port 23             │
│             (Shodan indexes millions of Telnet-exposed devices) │
│                           ↓                                     │
│ Exploit:    Telnet sends username + password in plain text.     │
│             Attacker on same network runs Wireshark and reads   │
│             credentials directly — no hacking required.         │
│                           ↓                                     │
│ Prevention: Log into router admin panel → Disable Telnet →     │
│             Enable SSH instead. Takes 5 minutes.                │
└─────────────────────────────────────────────────────────────────┘

PORT 445 — SMB (Windows File Sharing)
┌─────────────────────────────────────────────────────────────────┐
│ Discovery:  Attacker uses Nmap or Shodan to find SMB-exposed    │
│             hosts. This is the same scan NetWatcher just did.   │
│                           ↓                                     │
│ Exploit:    EternalBlue (CVE-2017-0144) exploits SMBv1.         │
│             WannaCry ransomware used this exact vector in 2017, │
│             infecting 230,000 machines in 150 countries.        │
│                           ↓                                     │
│ Prevention: Windows Update → patch all updates.                 │
│             Firewall → block port 445 from external access.     │
└─────────────────────────────────────────────────────────────────┘

PORT 6379 — REDIS
┌─────────────────────────────────────────────────────────────────┐
│ Discovery:  Attacker connects to port 6379. Default Redis       │
│             install: no password, no auth, full access.         │
│                           ↓                                     │
│ Exploit:    redis-cli -h 192.168.1.x  → KEYS *  →              │
│             dumps entire database. Or: CONFIG SET dir /root/.ssh │
│             to write SSH keys for server access.                │
│                           ↓                                     │
│ Prevention: Add to redis.conf:  requirepass yourpassword        │
│             Add:               bind 127.0.0.1                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack — Every Decision Explained

| Component | Choice | Why |
|-----------|--------|-----|
| **Scanner** | Nmap + python-nmap | Industry standard. XML output gives structured data for free. OS/version detection built in. |
| **Language** | Python 3.8+ | Standard in security tooling. Rich ecosystem. No compilation step — clone and run. |
| **CLI** | Typer + Rich | Typer: typed args + auto-help. Rich: professional tables, spinners, panels. Together = product-grade terminal UI. |
| **Data model** | Dataclasses | Typed contract between every layer. Catch bugs at definition time. No external dependency. Swap to Pydantic trivially. |
| **Rules** | Plain dict in `rules.py` | Rules are data, not code. Edit one file to add a vulnerability. Same pattern used in Snort IDS, Sigma rules, YARA. |
| **AI runtime** | Ollama (local) | Zero cost. Private. No internet. One-command install. Manages model downloads and GPU layers automatically. |
| **AI model** | Mistral 7B Q4_K_M | Best accuracy/VRAM tradeoff for RTX 3050 4GB. Instruction-tuned = follows JSON schema. Quantized = fits in 4GB. |
| **Templates** | Jinja2 | Python-native. Separates HTML from logic completely. Same engine used by Flask/Django. |
| **Charts** | Chart.js (CDN) | No build step. Renders in any browser. Report is self-contained single HTML file. |
| **Database** | SQLite | Zero infrastructure. Single file. Python stdlib. Identical API to PostgreSQL — swap with one line change. |
| **Storage format** | JSON in SQLite | Device data is nested (ports inside devices). JSON columns avoid complex joins while keeping SQLite simplicity. |

### What Was Deliberately NOT Used

| Skipped | Why |
|---------|-----|
| Docker | Adds friction for a local tool. Nmap needs raw sockets (host networking) which complicates Docker anyway. |
| FastAPI/Flask backend | No need for a server. The HTML report is static. A server would mean "always running" just to view history. |
| React frontend | Zero-dependency single HTML file is more portable and recruiter-readable than a `npm install` step. |
| OpenAI/Anthropic API | Privacy violation for a security tool. Network data should not leave the machine. |
| Fine-tuning | Requires labeled training data + 16GB+ VRAM + weeks of work. RAG + prompt engineering achieves 90% of the benefit at 1% of the cost. |

---

## 📁 Folder Structure

```
NetWatcher/
│
├── netwatcher/              # Core package
│   ├── __init__.py          # Developer watermark + version
│   ├── cli.py               # CLI entry point (Typer + Rich)
│   ├── scanner.py           # Nmap wrapper → typed Device objects
│   ├── devices.py           # Device + Port dataclasses (typed contract)
│   └── config.py            # All settings in one place
│
├── engine/                  # Analysis brain — pure logic, no I/O
│   ├── risk_engine.py       # Scoring algorithm
│   ├── rules.py             # Vulnerability rules ← EDIT THIS to add rules
│   └── fingerprint.py       # MAC OUI + device type detection
│
├── ai/                      # AI analysis layer
│   ├── analyzer.py          # Orchestrates AI pipeline + fallback
│   ├── ollama_client.py     # Ollama API client + model selection
│   └── prompts.py           # All prompts ← EDIT THIS to tune AI output
│
├── data/                    # Persistence
│   ├── db.py                # SQLite handler (scan history)
│   └── seed_data.json       # Mock CVE reference data
│
├── reports/                 # Output generation
│   ├── generator.py         # Jinja2 renderer
│   ├── templates/
│   │   └── report.html      # Dashboard template (Chart.js)
│   └── exports/             # Generated reports saved here
│
├── utils/
│   ├── logger.py            # Centralized logging
│   └── helpers.py           # Shared utilities
│
├── tests/
│   └── test_risk_engine.py  # Unit tests (7/7 passing)
│
├── scripts/
│   ├── install.sh           # One-command Linux/Mac setup
│   └── setup_ai.sh          # Ollama + model setup
│
├── netwatcher.py            # Single entry point
├── requirements.txt         # 4 dependencies only
├── README.md
└── .gitignore
```

---

## 🧪 Tests

```bash
python tests/test_risk_engine.py

  ✓  test_telnet_port_tagged_critical
  ✓  test_ssh_is_medium_risk
  ✓  test_multiple_critical_ports_max_score
  ✓  test_no_ports_low_risk
  ✓  test_router_modifier_applied
  ✓  test_score_devices_sorted_desc
  ✓  test_network_summary_structure

7/7 tests passed
```

Tests cover the risk engine in complete isolation — no Nmap, no SQLite, no file system, no Ollama. This is correct unit test design: test pure logic independently from I/O.

---

## 💼 Interview Questions This Generates

These are real questions you will get if you put NetWatcher on your resume:

**Architecture:**
- *"Why did you separate rules.py from risk_engine.py?"* → Rules are policy (data), engine is mechanism (logic). Adding a new vulnerability rule means one dict entry, zero code changes. Same pattern as Snort IDS rules, Sigma detection rules.
- *"How would you scale this to scan 10,000 hosts?"* → `ThreadPoolExecutor` for parallel Nmap processes, stream results to SQLite as they arrive, run AI analysis only on HIGH/CRITICAL devices, async progress bar.
- *"Why SQLite and not a proper database?"* → SQLite is appropriate for single-user local tooling. The `db.py` interface is identical to what you'd write for PostgreSQL — swap the connection string and it scales.

**AI/ML:**
- *"Why temperature=0 for the LLM?"* → Deterministic output for JSON parsing reliability. Any temperature > 0 introduces randomness that causes occasional preamble text breaking the JSON parser.
- *"How would you improve AI accuracy?"* → RAG: embed a CVE database with FAISS or Chroma, retrieve top-3 most relevant CVEs per open port, inject as context before generation. Grounds output in real data rather than model weights.
- *"What if the model hallucinates a fix recommendation?"* → The rule-based engine always runs first and generates verified recommendations. AI enriches the explanation but never replaces the deterministic rules. A hallucinated explanation doesn't change the underlying risk score.

**Security:**
- *"How is this different from just running Nmap?"* → Nmap gives raw data. NetWatcher gives scored, prioritized, explained, historically-tracked, actionable intelligence. The gap between data and insight is the entire value.
- *"What would you add to make this production-ready?"* → CVE database integration via NVD API, authenticated scanning (SSH into devices for deeper checks), scheduled scans with diff alerting via email/Slack, network topology graph visualization.

---

## 🗺 Roadmap

- [ ] **CVE Integration** — Pull live CVE data from NVD API, match against detected service versions
- [ ] **Network Topology Map** — Visual graph of all devices and their connections
- [ ] **Scheduled Scans** — Cron-based auto-scan with Slack/email diff alerts
- [ ] **RAG Enhancement** — FAISS vector store of CVE database for more accurate AI context
- [ ] **Authenticated Scanning** — SSH into Linux devices for deeper configuration checks
- [ ] **PDF Export** — One-click PDF version of the HTML report
- [ ] **Comparison View** — Side-by-side diff of two scan sessions

---

## ⚠️ Legal & Ethical Notice

> **For authorized networks only.**
> NetWatcher is built for ethical security auditing of networks you own or have explicit written permission to scan.
> This tool performs passive reconnaissance only — no exploitation, no credential attacks, no data modification.
> Unauthorized network scanning may violate computer crime laws (CFAA in the US, Computer Misuse Act in the UK, IT Act in India).
> The attack simulations in the report are educational descriptions only — no actual attacks are performed.

---

## 👨‍💻 Developer

<div align="center">

**Built by Akshay**

A security-minded developer focused on building tools that bridge the gap between complex technology and everyday usability.

| | |
|---|---|
| 🐙 GitHub | [github.com/Akshay-core](https://github.com/Akshay-core) |
| 💼 LinkedIn | [in/akshay-tb-791bb4372](https://www.linkedin.com/in/akshay-tb-791bb4372) |
| 🌐 Portfolio | [akshay.fruvvi.com](https://akshay.fruvvi.com) |
| 📸 Instagram | [@akshayyyy_2007](https://www.instagram.com/akshayyyy_2007) |

*If you are a recruiter or collaborator — feel free to connect.*

</div>

---

<div align="center">

**NetWatcher v1.0** · MIT License · Offline-first · Zero external services · Free forever

*Scan smart. Fix fast. Stay secure.*

</div>
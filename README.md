# 🛡 NetWatcher — Home Network Vulnerability Scanner

> **Offline-first network security auditing tool** — scans your local network, fingerprints devices, scores vulnerability risk, and generates a professional HTML security dashboard. Built as a lightweight alternative to enterprise scanners for home lab and internship showcase.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Nmap](https://img.shields.io/badge/Engine-Nmap-green)](https://nmap.org)
[![Rich CLI](https://img.shields.io/badge/CLI-Rich%20%2B%20Typer-blueviolet)](https://rich.readthedocs.io)
[![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Akshay--core-black?logo=github)](https://github.com/Akshay-core)
[![Portfolio](https://img.shields.io/badge/Portfolio-akshay.fruvvi.com-blue)](https://akshay.fruvvi.com)

---

## 👨‍💻 Developer

**Akshay**

| Platform | Link |
|----------|------|
| 🐙 GitHub    | [github.com/Akshay-core](https://github.com/Akshay-core) |
| 💼 LinkedIn  | [in/akshay-tb-791bb4372](https://www.linkedin.com/in/akshay-tb-791bb4372) |
| 🌐 Portfolio | [akshay.fruvvi.com](https://akshay.fruvvi.com) |
| 📸 Instagram | [@akshayyyy_2007](https://www.instagram.com/akshayyyy_2007) |

> *"Built with a focus on real-world security thinking, not just code execution."*

---

## ✨ What Makes This Different

Most network scanners just print ports. **NetWatcher** thinks like a security analyst:

| Feature | What it does |
|---------|-------------|
| 🧠 Risk Scoring Engine | Assigns a 0–100 risk score per device based on exposed services |
| 🔍 Device Fingerprinting | Identifies routers, servers, IoT, cameras by MAC OUI + OS hints |
| 📋 Rule-Based Analysis | Every open port gets a human-readable explanation + fix recommendation |
| 🗃 Scan History Timeline | SQLite-backed history — track improvement over time |
| 📊 HTML Security Dashboard | One-command report export with a SaaS-grade dark UI |
| 🛡 Ethical-Only Design | No exploitation, no active attacks — pure passive auditing |

---

## 🖥 CLI Demo

```
$ python netwatcher.py scan --local

╭─────────────────────────────────────────────╮
│  🛡  NetWatcher  v1.0.0                     │
│  Home Network Vulnerability Scanner         │
│  Developer : Akshay · akshay.fruvvi.com     │
╰─────────────────────────────────────────────╯

Target: 192.168.1.0/24
⠸ Discovering hosts…
⠸ Fingerprinting devices…
⠸ Running risk analysis…

┌──────────────────┬──────────────┬─────────┬───────┬────────────┬──────────┐
│ IP               │ Hostname     │ Type    │ Ports │ Risk Score │ Level    │
├──────────────────┼──────────────┼─────────┼───────┼────────────┼──────────┤
│ 192.168.1.1      │ router.home  │ router  │ 4     │ 87/100     │ CRITICAL │
│ 192.168.1.105    │ desktop-pc   │ win-pc  │ 2     │ 45/100     │ MEDIUM   │
│ 192.168.1.112    │ pi.local     │ linux   │ 1     │ 18/100     │ LOW      │
└──────────────────┴──────────────┴─────────┴───────┴────────────┴──────────┘

╭─────────────────────────────────────────────────────╮
│  NETWORK SECURITY SCORE: 50/100  HIGH RISK          │
│  Devices: 3  Critical: 1  High: 0  Medium: 1  Low: 1 │
╰─────────────────────────────────────────────────────╯

✓ Report saved: reports/exports/netwatcher_report_20240115_143022.html
```

---

## 🏗 Architecture

NetWatcher is built as a **layered pipeline** — each layer has exactly one job:

```
CLI Input (Typer + Rich)
        │
        ▼
  scanner.py          ← Nmap wrapper, returns typed Device objects
        │
        ▼
  fingerprint.py      ← MAC OUI + OS enrichment
        │
        ▼
  risk_engine.py      ← Scores 0–100, tags every port with severity
  rules.py            ← Rule definitions (editable data, not logic)
        │
        ▼
  data/db.py          ← SQLite persistence (scan history)
        │
        ▼
  reports/            ← Jinja2 HTML dashboard generation
```

### Why this design?

- **`scanner.py` knows nothing about risk** — pure separation of concerns  
- **`rules.py` is data, not code** — rules are editable without touching logic  
- **`devices.py` typed dataclass** — clean contract between every layer  
- **No global state** — every function takes inputs, returns outputs  

---

## 📁 Folder Structure

```
NetWatcher/
├── netwatcher/
│   ├── cli.py          ← CLI entry (Typer + Rich interface)
│   ├── scanner.py      ← Nmap scanning layer
│   ├── devices.py      ← Typed Device + Port dataclasses
│   └── config.py       ← All settings in one place
│
├── engine/
│   ├── risk_engine.py  ← Core risk scoring algorithm
│   ├── rules.py        ← Vulnerability rule definitions ← EDIT THIS
│   └── fingerprint.py  ← Device type detection
│
├── data/
│   ├── db.py           ← SQLite handler (scan history)
│   └── seed_data.json  ← Mock CVE reference data
│
├── reports/
│   ├── generator.py    ← Jinja2 HTML report builder
│   └── templates/
│       └── report.html ← Dashboard template
│
├── utils/
│   ├── logger.py       ← Centralized logging
│   └── helpers.py      ← Reusable utilities
│
├── tests/
│   └── test_risk_engine.py
│
├── netwatcher.py       ← Main entry point
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Nmap (required)
sudo apt install nmap        # Linux
brew install nmap            # Mac
# Windows: https://nmap.org/download.html
```

### 2. Install

```bash
git clone https://github.com/Akshay-core/netwatcher
cd netwatcher
pip install -r requirements.txt
```

### 3. Run

```bash
# Scan your local network (auto-detects subnet)
python netwatcher.py scan --local

# Scan a specific range
python netwatcher.py scan --target 192.168.1.0/24

# Scan and open HTML report immediately
python netwatcher.py scan --local --open

# View scan history
python netwatcher.py history

# Open last report
python netwatcher.py report

# Verify environment
python netwatcher.py check
```

---

## 🔬 Risk Scoring Model

Each device receives a **0–100 risk score** computed as:

```
base_score  = Σ (severity_weight per open port)   [capped at 70]
modifier    = device_type_offset (router = +15, server = +10, ...)
final_score = min(base_score + modifier, 100)
```

| Severity | Weight | Example Services |
|----------|--------|-----------------|
| CRITICAL |   30   | Telnet (23), SMB (445), Redis (6379), MongoDB (27017) |
| HIGH     |   20   | FTP (21), RDP (3389), VNC (5900), MySQL (3306) |
| MEDIUM   |   10   | SSH (22), SMTP (25), SNMP |
| LOW      |    5   | HTTP (80), HTTPS (443) |

**Score thresholds:**
- `75–100` → 🔴 CRITICAL  
- `50–74`  → 🟡 HIGH  
- `25–49`  → 🔵 MEDIUM  
- `0–24`   → 🟢 LOW  

---

## 🧪 Tests

```bash
python tests/test_risk_engine.py

  ✓  test_telnet_is_critical
  ✓  test_ssh_is_medium_risk
  ✓  test_multiple_critical_ports_max_score
  ✓  test_no_ports_low_risk
  ✓  test_router_modifier_applied
  ✓  test_score_devices_sorted_desc
  ✓  test_network_summary_structure

7/7 tests passed
```

---

## ⚠️ Legal & Ethical Notice

> NetWatcher is built for **ethical use only**.  
> Only scan networks you **own or have explicit permission to scan**.  
> The tool performs **passive auditing only** — no exploitation, no password attacks, no data modification.  
> Unauthorized network scanning may violate computer crime laws in your jurisdiction.

---

## 🗺 Roadmap

- [ ] CVE database integration (NVD API)
- [ ] Network topology map (ASCII + HTML graph)
- [ ] Scheduled scans with diff alerting
- [ ] Smart recommendations engine (prioritized fix list)
- [ ] Export to PDF / CSV

---

## ⚡ Developer Signature

Built by **Akshay** — security-minded developer focused on building tools with real-world utility.

🔗 [GitHub](https://github.com/Akshay-core) · 🌐 [Portfolio](https://akshay.fruvvi.com) · 💼 [LinkedIn](https://www.linkedin.com/in/akshay-tb-791bb4372) · 📸 [Instagram](https://www.instagram.com/akshayyyy_2007)

> *If you are a recruiter or collaborator, feel free to connect.*

---

*NetWatcher v1.0 · MIT License · Offline-first · Zero external services required*

---

## 🤖 AI-Powered Analysis (New)

NetWatcher now uses a **local LLM via Ollama** to generate beginner-friendly, plain-English security explanations — no cloud, no API keys, fully private.

### Why Ollama + Mistral (not fine-tuning, not OpenAI)

| Approach | Cost | Privacy | Accuracy | Setup |
|---|---|---|---|---|
| OpenAI API | 💰 Paid | ❌ Network data leaves device | ★★★★★ | Easy |
| Fine-tune own model | 💰💰 GPU cost | ✅ Local | ★★★★★ | Very hard |
| Ollama + Mistral 7B Q4 | **Free** | ✅ Local | ★★★★☆ | **5 min** |
| Rule-based only | Free | ✅ Local | ★★★☆☆ | Zero |

**Mistral 7B Q4_K_M** is chosen because:
- Fits in **4GB VRAM** (RTX 3050 compatible — 35 GPU layers, ~15 tok/s)
- Instruction-tuned → follows strict JSON schema reliably
- Sliding window attention handles long scan data without truncation
- `temperature=0` → deterministic, parseable output every time

### GPU Compatibility

| GPU | VRAM | Recommended Model | Speed |
|---|---|---|---|
| RTX 3050 | 4 GB | `mistral:7b-instruct-q4_K_M` | ~15 tok/s |
| RTX 3060 | 8 GB | `llama3.1:8b-instruct-q4_K_M` | ~22 tok/s |
| RTX 3080+ | 10 GB+ | `mistral:7b-instruct` (full) | ~40 tok/s |
| CPU only | — | `llama3.2:3b` | ~4 tok/s |

### Setup AI (one time)

```bash
# 1. Install Ollama
bash scripts/setup_ai.sh        # Linux/Mac
# Windows: https://ollama.ai/download

# 2. Pull model (~4GB, one time)
ollama pull mistral:7b-instruct-q4_K_M

# 3. Run — AI activates automatically
python netwatcher.py scan --local
```

**No Ollama? No problem.** NetWatcher falls back to full rule-based analysis automatically. The report still generates perfectly — it just won't have AI plain-English explanations.

### Prompt Engineering Design

The AI prompt is surgically crafted with 5 techniques:

```
1. ROLE ANCHORING   → "You are a senior security analyst writing for non-technical users"
2. STRICT SCHEMA    → JSON output format defined explicitly in system prompt
3. FEW-SHOT EXAMPLE → One example shows exact expected tone and structure
4. NEGATIVE RULES   → "Do NOT add markdown, do NOT explain outside the JSON"
5. CONTEXT LAST     → Scan data injected at END of prompt (recency bias in attention)
```

Temperature is set to `0.0` — not for creativity, but for **reliable JSON parsing**. A temperature of 0.3+ causes the model to occasionally add preamble text that breaks JSON parsing.

---

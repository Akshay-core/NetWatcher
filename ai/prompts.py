"""
ai/prompts.py — Surgical prompt engineering for NetWatcher AI analysis.

WHY THIS ARCHITECTURE:
  Prompts are the "weights" of a prompt-engineered system.
  Keeping them in one file means:
    1. You tune ONE file, not hunt through code
    2. You can version-control prompt changes like code changes
    3. Clear separation: prompts are policy, code is mechanism

MODEL CHOICE REASONING (RTX 3050 4GB+):
  ┌─────────────────┬──────────┬────────────┬─────────────────────┐
  │ Model           │ VRAM     │ Accuracy   │ Speed (3050)        │
  ├─────────────────┼──────────┼────────────┼─────────────────────┤
  │ mistral:7b-q4   │ ~4.1 GB  │ ★★★★☆     │ ~15 tok/s  ← BEST  │
  │ llama3.2:3b     │ ~2.0 GB  │ ★★★☆☆     │ ~35 tok/s  ← FAST  │
  │ phi3:mini       │ ~2.3 GB  │ ★★★★☆     │ ~30 tok/s  ← ALT   │
  │ llama3.1:8b-q4  │ ~5.0 GB  │ ★★★★★     │ ~10 tok/s  (tight) │
  └─────────────────┴──────────┴────────────┴─────────────────────┘
  
  DEFAULT: mistral:7b-instruct-q4_K_M
    - Best accuracy/VRAM balance for security analysis
    - 4-bit quantized = fits 4GB VRAM with headroom
    - Instruction-tuned = follows JSON schema strictly
    - Mistral attention (sliding window) = handles long scan data well

PROMPT DESIGN PRINCIPLES APPLIED:
  1. ROLE ANCHORING    → "You are a senior network security analyst..."
  2. STRICT SCHEMA     → JSON output format defined explicitly
  3. FEW-SHOT EXAMPLES → One example shows exact expected output shape
  4. NEGATIVE RULES    → "Do NOT add markdown, do NOT explain your reasoning"
  5. CONTEXT INJECTION → Real scan data injected at the END (recency bias)
  6. TEMPERATURE=0     → Deterministic output for JSON parsing reliability
  7. STOP TOKENS       → Stop at closing brace to prevent hallucination runoff
"""

# ─── System prompt: role + rules + schema ─────────────────────────────────────
SYSTEM_PROMPT = """You are a senior network security analyst writing reports for NON-TECHNICAL users — homeowners, small business owners, students. Your job is to explain security risks in plain English that a 14-year-old could understand, while keeping the analysis technically accurate.

STRICT OUTPUT RULES:
- Respond ONLY with valid JSON. No markdown. No backticks. No extra text before or after.
- Use the EXACT schema shown below. No extra keys. No missing keys.
- Keep all text short and plain. Max 2 sentences per explanation.
- Use everyday analogies (door locks, car keys, etc.) to explain technical risks.
- Never use jargon without immediately explaining it in parentheses.

OUTPUT SCHEMA (copy this structure exactly):
{
  "network_verdict": "one sentence summary of the overall network health",
  "danger_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "plain_summary": "2-3 sentences explaining the overall situation to a non-technical person",
  "top_threat": "the single most dangerous thing found, in plain English",
  "devices": [
    {
      "ip": "device IP address",
      "nickname": "friendly name like 'Your Router' or 'Windows Laptop'",
      "what_it_is": "one sentence plain description of what this device is",
      "biggest_risk": "the most dangerous issue on this device in plain English",
      "fix_priority": "URGENT|SOON|OPTIONAL",
      "beginner_action": "one clear action step a non-technical person can take right now"
    }
  ],
  "action_plan": [
    {
      "step": 1,
      "priority": "URGENT|SOON|OPTIONAL",
      "what_to_do": "plain English instruction",
      "why_it_matters": "one-sentence analogy explaining the risk",
      "time_estimate": "e.g. 5 minutes, 30 minutes"
    }
  ],
  "good_news": "one positive thing about the network if any, or empty string"
}

FEW-SHOT EXAMPLE (learn the tone from this):
Input device: port 23 telnet open on router
Output snippet:
{
  "nickname": "Your Home Router",
  "biggest_risk": "Telnet is open — this is like leaving your front door unlocked with a sign that says 'password is 1234'",
  "beginner_action": "Log into your router settings (usually 192.168.1.1 in your browser) and turn off Telnet"
}"""


# ─── User prompt builder: inject real scan data ───────────────────────────────
def build_analysis_prompt(scan_data: dict) -> str:
    """
    Build the user-turn prompt by injecting real scan data.
    
    Design decisions:
      - Data comes LAST (LLMs attend more to recent context)
      - We compress the data to reduce token count (fits in 4K context)
      - We repeat the schema reminder at the end (instruction following improves)
    """
    devices_summary = []
    for d in scan_data.get("devices", []):
        ports_str = ", ".join(
            f"{p['number']}/{p['service']}[{p['risk_tag']}]"
            for p in d.get("ports", [])[:8]  # cap at 8 ports to save tokens
        )
        devices_summary.append(
            f"  IP={d['ip']} type={d['device_type']} score={d['risk_score']}/100 "
            f"level={d['risk_level']} ports=[{ports_str}]"
        )

    devices_block = "\n".join(devices_summary) if devices_summary else "  (no devices found)"

    return f"""Analyze this home network scan and generate a beginner-friendly security report.

SCAN DATA:
Target: {scan_data.get('target', 'unknown')}
Total hosts: {scan_data.get('total_devices', 0)}
Overall risk score: {scan_data.get('overall_score', 0)}/100

Devices found:
{devices_block}

Critical findings: {scan_data.get('critical', 0)} CRITICAL, {scan_data.get('high', 0)} HIGH, {scan_data.get('medium', 0)} MEDIUM

Remember: Output ONLY valid JSON matching the schema. No markdown. No explanation text outside the JSON."""


# ─── CVE context prompt (optional enrichment pass) ────────────────────────────
def build_cve_prompt(port: int, service: str, version: str) -> str:
    """
    Secondary prompt: ask the model about a specific service.
    Used only for HIGH/CRITICAL ports to add CVE context without hallucination.
    Kept short to stay within context window.
    """
    return f"""You are a CVE database. For this service, give ONLY a JSON object:
{{
  "known_risk": "one sentence about the main known risk for this service",
  "real_world_example": "one famous attack or incident involving this service (be specific)",
  "patch_command": "exact command or setting to fix this, or empty string if no single command"
}}

Service: port {port} running {service} version "{version or 'unknown'}"
Output ONLY JSON. No markdown. No extra text."""

"""
ai/analyzer.py — Orchestrates AI analysis pipeline for NetWatcher.

PIPELINE:
  scan data → compress → system+user prompt → Ollama → parse JSON
                                                    ↓ on failure
                                             rule-based fallback

FALLBACK STRATEGY (critical for reliability):
  If Ollama is down, model fails, or JSON parse fails → we generate
  a structured fallback report from the existing rule-based engine.
  The report still looks great; it just says "AI analysis unavailable."
  This is production-grade thinking: never crash because of an optional feature.
"""

from typing import Optional

from ai.ollama_client import generate, parse_json_response, is_ollama_running, pick_best_model
from ai.prompts import SYSTEM_PROMPT, build_analysis_prompt
from utils.logger import get_logger

log = get_logger(__name__)


def run_ai_analysis(devices: list, summary: dict, target: str) -> dict:
    """
    Run AI-powered analysis. Returns a structured dict that the
    report template renders. Falls back gracefully if Ollama unavailable.

    Args:
        devices: list of Device objects (already scored)
        summary: network_summary() output dict
        target:  scan target string

    Returns:
        dict with keys: ai_available, model_used, analysis (the JSON from model)
    """
    result = {
        "ai_available": False,
        "model_used":   None,
        "analysis":     _fallback_analysis(devices, summary),
    }

    if not is_ollama_running():
        log.info("Ollama not running — using rule-based analysis")
        return result

    model = pick_best_model()
    if not model:
        log.info("No Ollama model found — using rule-based analysis")
        return result

    # Build scan context for prompt
    scan_data = {
        "target":         target,
        "total_devices":  summary.get("total_devices", 0),
        "overall_score":  summary.get("overall_score", 0),
        "critical":       summary.get("critical", 0),
        "high":           summary.get("high", 0),
        "medium":         summary.get("medium", 0),
        "devices": [
            {
                "ip":          d.ip,
                "device_type": d.device_type,
                "risk_score":  d.risk_score,
                "risk_level":  d.risk_level,
                "ports": [
                    {"number": p.number, "service": p.service, "risk_tag": p.risk_tag}
                    for p in d.ports
                ],
            }
            for d in devices
        ],
    }

    user_prompt = build_analysis_prompt(scan_data)
    raw_text    = generate(SYSTEM_PROMPT, user_prompt, model=model)
    parsed      = parse_json_response(raw_text) if raw_text else None

    if parsed and _validate_schema(parsed):
        log.info(f"AI analysis successful — model={model}")
        result["ai_available"] = True
        result["model_used"]   = model
        result["analysis"]     = parsed
    else:
        log.warning("AI response invalid — using fallback")

    return result


def _validate_schema(data: dict) -> bool:
    """Quick check that the model returned the required keys."""
    required = {"network_verdict", "danger_level", "plain_summary",
                "top_threat", "devices", "action_plan"}
    return required.issubset(data.keys())


def _fallback_analysis(devices: list, summary: dict) -> dict:
    """
    Generate a structured analysis dict using only rule-based data.
    Identical shape to the AI response so the template renders either identically.
    """
    level = summary.get("level", "UNKNOWN")

    verdict_map = {
        "CRITICAL": "Your network has serious security vulnerabilities that need immediate attention.",
        "HIGH":     "Your network has significant risks. Action recommended within the next few days.",
        "MEDIUM":   "Your network has some risks that should be addressed when possible.",
        "LOW":      "Your network looks reasonably secure. Minor improvements possible.",
    }

    device_nicknames = {
        "router":       "Your Router",
        "windows-pc":   "Windows Computer",
        "linux-device": "Linux Device",
        "server":       "Home Server",
        "mobile":       "Mobile Phone",
        "ip-camera":    "Security Camera",
        "printer":      "Printer",
        "iot-device":   "Smart Device",
        "unknown":      "Unknown Device",
    }

    ai_devices = []
    for d in devices[:6]:  # cap at 6 for report readability
        top_issue = d.issues[0]["text"] if d.issues else "No critical issues found."
        top_rec   = d.recommendations[0] if d.recommendations else "Monitor this device."
        ai_devices.append({
            "ip":              d.ip,
            "nickname":        device_nicknames.get(d.device_type, "Network Device"),
            "what_it_is":      f"A {d.device_type} at {d.ip} with {len(d.ports)} open ports.",
            "biggest_risk":    top_issue,
            "fix_priority":    "URGENT" if d.risk_level == "CRITICAL" else
                               "SOON"   if d.risk_level == "HIGH" else "OPTIONAL",
            "beginner_action": top_rec,
        })

    # Build action plan from top recommendations across all devices
    all_recs = []
    seen = set()
    for d in devices:
        for rec in d.recommendations:
            if rec not in seen:
                priority = "URGENT" if d.risk_level in ("CRITICAL", "HIGH") else "SOON"
                all_recs.append({"rec": rec, "priority": priority, "device": d.ip})
                seen.add(rec)

    action_plan = []
    for i, item in enumerate(all_recs[:5], 1):
        action_plan.append({
            "step":          i,
            "priority":      item["priority"],
            "what_to_do":    item["rec"],
            "why_it_matters": "Reduces the attack surface on your network.",
            "time_estimate": "5–15 minutes",
        })

    return {
        "network_verdict": verdict_map.get(level, "Network analysis complete."),
        "danger_level":    level,
        "plain_summary":   verdict_map.get(level, ""),
        "top_threat":      summary.get("top_issues", [{}])[0].get("text", "No critical threats.") if summary.get("top_issues") else "No critical threats found.",
        "devices":         ai_devices,
        "action_plan":     action_plan,
        "good_news":       "Your network scan completed successfully and no unknown devices were detected." if level == "LOW" else "",
    }

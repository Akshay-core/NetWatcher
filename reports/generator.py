"""
generator.py — HTML report generation via Jinja2.
Now accepts ai_result dict and passes it into template context.
"""

from datetime import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from netwatcher.config import REPORTS_DIR, TEMPLATES_DIR
from utils.logger import get_logger

log = get_logger(__name__)


def generate_html_report(
    devices,
    summary: dict,
    target:  str,
    scan_id: int,
    ai_result: dict = None,
) -> Path:
    env      = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = REPORTS_DIR / f"netwatcher_report_{ts}.html"

    # Default ai_result if not provided (Ollama offline path)
    if ai_result is None:
        ai_result = {"ai_available": False, "model_used": None,
                     "analysis": {"plain_summary": "", "action_plan": [],
                                  "devices": [], "good_news": ""}}

    context = {
        "target":        target,
        "scan_id":       scan_id,
        "summary":       summary,
        "devices":       [d.to_dict() for d in devices],
        "ai":            ai_result,
        "generated":     datetime.now().strftime("%B %d, %Y at %H:%M"),
        "dev_name":      "Akshay",
        "dev_github":    "https://github.com/Akshay-core",
        "dev_portfolio": "https://akshay.fruvvi.com",
        "dev_linkedin":  "https://www.linkedin.com/in/akshay-tb-791bb4372",
    }

    out_path.write_text(template.render(**context), encoding="utf-8")
    log.info(f"Report → {out_path}")
    return out_path

"""
ai/ollama_client.py — Clean Ollama API wrapper for NetWatcher.

WHY OLLAMA vs alternatives:
  - Ollama: zero-config local inference, one install, model library built-in
  - llama.cpp direct: faster but complex setup, no model management
  - Hugging Face transformers: huge deps (~5GB), slow cold start
  - OpenAI API: costs money, requires internet, privacy concern for network data

OLLAMA API:
  POST http://localhost:11434/api/generate
  POST http://localhost:11434/api/chat  (preferred for instruct models)

RTX 3050 OPTIMIZATION:
  - num_gpu=35 layers on GPU (leaves 1-2 layers on CPU to avoid OOM)
  - num_ctx=4096 (full context for scan data)
  - temperature=0 for deterministic JSON output
  - repeat_penalty=1.1 reduces repetition loops
  - stop=["}\\n}"] to halt at JSON close brace
"""

import json
import re
import time
from typing import Optional

import urllib.request
import urllib.error

from utils.logger import get_logger

log = get_logger(__name__)

OLLAMA_BASE    = "http://localhost:11434"
DEFAULT_MODEL  = "mistral:7b-instruct-q4_K_M"  # Best for RTX 3050 4GB
FALLBACK_MODEL = "llama3.2:3b"                   # If 7B doesn't fit


# ─── Public API ───────────────────────────────────────────────────────────────

def is_ollama_running() -> bool:
    """Check if Ollama server is up."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def get_available_models() -> list:
    """Return list of model names installed in Ollama."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def pick_best_model() -> Optional[str]:
    """
    Auto-select the best available model for security analysis.
    Priority: mistral 7b > phi3 > llama3.2:3b > any available
    """
    available = get_available_models()
    if not available:
        return None

    # Priority order for security analysis quality vs VRAM
    preference = [
        "mistral:7b-instruct-q4_K_M",
        "mistral:7b-instruct-q4_0",
        "mistral:7b-instruct",
        "mistral",
        "phi3:mini-4k-instruct",
        "phi3:mini",
        "phi3",
        "llama3.2:3b-instruct-q4_K_M",
        "llama3.2:3b",
        "llama3.1:8b-instruct-q4_K_M",  # only if user has > 5GB VRAM
    ]

    # Exact match first
    for preferred in preference:
        if preferred in available:
            return preferred

    # Partial match (e.g. user has "mistral:latest")
    for preferred in ["mistral", "phi3", "llama3.2", "llama3"]:
        for av in available:
            if av.startswith(preferred):
                return av

    # Last resort: whatever is installed
    return available[0]


def generate(
    system_prompt: str,
    user_prompt:   str,
    model:         Optional[str] = None,
    temperature:   float = 0.0,
    max_tokens:    int   = 1500,
) -> Optional[str]:
    """
    Send a chat completion request to Ollama.
    Returns the raw text response or None on failure.
    
    Uses /api/chat (instruct format) instead of /api/generate
    because instruct models follow system prompts much better.
    """
    if not is_ollama_running():
        log.warning("Ollama is not running. AI analysis skipped.")
        return None

    if model is None:
        model = pick_best_model()
        if model is None:
            log.warning("No models installed in Ollama. Run: ollama pull mistral:7b-instruct-q4_K_M")
            return None

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature":    temperature,
            "num_predict":    max_tokens,
            "num_gpu":        35,       # keeps most layers on GPU (RTX 3050 safe)
            "num_ctx":        4096,
            "repeat_penalty": 1.1,
            "stop": ["\n}\n}"],        # stop after JSON closes
        },
    }

    log.info(f"AI request → model={model}")
    t0 = time.time()

    try:
        data    = json.dumps(payload).encode("utf-8")
        req     = urllib.request.Request(
            f"{OLLAMA_BASE}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read())
            elapsed = time.time() - t0
            text = result.get("message", {}).get("content", "")
            log.info(f"AI response received in {elapsed:.1f}s  tokens≈{len(text.split())}")
            return text
    except urllib.error.URLError as e:
        log.error(f"Ollama request failed: {e}")
        return None
    except Exception as e:
        log.error(f"AI generation error: {e}")
        return None


def parse_json_response(text: str) -> Optional[dict]:
    """
    Robustly extract JSON from model output.
    Models sometimes wrap JSON in markdown fences or add preamble —
    this strips all of that before parsing.
    """
    if not text:
        return None

    # Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find outermost { } block
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    # Last resort: try to fix common model mistakes (trailing commas)
    try:
        cleaned = re.sub(r",\s*([}\]])", r"\1", text[start:end + 1])
        return json.loads(cleaned)
    except Exception:
        log.warning("Could not parse AI JSON response. Falling back to rule-based report.")
        return None

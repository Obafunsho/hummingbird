"""
hummingbird/logic/audit_logger.py
Append-only audit log. Never delete rows.
Every recommendation logged from day one — regulatory requirement.

Fields per Analyst Brief v2.1 section 7.1:
  timestamp_iso, hbid, session_id, age_band, fit_result,
  symptoms_json, examination_findings_json, performance_status,
  modifiers_json, free_text_char_count, nhs_number_provided,
  layer_triggered, rule_name, stt_flag, stt_eligible,
  stt_ineligible_reason, prompt_version, model_version,
  output_tier, escalation_score, escalation_tier,
  confidence, api_response_id
"""

import csv
import json
import os
import random
import string
from datetime import datetime, timezone
from pathlib import Path

AUDIT_DIR = Path(__file__).parent.parent / "audit"
AUDIT_FILE = AUDIT_DIR / "audit_log.csv"

FIELDNAMES = [
    "timestamp_iso",
    "hbid",
    "session_id",
    "age_band",
    "fit_result",
    "symptoms_json",
    "examination_findings_json",
    "performance_status",
    "modifiers_json",
    "free_text_char_count",
    "nhs_number_provided",
    "layer_triggered",
    "rule_name",
    "stt_flag",
    "stt_eligible",
    "stt_ineligible_reason",
    "prompt_version",
    "model_version",
    "output_tier",
    "escalation_score",
    "escalation_tier",
    "confidence",
    "api_response_id",
]


def generate_session_id() -> str:
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"SES-{suffix}"


def generate_hbid() -> str:
    """
    Format: HB-YYYYMMDD-XXXXXX (6-char uppercase alphanumeric, no ambiguous chars)
    Example: HB-20260312-X7KP2M
    """
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I
    suffix = "".join(random.choices(chars, k=6))
    return f"HB-{today}-{suffix}"


def _ensure_audit_file():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    if not AUDIT_FILE.exists():
        with open(AUDIT_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def log_recommendation(
    hbid: str,
    session_id: str,
    age_band: str,
    fit_result: str,
    symptoms: list,
    examination_findings: list,
    performance_status: str,
    modifiers: list,
    free_text: str,
    nhs_number: str,
    result: dict,
    escalation_score: int,
    escalation_tier: str,
) -> None:
    _ensure_audit_file()

    row = {
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
        "hbid": hbid,
        "session_id": session_id,
        "age_band": age_band,
        "fit_result": fit_result,
        "symptoms_json": json.dumps(sorted(symptoms)),
        "examination_findings_json": json.dumps(sorted(examination_findings)),
        "performance_status": performance_status,
        "modifiers_json": json.dumps(sorted(modifiers)),
        "free_text_char_count": len(free_text.strip()) if free_text else 0,
        "nhs_number_provided": "yes" if nhs_number and nhs_number.strip() else "no",
        "layer_triggered": result.get("layer", ""),
        "rule_name": result.get("rule_name", ""),
        "stt_flag": "yes" if result.get("tier") == "2WW_URGENT_STT" else "no",
        "stt_eligible": str(result.get("stt_eligible", "")),
        "stt_ineligible_reason": result.get("stt_ineligible_reason", "") or "",
        "prompt_version": result.get("prompt_version", ""),
        "model_version": result.get("model_version", ""),
        "output_tier": result.get("tier", ""),
        "escalation_score": escalation_score,
        "escalation_tier": escalation_tier,
        "confidence": result.get("confidence", ""),
        "api_response_id": result.get("api_response_id", "") or "",
    }

    with open(AUDIT_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)

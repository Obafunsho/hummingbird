"""
hummingbird/logic/claude_layer.py
Layer 2 — Claude API call and response parsing.
Input serialisation per Analyst Brief v3.0 spec.
Model pinned: claude-sonnet-4-6

v3.0 changes:
- Output validated against five permitted tiers only
- Invalid tier returns FALLBACK_ALERT result (never displays bad data)
- Prompt version bumped to v3.0
- SAFETY_NET replaces SAFETY_NET_ACTIVE / SAFETY_NET_PASSIVE / REASSURE_DISCHARGE
- INVESTIGATE_FIRST replaces the old INVESTIGATE_FIRST label
"""

import json
import os
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Permitted output tiers — any other value triggers fallback (v3.0)
PERMITTED_TIERS = {
    "2WW_URGENT_STT",
    "2WW_URGENT",
    "ROUTINE_REFERRAL",
    "INVESTIGATE_FIRST",
    "SAFETY_NET",
}

TIER_LABELS = {
    "2WW_URGENT_STT":    "2WW Urgent — Straight to Test",
    "2WW_URGENT":        "2WW Urgent Referral",
    "ROUTINE_REFERRAL":  "Routine Referral",
    "INVESTIGATE_FIRST": "Order FIT Before Referral",
    "SAFETY_NET":        "Safety Net",
}


def get_active_prompt_version(cancer_site: str = "lower_gi") -> str:
    registry_path = PROMPTS_DIR / "prompt_registry.json"
    with open(registry_path) as f:
        registry = json.load(f)
    return registry["active_prompts"][cancer_site]


def load_system_prompt(cancer_site: str, version: str) -> str:
    prompt_path = PROMPTS_DIR / cancer_site / f"system_prompt_{version}.txt"
    with open(prompt_path) as f:
        return f.read()


def build_user_message(
    age_band: str,
    fit_result: str,
    symptoms: list[str],
    examination_findings: list[str],
    performance_status: str,
    modifiers: list[str],
    free_text: str,
) -> str:
    """
    Serialise all inputs to structured JSON string per v3.0 spec.
    """
    payload = {
        "age_band": age_band,
        "fit_result": fit_result,
        "symptoms": symptoms,
        "examination_findings": examination_findings,
        "performance_status": performance_status,
        "modifiers": {
            "colonoscopy_clear_3yr": "colonoscopy_clear" in modifiers,
            "ct_clear_3yr": "ct_clear" in modifiers,
            "mcd_ctdna_positive": "mcd_ctdna" in modifiers,
            "free_text": free_text.strip() if free_text else "",
        }
    }
    return json.dumps(payload)


def _fallback_result(reason: str, prompt_version: str) -> dict:
    """
    Return a safe fallback result when model output is invalid.
    Displayed as an alert in the UI — never silently shows bad data.
    """
    return {
        "tier": "FALLBACK_ALERT",
        "tier_label": "Clinical Review Required",
        "stt_eligible": None,
        "stt_driver": None,
        "rationale": (
            "The AI layer returned an unexpected response and could not be validated. "
            "Please review this case manually and do not act on an automated recommendation."
        ),
        "safety_netting": None,
        "inputs_driving_decision": [],
        "deflecting_factors": [],
        "escalating_factors": [],
        "confidence": "uncertain",
        "api_response_id": None,
        "prompt_version": prompt_version,
        "model_version": MODEL,
        "layer": "2",
        "fallback_reason": reason,
    }


def call_claude(
    age_band: str,
    fit_result: str,
    symptoms: list[str],
    examination_findings: list[str],
    performance_status: str,
    modifiers: list[str],
    free_text: str,
    cancer_site: str = "lower_gi",
    max_retries: int = 3,
) -> dict:
    """
    Call Claude API with clinical inputs.
    Retries on 529 overloaded errors with exponential backoff.
    Validates output against permitted tier list (v3.0).
    Returns fallback result if tier is invalid.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt_version = get_active_prompt_version(cancer_site)
    system_prompt = load_system_prompt(cancer_site, prompt_version)
    user_message = build_user_message(
        age_band=age_band,
        fit_result=fit_result,
        symptoms=symptoms,
        examination_findings=examination_findings,
        performance_status=performance_status,
        modifiers=modifiers,
        free_text=free_text,
    )
    pv_tag = f"{cancer_site}_{prompt_version}"

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            api_response_id = response.id
            raw_text = response.content[0].text.strip()

            # Strip accidental markdown fences
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            result = json.loads(raw_text)

            # ── Tier validation (v3.0) ────────────────────────────────────────
            tier = result.get("tier", "")
            if tier not in PERMITTED_TIERS:
                fallback = _fallback_result(
                    reason=f"Model returned invalid tier: '{tier}'",
                    prompt_version=pv_tag,
                )
                fallback["api_response_id"] = api_response_id
                return fallback

            # Ensure tier_label matches canonical label
            result["tier_label"] = TIER_LABELS[tier]
            result["api_response_id"] = api_response_id
            result["prompt_version"] = pv_tag
            result["model_version"] = MODEL
            result["layer"] = "2"

            return result

        except Exception as e:
            last_error = e
            error_str = str(e)
            if "529" in error_str or "overloaded" in error_str.lower():
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            raise

    raise last_error


def build_hard_rule_response(
    rule_name: str,
    rule_description: str,
    tier: str,
    stt_eligible: bool,
    stt_driver: str,
    stt_ineligible_reason: str,
    drivers: list[str],
) -> dict:
    """
    Build a standardised response dict for Layer 1 hard rule triggers.
    Mirrors Claude response structure so colorectal.py handles both uniformly.
    Includes WEIGHT_LOSS_CUP tier for Rule 1.4.
    """
    if tier == "2WW_URGENT_STT":
        tier_label = "2WW Urgent — Straight to Test"
        rationale = (
            f"This presentation meets a Straight to Test criterion: {rule_description}. "
            f"STT driver: {stt_driver}. PS 0–1 and confirmed age <80 — patient is STT eligible. "
            "Contact receiving team directly. Same-day notification."
        )
        safety_netting = (
            "Direct access colonoscopy or CT colonography. "
            "Contact receiving team directly — do not wait for standard 2WW slot."
        )

    elif tier == "WEIGHT_LOSS_CUP":
        tier_label = "Clinical Judgement Required"
        rationale = (
            "Unexplained weight loss ≥3kg is the sole presenting feature with no colorectal symptoms "
            "and FIT is negative or not yet performed. This presentation does not meet colorectal 2WW criteria. "
            "Clinical assessment is required to determine the appropriate pathway."
        )
        safety_netting = (
            "If cancer concern persists on clinical assessment, refer to the Cancer of Unknown Primary (CUP) pathway. "
            "If no persistent cancer concern, investigate in primary care with FIT, blood tests, and clinical review."
        )

    else:
        tier_label = "2WW Urgent Referral"
        rationale = (
            f"This presentation meets a mandatory urgent referral criterion: {rule_description}. "
            "NICE NG12 guidance requires immediate referral via the Urgent Suspected Cancer (2WW) pathway. "
            "This decision was made by a deterministic clinical rule and does not require AI reasoning."
        )
        safety_netting = None

    return {
        "tier": tier,
        "tier_label": tier_label,
        "stt_eligible": stt_eligible if tier == "2WW_URGENT_STT" else None,
        "stt_driver": stt_driver if stt_driver else None,
        "stt_ineligible_reason": stt_ineligible_reason if stt_ineligible_reason else None,
        "rationale": rationale,
        "safety_netting": safety_netting,
        "inputs_driving_decision": drivers,
        "deflecting_factors": [],
        "escalating_factors": drivers,
        "confidence": "high",
        "api_response_id": None,
        "prompt_version": "layer_1_hard_rule",
        "model_version": "none",
        "layer": "1",
        "rule_name": rule_name,
    }

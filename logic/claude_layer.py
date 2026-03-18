"""
hummingbird/logic/claude_layer.py
Layer 2 — Claude API call and response parsing.
Input serialisation per Analyst Brief v2.1 spec.
Model pinned: claude-sonnet-4-6
"""

import json
import os
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


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
    modifiers: dict,
    free_text: str,
) -> str:
    """
    Serialise all inputs to structured JSON string per v2.1 spec.
    This format must be consistent across all calls.
    Changes to this format require the same change protocol as prompt changes.
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

    Returns dict with keys:
      tier, tier_label, stt_eligible, stt_driver,
      rationale, safety_netting, inputs_driving_decision,
      deflecting_factors, escalating_factors, confidence,
      api_response_id, prompt_version, model_version, layer
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
            result["api_response_id"] = api_response_id
            result["prompt_version"] = f"{cancer_site}_{prompt_version}"
            result["model_version"] = MODEL
            result["layer"] = "2"

            return result

        except Exception as e:
            last_error = e
            error_str = str(e)
            if "529" in error_str or "overloaded" in error_str.lower():
                wait = 2 ** attempt  # 1s, 2s, 4s
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
    Mirrors Claude response structure so app.py handles both uniformly.
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

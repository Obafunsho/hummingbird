"""
hummingbird/logic/claude_layer_upper_gi.py
Layer 2 — Claude API call for Upper GI module.
Per Analyst Brief v1.0. Model pinned: claude-sonnet-4-6.

Key difference from colorectal: no FIT field.
Additional fields: hpylori_status, barretts_known.
"""

import json
import os
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def get_active_prompt_version_upper_gi() -> str:
    registry_path = PROMPTS_DIR / "prompt_registry.json"
    with open(registry_path) as f:
        registry = json.load(f)
    return registry["active_prompts"].get("upper_gi", "v1.0")


def load_system_prompt_upper_gi(version: str) -> str:
    prompt_path = PROMPTS_DIR / "upper_gi" / f"system_prompt_{version}.txt"
    with open(prompt_path) as f:
        return f.read()


def build_upper_gi_user_message(
    age_band: str,
    symptoms: list[str],
    examination_findings: list[str],
    performance_status: str,
    hpylori_status: str,
    modifiers: list[str],
    free_text: str,
) -> str:
    payload = {
        "age_band": age_band,
        "symptoms": symptoms,
        "examination_findings": examination_findings,
        "performance_status": performance_status,
        "hpylori_status": hpylori_status,
        "modifiers": {
            "ogd_clear_3yr": "ogd_clear" in modifiers,
            "ct_clear_3yr": "ct_clear" in modifiers,
            "barretts_known": "barretts" in modifiers,
            "on_long_term_ppis": "ppis" in modifiers,
            "free_text": free_text.strip() if free_text else "",
        }
    }
    return json.dumps(payload)


def build_hard_rule_response_upper_gi(
    rule_name: str,
    rule_description: str,
    tier: str,
    stt_eligible: bool,
    stt_driver: str,
    stt_ineligible_reason: str,
    drivers: list[str],
) -> dict:
    tier_labels = {
        "2WW_URGENT_STT": "2WW Urgent — Straight to Test",
        "2WW_URGENT":     "2WW Urgent Referral",
    }
    return {
        "tier": tier,
        "tier_label": tier_labels.get(tier, tier),
        "stt_eligible": stt_eligible,
        "stt_driver": stt_driver,
        "stt_ineligible_reason": stt_ineligible_reason,
        "rationale": (
            f"Hard rule triggered: {rule_description}. "
            f"This is a deterministic NICE NG12 rule — no AI reasoning required."
        ),
        "safety_netting": None,
        "inputs_driving_decision": drivers,
        "deflecting_factors": [],
        "escalating_factors": drivers,
        "confidence": "high",
        "layer": "1",
        "prompt_version": "hard_rule",
        "model_version": "layer_1_deterministic",
        "module": "upper_gi",
    }


def call_claude_upper_gi(
    age_band: str,
    symptoms: list[str],
    examination_findings: list[str],
    performance_status: str,
    hpylori_status: str,
    modifiers: list[str],
    free_text: str,
    max_retries: int = 3,
) -> dict:

    version = get_active_prompt_version_upper_gi()
    system_prompt = load_system_prompt_upper_gi(version)
    user_message = build_upper_gi_user_message(
        age_band, symptoms, examination_findings,
        performance_status, hpylori_status, modifiers, free_text
    )

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw.strip())
            result["layer"] = "2"
            result["prompt_version"] = version
            result["model_version"] = MODEL
            result["module"] = "upper_gi"
            return result
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
        except Exception:
            raise

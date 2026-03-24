"""
hummingbird/logic/hard_rules_upper_gi.py
Layer 1 — Deterministic hard rules for Upper GI (Oesophagogastric) module.
No AI. No exceptions. Per Analyst Brief v1.0.

Rule evaluation order:
  1. Examination findings (upper abdominal mass, cervical lymphadenopathy) — direct 2WW
  2. Dysphagia (any age) — direct 2WW
  3. Haematemesis (any age) — direct 2WW
  4. STT sub-rule — dysphagia + weight loss + age ≥55 + PS 0-1
  5. Weight loss ≥3kg + age ≥55 + any upper GI symptom
  6. No hard rule → return triggered=False → Layer 2

IMPORTANT: FIT has no role in the upper GI pathway.
"""

from dataclasses import dataclass, field


@dataclass
class HardRuleResult:
    triggered: bool
    rule_name: str = ""
    rule_description: str = ""
    tier: str = ""
    stt_eligible: bool = False
    stt_driver: str = ""
    stt_ineligible_reason: str = ""
    drivers: list = field(default_factory=list)


def _age_gte_55(age_band: str) -> bool:
    return age_band == "55plus"


def _stt_eligible(age_band: str, performance_status: str) -> tuple[bool, str]:
    """STT requires PS 0-1 AND age ≥55 confirmed under 80 (55plus band assumed <80 unless stated)."""
    if performance_status == "limited":
        return False, (
            "STT clinically indicated but PS 2–4 — STT pathway not appropriate. "
            "Refer via standard 2WW urgent pathway."
        )
    return True, ""


def check_hard_rules_upper_gi(
    age_band: str,               # "u55" | "55plus"
    performance_status: str,     # "fit" | "limited"
    symptoms: list[str],
    examination_findings: list[str],
    hpylori_status: str,         # "notdone"|"negative"|"treated"|"untreated" — not a Layer 1 trigger
    modifiers: list[str],
) -> HardRuleResult:

    s = set(symptoms)
    e = set(examination_findings)

    # ── 1. Examination findings ───────────────────────────────────────────────
    if "upper_abdominal_mass" in e:
        return HardRuleResult(
            triggered=True,
            rule_name="UPPER_ABDOMINAL_MASS",
            rule_description="Unexplained upper abdominal mass (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Upper abdominal mass (unexplained)"],
        )

    if "cervical_lymphadenopathy" in e:
        return HardRuleResult(
            triggered=True,
            rule_name="CERVICAL_LYMPHADENOPATHY",
            rule_description="Unexplained cervical lymphadenopathy (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Cervical lymphadenopathy (unexplained)"],
        )

    # ── 2. Dysphagia — any age ────────────────────────────────────────────────
    if "dysphagia" in s:
        # STT sub-rule: dysphagia + weight loss + age ≥55 + PS 0-1
        if "weight_loss" in s and _age_gte_55(age_band):
            eligible, reason = _stt_eligible(age_band, performance_status)
            if eligible:
                return HardRuleResult(
                    triggered=True,
                    rule_name="DYSPHAGIA_WEIGHT_LOSS_STT",
                    rule_description="Dysphagia + weight loss ≥3kg + age ≥55 — highest risk combination",
                    tier="2WW_URGENT_STT",
                    stt_eligible=True,
                    stt_driver="Dysphagia + weight loss ≥3kg",
                    drivers=["Dysphagia", "Unexplained weight loss ≥3kg", "Age ≥55", "PS 0–1"],
                )
            else:
                return HardRuleResult(
                    triggered=True,
                    rule_name="DYSPHAGIA_WEIGHT_LOSS_2WW",
                    rule_description="Dysphagia + weight loss ≥3kg — STT indicated but patient ineligible",
                    tier="2WW_URGENT",
                    stt_eligible=False,
                    stt_driver="Dysphagia + weight loss ≥3kg",
                    stt_ineligible_reason=reason,
                    drivers=["Dysphagia", "Unexplained weight loss ≥3kg"],
                )
        # Standard dysphagia 2WW
        return HardRuleResult(
            triggered=True,
            rule_name="DYSPHAGIA",
            rule_description="Dysphagia at any age (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Dysphagia"],
        )

    # ── 3. Haematemesis — any age ─────────────────────────────────────────────
    if "haematemesis" in s:
        return HardRuleResult(
            triggered=True,
            rule_name="HAEMATEMESIS",
            rule_description="Haematemesis at any age (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Haematemesis"],
        )

    # ── 4. Weight loss + age ≥55 + any upper GI symptom ──────────────────────
    upper_gi_symptoms = {"dyspepsia", "upper_abdominal_pain", "nausea_vomiting"}
    if "weight_loss" in s and _age_gte_55(age_band) and (s & upper_gi_symptoms):
        co_present = [
            {"dyspepsia": "Dyspepsia / reflux",
             "upper_abdominal_pain": "Upper abdominal pain",
             "nausea_vomiting": "Nausea / vomiting"}[k]
            for k in (s & upper_gi_symptoms)
        ]
        return HardRuleResult(
            triggered=True,
            rule_name="WEIGHT_LOSS_AGE55_UPPER_GI",
            rule_description="Weight loss ≥3kg + age ≥55 + upper GI symptom (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Unexplained weight loss ≥3kg", "Age ≥55"] + co_present,
        )

    return HardRuleResult(triggered=False)

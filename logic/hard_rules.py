"""
hummingbird/logic/hard_rules.py
Layer 1 — Deterministic hard rules. No AI. No exceptions.
Implements NICE NG12 + STT sub-rules per Analyst Brief v3.0.

Rule evaluation order:
  1. Examination findings (mass/ulceration) — direct 2WW, no FIT required
  2. STT sub-rules (FIT ≥100, MCD/ctDNA, 3+ flag symptoms)
  3. Standard NICE NG12 hard rules
  4. Rule 1.4 — Weight loss sole feature, no colorectal symptoms, FIT negative/not done
     → CUP pathway or primary care investigation (does NOT proceed to Layer 2)
  5. No hard rule → return triggered=False → Layer 2

IMPORTANT: This module never touches the Claude API.
All logic is transparent, auditable Python.
"""

from dataclasses import dataclass, field


@dataclass
class HardRuleResult:
    triggered: bool
    rule_name: str = ""
    rule_description: str = ""
    tier: str = ""                   # 2WW_URGENT, 2WW_URGENT_STT, or WEIGHT_LOSS_CUP
    stt_eligible: bool = False
    stt_driver: str = ""
    stt_ineligible_reason: str = ""  # logged if STT indicated but patient ineligible
    drivers: list = field(default_factory=list)


# ── Age band helpers ──────────────────────────────────────────────────────────

def _age_gte_60(age_band: str) -> bool:
    return age_band in ("60-69", "70+")

def _age_is_70_plus(age_band: str) -> bool:
    return age_band == "70+"

def _age_lt_80_confirmed(age_band: str) -> bool:
    """
    STT requires confirmed age <80.
    70+ band cannot confirm age <80 — treated as ineligible by default.
    """
    return age_band in ("u60", "60-69")


# ── STT eligibility gate ──────────────────────────────────────────────────────

def _stt_eligible(age_band: str, performance_status: str) -> tuple[bool, str]:
    """
    Returns (eligible: bool, ineligible_reason: str).
    STT requires PS 0-1 AND confirmed age <80.
    70+ band is ineligible by default — exact age unknown.
    """
    if _age_is_70_plus(age_band):
        return False, (
            "STT clinically indicated but patient is in 70+ age band. "
            "Exact age unknown — STT requires confirmed age <80. "
            "Refer via standard 2WW and consider direct contact with receiving team to expedite."
        )
    if performance_status == "limited":
        return False, (
            "STT clinically indicated but PS 2–4 — STT pathway not appropriate. "
            "Refer via standard 2WW urgent pathway."
        )
    return True, ""


# ── Main entry point ──────────────────────────────────────────────────────────

def check_hard_rules(
    age_band: str,
    performance_status: str,        # "fit" or "limited"
    symptoms: list[str],            # keys from SYMPTOMS constant
    examination_findings: list[str],# keys from EXAMINATION_FINDINGS constant
    fit_result: str,                # "notdone" | "negative" | "positive" | "high"
    modifiers: list[str],           # keys from MODIFIERS constant
) -> HardRuleResult:
    """
    Evaluate all Layer 1 hard rules in priority order.
    Returns HardRuleResult with triggered=False if no rule fires.
    """

    s = set(symptoms)
    e = set(examination_findings)
    m = set(modifiers)

    # ── Rule 1.1: Examination findings — direct 2WW, no FIT required ──────────

    if "anal_mass" in e:
        return HardRuleResult(
            triggered=True,
            rule_name="ANAL_MASS",
            rule_description="Unexplained anal mass or ulceration",
            tier="2WW_URGENT",
            drivers=["Anal mass or ulceration"],
        )

    if "rectal_mass" in e:
        return HardRuleResult(
            triggered=True,
            rule_name="RECTAL_MASS",
            rule_description="Rectal mass on examination",
            tier="2WW_URGENT",
            drivers=["Rectal mass on examination"],
        )

    if "abdominal_mass" in e:
        return HardRuleResult(
            triggered=True,
            rule_name="ABDOMINAL_MASS",
            rule_description="Unexplained abdominal mass",
            tier="2WW_URGENT",
            drivers=["Unexplained abdominal mass"],
        )

    # ── Rule 1.2: STT sub-rules ───────────────────────────────────────────────

    # FIT ≥100 µg/g
    if fit_result == "high":
        eligible, reason = _stt_eligible(age_band, performance_status)
        if eligible:
            return HardRuleResult(
                triggered=True,
                rule_name="FIT_HIGH_STT",
                rule_description="FIT ≥100 µg/g — cancer detection rate 20–30%",
                tier="2WW_URGENT_STT",
                stt_eligible=True,
                stt_driver="FIT ≥100 µg/g",
                drivers=["FIT ≥100 µg/g", "PS 0–1", "Age <80"],
            )
        else:
            return HardRuleResult(
                triggered=True,
                rule_name="FIT_HIGH_2WW",
                rule_description="FIT ≥100 µg/g — STT indicated but patient ineligible",
                tier="2WW_URGENT",
                stt_eligible=False,
                stt_driver="FIT ≥100 µg/g",
                stt_ineligible_reason=reason,
                drivers=["FIT ≥100 µg/g"],
            )

    # Positive MCD/ctDNA
    if "mcd_ctdna" in m:
        eligible, reason = _stt_eligible(age_band, performance_status)
        if eligible:
            return HardRuleResult(
                triggered=True,
                rule_name="MCD_CTDNA_STT",
                rule_description="Positive MCD/ctDNA test in a symptomatic patient",
                tier="2WW_URGENT_STT",
                stt_eligible=True,
                stt_driver="Positive MCD/ctDNA",
                drivers=["Positive MCD/ctDNA", "PS 0–1", "Age <80"],
            )
        else:
            return HardRuleResult(
                triggered=True,
                rule_name="MCD_CTDNA_2WW",
                rule_description="Positive MCD/ctDNA — STT indicated but patient ineligible",
                tier="2WW_URGENT",
                stt_eligible=False,
                stt_driver="Positive MCD/ctDNA",
                stt_ineligible_reason=reason,
                drivers=["Positive MCD/ctDNA"],
            )

    # 3+ hard flag symptoms co-present
    hard_flag_symptoms = {"rectal_bleeding", "change_in_bowel_habit", "weight_loss", "iron_deficiency_anaemia"}
    flags_present = s & hard_flag_symptoms
    if len(flags_present) >= 3:
        flag_labels = {
            "rectal_bleeding": "Rectal bleeding",
            "change_in_bowel_habit": "Change in bowel habit",
            "weight_loss": "Unexplained weight loss ≥3kg",
            "iron_deficiency_anaemia": "Iron deficiency anaemia",
        }
        drivers = [flag_labels[f] for f in flags_present]
        eligible, reason = _stt_eligible(age_band, performance_status)
        if eligible:
            return HardRuleResult(
                triggered=True,
                rule_name="MULTI_FLAG_STT",
                rule_description=f"{len(flags_present)} hard-flag symptoms co-present",
                tier="2WW_URGENT_STT",
                stt_eligible=True,
                stt_driver=f"{len(flags_present)} hard-flag symptoms",
                drivers=drivers + ["PS 0–1", "Age <80"],
            )
        else:
            return HardRuleResult(
                triggered=True,
                rule_name="MULTI_FLAG_2WW",
                rule_description=f"{len(flags_present)} hard-flag symptoms co-present — STT indicated but ineligible",
                tier="2WW_URGENT",
                stt_eligible=False,
                stt_driver=f"{len(flags_present)} hard-flag symptoms",
                stt_ineligible_reason=reason,
                drivers=drivers,
            )

    # ── Rule 1.3: Standard NICE NG12 hard rules ───────────────────────────────

    # FIT positive 10–99 µg/g
    if fit_result == "positive":
        return HardRuleResult(
            triggered=True,
            rule_name="FIT_POSITIVE",
            rule_description="FIT positive 10–99 µg/g (NICE NG12 1.3.2)",
            tier="2WW_URGENT",
            drivers=["FIT positive 10–99 µg/g"],
        )

    # Iron deficiency anaemia — standalone trigger, no age dependency
    if "iron_deficiency_anaemia" in s:
        return HardRuleResult(
            triggered=True,
            rule_name="IDA_STANDALONE",
            rule_description="Iron deficiency anaemia confirmed (NICE NG12)",
            tier="2WW_URGENT",
            drivers=["Iron deficiency anaemia"],
        )

    # Rectal bleeding + age ≥60
    if "rectal_bleeding" in s and _age_gte_60(age_band):
        return HardRuleResult(
            triggered=True,
            rule_name="RECTAL_BLEEDING_AGE_60_PLUS",
            rule_description="Rectal bleeding in patient aged ≥60 (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Rectal bleeding", "Age ≥60"],
        )

    # Rectal bleeding + change in bowel habit — any age
    if "rectal_bleeding" in s and "change_in_bowel_habit" in s:
        return HardRuleResult(
            triggered=True,
            rule_name="BLEEDING_PLUS_BOWEL",
            rule_description="Rectal bleeding with change in bowel habit at any age (NICE NG12 1.3.1)",
            tier="2WW_URGENT",
            drivers=["Rectal bleeding", "Change in bowel habit"],
        )

    # Weight loss ≥3kg + age ≥60 + any co-present GI symptom
    gi_symptoms = {"rectal_bleeding", "change_in_bowel_habit", "iron_deficiency_anaemia"}
    if (
        "weight_loss" in s
        and _age_gte_60(age_band)
        and (s & gi_symptoms)
    ):
        co_present = [
            {"rectal_bleeding": "Rectal bleeding",
             "change_in_bowel_habit": "Change in bowel habit",
             "iron_deficiency_anaemia": "Iron deficiency anaemia"}[k]
            for k in (s & gi_symptoms)
        ]
        return HardRuleResult(
            triggered=True,
            rule_name="WEIGHT_LOSS_AGE_60_GI",
            rule_description="Unexplained weight loss ≥3kg with age ≥60 and co-present GI symptom (NICE NG12)",
            tier="2WW_URGENT",
            drivers=["Weight loss ≥3kg", "Age ≥60"] + co_present,
        )

    # ── Rule 1.4: Weight loss sole feature, no colorectal symptoms ────────────
    # FIT negative or not done + weight loss only + no other colorectal symptoms
    # → Does NOT proceed to Layer 2. Output: CUP pathway / primary care.

    colorectal_symptoms = {"rectal_bleeding", "change_in_bowel_habit", "iron_deficiency_anaemia"}
    if (
        "weight_loss" in s
        and not (s & colorectal_symptoms)
        and fit_result in ("negative", "notdone")
        and not e  # no examination findings (those fire earlier)
    ):
        return HardRuleResult(
            triggered=True,
            rule_name="WEIGHT_LOSS_CUP",
            rule_description=(
                "Unexplained weight loss ≥3kg as sole feature with no colorectal symptoms "
                "and FIT negative or not done (Rule 1.4)"
            ),
            tier="WEIGHT_LOSS_CUP",
            drivers=["Weight loss ≥3kg", "No colorectal symptoms",
                     f"FIT {fit_result}"],
        )

    # ── No hard rule fired ────────────────────────────────────────────────────
    return HardRuleResult(triggered=False)

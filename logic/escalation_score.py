"""
hummingbird/logic/escalation_score.py
Within-2WW escalation priority score.
Derived from same inputs as referral decision — no additional data needed.
Per Analyst Brief v3.0 (Prof Aneel Bhangu sign-off).

Scoring table:
  Age <60        → +0
  Age 60–69      → +2  (Hamilton CAPER, PMID 16136048)
  Age 70+        → +3  (QCancer, PMID 22240376)
  FIT not done   → +0
  FIT negative   → FORCES STANDARD regardless of other scores (override)
  FIT positive   → +3  (Bailey BJS Open 2021, PMID 33693553)
  FIT high ≥100  → +8  (not additive with +3; replaces it)
  Rectal bleeding         → +1  (Astin et al., BJGP 2011, PMID 21619747)
  Change in bowel habit   → +1  (Hamilton CAPER, PMID 16136048)
  Weight loss ≥3kg        → +1  (QCancer, PMID 22240376)
  Iron deficiency anaemia → +1  (Hamilton Br J Cancer 2008, PMID 17876329)

Score tiers (per Prof Aneel Bhangu, v3.0):
  0–3   → STANDARD   — routine 2WW processing
  4–8   → ELEVATED   — target appointment within 7 days
  9+    → HIGH       — target appointment within 72 hours

FIT negative override: score always returns STANDARD regardless of total.

Hard override flags (displayed regardless of score):
  FIT ≥100 + IDA         → HIGH RISK — consider STT if PS 0–1 and age <80
  FIT ≥100 + weight loss → HIGH RISK — consider STT if PS 0–1 and age <80
"""

from dataclasses import dataclass, field


@dataclass
class EscalationResult:
    score: int
    score_tier: str
    score_tier_colour: str
    score_tier_class: str
    action: str
    fit_negative_override: bool = False   # True when FIT negative forced STANDARD
    override_flags: list[str] = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)


# ── Scoring constants ─────────────────────────────────────────────────────────

AGE_SCORES = {
    "u60":   0,
    "60-69": 2,
    "70+":   3,
}

FIT_SCORES = {
    "notdone":  0,
    "negative": 0,   # score is 0 AND triggers STANDARD override
    "positive": 3,
    "high":     8,
}

SYMPTOM_SCORES = {
    "rectal_bleeding":          1,
    "change_in_bowel_habit":    1,
    "weight_loss":              1,
    "iron_deficiency_anaemia":  1,
}

SCORE_TIERS = [
    (9,  "HIGH — ACCELERATED 2WW",       "#dc2626", "sc-high",
     "Accelerated 2WW. Target investigation within 72 hours. Consider STT if PS 0–1 and age <80."),
    (4,  "ELEVATED — PRIORITISED 2WW",   "#d97706", "sc-elev",
     "Prioritised 2WW. Aim for investigation within 7 days. Consider STT if high-risk features present."),
    (0,  "STANDARD",                     "#64748b", "sc-std",
     "Standard 2WW processing."),
]

STANDARD_TIER = SCORE_TIERS[2]  # (0, "STANDARD", ...)


def calculate_escalation_score(
    age_band: str,
    fit_result: str,
    symptoms: list[str],
) -> EscalationResult:
    """
    Calculate within-2WW escalation priority score.
    FIT negative forces STANDARD regardless of other factors (v3.0 rule).

    age_band:   "u60" | "60-69" | "70+"
    fit_result: "notdone" | "negative" | "positive" | "high"
    symptoms:   list of symptom keys
    """
    s = set(symptoms)
    breakdown = {}

    age_score = AGE_SCORES.get(age_band, 0)
    if age_score:
        breakdown[f"Age {age_band}"] = age_score

    fit_score = FIT_SCORES.get(fit_result, 0)
    if fit_score:
        breakdown[f"FIT {fit_result}"] = fit_score

    sym_score = 0
    sym_labels = {
        "rectal_bleeding":         "Rectal bleeding",
        "change_in_bowel_habit":   "Change in bowel habit",
        "weight_loss":             "Weight loss ≥3kg",
        "iron_deficiency_anaemia": "Iron deficiency anaemia",
    }
    for key, pts in SYMPTOM_SCORES.items():
        if key in s:
            breakdown[sym_labels[key]] = pts
            sym_score += pts

    total = age_score + fit_score + sym_score

    # ── FIT negative override — always STANDARD ───────────────────────────────
    fit_negative_override = (fit_result == "negative")
    if fit_negative_override:
        _, tier_name, colour, css_class, action = STANDARD_TIER
        return EscalationResult(
            score=total,
            score_tier=tier_name,
            score_tier_colour=colour,
            score_tier_class=css_class,
            action=action,
            fit_negative_override=True,
            override_flags=[],
            breakdown=breakdown,
        )

    # ── Normal tier calculation ───────────────────────────────────────────────
    matched_tier = STANDARD_TIER
    for threshold, tier_name, colour, css_class, action in SCORE_TIERS:
        if total >= threshold:
            matched_tier = (threshold, tier_name, colour, css_class, action)
            break

    _, tier_name, colour, css_class, action = matched_tier

    # Override flags
    override_flags = []
    if fit_result == "high" and "iron_deficiency_anaemia" in s:
        override_flags.append(
            "HIGH RISK — FIT ≥100 µg/g with iron deficiency anaemia. "
            "Consider STT pathway if PS 0–1 and age <80."
        )
    elif fit_result == "high" and "weight_loss" in s:
        override_flags.append(
            "HIGH RISK — FIT ≥100 µg/g with unexplained weight loss ≥3kg. "
            "Consider STT pathway if PS 0–1 and age <80."
        )

    return EscalationResult(
        score=total,
        score_tier=tier_name,
        score_tier_colour=colour,
        score_tier_class=css_class,
        action=action,
        fit_negative_override=False,
        override_flags=override_flags,
        breakdown=breakdown,
    )

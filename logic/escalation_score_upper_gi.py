"""
hummingbird/logic/escalation_score_upper_gi.py
Within-2WW escalation priority score — Upper GI module.
Per Analyst Brief v1.0, section 5.

Key difference from colorectal: negative deflectors (OGD −3, CT −2).
Score is floored at 0.

Scoring table:
  Age ≥55                    → +3
  Dysphagia                  → +4
  Haematemesis               → +3
  Unexplained weight loss    → +2
  Dyspepsia + age ≥55        → +1
  Upper abdominal pain       → +1
  Nausea / vomiting          → +1
  OGD clear <3 years         → −3
  CT chest/abdomen clear <3yr→ −2

Score tiers (per Analyst Brief v1.0):
  0–3  → LOW RISK  (grey)
  4–8  → ELEVATED  (amber)
  9+   → HIGH      (red)
"""

from dataclasses import dataclass, field


@dataclass
class EscalationResultUpperGI:
    score: int
    score_tier: str
    score_tier_colour: str
    score_tier_class: str
    action: str
    override_flags: list[str] = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)


SCORE_TIERS = [
    (9,  "HIGH",      "#dc2626", "sc-high",
     "Accelerated 2WW — aim for OGD within 72 hours or STT if PS 0–1."),
    (4,  "ELEVATED",  "#d97706", "sc-elev",
     "Prioritised 2WW — aim for OGD within 7 days or STT if eligible."),
    (0,  "LOW RISK",  "#64748b", "sc-std",
     "Safety net — refer routinely if needed; 2WW if ongoing or escalating concern."),
]


def calculate_escalation_score_upper_gi(
    age_band: str,           # "u55" | "55plus"
    symptoms: list[str],
    modifiers: list[str],
) -> EscalationResultUpperGI:

    s = set(symptoms)
    m = set(modifiers)
    breakdown = {}
    total = 0

    # Age
    if age_band == "55plus":
        breakdown["Age ≥55"] = 3
        total += 3

    # Symptoms
    if "dysphagia" in s:
        breakdown["Dysphagia"] = 4; total += 4
    if "haematemesis" in s:
        breakdown["Haematemesis"] = 3; total += 3
    if "weight_loss" in s:
        breakdown["Unexplained weight loss"] = 2; total += 2
    if "dyspepsia" in s and age_band == "55plus":
        breakdown["Dyspepsia (age ≥55)"] = 1; total += 1
    if "upper_abdominal_pain" in s:
        breakdown["Upper abdominal pain"] = 1; total += 1
    if "nausea_vomiting" in s:
        breakdown["Nausea / vomiting"] = 1; total += 1

    # Deflectors
    if "ogd_clear" in m:
        breakdown["OGD clear <3 years"] = -3; total -= 3
    if "ct_clear" in m:
        breakdown["CT chest/abdomen clear <3 years"] = -2; total -= 2

    # Floor at 0
    total = max(0, total)

    # Tier
    score_tier = SCORE_TIERS[-1]
    for threshold, tier_name, colour, css_class, action in SCORE_TIERS:
        if total >= threshold:
            score_tier = (threshold, tier_name, colour, css_class, action)
            break

    _, tier_name, colour, css_class, action = score_tier

    # Override flags
    override_flags = []
    if "dysphagia" in s and "weight_loss" in s:
        override_flags.append(
            "HIGH RISK — Dysphagia with unexplained weight loss. "
            "Expedite OGD. Direct consultant contact if PS 0–1 and age ≥55."
        )
    if "barretts" in m and ("dysphagia" in s or "weight_loss" in s or "haematemesis" in s):
        override_flags.append(
            "Known Barrett's oesophagus with new alarm feature. "
            "Do not defer to surveillance schedule — expedite OGD."
        )

    return EscalationResultUpperGI(
        score=total,
        score_tier=tier_name,
        score_tier_colour=colour,
        score_tier_class=css_class,
        action=action,
        override_flags=override_flags,
        breakdown=breakdown,
    )

"""
hummingbird/logic/stt_eligibility.py
STT (Straight to Test) eligibility gate — standalone helper.
Used by hard_rules.py and referenced in audit logging.

STT requires:
  - Performance status PS 0–1 (fit & active)
  - Confirmed age <80 (70+ band is ineligible — exact age unknown)

The 70+ band must be treated as STT-ineligible by default.
The ineligibility reason is logged and surfaced to the GP.
"""


def check_stt_eligible(age_band: str, performance_status: str) -> tuple[bool, str]:
    """
    Returns (eligible: bool, ineligible_reason: str).
    ineligible_reason is empty string if eligible.

    age_band: "u60" | "60-69" | "70+"
    performance_status: "fit" | "limited"
    """
    if age_band == "70+":
        return False, (
            "STT clinically indicated but patient is in 70+ age band. "
            "Exact age unknown — STT requires confirmed age <80. "
            "Refer via standard 2WW and consider direct contact with receiving "
            "team to expedite."
        )
    if performance_status == "limited":
        return False, (
            "STT clinically indicated but PS 2–4 — STT pathway not appropriate. "
            "Refer via standard 2WW urgent pathway."
        )
    return True, ""

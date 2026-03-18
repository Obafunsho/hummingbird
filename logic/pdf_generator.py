"""
hummingbird/logic/pdf_generator.py
PDF generation using WeasyPrint from HTML template.
Includes: HBID, tier, escalation score, STT flag, model version, regulatory footer.
Falls back to HTML download if WeasyPrint unavailable.
"""

from datetime import datetime, timezone
from pathlib import Path

try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def generate_pdf(
    hbid: str,
    age_band: str,
    sex: str,
    performance_status: str,
    symptoms: list,
    examination_findings: list,
    modifiers: list,
    fit_result: str,
    nhs_number: str,
    result: dict,
    escalation_score: int,
    escalation_tier: str,
    escalation_action: str,
) -> bytes:
    """
    Generate PDF (or HTML fallback) for download.
    Never stored server-side — generated on demand only.
    """
    html = _build_html(
        hbid=hbid,
        age_band=age_band,
        sex=sex,
        performance_status=performance_status,
        symptoms=symptoms,
        examination_findings=examination_findings,
        modifiers=modifiers,
        fit_result=fit_result,
        nhs_number=nhs_number,
        result=result,
        escalation_score=escalation_score,
        escalation_tier=escalation_tier,
        escalation_action=escalation_action,
    )

    if WEASYPRINT_AVAILABLE:
        return WeasyHTML(string=html).write_pdf()
    else:
        return html.encode("utf-8")


def _build_html(
    hbid, age_band, sex, performance_status,
    symptoms, examination_findings, modifiers, fit_result,
    nhs_number, result,
    escalation_score, escalation_tier, escalation_action,
) -> str:
    tier = result.get("tier", "")
    tier_label = result.get("tier_label", tier)
    rationale = result.get("rationale", "")
    safety_netting = result.get("safety_netting") or ""
    stt_flag = tier == "2WW_URGENT_STT"
    stt_ineligible = result.get("stt_ineligible_reason", "") or ""
    prompt_version = result.get("prompt_version", "")
    model_version = result.get("model_version", "")
    layer = result.get("layer", "")
    confidence = result.get("confidence", "")
    drivers = result.get("inputs_driving_decision", [])

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%d %B %Y")
    time_str = now.strftime("%H:%M UTC")

    # Tier colour
    tier_colours = {
        "2WW_URGENT_STT":    "#7f1d1d",
        "2WW_URGENT":        "#dc2626",
        "ROUTINE_REFERRAL":  "#d97706",
        "INVESTIGATE_FIRST": "#3b82f6",
        "SAFETY_NET_ACTIVE": "#0E9B8A",
        "SAFETY_NET_PASSIVE":"#64748b",
        "REASSURE_DISCHARGE":"#22c55e",
    }
    tier_colour = tier_colours.get(tier, "#0E9B8A")

    sym_labels = {
        "rectal_bleeding": "Rectal bleeding",
        "change_in_bowel_habit": "Change in bowel habit",
        "weight_loss": "Unexplained weight loss ≥3kg",
        "iron_deficiency_anaemia": "Iron deficiency anaemia",
    }
    exam_labels = {
        "rectal_mass": "Rectal mass on examination",
        "abdominal_mass": "Unexplained abdominal mass",
        "anal_mass": "Anal mass or ulceration",
    }
    mod_labels = {
        "colonoscopy_clear": "Colonoscopy clear <3 years",
        "ct_clear": "CT abdomen clear <3 years",
        "mcd_ctdna": "Positive MCD/ctDNA",
    }
    fit_labels = {
        "notdone": "Not done",
        "negative": "Negative <10 µg/g",
        "positive": "Positive 10–99 µg/g",
        "high": "High ≥100 µg/g",
    }
    ps_labels = {"fit": "Fit & active (PS 0–1)", "limited": "Limited/bed-bound (PS 2–4)"}

    sym_html = "".join(f"<li>{sym_labels.get(s, s)}</li>" for s in symptoms) or "<li>None selected</li>"
    exam_html = "".join(f"<li>{exam_labels.get(e, e)}</li>" for e in examination_findings) or "<li>None</li>"
    mod_html = "".join(f"<li>{mod_labels.get(m, m)}</li>" for m in modifiers) or "<li>None</li>"
    driver_html = "".join(f"<li>{d}</li>" for d in drivers) or "<li>—</li>"

    nhs_html = f"<p><strong>NHS Number:</strong> {nhs_number}</p>" if nhs_number and nhs_number.strip() else ""
    stt_html = f'<p style="color:{tier_colour};font-weight:600;">⚡ Straight to Test (STT) pathway indicated</p>' if stt_flag else ""
    stt_ineligible_html = f'<p style="color:#d97706;"><strong>Note:</strong> {stt_ineligible}</p>' if stt_ineligible else ""
    safety_html = f"<h3>Safety Netting</h3><p>{safety_netting}</p>" if safety_netting else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11px; color: #1a2e42; margin: 40px; line-height: 1.6; }}
  h1 {{ font-size: 22px; color: {tier_colour}; margin-bottom: 2px; }}
  h2 {{ font-size: 14px; color: #0B1826; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-top: 20px; }}
  h3 {{ font-size: 12px; color: #334155; margin-bottom: 4px; }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; border-bottom: 2px solid {tier_colour}; padding-bottom: 16px; }}
  .wordmark {{ font-size: 18px; font-weight: 700; color: #0E9B8A; letter-spacing: 0.05em; }}
  .hbid {{ font-family: monospace; font-size: 12px; color: #64748b; }}
  .tier-box {{ background: #f8fafc; border-left: 4px solid {tier_colour}; padding: 12px 16px; margin: 12px 0; border-radius: 4px; }}
  .tier-name {{ font-size: 16px; font-weight: 700; color: {tier_colour}; }}
  .score-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; margin: 12px 0; border-radius: 4px; }}
  .score-num {{ font-size: 32px; font-weight: 700; color: {tier_colour}; }}
  ul {{ margin: 4px 0; padding-left: 20px; }}
  .footer {{ margin-top: 32px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 9px; color: #94a3b8; line-height: 1.5; }}
  .meta {{ font-family: monospace; font-size: 9px; color: #94a3b8; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0; }}
  td {{ padding: 4px 8px; vertical-align: top; }}
  td:first-child {{ width: 160px; font-weight: 500; color: #64748b; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="wordmark">HUMMINGBIRD</div>
    <div style="font-size:10px;color:#64748b;">Cancer Referral Decision Support · Lower GI</div>
  </div>
  <div style="text-align:right;">
    <div class="hbid">{hbid}</div>
    <div class="meta">{date_str} · {time_str}</div>
  </div>
</div>

<h2>Patient Profile</h2>
<table>
  <tr><td>Age band</td><td>{age_band}</td></tr>
  <tr><td>Performance status</td><td>{ps_labels.get(performance_status, performance_status)}</td></tr>
  <tr><td>FIT result</td><td>{fit_labels.get(fit_result, fit_result)}</td></tr>
</table>
{nhs_html}

<h2>Referral Decision</h2>
<div class="tier-box">
  <div class="tier-name">{tier_label}</div>
  {stt_html}
  <p>{rationale}</p>
  {stt_ineligible_html}
</div>

{safety_html}

<h2>Escalation Priority</h2>
<div class="score-box">
  <div class="score-num">{escalation_score} <span style="font-size:14px;font-weight:400;color:#64748b;">/ 15</span></div>
  <div style="font-weight:600;color:{tier_colour};">{escalation_tier}</div>
  <p>{escalation_action}</p>
</div>

<h2>Inputs</h2>
<table>
  <tr><td>Symptoms</td><td><ul>{sym_html}</ul></td></tr>
  <tr><td>Examination findings</td><td><ul>{exam_html}</ul></td></tr>
  <tr><td>Modifiers</td><td><ul>{mod_html}</ul></td></tr>
</table>

<h2>Inputs Driving Decision</h2>
<ul>{driver_html}</ul>

<h2>Decision Metadata</h2>
<table>
  <tr><td>Layer</td><td>{layer}</td></tr>
  <tr><td>Confidence</td><td>{confidence}</td></tr>
  <tr><td>Prompt version</td><td>{prompt_version}</td></tr>
  <tr><td>Model version</td><td>{model_version}</td></tr>
  <tr><td>HBID</td><td>{hbid}</td></tr>
</table>

<div class="footer">
  This recommendation was generated by Hummingbird using prompt {prompt_version} and model {model_version},
  approved by Prof Aneel Bhangu, Consultant Colorectal Surgeon.
  This tool supports but does not replace clinical judgement.
  For use in education and audit mode. MHRA registration in progress.
  Generated: {date_str} {time_str}
</div>

</body>
</html>"""

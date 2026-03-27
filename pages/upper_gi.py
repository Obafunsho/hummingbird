"""
hummingbird/pages/upper_gi.py — Upper GI Module v1.0
"""
import os, sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Robust path resolution for Streamlit Cloud
_HERE = Path(__file__).resolve().parent          # pages/
_ROOT = _HERE.parent                              # hummingbird/
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    load_dotenv(_ROOT / ".env", override=False)
except Exception:
    pass

try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str) and _k not in os.environ:
            os.environ[_k] = _v
except Exception:
    pass

from logic.hard_rules_upper_gi import check_hard_rules_upper_gi
from logic.claude_layer_upper_gi import (
    call_claude_upper_gi, build_hard_rule_response_upper_gi
)
from logic.escalation_score_upper_gi import calculate_escalation_score_upper_gi
from logic.audit_logger import log_recommendation, generate_session_id, generate_hbid
from auth import do_logout

# name is available from session state set by app.py auth gate
name = st.session_state.get("name", "")

# ── CSS (shared with colorectal) ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
:root { --bg:#f5f4f1; --card:#fff; --border:#e2dfd8; --border2:#d4d2cc; --text:#1a1a1a; --muted:#666; --dim:#999; --accent:#1a1a1a; }
.stApp { background:var(--bg) !important; font-family:'DM Sans',sans-serif !important; color:var(--text) !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
.stButton > button {
  background:#fff !important; border:0.5px solid var(--border2) !important;
  border-radius:8px !important; color:var(--muted) !important;
  font-family:'DM Sans',sans-serif !important; font-size:13px !important;
  font-weight:400 !important; padding:9px 14px !important; width:100% !important;
  transition:all 0.12s !important; cursor:pointer !important;
}
.stButton > button:hover { border-color:var(--accent) !important; color:var(--accent) !important; background:#fafaf8 !important; }
.stButton > button:focus { outline:none !important; box-shadow:none !important; }
.hb-submit .stButton > button {
  background:var(--accent) !important; border:none !important; border-radius:8px !important;
  color:#fff !important; font-size:14px !important; font-weight:500 !important; padding:13px 24px !important;
}
.hb-submit .stButton > button:hover { background:#333 !important; }
.hb-submit .stButton > button:disabled { background:#ccc !important; color:rgba(255,255,255,0.6) !important; }
.hb-reset .stButton > button {
  background:none !important; border:none !important; color:var(--dim) !important;
  font-size:12px !important; text-decoration:underline !important; padding:4px !important;
}
.hb-reset .stButton > button:hover { color:var(--text) !important; background:none !important; border:none !important; }
.hb-tile-btn .stButton > button {
  font-size:12px !important; padding:7px 12px !important;
  border-radius:0 0 8px 8px !important; margin-top:0 !important;
  border-top:none !important; border-color:var(--border) !important; background:#fafaf8 !important;
}
.stTextArea textarea { background:#fafaf8 !important; border:0.5px solid var(--border2) !important; border-radius:6px !important; color:var(--text) !important; font-size:13px !important; }
.stTextArea textarea::placeholder { color:var(--dim) !important; }
.stDownloadButton > button { background:#fafaf8 !important; border:0.5px solid var(--border2) !important; border-radius:6px !important; color:var(--text) !important; font-size:13px !important; font-weight:500 !important; padding:9px 16px !important; width:100% !important; }
.stSpinner > div { border-top-color:var(--accent) !important; }

/* Module switcher active state */
.sw-active > div > button {
  background:#1a1a1a !important;
  border:0.5px solid #1a1a1a !important;
  color:#fff !important;
  font-weight:500 !important;
}
.sw-active > div > button:hover {
  background:#1a1a1a !important;
  color:#fff !important;
}
</style>
""", unsafe_allow_html=True)

# ── Style constants ────────────────────────────────────────────────────────────
TILE_SEL_SYM  = "background:#1a1a1a;border:0.5px solid #1a1a1a;"
TILE_SEL_HARD = "background:#c0392b;border:0.5px solid #c0392b;"
TILE_SEL_MOD  = "background:#f0ede8;border:0.5px solid #a8a49e;"
TILE_BASE     = "background:#fff;border:0.5px solid #e2dfd8;"
TILE_BASE_HARD= "background:#fff;border:0.5px solid #e8c8c4;"
TILE_BASE_MOD = "background:#fafaf8;border:0.5px solid #e2dfd8;opacity:0.8;"

TIER_STYLES = {
    "2WW_URGENT_STT":    {"border":"#c0392b","badge_bg":"#fdf2f1","badge_col":"#c0392b","badge":"Straight to Test"},
    "2WW_URGENT":        {"border":"#e8c8c4","badge_bg":"#fdf2f1","badge_col":"#c0392b","badge":"Urgent 2WW"},
    "ROUTINE_REFERRAL":  {"border":"#f0d8a8","badge_bg":"#fffbeb","badge_col":"#92400e","badge":"Routine"},
    "INVESTIGATE_FIRST": {"border":"#bfdbfe","badge_bg":"#eff6ff","badge_col":"#1d4ed8","badge":"Investigate First"},
    "SAFETY_NET_ACTIVE": {"border":"#d4d2cc","badge_bg":"#f5f4f1","badge_col":"#555","badge":"Active Review"},
    "SAFETY_NET_PASSIVE":{"border":"#e2dfd8","badge_bg":"#f5f4f1","badge_col":"#666","badge":"Safety Net"},
    "REASSURE_DISCHARGE":{"border":"#bbf7d0","badge_bg":"#f0fdf4","badge_col":"#15803d","badge":"Discharge"},
}


def tile_indicator(label, sublabel, selected, kind="sym"):
    if kind == "hard":  bg = TILE_SEL_HARD if selected else TILE_BASE_HARD
    elif kind == "mod": bg = TILE_SEL_MOD  if selected else TILE_BASE_MOD
    else:               bg = TILE_SEL_SYM  if selected else TILE_BASE
    col  = "#fff" if selected else "#1a1a1a"
    icon = "✓  " if selected else ""
    sub_col = "rgba(255,255,255,0.7)" if selected else "#999"
    sub  = f'<span style="font-size:12px;color:{sub_col};display:block;margin-top:3px;">{sublabel}</span>' if sublabel else ""
    st.markdown(
        f'<div style="{bg}border-radius:8px 8px 0 0;padding:12px 14px;color:{col};'
        f'font-size:14px;font-weight:500;line-height:1.35;margin-bottom:0;min-height:62px;pointer-events:none;">'
        f'{icon}{label}{sub}</div>', unsafe_allow_html=True)


def section_label(text, anno=""):
    if anno:
        st.markdown(
            f'<div style="font-size:10px;font-weight:600;letter-spacing:.12em;'
            f'color:#aaa;margin-bottom:5px;text-transform:uppercase;">{anno}</div>',
            unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:11px;font-weight:600;letter-spacing:.12em;'
        f'text-transform:uppercase;color:#999;margin-bottom:10px;'
        f'display:flex;align-items:center;gap:8px;">'
        f'{text}<span style="flex:1;height:0.5px;background:#e2dfd8;display:block;"></span></div>',
        unsafe_allow_html=True)


# ── Constants ──────────────────────────────────────────────────────────────────
AGE_BANDS    = [("u55","Under 55"), ("55plus","55 or over")]
SYMPTOMS     = [
    ("dysphagia",          "Dysphagia",             "Difficulty swallowing"),
    ("weight_loss",        "Unexplained weight loss","≥3 kg"),
    ("haematemesis",       "Haematemesis",           "Vomiting blood"),
    ("dyspepsia",          "Dyspepsia / reflux",     "Persistent"),
    ("upper_abdominal_pain","Upper abdominal pain",  "Unexplained"),
    ("nausea_vomiting",    "Nausea / vomiting",      "Persistent / unexplained"),
]
EXAM_FINDINGS = [
    ("upper_abdominal_mass",    "Upper abdominal mass",      "Unexplained"),
    ("cervical_lymphadenopathy","Cervical lymphadenopathy",  "Unexplained"),
]
HPYLORI_OPTIONS = [
    ("notdone",   "Not tested"),
    ("negative",  "Negative"),
    ("treated",   "Positive — treated"),
    ("untreated", "Positive — untreated"),
]
PS_OPTIONS = [
    ("fit",     "Fit & active  ·  PS 0–1"),
    ("limited", "Limited / bed-bound  ·  PS 2–4"),
]
MODIFIERS = [
    ("ogd_clear", "OGD clear",               "Within 3 years"),
    ("ct_clear",  "CT chest/abdomen clear",  "Within 3 years"),
    ("barretts",  "Known Barrett's oesophagus", "Under surveillance"),
    ("ppis",      "On long-term PPIs",        ""),
]

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "ugi_session_id": generate_session_id(),
        "ugi_age_band": None,
        "ugi_hpylori": "notdone",
        "ugi_ps": "fit",
        "ugi_symptoms": set(),
        "ugi_exam": set(),
        "ugi_modifiers": set(),
        "ugi_result": None,
        "ugi_escalation": None,
        "ugi_hbid": None,
        "ugi_last_inputs": {},
        "ugi_free_text_key": 0,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ── Topbar ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:12px 32px;border-bottom:0.5px solid #e2dfd8;background:#fff;">
  <div style="display:flex;align-items:baseline;gap:12px;">
    <a href="https://obafunsho.github.io/hummingbird_landing" target="_blank" style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a1a;letter-spacing:.01em;text-decoration:none;cursor:pointer;" onmouseover="this.style.opacity='0.6'" onmouseout="this.style.opacity='1'">Hummingbird</a>
    <span style="font-size:11px;font-weight:400;color:#999;letter-spacing:.1em;text-transform:uppercase;">Upper GI · Oesophagogastric</span>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#999;
      background:#f5f4f1;padding:4px 10px;border-radius:4px;border:0.5px solid #e2dfd8;">
      v1.0 · NICE NG12</span>
    <span style="font-size:12px;color:#555;">{name}</span>
    <a href="/?signout=1" target="_self"
      style="font-family:'JetBrains Mono',monospace;font-size:10px;
      color:#bbb;text-decoration:underline;text-underline-offset:3px;cursor:pointer;"
      onmouseover="this.style.color='#c0392b'"
      onmouseout="this.style.color='#bbb'">sign out</a>
  </div>
</div>""", unsafe_allow_html=True)

# Module switcher using st.switch_page
_sw_col1, _sw_col2, _sw_col3, _sw_col4, _sw_col5 = st.columns([5, 1, 1, 1, 1])
with _sw_col2:
    if st.button("Colorectal", key="sw_col", use_container_width=True):
        st.switch_page("pages/colorectal.py")
with _sw_col3:
    st.button("Upper GI", key="sw_ugi2", use_container_width=True, disabled=True)
with _sw_col4:
    if st.button("Appendicitis Risk", key="sw_app2", use_container_width=True):
        st.switch_page("pages/appendicitis.py")
with _sw_col5:
    if st.button("Surgical Risk", key="sw_surg2", use_container_width=True):
        st.switch_page("pages/surgical_risk.py")

if st.query_params.get("signout") == "1":
    st.query_params.clear()
    do_logout()

left_col, right_col = st.columns([3, 2], gap="small")

# ════════════════════════════ LEFT PANEL ══════════════════════════════════════
with left_col:
    st.markdown('<div style="padding:8px 32px 80px;background:#f5f4f1;">', unsafe_allow_html=True)

    # AGE
    section_label("Age", "1 CLICK · REQUIRED")
    cols = st.columns(2)
    for i, (val, label) in enumerate(AGE_BANDS):
        with cols[i]:
            sel = st.session_state.ugi_age_band == val
            tile_indicator(label, "", sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_age_{val}", use_container_width=True):
                st.session_state.ugi_age_band = val
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # SYMPTOMS
    section_label("Symptoms", "0–6 CLICKS · SELECT ALL PRESENT")
    cols = st.columns(2)
    for i, (key, label, sub) in enumerate(SYMPTOMS):
        with cols[i % 2]:
            sel = key in st.session_state.ugi_symptoms
            tile_indicator(label, sub, sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_sym_{key}", use_container_width=True):
                st.session_state.ugi_symptoms.symmetric_difference_update({key})
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # EXAMINATION FINDINGS
    section_label("Examination Findings", "NICE NG12 HARD RULE · DIRECT 2WW")
    st.markdown("""<div style="display:inline-flex;align-items:center;gap:5px;
      background:#f5f4f1;border:0.5px solid #d4d2cc;
      border-radius:4px;padding:4px 10px;
      font-size:11px;color:#666;letter-spacing:.05em;margin-bottom:10px;">
      ⚑ NICE NG12 · Direct pathway triggers — no prior investigation required</div>""",
      unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (key, label, sub) in enumerate(EXAM_FINDINGS):
        with cols[i]:
            sel = key in st.session_state.ugi_exam
            tile_indicator(label, sub, sel, "hard")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_exam_{key}", use_container_width=True):
                st.session_state.ugi_exam.symmetric_difference_update({key})
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.ugi_exam:
        st.markdown("""<div style="padding:12px 14px;border-radius:8px;margin-top:8px;
          background:#fdf2f1;border:0.5px solid #e8c8c4;
          font-size:13px;color:#c0392b;line-height:1.5;border-left:3px solid #c0392b;">
          ⚑ Hard rule triggered — direct suspected cancer pathway.</div>""",
          unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # H. PYLORI
    section_label("H. pylori Status", "1 CLICK · DEFAULTS TO NOT TESTED")
    cols = st.columns(4)
    for i, (val, label) in enumerate(HPYLORI_OPTIONS):
        with cols[i]:
            sel = st.session_state.ugi_hpylori == val
            tile_indicator(label, "", sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_hp_{val}", use_container_width=True):
                st.session_state.ugi_hpylori = val
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # PERFORMANCE STATUS
    section_label("Performance Status", "1 CLICK · DEFAULTS TO FIT · USED FOR STT GATE")
    cols = st.columns(2)
    for i, (val, label) in enumerate(PS_OPTIONS):
        with cols[i]:
            sel = st.session_state.ugi_ps == val
            tile_indicator(label, "", sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_ps_{val}", use_container_width=True):
                st.session_state.ugi_ps = val
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""<p style="font-size:12px;color:#999;margin-top:8px;line-height:1.6;padding-left:2px;">
      <strong style="color:#555;">PS 0–1:</strong> Fully active — eligible for Straight to Test.&nbsp;&nbsp;
      <strong style="color:#555;">PS 2–4:</strong> Significant limitations — standard 2WW only.</p>""",
      unsafe_allow_html=True)

    # ADDITIONAL DETAIL
    st.markdown("""<div style="display:flex;align-items:center;gap:10px;margin:24px 0 16px;">
      <span style="flex:1;height:0.5px;background:#e2dfd8;"></span>
      <span style="font-size:10px;font-weight:600;
        color:#bbb;letter-spacing:.12em;text-transform:uppercase;white-space:nowrap;">additional detail — optional</span>
      <span style="flex:1;height:0.5px;background:#e2dfd8;"></span>
    </div>""", unsafe_allow_html=True)
    section_label("Recent Investigations & Other", "SELECT IF PRESENT")
    cols = st.columns(2)
    for i, (key, label, sub) in enumerate(MODIFIERS):
        with cols[i % 2]:
            sel = key in st.session_state.ugi_modifiers
            tile_indicator(label, sub, sel, "mod")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ugi_mod_{key}", use_container_width=True):
                st.session_state.ugi_modifiers.symmetric_difference_update({key})
                st.session_state.ugi_result = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    free_text = st.text_area("", placeholder="Anything else relevant? (optional · max 300 chars)",
        max_chars=300, height=72, label_visibility="collapsed",
        key=f"ugi_ft_{st.session_state.ugi_free_text_key}")
    st.markdown("<br>", unsafe_allow_html=True)

    # SUBMIT
    if not bool(os.environ.get("ANTHROPIC_API_KEY")):
        st.warning("⚠️ ANTHROPIC_API_KEY not set in .env")
    hard_triggered = bool(st.session_state.ugi_exam)
    submit_enabled = (st.session_state.ugi_age_band is not None) or hard_triggered

    st.markdown('<div class="hb-submit">', unsafe_allow_html=True)
    submit_clicked = st.button("Get recommendation →", disabled=not submit_enabled,
                               use_container_width=True, key="ugi_submit_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    if not submit_enabled:
        st.markdown("""<p style="text-align:center;font-size:12px;color:#bbb;
          margin-top:6px;">Select age to begin</p>""",
          unsafe_allow_html=True)

    st.markdown('<div class="hb-reset">', unsafe_allow_html=True)
    if st.button("Reset all", key="ugi_reset_btn", use_container_width=True):
        st.session_state.update({
            "ugi_age_band": None, "ugi_result": None, "ugi_escalation": None,
            "ugi_hbid": None, "ugi_last_inputs": {}, "ugi_hpylori": "notdone",
            "ugi_ps": "fit", "ugi_symptoms": set(), "ugi_exam": set(),
            "ugi_modifiers": set(),
        })
        st.session_state.ugi_free_text_key += 1
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ════════════════════════════ PROCESSING ══════════════════════════════════════
if submit_clicked and submit_enabled:
    ft_val  = st.session_state.get(f"ugi_ft_{st.session_state.ugi_free_text_key}", "")
    age     = st.session_state.ugi_age_band or "u55"
    hp      = st.session_state.ugi_hpylori
    ps      = st.session_state.ugi_ps
    syms    = sorted(st.session_state.ugi_symptoms)
    exams   = sorted(st.session_state.ugi_exam)
    mods    = sorted(st.session_state.ugi_modifiers)

    with right_col:
        st.markdown('<div style="background:#f5f4f1;padding:0 24px 60px;border-left:0.5px solid #e2dfd8;">', unsafe_allow_html=True)
        with st.spinner("Applying NICE NG12 rules and AI reasoning…"):
            hard_result = check_hard_rules_upper_gi(
                age_band=age, performance_status=ps,
                symptoms=syms, examination_findings=exams,
                hpylori_status=hp, modifiers=mods)
            if hard_result.triggered:
                result = build_hard_rule_response_upper_gi(
                    rule_name=hard_result.rule_name,
                    rule_description=hard_result.rule_description,
                    tier=hard_result.tier, stt_eligible=hard_result.stt_eligible,
                    stt_driver=hard_result.stt_driver,
                    stt_ineligible_reason=hard_result.stt_ineligible_reason,
                    drivers=hard_result.drivers)
            else:
                try:
                    result = call_claude_upper_gi(
                        age_band=age, symptoms=syms, examination_findings=exams,
                        performance_status=ps, hpylori_status=hp,
                        modifiers=mods, free_text=ft_val)
                except Exception as e:
                    st.error(f"API error: {e}"); st.stop()

            escalation = calculate_escalation_score_upper_gi(
                age_band=age, symptoms=syms, modifiers=mods)
            hbid = generate_hbid().replace("HB-", "HB-UGI-")
            log_recommendation(
                hbid=hbid, session_id=st.session_state.ugi_session_id,
                age_band=age, fit_result="n/a", symptoms=syms,
                examination_findings=exams, performance_status=ps,
                modifiers=mods, free_text=ft_val, nhs_number="",
                result=result, escalation_score=escalation.score,
                escalation_tier=escalation.score_tier)
            st.session_state.ugi_result = result
            st.session_state.ugi_escalation = escalation
            st.session_state.ugi_hbid = hbid
            st.session_state.ugi_last_inputs = {
                "age_band": age, "hpylori": hp, "performance_status": ps,
                "symptoms": syms, "exam_findings": exams, "modifiers": mods}
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()

# ════════════════════════════ RIGHT PANEL ═════════════════════════════════════
with right_col:
    st.markdown('<div style="background:#f5f4f1;padding:0 24px 60px;border-left:0.5px solid #e2dfd8;">', unsafe_allow_html=True)

    if not st.session_state.ugi_result:
        st.markdown("""
        <div style="position:fixed;bottom:0;right:0;width:40%;
          display:flex;flex-direction:column;align-items:center;justify-content:center;
          height:100vh;pointer-events:none;z-index:0;">
          <div style="font-size:56px;margin-bottom:18px;opacity:0.1;color:#1a1a1a;">◎</div>
          <div style="font-family:'DM Serif Display',serif;font-size:24px;
            color:#ccc;margin-bottom:10px;text-align:center;">Awaiting inputs</div>
          <div style="font-size:14px;color:#ccc;line-height:1.8;
            max-width:240px;text-align:center;">
            Select age and symptoms on the left,<br>then tap <em>Get recommendation</em>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        result     = st.session_state.ugi_result
        escalation = st.session_state.ugi_escalation
        hbid       = st.session_state.ugi_hbid

        tier                  = result.get("tier", "SAFETY_NET_ACTIVE")
        tier_label            = result.get("tier_label", tier)
        rationale             = result.get("rationale", "")
        safety_netting        = result.get("safety_netting") or ""
        stt_ineligible_reason = result.get("stt_ineligible_reason") or ""
        layer                 = result.get("layer", "2")
        confidence            = result.get("confidence", "")
        drivers               = result.get("inputs_driving_decision", [])
        prompt_version        = result.get("prompt_version", "")
        model_version         = result.get("model_version", "")
        style = TIER_STYLES.get(tier, TIER_STYLES["SAFETY_NET_ACTIVE"])

        st.markdown(f'<div style="font-size:10px;color:#bbb;letter-spacing:.08em;text-align:right;margin-bottom:12px;">{hbid}</div>', unsafe_allow_html=True)

        if escalation and escalation.override_flags:
            for flag in escalation.override_flags:
                st.markdown(f'<div style="padding:12px 15px;border-radius:8px;background:#fdf2f1;border:0.5px solid #e8c8c4;border-left:3px solid #c0392b;font-size:13px;font-weight:600;color:#c0392b;line-height:1.5;margin-bottom:14px;">⚠ {flag}</div>', unsafe_allow_html=True)

        lc = "background:#fdf2f1;border:0.5px solid #e8c8c4;color:#c0392b" if layer=="1" else "background:#f5f4f1;border:0.5px solid #d4d2cc;color:#555"
        lt = f"Layer {layer} — {'NICE NG12 hard rule' if layer=='1' else 'AI reasoning'}"
        dts = "".join(f'<span style="font-size:11px;padding:3px 9px;border-radius:5px;background:#f5f4f1;border:0.5px solid #d4d2cc;color:#555;display:inline-block;margin:2px;">{d}</span>' for d in drivers)

        st.markdown(f"""
        <div style="border-radius:10px;border:0.5px solid {style['border']};background:#fff;overflow:hidden;margin-bottom:14px;">
          <div style="padding:16px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:0.5px solid {style['border']};">
            <div>
              <div style="font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#999;margin-bottom:5px;">Referral decision</div>
              <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a1a;">{tier_label}</div>
            </div>
            <span style="padding:5px 14px;border-radius:100px;background:{style['badge_bg']};color:{style['badge_col']};font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;">{style['badge']}</span>
          </div>
          <div style="padding:4px 18px 16px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 9px;border-radius:4px;display:inline-block;margin:10px 0 4px;background:{lc};">{lt}</span>
        """, unsafe_allow_html=True)

        if stt_ineligible_reason:
            st.markdown(f'<div style="font-size:13px;color:#92400e;margin-top:6px;padding:8px 12px;border-radius:6px;background:#fffbeb;border:0.5px solid #fde68a;border-left:3px solid #f59e0b;">⚠ {stt_ineligible_reason}</div>', unsafe_allow_html=True)

        st.markdown(f'<p style="font-size:14px;color:#444;line-height:1.7;margin-top:10px;">{rationale}</p>', unsafe_allow_html=True)

        if safety_netting:
            st.markdown(f'<p style="font-size:13px;color:#555;margin-top:10px;line-height:1.6;padding-top:10px;border-top:0.5px solid #e2dfd8;">⚑ {safety_netting}</p>', unsafe_allow_html=True)

        if dts:
            st.markdown(f'<div style="margin-top:10px;padding-top:10px;border-top:0.5px solid #e2dfd8;"><div style="font-size:10px;font-weight:600;color:#bbb;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">Inputs driving decision</div><div>{dts}</div></div>', unsafe_allow_html=True)

        if confidence:
            cc = {"high":"background:#f0fdf4;border:0.5px solid #bbf7d0;color:#15803d","moderate":"background:#fffbeb;border:0.5px solid #fde68a;color:#92400e","uncertain":"background:#fdf2f1;border:0.5px solid #e8c8c4;color:#c0392b"}.get(confidence,"background:#fffbeb;border:0.5px solid #fde68a;color:#92400e")
            ci = {"high":"●","moderate":"◑","uncertain":"○"}.get(confidence,"◑")
            st.markdown(f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;padding:3px 9px;border-radius:4px;display:inline-flex;align-items:center;gap:5px;margin-top:8px;background:{cc};">{ci} Confidence: {confidence}</span>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

        # Escalation score
        if escalation:
            pct = min((escalation.score / 14) * 100, 100)
            st.markdown(f"""
            <div style="border-radius:10px;border:0.5px solid #e2dfd8;background:#fff;padding:18px;margin-bottom:14px;">
              <div style="font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#bbb;margin-bottom:12px;">If referred — escalation priority</div>
              <div style="display:flex;align-items:flex-end;gap:14px;margin-bottom:10px;">
                <div style="font-family:'DM Serif Display',serif;font-size:56px;line-height:1;color:{escalation.score_tier_colour};">{escalation.score}</div>
                <div style="padding-bottom:6px;">
                  <div style="font-size:14px;font-weight:600;color:{escalation.score_tier_colour};">{escalation.score_tier}</div>
                  <div style="font-size:13px;color:#666;margin-top:3px;">{escalation.action}</div>
                </div>
              </div>
              <div style="height:5px;border-radius:100px;background:#f0ede8;overflow:hidden;">
                <div style="height:100%;border-radius:100px;width:{pct:.0f}%;background:{escalation.score_tier_colour};"></div>
              </div>
              <div style="font-size:11px;color:#bbb;margin-top:5px;">Score {escalation.score} / 14</div>
              <div style="font-size:12px;color:#aaa;margin-top:10px;line-height:1.6;">Literature-derived escalation support. Not a prospectively validated risk model.</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        nhs_number = st.text_input("NHS Number (optional · appears on PDF only)", max_chars=12, key="ugi_nhs_input")

        now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
        st.markdown(f"""
        <div style="font-size:11px;color:#bbb;line-height:1.7;
          border-top:0.5px solid #e2dfd8;padding-top:12px;margin-top:10px;">
          Hummingbird v1.0 · Upper GI · Clinician-authored · NICE NG12 compliant · Not prospectively validated ·
          Does not replace clinical judgement · MHRA registration in progress ·<br>
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;">
          prompt:{prompt_version} · model:{model_version} · layer:{layer} · {now_str}
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

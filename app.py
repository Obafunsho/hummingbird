"""
hummingbird/app.py — v2.1
"""
import os, sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)
sys.path.insert(0, str(Path(__file__).parent))

# Inject Streamlit secrets into environment (for Community Cloud deployment)
try:
    import streamlit as _st
    for _k, _v in _st.secrets.items():
        if isinstance(_v, str) and _k not in os.environ:
            os.environ[_k] = _v
except Exception:
    pass

from logic.hard_rules import check_hard_rules
from logic.claude_layer import call_claude, build_hard_rule_response
from logic.escalation_score import calculate_escalation_score
from logic.audit_logger import log_recommendation, generate_session_id, generate_hbid
from logic.qr_generator import generate_qr_bytes
from logic.pdf_generator import generate_pdf, WEASYPRINT_AVAILABLE
from auth import init_auth, render_login_page, do_logout

st.set_page_config(page_title="Hummingbird", page_icon="🐦",
                   layout="wide", initial_sidebar_state="collapsed")

# ── AUTH GATE ─────────────────────────────────────────────────────────────────
_, auth_status, username, name = init_auth()
if not auth_status:
    render_login_page()
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --navy:#0B1826; --navy-mid:#0D2137; --navy-card:#112233; --navy-tile:#1B3A52;
  --teal:#0E9B8A; --teal-b:#12C4AF; --red:#C0392B; --red-d:#7f1d1d;
  --white:#F0F4F8; --muted:rgba(240,244,248,0.55); --border:rgba(14,155,138,0.18);
}
.stApp { background:var(--navy) !important; font-family:'DM Sans',sans-serif !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }

/* ── All buttons base ── */
.stButton > button {
  background:#1B3A52 !important;
  border:1.5px solid rgba(240,244,248,0.1) !important;
  border-radius:8px !important;
  color:rgba(240,244,248,0.6) !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:13px !important; font-weight:500 !important;
  padding:9px 14px !important; width:100% !important;
  transition:background 0.15s,border-color 0.15s !important;
  cursor:pointer !important; line-height:1.3 !important;
}
.stButton > button:hover {
  border-color:#0E9B8A !important; color:#F0F4F8 !important;
  background:rgba(14,155,138,0.1) !important;
}
.stButton > button:focus { outline:none !important; box-shadow:none !important; }

/* Sign out */
div[data-testid="column"] .stButton > button[kind="secondary"] {
  background:none !important; border:1px solid rgba(240,244,248,0.12) !important;
  border-radius:6px !important; color:rgba(240,244,248,0.35) !important;
  font-size:11px !important; font-weight:400 !important;
  padding:5px 12px !important; width:auto !important;
}
div[data-testid="column"] .stButton > button[kind="secondary"]:hover {
  border-color:rgba(192,57,43,0.5) !important; color:#f87171 !important;
  background:rgba(192,57,43,0.08) !important;
}

/* Submit */
.hb-submit .stButton > button {
  background:linear-gradient(135deg,#0E9B8A,#12C4AF) !important;
  border:none !important; border-radius:10px !important;
  color:white !important; font-size:15px !important;
  font-weight:600 !important; padding:15px 24px !important;
  letter-spacing:0.01em !important;
  box-shadow:0 4px 24px rgba(14,155,138,0.4) !important;
}
.hb-submit .stButton > button:hover {
  box-shadow:0 6px 28px rgba(14,155,138,0.5) !important;
  transform:translateY(-1px) !important;
}
.hb-submit .stButton > button:disabled {
  background:rgba(14,155,138,0.15) !important;
  color:rgba(255,255,255,0.25) !important; box-shadow:none !important;
}

/* Reset */
.hb-reset .stButton > button {
  background:none !important; border:none !important;
  color:rgba(240,244,248,0.2) !important; font-size:12px !important;
  text-decoration:underline !important; padding:4px !important;
}
.hb-reset .stButton > button:hover {
  color:#12C4AF !important; background:none !important; border:none !important;
}

/* Tile select buttons — flush under tile, no gap */
.hb-tile-btn .stButton > button {
  font-size:12px !important; padding:7px 12px !important;
  border-radius:0 0 10px 10px !important; margin-top:0 !important;
  border-top:none !important;
  border-color:rgba(240,244,248,0.06) !important;
}

/* Inputs */
.stTextInput input {
  background:#1B3A52 !important; border:1.5px solid rgba(240,244,248,0.08) !important;
  border-radius:8px !important; color:#F0F4F8 !important;
  font-family:'JetBrains Mono',monospace !important; font-size:13px !important;
}
.stTextArea textarea {
  background:#1B3A52 !important; border:1.5px solid rgba(240,244,248,0.08) !important;
  border-radius:8px !important; color:#F0F4F8 !important; font-size:13px !important;
}
.stTextArea textarea::placeholder { color:rgba(240,244,248,0.3) !important; }
.stDownloadButton > button {
  background:rgba(14,155,138,0.1) !important;
  border:1.5px solid rgba(14,155,138,0.35) !important;
  border-radius:8px !important; color:#12C4AF !important;
  font-size:13px !important; font-weight:600 !important;
  padding:9px 16px !important; width:100% !important;
}
.stDownloadButton > button:hover { background:rgba(14,155,138,0.2) !important; }
.stSpinner > div { border-top-color:#12C4AF !important; }

/* Collapse Streamlit's internal column top gap */
div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
  gap: 0 !important;
  padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Style constants ────────────────────────────────────────────────────────────
TEAL_SEL    = "background:#0E9B8A;border:1.5px solid #0E9B8A;color:#fff;font-weight:600;box-shadow:0 0 0 3px rgba(14,155,138,0.25);"
RED_SEL     = "background:#C0392B;border:1.5px solid #C0392B;color:#fff;font-weight:600;box-shadow:0 0 0 3px rgba(192,57,43,0.25);"
DARKRED_SEL = "background:#7f1d1d;border:1.5px solid #7f1d1d;color:#fff;font-weight:600;box-shadow:0 0 0 3px rgba(127,29,29,0.3);"
BASE_BTN    = "background:#1B3A52;border:1.5px solid rgba(240,244,248,0.1);color:rgba(240,244,248,0.6);font-weight:500;"

TILE_SEL_SYM  = "background:rgba(14,155,138,0.18);border:1.5px solid #0E9B8A;box-shadow:0 0 0 3px rgba(14,155,138,0.15);"
TILE_SEL_HARD = "background:rgba(192,57,43,0.2);border:1.5px solid #C0392B;box-shadow:0 0 0 3px rgba(192,57,43,0.15);"
TILE_SEL_MOD  = "background:rgba(14,155,138,0.15);border:1.5px solid #0E9B8A;"
TILE_BASE     = "background:#1B3A52;border:1.5px solid rgba(240,244,248,0.07);"
TILE_BASE_HARD= "background:#1B3A52;border:1.5px solid rgba(192,57,43,0.28);"
TILE_BASE_MOD = "background:#1B3A52;border:1.5px solid rgba(240,244,248,0.05);opacity:0.65;"


def pill_indicator(label: str, selected: bool, colour: str = "teal") -> None:
    """Styled selection indicator rendered above the Streamlit button."""
    if colour == "red":       bg = RED_SEL
    elif colour == "darkred": bg = DARKRED_SEL
    else:                     bg = TEAL_SEL if selected else BASE_BTN
    icon = "✓  " if selected else ""
    st.markdown(
        f'<div style="{bg}border-radius:8px;padding:11px 14px;'
        f'font-family:DM Sans,sans-serif;font-size:14px;line-height:1.3;'
        f'margin-bottom:3px;pointer-events:none;">{icon}{label}</div>',
        unsafe_allow_html=True)


def tile_indicator(label: str, sublabel: str, selected: bool, kind: str = "sym") -> None:
    """Tile indicator for symptoms / exam / modifiers."""
    if kind == "hard":
        bg = TILE_SEL_HARD if selected else TILE_BASE_HARD
    elif kind == "mod":
        bg = TILE_SEL_MOD if selected else TILE_BASE_MOD
    else:
        bg = TILE_SEL_SYM if selected else TILE_BASE
    col  = "#F0F4F8" if selected else "rgba(240,244,248,0.65)"
    icon = "✓  " if selected else ""
    sub  = f'<span style="font-size:12px;color:rgba(240,244,248,0.5);display:block;margin-top:3px;">{sublabel}</span>' if sublabel else ""
    st.markdown(
        f'<div style="{bg}border-radius:10px 10px 0 0;padding:12px 14px;color:{col};'
        f'font-size:14px;font-weight:500;line-height:1.35;margin-bottom:0;'
        f'min-height:62px;pointer-events:none;">'
        f'{icon}{label}{sub}</div>',
        unsafe_allow_html=True)


def section_label(text: str, anno: str = "") -> None:
    if anno:
        st.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'letter-spacing:.1em;color:rgba(14,155,138,0.5);margin-bottom:5px;">{anno}</div>',
            unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
        f'letter-spacing:.15em;text-transform:uppercase;color:#0E9B8A;margin-bottom:10px;'
        f'display:flex;align-items:center;gap:8px;">'
        f'{text}<span style="flex:1;height:1px;background:rgba(14,155,138,0.18);display:block;"></span></div>',
        unsafe_allow_html=True)


# ── Constants ──────────────────────────────────────────────────────────────────
AGE_BANDS    = [("u60","Under 60"),("60-69","60 – 69"),("70+","70 or over")]
FIT_OPTIONS  = [("notdone","Not done",""),("negative","Negative  <10",""),
                ("positive","Positive · 10–99 µg/g","red"),("high","High · ≥100 µg/g","darkred")]
SYMPTOMS     = [("rectal_bleeding","Rectal bleeding","Frank / visible"),
                ("change_in_bowel_habit","Change in bowel habit",""),
                ("weight_loss","Unexplained weight loss","≥3 kg"),
                ("iron_deficiency_anaemia","Iron deficiency anaemia","Confirmed on bloods")]
EXAM_FINDINGS= [("rectal_mass","Rectal mass","On examination"),
                ("abdominal_mass","Abdominal mass","Unexplained"),
                ("anal_mass","Anal mass or ulceration","Unexplained · anal cancer pathway")]
PS_OPTIONS   = [("fit","Fit & active  ·  PS 0–1"),("limited","Limited / bed-bound  ·  PS 2–4")]
MODIFIERS    = [("colonoscopy_clear","Colonoscopy clear","Within 3 years"),
                ("ct_clear","CT abdomen clear","Within 3 years"),
                ("mcd_ctdna","Positive MCD / ctDNA","e.g. Galleri")]
TIER_STYLES  = {
    "2WW_URGENT_STT":    {"border":"#7f1d1d","badge_bg":"rgba(127,29,29,.4)","badge_col":"#fca5a5","badge":"Straight to Test"},
    "2WW_URGENT":        {"border":"#C0392B","badge_bg":"rgba(192,57,43,.3)","badge_col":"#f87171","badge":"Urgent 2WW"},
    "ROUTINE_REFERRAL":  {"border":"#d97706","badge_bg":"rgba(217,119,6,.25)","badge_col":"#fbbf24","badge":"Routine"},
    "INVESTIGATE_FIRST": {"border":"#3b82f6","badge_bg":"rgba(59,130,246,.25)","badge_col":"#93c5fd","badge":"Order FIT"},
    "SAFETY_NET_ACTIVE": {"border":"#0E9B8A","badge_bg":"rgba(14,155,138,.2)","badge_col":"#12C4AF","badge":"Active Review"},
    "SAFETY_NET_PASSIVE":{"border":"#64748b","badge_bg":"rgba(100,116,139,.25)","badge_col":"#94a3b8","badge":"Safety Net"},
    "REASSURE_DISCHARGE":{"border":"#22c55e","badge_bg":"rgba(34,197,94,.2)","badge_col":"#86efac","badge":"Discharge"},
}

# ── Session state ──────────────────────────────────────────────────────────────
def _init():
    for k, v in {
        "session_id":generate_session_id(),"age_band":None,"fit_result":"notdone",
        "performance_status":"fit","selected_symptoms":set(),"selected_exam":set(),
        "selected_modifiers":set(),"result":None,"escalation":None,"hbid":None,
        "last_inputs":{},"free_text_key":0,
    }.items():
        if k not in st.session_state: st.session_state[k]=v
_init()

# ── Topbar ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:12px 32px;border-bottom:1px solid rgba(14,155,138,0.18);background:#0B1826;">
  <div style="display:flex;align-items:baseline;gap:12px;">
    <span style="font-family:'DM Serif Display',serif;font-size:22px;color:#12C4AF;letter-spacing:.01em;">Hummingbird</span>
    <span style="font-size:12px;font-weight:400;color:rgba(240,244,248,0.35);letter-spacing:.1em;text-transform:uppercase;">Colorectal Cancer · Lower GI</span>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(240,244,248,0.35);
      background:rgba(240,244,248,0.05);padding:4px 10px;border-radius:4px;border:1px solid rgba(14,155,138,0.18);">
      v2.1 · NICE NG12</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(14,155,138,0.6);">{name}</span>
    <a href="/?signout=1" target="_self" onclick="window.location.href='/?signout=1'"
      style="font-family:'JetBrains Mono',monospace;font-size:10px;
      color:rgba(240,244,248,0.25);text-decoration:underline;text-underline-offset:3px;
      cursor:pointer;letter-spacing:.05em;"
      onmouseover="this.style.color='rgba(192,57,43,0.7)'"
      onmouseout="this.style.color='rgba(240,244,248,0.25)'">sign out</a>
  </div>
</div>""", unsafe_allow_html=True)

# Handle signout via query param
if st.query_params.get("signout") == "1":
    st.query_params.clear()
    do_logout()

left_col, right_col = st.columns([3, 2], gap="small")

# ════════════════════════════════════════════════ LEFT PANEL ══════════════════
with left_col:
    st.markdown('<div style="padding:8px 32px 80px;">', unsafe_allow_html=True)

    # SUBMIT — at top so result is always visible
    if not bool(os.environ.get("ANTHROPIC_API_KEY")):
        st.warning("⚠️ ANTHROPIC_API_KEY not set in .env")
    hard_triggered = bool(st.session_state.selected_exam)
    submit_enabled = (st.session_state.age_band is not None) or hard_triggered

    st.markdown('<div class="hb-submit">', unsafe_allow_html=True)
    submit_clicked = st.button("Get recommendation →", disabled=not submit_enabled,
                               use_container_width=True, key="submit_btn")
    st.markdown('</div>', unsafe_allow_html=True)
    if not submit_enabled:
        st.markdown("""<p style="text-align:center;font-size:12px;
          color:rgba(240,244,248,0.25);margin-top:4px;margin-bottom:8px;
          font-family:'JetBrains Mono',monospace;">Select age to begin</p>""",
          unsafe_allow_html=True)

    st.markdown('<div class="hb-reset">', unsafe_allow_html=True)
    if st.button("Reset all", key="reset_btn", use_container_width=True):
        st.session_state.update({
            "age_band":None,"result":None,"escalation":None,"hbid":None,
            "last_inputs":{},"fit_result":"notdone","performance_status":"fit",
            "selected_symptoms":set(),"selected_exam":set(),"selected_modifiers":set(),
        })
        st.session_state.free_text_key += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # AGE
    section_label("Age", "1 CLICK · REQUIRED")
    cols = st.columns(3)
    for i,(val,label) in enumerate(AGE_BANDS):
        with cols[i]:
            sel = st.session_state.age_band == val
            tile_indicator(label, "", sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"age_{val}", use_container_width=True):
                st.session_state.age_band=val; st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # FIT
    section_label("FIT Result", "1 CLICK · DEFAULTS TO NOT DONE")
    cols = st.columns(4)
    for i,(val,label,colour) in enumerate(FIT_OPTIONS):
        with cols[i]:
            sel = st.session_state.fit_result == val
            kind = "hard" if colour == "red" or colour == "darkred" else "sym"
            tile_indicator(label, "", sel, kind)
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"fit_{val}", use_container_width=True):
                st.session_state.fit_result=val; st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # SYMPTOMS
    section_label("Symptoms", "0–4 CLICKS · SELECT ALL PRESENT")
    cols = st.columns(2)
    for i,(key,label,sub) in enumerate(SYMPTOMS):
        with cols[i%2]:
            sel = key in st.session_state.selected_symptoms
            tile_indicator(label, sub, sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"sym_{key}", use_container_width=True):
                st.session_state.selected_symptoms.symmetric_difference_update({key})
                st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # EXAM FINDINGS
    section_label("Examination Findings", "NICE NG12 HARD RULE · DIRECT 2WW")
    st.markdown("""<div style="display:inline-flex;align-items:center;gap:5px;
      background:rgba(14,155,138,.08);border:1px solid rgba(14,155,138,.22);
      border-radius:4px;padding:4px 10px;font-family:JetBrains Mono,monospace;
      font-size:11px;color:#0E9B8A;letter-spacing:.05em;margin-bottom:10px;">
      ⚑ NICE NG12 · Direct pathway triggers — no FIT required before referral</div>""",
      unsafe_allow_html=True)
    cols = st.columns(3)
    for i,(key,label,sub) in enumerate(EXAM_FINDINGS):
        with cols[i]:
            sel = key in st.session_state.selected_exam
            tile_indicator(label, sub, sel, "hard")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"exam_{key}", use_container_width=True):
                st.session_state.selected_exam.symmetric_difference_update({key})
                st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.selected_exam:
        st.markdown("""<div style="padding:12px 14px;border-radius:8px;margin-top:8px;
          background:rgba(192,57,43,.12);border:1.5px solid rgba(192,57,43,.35);
          font-size:13px;color:#f87171;line-height:1.5;">
          ⚑ Hard rule triggered — direct suspected cancer pathway. FIT not required before referral.</div>""",
          unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # PERFORMANCE STATUS
    section_label("Performance Status", "1 CLICK · DEFAULTS TO FIT · USED FOR STT GATE")
    cols = st.columns(2)
    for i,(val,label) in enumerate(PS_OPTIONS):
        with cols[i]:
            sel = st.session_state.performance_status == val
            tile_indicator(label, "", sel, "sym")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"ps_{val}", use_container_width=True):
                st.session_state.performance_status=val; st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""<p style="font-size:12px;color:rgba(240,244,248,0.35);margin-top:8px;
      line-height:1.6;padding-left:2px;">
      <strong style="color:rgba(240,244,248,0.6);">PS 0–1:</strong> Fully active — eligible for Straight to Test.&nbsp;&nbsp;
      <strong style="color:rgba(240,244,248,0.6);">PS 2–4:</strong> Significant limitations — standard 2WW only.</p>""",
      unsafe_allow_html=True)

    # OPTIONAL
    st.markdown("""<div style="display:flex;align-items:center;gap:10px;margin:24px 0 16px;">
      <span style="flex:1;height:1px;background:rgba(240,244,248,0.06);"></span>
      <span style="font-family:JetBrains Mono,monospace;font-size:10px;
        color:rgba(240,244,248,0.2);letter-spacing:.12em;text-transform:uppercase;
        white-space:nowrap;">additional detail — optional</span>
      <span style="flex:1;height:1px;background:rgba(240,244,248,0.06);"></span>
    </div>""", unsafe_allow_html=True)
    section_label("Recent Investigations & Other", "SELECT IF PRESENT")
    cols = st.columns(3)
    for i,(key,label,sub) in enumerate(MODIFIERS):
        with cols[i]:
            sel = key in st.session_state.selected_modifiers
            tile_indicator(label, sub, sel, "mod")
            st.markdown('<div class="hb-tile-btn">', unsafe_allow_html=True)
            if st.button("✓ Selected" if sel else "+ Select", key=f"mod_{key}", use_container_width=True):
                st.session_state.selected_modifiers.symmetric_difference_update({key})
                st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    free_text = st.text_area("", placeholder="Anything else relevant? (optional · max 300 chars)",
        max_chars=300, height=72, label_visibility="collapsed",
        key=f"ft_{st.session_state.free_text_key}")
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════ PROCESSING ══════════════════
if submit_clicked and submit_enabled:
    ft_val     = st.session_state.get(f"ft_{st.session_state.free_text_key}","")
    age_band   = st.session_state.age_band or "u60"
    fit_result = st.session_state.fit_result
    perf       = st.session_state.performance_status
    syms       = sorted(st.session_state.selected_symptoms)
    exams      = sorted(st.session_state.selected_exam)
    mods       = sorted(st.session_state.selected_modifiers)

    with right_col:
        st.markdown('<div style="background:#0B1826;padding:0 24px 60px;border-left:1px solid rgba(14,155,138,0.18);">', unsafe_allow_html=True)
        with st.spinner("Applying NICE NG12 rules and AI reasoning…"):
            hard_result = check_hard_rules(age_band=age_band,performance_status=perf,
                symptoms=syms,examination_findings=exams,fit_result=fit_result,modifiers=mods)
            if hard_result.triggered:
                result = build_hard_rule_response(
                    rule_name=hard_result.rule_name,rule_description=hard_result.rule_description,
                    tier=hard_result.tier,stt_eligible=hard_result.stt_eligible,
                    stt_driver=hard_result.stt_driver,stt_ineligible_reason=hard_result.stt_ineligible_reason,
                    drivers=hard_result.drivers)
            else:
                try:
                    result = call_claude(age_band=age_band,fit_result=fit_result,symptoms=syms,
                        examination_findings=exams,performance_status=perf,modifiers=mods,free_text=ft_val)
                except Exception as e:
                    st.error(f"API error: {e}"); st.stop()
            escalation = calculate_escalation_score(age_band=age_band,fit_result=fit_result,symptoms=syms)
            hbid = generate_hbid()
            log_recommendation(hbid=hbid,session_id=st.session_state.session_id,
                age_band=age_band,fit_result=fit_result,symptoms=syms,
                examination_findings=exams,performance_status=perf,modifiers=mods,
                free_text=ft_val,nhs_number="",result=result,
                escalation_score=escalation.score,escalation_tier=escalation.score_tier)
            st.session_state.result=result; st.session_state.escalation=escalation
            st.session_state.hbid=hbid
            st.session_state.last_inputs={"age_band":age_band,"fit_result":fit_result,
                "performance_status":perf,"symptoms":syms,"exam_findings":exams,"modifiers":mods}
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()

# ════════════════════════════════════════════════ RIGHT PANEL ═════════════════
with right_col:
    st.markdown('<div style="background:#0B1826;padding:0 24px 60px;border-left:1px solid rgba(14,155,138,0.18);">', unsafe_allow_html=True)

    if not st.session_state.result:
        st.markdown("""
        <div style="position:fixed;bottom:0;right:0;width:40%;
          display:flex;flex-direction:column;align-items:center;justify-content:center;
          height:100vh;pointer-events:none;z-index:0;">
          <div style="font-size:56px;margin-bottom:18px;opacity:0.12;color:#12C4AF;">◎</div>
          <div style="font-family:'DM Serif Display',serif;font-size:24px;
            color:rgba(240,244,248,0.15);margin-bottom:10px;text-align:center;">Awaiting inputs</div>
          <div style="font-size:14px;color:rgba(240,244,248,0.18);line-height:1.8;
            max-width:240px;text-align:center;">
            Select age and symptoms on the left,<br>then tap <em>Get recommendation</em>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        result     = st.session_state.result
        escalation = st.session_state.escalation
        hbid       = st.session_state.hbid
        inputs     = st.session_state.last_inputs

        tier                  = result.get("tier","SAFETY_NET_ACTIVE")
        tier_label            = result.get("tier_label",tier)
        rationale             = result.get("rationale","")
        safety_netting        = result.get("safety_netting") or ""
        stt_ineligible_reason = result.get("stt_ineligible_reason") or ""
        layer                 = result.get("layer","2")
        confidence            = result.get("confidence","")
        drivers               = result.get("inputs_driving_decision",[])
        prompt_version        = result.get("prompt_version","")
        model_version         = result.get("model_version","")
        style = TIER_STYLES.get(tier, TIER_STYLES["SAFETY_NET_ACTIVE"])

        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:rgba(14,155,138,.4);letter-spacing:.08em;text-align:right;margin-bottom:12px;">{hbid}</div>', unsafe_allow_html=True)

        if escalation and escalation.override_flags:
            for flag in escalation.override_flags:
                if "HIGHEST RISK" in flag:
                    st.markdown(f'<div style="padding:12px 15px;border-radius:8px;background:rgba(127,29,29,.22);border:1.5px solid rgba(192,57,43,.45);font-size:13px;font-weight:600;color:#fca5a5;line-height:1.5;margin-bottom:14px;">⚠ {flag}</div>', unsafe_allow_html=True)

        lc = "rgba(192,57,43,.12);border:1px solid rgba(192,57,43,.28);color:#f87171" if layer=="1" else "rgba(14,155,138,.08);border:1px solid rgba(14,155,138,.22);color:#12C4AF"
        lt = f"Layer {layer} — {'NICE NG12 hard rule' if layer=='1' else 'AI reasoning'}"
        dts = "".join(f'<span style="font-size:11px;padding:3px 9px;border-radius:5px;background:rgba(14,155,138,0.12);border:1px solid rgba(14,155,138,.2);color:#12C4AF;display:inline-block;margin:2px;">{d}</span>' for d in drivers)

        # Tier card
        st.markdown(f"""
        <div style="border-radius:14px;border:1.5px solid {style['border']};background:#112233;overflow:hidden;margin-bottom:14px;">
          <div style="padding:16px 18px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid {style['border']};">
            <div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:rgba(240,244,248,0.45);margin-bottom:5px;">Referral decision</div>
              <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#F0F4F8;">{tier_label}</div>
            </div>
            <span style="padding:5px 14px;border-radius:100px;background:{style['badge_bg']};color:{style['badge_col']};font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;">{style['badge']}</span>
          </div>
          <div style="padding:4px 18px 16px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 9px;border-radius:4px;display:inline-block;margin:10px 0 4px;background:{lc};">{lt}</span>
        """, unsafe_allow_html=True)

        if stt_ineligible_reason:
            st.markdown(f'<div style="font-size:13px;color:#fbbf24;margin-top:6px;padding:8px 12px;border-radius:6px;background:rgba(217,119,6,.1);border:1px solid rgba(217,119,6,.22);">⚠ {stt_ineligible_reason}</div>', unsafe_allow_html=True)

        st.markdown(f'<p style="font-size:14px;color:rgba(240,244,248,0.75);line-height:1.7;margin-top:10px;">{rationale}</p>', unsafe_allow_html=True)

        if safety_netting:
            st.markdown(f'<p style="font-size:13px;color:#12C4AF;margin-top:10px;line-height:1.6;padding-top:10px;border-top:1px solid rgba(14,155,138,.15);">⚑ {safety_netting}</p>', unsafe_allow_html=True)

        if dts:
            st.markdown(f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(240,244,248,0.06);"><div style="font-family:JetBrains Mono,monospace;font-size:10px;color:rgba(240,244,248,0.35);letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;">Inputs driving decision</div><div>{dts}</div></div>', unsafe_allow_html=True)

        if confidence:
            cc = {"high":"rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);color:#86efac",
                  "moderate":"rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.25);color:#fbbf24",
                  "uncertain":"rgba(192,57,43,.08);border:1px solid rgba(192,57,43,.25);color:#f87171"}.get(confidence,"rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.25);color:#fbbf24")
            ci = {"high":"●","moderate":"◑","uncertain":"○"}.get(confidence,"◑")
            st.markdown(f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;padding:3px 9px;border-radius:4px;display:inline-flex;align-items:center;gap:5px;margin-top:8px;background:{cc};">{ci} Confidence: {confidence}</span>', unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

        # Escalation score
        if escalation:
            pct = min((escalation.score/15)*100,100)
            st.markdown(f"""
            <div style="border-radius:14px;border:1.5px solid rgba(14,155,138,0.18);background:#112233;padding:18px;margin-bottom:14px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:rgba(240,244,248,0.3);margin-bottom:12px;">If referred — escalation priority</div>
              <div style="display:flex;align-items:flex-end;gap:14px;margin-bottom:10px;">
                <div style="font-family:'DM Serif Display',serif;font-size:56px;line-height:1;color:{escalation.score_tier_colour};">{escalation.score}</div>
                <div style="padding-bottom:6px;">
                  <div style="font-size:14px;font-weight:600;color:{escalation.score_tier_colour};">{escalation.score_tier}</div>
                  <div style="font-size:13px;color:rgba(240,244,248,0.5);margin-top:3px;">{escalation.action}</div>
                </div>
              </div>
              <div style="height:5px;border-radius:100px;background:rgba(240,244,248,0.06);overflow:hidden;">
                <div style="height:100%;border-radius:100px;width:{pct:.0f}%;background:{escalation.score_tier_colour};"></div>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(240,244,248,0.25);margin-top:5px;">Score {escalation.score} / 15</div>
              <div style="font-size:12px;color:rgba(240,244,248,0.25);margin-top:10px;line-height:1.6;">Literature-derived escalation support. Not a prospectively validated risk model. Score determines speed of referral, not whether to refer.</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        nhs_number = st.text_input("NHS Number (optional · appears on PDF only)", max_chars=12, key="nhs_input")

        dl_col, email_col = st.columns(2)
        with dl_col:
            try:
                pdf_bytes = generate_pdf(hbid=hbid,age_band=inputs.get("age_band",""),sex="",
                    performance_status=inputs.get("performance_status",""),
                    symptoms=inputs.get("symptoms",[]),examination_findings=inputs.get("exam_findings",[]),
                    modifiers=inputs.get("modifiers",[]),fit_result=inputs.get("fit_result",""),
                    nhs_number=nhs_number,result=result,
                    escalation_score=escalation.score if escalation else 0,
                    escalation_tier=escalation.score_tier if escalation else "",
                    escalation_action=escalation.action if escalation else "")
                ext  = "pdf" if WEASYPRINT_AVAILABLE else "html"
                mime = "application/pdf" if WEASYPRINT_AVAILABLE else "text/html"
                ts   = datetime.now().strftime("%Y%m%d_%H%M")
                st.download_button(f"⬇ Download {'PDF' if WEASYPRINT_AVAILABLE else 'HTML'}",
                    data=pdf_bytes,file_name=f"hummingbird_{hbid}_{ts}.{ext}",mime=mime,key="dl_pdf")
            except Exception as e:
                st.caption(f"PDF unavailable: {e}")
        with email_col:
            subject = f"Hummingbird {hbid}: {tier_label}"
            body    = f"Hummingbird ID: {hbid}\n\nRecommendation: {tier_label}\n\nRationale: {rationale}"
            if safety_netting: body += f"\n\nSafety netting: {safety_netting}"
            if escalation: body += f"\n\nEscalation score: {escalation.score}/15 — {escalation.score_tier}"
            body += f"\n\nPrompt: {prompt_version} | Model: {model_version}"
            mailto = f"mailto:?subject={subject}&body={body}".replace(" ","%20").replace("\n","%0A")
            st.markdown(f'<a href="{mailto}" style="text-decoration:none;display:block;margin-top:4px;"><button style="width:100%;padding:9px;border-radius:8px;border:1.5px solid rgba(14,155,138,0.2);background:transparent;color:rgba(240,244,248,0.4);font-family:DM Sans,sans-serif;font-size:13px;font-weight:500;cursor:pointer;">✉ Email summary</button></a>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        try:
            qr_bytes = generate_qr_bytes(tier)
            qc,ql = st.columns([1,2])
            with qc: st.image(qr_bytes,width=90)
            with ql: st.markdown('<p style="font-size:12px;color:rgba(240,244,248,0.3);line-height:1.6;padding-top:6px;">Patient information QR<br>Scan with phone</p>', unsafe_allow_html=True)
        except Exception: pass

        now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
        st.markdown(f"""
        <div style="font-size:11px;color:rgba(240,244,248,0.2);line-height:1.7;
          border-top:1px solid rgba(240,244,248,0.06);padding-top:12px;margin-top:10px;">
          Hummingbird v2.1 · Clinician-authored · NICE NG12 compliant · Not prospectively validated ·
          Does not replace clinical judgement · MHRA registration in progress ·<br>
          <span style="font-family:'JetBrains Mono',monospace;font-size:10px;">
          prompt:{prompt_version} · model:{model_version} · layer:{layer} · {now_str}
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

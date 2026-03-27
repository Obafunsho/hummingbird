"""
hummingbird/pages/colorectal.py — Colorectal Lower GI Module v2.1
"""
import os, sys
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from logic.hard_rules import check_hard_rules
from logic.claude_layer import call_claude, build_hard_rule_response
from logic.escalation_score import calculate_escalation_score
from logic.audit_logger import log_recommendation, generate_session_id, generate_hbid
from logic.qr_generator import generate_qr_bytes
from logic.pdf_generator import generate_pdf, WEASYPRINT_AVAILABLE
from auth import do_logout

# name is available from session state set by app.py auth gate
name = st.session_state.get("name", "")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
:root {
  --bg:#f5f4f1; --card:#ffffff; --border:#e2dfd8; --border2:#d4d2cc;
  --text:#1a1a1a; --muted:#666; --dim:#999; --accent:#1a1a1a; --danger:#c0392b;
}
.stApp { background:var(--bg) !important; font-family:'DM Sans',sans-serif !important; color:var(--text) !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
.stButton > button {
  background:#fff !important; border:0.5px solid var(--border2) !important;
  border-radius:8px !important; color:var(--muted) !important;
  font-family:'DM Sans',sans-serif !important; font-size:13px !important;
  font-weight:400 !important; padding:9px 14px !important; width:100% !important;
  transition:all 0.12s !important; cursor:pointer !important; line-height:1.3 !important;
}
.stButton > button:hover { border-color:var(--accent) !important; color:var(--accent) !important; background:#fafaf8 !important; }
.stButton > button:focus { outline:none !important; box-shadow:none !important; }
.hb-submit .stButton > button {
  background:var(--accent) !important; border:none !important; border-radius:8px !important;
  color:#fff !important; font-size:14px !important; font-weight:500 !important;
  padding:13px 24px !important; box-shadow:none !important;
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
.stTextInput input {
  background:#fafaf8 !important; border:0.5px solid var(--border2) !important;
  border-radius:6px !important; color:var(--text) !important; font-size:13px !important;
}
.stTextArea textarea {
  background:#fafaf8 !important; border:0.5px solid var(--border2) !important;
  border-radius:6px !important; color:var(--text) !important; font-size:13px !important;
}
.stTextArea textarea::placeholder { color:var(--dim) !important; }
.stDownloadButton > button {
  background:#fafaf8 !important; border:0.5px solid var(--border2) !important;
  border-radius:6px !important; color:var(--text) !important;
  font-size:13px !important; font-weight:500 !important;
  padding:9px 16px !important; width:100% !important;
}
.stDownloadButton > button:hover { background:#fff !important; border-color:var(--accent) !important; }
.stSpinner > div { border-top-color:var(--accent) !important; }
div[data-testid="stVerticalBlockBorderWrapper"] > div:first-child { padding-top:0 !important; margin-top:0 !important; }
div[data-testid="column"] > div[data-testid="stVerticalBlock"] { gap:0 !important; padding-top:0 !important; }

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

# ── Style constants (light theme) ─────────────────────────────────────────────
TEAL_SEL    = "background:#1a1a1a;border:0.5px solid #1a1a1a;color:#fff;font-weight:500;"
RED_SEL     = "background:#c0392b;border:0.5px solid #c0392b;color:#fff;font-weight:500;"
DARKRED_SEL = "background:#7f1d1d;border:0.5px solid #7f1d1d;color:#fff;font-weight:500;"
BASE_BTN    = "background:#fff;border:0.5px solid #d4d2cc;color:#666;font-weight:400;"

TILE_SEL_SYM  = "background:#1a1a1a;border:0.5px solid #1a1a1a;"
TILE_SEL_HARD = "background:#c0392b;border:0.5px solid #c0392b;"
TILE_SEL_MOD  = "background:#f0ede8;border:0.5px solid #a8a49e;"
TILE_BASE     = "background:#fff;border:0.5px solid #e2dfd8;"
TILE_BASE_HARD= "background:#fff;border:0.5px solid #e8c8c4;"
TILE_BASE_MOD = "background:#fafaf8;border:0.5px solid #e2dfd8;opacity:0.8;"


def pill_indicator(label: str, selected: bool, colour: str = "teal") -> None:
    """Styled selection indicator rendered above the Streamlit button."""
    if colour == "red":       bg = RED_SEL
    elif colour == "darkred": bg = DARKRED_SEL
    else:                     bg = TEAL_SEL if selected else BASE_BTN
    icon = "✓  " if selected else ""
    col = "#fff" if selected else "#666"
    st.markdown(
        f'<div style="{bg}border-radius:8px;padding:11px 14px;'
        f'font-family:DM Sans,sans-serif;font-size:14px;line-height:1.3;color:{col};'
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
    col  = "#fff" if selected else "#1a1a1a"
    icon = "✓  " if selected else ""
    sub_col = "rgba(255,255,255,0.7)" if selected else "#999"
    sub  = f'<span style="font-size:12px;color:{sub_col};display:block;margin-top:3px;">{sublabel}</span>' if sublabel else ""
    st.markdown(
        f'<div style="{bg}border-radius:8px 8px 0 0;padding:12px 14px;color:{col};'
        f'font-size:14px;font-weight:500;line-height:1.35;margin-bottom:0;'
        f'min-height:62px;pointer-events:none;">'
        f'{icon}{label}{sub}</div>',
        unsafe_allow_html=True)


def section_label(text: str, anno: str = "") -> None:
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
    "2WW_URGENT_STT":    {"border":"#c0392b","badge_bg":"#fdf2f1","badge_col":"#c0392b","badge":"Straight to Test"},
    "2WW_URGENT":        {"border":"#e8c8c4","badge_bg":"#fdf2f1","badge_col":"#c0392b","badge":"Urgent 2WW"},
    "ROUTINE_REFERRAL":  {"border":"#f0d8a8","badge_bg":"#fffbeb","badge_col":"#92400e","badge":"Routine"},
    "INVESTIGATE_FIRST": {"border":"#bfdbfe","badge_bg":"#eff6ff","badge_col":"#1d4ed8","badge":"Order FIT"},
    "SAFETY_NET":        {"border":"#e2dfd8","badge_bg":"#f5f4f1","badge_col":"#666","badge":"Safety Net"},
    "WEIGHT_LOSS_CUP":   {"border":"#c4b5fd","badge_bg":"#f5f3ff","badge_col":"#7c3aed","badge":"Clinical Judgement"},
    "FALLBACK_ALERT":    {"border":"#e8c8c4","badge_bg":"#fdf2f1","badge_col":"#c0392b","badge":"Review Required"},
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
  padding:12px 32px;border-bottom:0.5px solid #e2dfd8;background:#fff;">
  <div style="display:flex;align-items:baseline;gap:12px;">
    <a href="https://obafunsho.github.io/hummingbird_landing" target="_blank" style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a1a;letter-spacing:.01em;text-decoration:none;cursor:pointer;" onmouseover="this.style.opacity='0.6'" onmouseout="this.style.opacity='1'">Hummingbird</a>
    <span style="font-size:11px;font-weight:400;color:#999;letter-spacing:.1em;text-transform:uppercase;">Colorectal Cancer · Lower GI</span>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#999;
      background:#f5f4f1;padding:4px 10px;border-radius:4px;border:0.5px solid #e2dfd8;">
      v3.0 · NICE NG12</span>
    <span style="font-size:12px;color:#555;">{name}</span>
    <a href="/?signout=1" target="_self" onclick="window.location.href='/?signout=1'"
      style="font-family:'JetBrains Mono',monospace;font-size:10px;
      color:#bbb;text-decoration:underline;text-underline-offset:3px;
      cursor:pointer;"
      onmouseover="this.style.color='#c0392b'"
      onmouseout="this.style.color='#bbb'">sign out</a>
  </div>
</div>""", unsafe_allow_html=True)

# Module switcher using st.switch_page
_sw_col1, _sw_col2, _sw_col3, _sw_col4, _sw_col5 = st.columns([5, 1, 1, 1, 1])
with _sw_col2:
    st.markdown('<div class="sw-active">', unsafe_allow_html=True)
    st.button("Colorectal", key="sw_col2", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with _sw_col3:
    if st.button("Upper GI", key="sw_ugi", use_container_width=True):
        st.switch_page("pages/upper_gi.py")
with _sw_col4:
    if st.button("Appendicitis Risk", key="sw_app", use_container_width=True):
        st.switch_page("pages/appendicitis.py")
with _sw_col5:
    if st.button("Surgical Risk", key="sw_surg", use_container_width=True):
        st.switch_page("pages/surgical_risk.py")
with _sw_col5:
    st.markdown('''<div style="height:4px;"></div>''', unsafe_allow_html=True)
    if st.button("Surgical Risk", key="sw_surg", use_container_width=True):
        st.switch_page("pages/surgical_risk.py")

# Handle signout via query param
if st.query_params.get("signout") == "1":
    st.query_params.clear()
    do_logout()

left_col, right_col = st.columns([3, 2], gap="small")

# ════════════════════════════════════════════════ LEFT PANEL ══════════════════
with left_col:
    st.markdown('<div style="padding:8px 32px 80px;background:#f5f4f1;">', unsafe_allow_html=True)

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
      background:#f5f4f1;border:0.5px solid #d4d2cc;
      border-radius:4px;padding:4px 10px;
      font-size:11px;color:#666;letter-spacing:.05em;margin-bottom:10px;">
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
          background:#fdf2f1;border:0.5px solid #e8c8c4;
          font-size:13px;color:#c0392b;line-height:1.5;">
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
    st.markdown("""<p style="font-size:12px;color:#999;margin-top:8px;
      line-height:1.6;padding-left:2px;">
      <strong style="color:#555;">PS 0–1:</strong> Fully active — eligible for Straight to Test.&nbsp;&nbsp;
      <strong style="color:#555;">PS 2–4:</strong> Significant limitations — standard 2WW only.</p>""",
      unsafe_allow_html=True)

    # OPTIONAL
    st.markdown("""<div style="display:flex;align-items:center;gap:10px;margin:24px 0 16px;">
      <span style="flex:1;height:0.5px;background:#e2dfd8;"></span>
      <span style="font-size:10px;font-weight:600;
        color:#bbb;letter-spacing:.12em;text-transform:uppercase;
        white-space:nowrap;">additional detail — optional</span>
      <span style="flex:1;height:0.5px;background:#e2dfd8;"></span>
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
    st.markdown("<br>", unsafe_allow_html=True)

    # SUBMIT
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
          color:#bbb;margin-top:6px;">Select age to begin</p>""",
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
    st.markdown('</div></div>', unsafe_allow_html=True)

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
        st.markdown('<div style="background:#f5f4f1;padding:0 24px 60px;border-left:0.5px solid #e2dfd8;">', unsafe_allow_html=True)
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
    st.markdown('<div style="background:#f5f4f1;padding:0 24px 60px;border-left:0.5px solid #e2dfd8;">', unsafe_allow_html=True)

    if not st.session_state.result:
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
        result     = st.session_state.result
        escalation = st.session_state.escalation
        hbid       = st.session_state.hbid
        inputs     = st.session_state.last_inputs

        tier                  = result.get("tier","SAFETY_NET")
        tier_label            = result.get("tier_label",tier)
        rationale             = result.get("rationale","")
        safety_netting        = result.get("safety_netting") or ""
        stt_ineligible_reason = result.get("stt_ineligible_reason") or ""
        layer                 = result.get("layer","2")
        confidence            = result.get("confidence","")
        drivers               = result.get("inputs_driving_decision",[])
        prompt_version        = result.get("prompt_version","")
        model_version         = result.get("model_version","")
        style = TIER_STYLES.get(tier, TIER_STYLES["SAFETY_NET"])

        st.markdown(f'<div style="font-size:10px;color:#bbb;letter-spacing:.08em;text-align:right;margin-bottom:12px;">{hbid}</div>', unsafe_allow_html=True)

        if escalation and escalation.override_flags:
            for flag in escalation.override_flags:
                if "HIGHEST RISK" in flag:
                    st.markdown(f'<div style="padding:12px 15px;border-radius:8px;background:#fdf2f1;border:0.5px solid #e8c8c4;border-left:3px solid #c0392b;font-size:13px;font-weight:600;color:#c0392b;line-height:1.5;margin-bottom:14px;">⚠ {flag}</div>', unsafe_allow_html=True)

        lc = "background:#fdf2f1;border:0.5px solid #e8c8c4;color:#c0392b" if layer=="1" else "background:#f5f4f1;border:0.5px solid #d4d2cc;color:#555"
        lt = f"Layer {layer} — {'NICE NG12 hard rule' if layer=='1' else 'AI reasoning'}"
        dts = "".join(f'<span style="font-size:11px;padding:3px 9px;border-radius:5px;background:#f5f4f1;border:0.5px solid #d4d2cc;color:#555;display:inline-block;margin:2px;">{d}</span>' for d in drivers)

        # Special tiers — Rule 1.4 and Fallback
        if tier == "WEIGHT_LOSS_CUP":
            sn = safety_netting or ""
            st.markdown(f"""
            <div style="border-radius:10px;border:0.5px solid #c4b5fd;background:#fff;overflow:hidden;margin-bottom:14px;">
              <div style="padding:16px 18px;border-bottom:0.5px solid #e9e4fc;">
                <div style="font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#999;margin-bottom:5px;">Rule 1.4 · Weight loss sole feature</div>
                <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a1a;">Clinical Judgement Required</div>
              </div>
              <div style="padding:16px 18px;">
                <p style="font-size:14px;color:#444;line-height:1.7;margin-bottom:14px;">{rationale}</p>
                <div style="padding:12px 14px;border-radius:8px;background:#f5f4f1;border:0.5px solid #d4d2cc;font-size:13px;color:#555;line-height:1.6;border-left:3px solid #a78bfa;">⚑ {sn}</div>
              </div>
            </div>""", unsafe_allow_html=True)

        elif tier == "FALLBACK_ALERT":
            st.markdown(f"""
            <div style="border-radius:10px;border:0.5px solid #e8c8c4;background:#fff;overflow:hidden;margin-bottom:14px;">
              <div style="padding:16px 18px;border-bottom:0.5px solid #fde8e8;">
                <div style="font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#999;margin-bottom:5px;">System alert · AI output invalid</div>
                <div style="font-family:'DM Serif Display',serif;font-size:22px;color:#c0392b;">Clinical Review Required</div>
              </div>
              <div style="padding:16px 18px;">
                <p style="font-size:14px;color:#c0392b;line-height:1.7;">{rationale}</p>
              </div>
            </div>""", unsafe_allow_html=True)

        else:
            # Standard tier card
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
                cc = {"high":"rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);color:#86efac",
                      "moderate":"rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.25);color:#fbbf24",
                      "uncertain":"rgba(192,57,43,.08);border:1px solid rgba(192,57,43,.25);color:#f87171"}.get(confidence,"rgba(217,119,6,.08);border:1px solid rgba(217,119,6,.25);color:#fbbf24")
                ci = {"high":"●","moderate":"◑","uncertain":"○"}.get(confidence,"◑")
                st.markdown(f'<span style="font-family:JetBrains Mono,monospace;font-size:10px;padding:3px 9px;border-radius:4px;display:inline-flex;align-items:center;gap:5px;margin-top:8px;background:{cc};">{ci} Confidence: {confidence}</span>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

        # Escalation score — only shown for 2WW referral tiers
        show_escalation = tier in ("2WW_URGENT_STT", "2WW_URGENT")
        if escalation and show_escalation:
            pct = min((escalation.score/15)*100,100)
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
              <div style="font-size:11px;color:#bbb;margin-top:5px;">Score {escalation.score} / 15</div>
              <div style="font-size:12px;color:#aaa;margin-top:10px;line-height:1.6;">Literature-derived escalation support. Not a prospectively validated risk model. Score determines speed of referral, not whether to refer.</div>
              {'<div style="font-size:12px;color:#666;margin-top:6px;padding:6px 10px;border-radius:6px;background:#f5f4f1;border:0.5px solid #d4d2cc;">ℹ FIT negative — escalation constrained to STANDARD regardless of other factors.</div>' if escalation.fit_negative_override else ''}
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
            st.markdown(f'<a href="{mailto}" style="text-decoration:none;display:block;margin-top:4px;"><button style="width:100%;padding:9px;border-radius:6px;border:0.5px solid #d4d2cc;background:#fafaf8;color:#666;font-family:DM Sans,sans-serif;font-size:13px;font-weight:400;cursor:pointer;">✉ Email summary</button></a>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        try:
            qr_bytes = generate_qr_bytes(tier)
            qc,ql = st.columns([1,2])
            with qc: st.image(qr_bytes,width=90)
            with ql: st.markdown('<p style="font-size:12px;color:#bbb;line-height:1.6;padding-top:6px;">Patient information QR<br>Scan with phone</p>', unsafe_allow_html=True)
        except Exception: pass

        now_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
        st.markdown(f"""
        <div style="font-size:11px;color:#bbb;line-height:1.7;
          border-top:0.5px solid #e2dfd8;padding-top:12px;margin-top:10px;">
          Hummingbird v3.0 · Clinician-authored · NICE NG12 compliant · Not prospectively validated ·
          Does not replace clinical judgement · MHRA registration in progress ·<br>
          <span style="font-size:10px;color:#bbb;">
          prompt:{prompt_version} · model:{model_version} · layer:{layer} · {now_str}
          </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

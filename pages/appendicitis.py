"""
hummingbird/pages/appendicitis.py — Appendicitis Risk Score v2.0
Renders Aneel's standalone HTML tool via st.components.v1.html
Auth inherited from app.py via st.navigation()
"""
import sys
from pathlib import Path
import streamlit as st
from auth import do_logout

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

name = st.session_state.get("name", "")

# ── Minimal CSS override — hide Streamlit chrome ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
.stApp { background:#f5f4f1 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
div[data-testid="stHorizontalBlock"] button:disabled {
  background: #1a1a1a !important;
  border: 0.5px solid #1a1a1a !important;
  color: #fff !important;
  font-weight: 500 !important;
  opacity: 1 !important;
  cursor: default !important;
}
</style>
""", unsafe_allow_html=True)

# ── Topbar ─────────────────────────────────────────────────────────────────────
import streamlit.components.v1 as components

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:10px 32px;border-bottom:0.5px solid #e2dfd8;background:#fff;
  position:sticky;top:0;z-index:999;">
  <div style="display:flex;align-items:baseline;gap:12px;">
    <a href="https://obafunsho.github.io/hummingbird_landing" target="_blank"
      style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a1a;
      letter-spacing:.01em;text-decoration:none;"
      onmouseover="this.style.opacity='0.6'" onmouseout="this.style.opacity='1'">Hummingbird</a>
    <span style="font-size:11px;color:#999;letter-spacing:.1em;text-transform:uppercase;">
      Surgical Decisions · Appendicitis Risk</span>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <span style="font-size:12px;color:#555;">{name}</span>
    <a href="/?signout=1" target="_self"
      style="font-size:10px;color:#bbb;text-decoration:underline;cursor:pointer;"
      onmouseover="this.style.color='#c0392b'"
      onmouseout="this.style.color='#bbb'">sign out</a>
  </div>
</div>""", unsafe_allow_html=True)

if st.query_params.get("signout") == "1":
    st.query_params.clear()
    do_logout()

# ── Module switcher ───────────────────────────────────────────────────────────
from pages._nav import render_more_popover
_sw_col1, _sw_col2, _sw_col3, _sw_col4, _sw_col5 = st.columns([5, 1, 1, 1, 1])
with _sw_col2:
    if st.button("Colorectal", key="sw_col_a", use_container_width=True):
        st.switch_page("pages/colorectal.py")
with _sw_col3:
    if st.button("Upper GI", key="sw_ugi_a", use_container_width=True):
        st.switch_page("pages/upper_gi.py")
with _sw_col4:
    st.button("Appendicitis Risk", key="sw_app_cur", use_container_width=True, disabled=True)
render_more_popover("appendicitis", _sw_col5)

# ── Render HTML tool ──────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hummingbird — Appendicitis Risk Pathway</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:       #f5f4f1;
    --card:     #ffffff;
    --border:   #e2dfd8;
    --border2:  #d4d2cc;
    --text:     #1a1a1a;
    --muted:    #666666;
    --dim:      #999999;
    --danger:   #c0392b;
    --amber:    #d97706;
    --low-bg:   #f0fdf4;
    --low-tx:   #15803d;
    --low-bd:   #86efac;
    --med-bg:   #fffbeb;
    --med-tx:   #92400e;
    --med-bd:   #fde68a;
    --high-bg:  #fdf2f1;
    --high-tx:  #c0392b;
    --high-bd:  #e8c8c4;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-weight: 300;
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
    padding: 28px 16px 60px;
  }

  .wrap { max-width: 720px; margin: 0 auto; }

  /* ── HEADER ── */
  .page-header { margin-bottom: 24px; padding-bottom: 18px; border-bottom: 0.5px solid var(--border); }
  .page-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    font-weight: 400;
    color: var(--text);
    letter-spacing: -0.01em;
    margin-bottom: 5px;
  }
  .page-header p {
    font-size: 13px;
    color: var(--dim);
    font-weight: 300;
  }

  /* ── SECTION LABEL ── */
  .section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-title::after {
    content: '';
    flex: 1;
    height: 0.5px;
    background: var(--border);
    display: block;
  }

  /* ── CARD ── */
  .card {
    background: var(--card);
    border-radius: 10px;
    border: 0.5px solid var(--border);
    padding: 22px 24px;
    margin-bottom: 14px;
  }

  /* ── GRID ── */
  .grid   { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }

  /* ── FIELDS ── */
  .field { display: flex; flex-direction: column; gap: 5px; }
  .field label {
    font-size: 11px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.02em;
  }
  .field select,
  .field input[type=number] {
    width: 100%;
    padding: 9px 12px;
    font-size: 13px;
    font-family: 'DM Sans', sans-serif;
    border: 0.5px solid var(--border2);
    border-radius: 7px;
    background: #fafaf8;
    color: var(--text);
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23aaa' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 28px;
    transition: border-color 0.12s;
  }
  .field input[type=number] { background-image: none; padding-right: 12px; }
  .field select:focus,
  .field input[type=number]:focus { outline: none; border-color: var(--text); background: #fff; }

  /* ── ROUTE / WARN BOXES ── */
  .route {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 7px;
    background: var(--bg);
    border: 0.5px solid var(--border2);
    font-size: 12px;
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.04em;
  }
  .warn {
    margin-top: 8px;
    padding: 10px 14px;
    border-radius: 7px;
    background: var(--med-bg);
    border: 0.5px solid var(--med-bd);
    border-left: 3px solid var(--amber);
    font-size: 12px;
    color: var(--med-tx);
    line-height: 1.55;
  }
  .hidden { display: none; }

  /* ── TOGGLE BUTTONS ── */
  .row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 0.5px solid var(--bg);
    gap: 12px;
  }
  .row:last-of-type { border-bottom: none; }
  .row-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
    flex: 1;
  }
  .row-sub {
    font-size: 11px;
    color: var(--dim);
    margin-top: 2px;
    font-weight: 300;
  }
  .toggle {
    display: flex;
    gap: 5px;
    flex-shrink: 0;
  }
  .toggle button {
    padding: 6px 14px;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 400;
    border: 0.5px solid var(--border2);
    border-radius: 6px;
    background: #fafaf8;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.1s;
    white-space: nowrap;
  }
  .toggle button:hover { border-color: var(--text); color: var(--text); }
  .toggle button.active { background: var(--text); color: #fff; border-color: var(--text); font-weight: 500; }

  /* ── CALCULATE BUTTON ── */
  .calculate {
    width: 100%;
    padding: 13px;
    font-size: 14px;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    border: none;
    border-radius: 8px;
    background: var(--text);
    color: #fff;
    cursor: pointer;
    transition: background 0.15s;
    letter-spacing: 0.01em;
  }
  .calculate:hover { background: #333; }

  /* ── RESULT CARD ── */
  .result-score {
    font-family: 'DM Serif Display', serif;
    font-size: 52px;
    line-height: 1;
    color: var(--text);
    margin: 8px 0 10px;
    letter-spacing: -0.02em;
  }
  .result-score span { font-size: 20px; color: var(--dim); letter-spacing: 0; }

  .pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .pill.low  { background: var(--low-bg);  color: var(--low-tx);  border: 0.5px solid var(--low-bd); }
  .pill.medium { background: var(--med-bg); color: var(--med-tx); border: 0.5px solid var(--med-bd); }
  .pill.high { background: var(--high-bg); color: var(--high-tx); border: 0.5px solid var(--high-bd); }

  .cutoff-text {
    font-size: 12px;
    color: var(--dim);
    margin-bottom: 14px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.03em;
  }

  .pathway {
    padding: 14px 16px;
    border-radius: 8px;
    border-left: 3px solid var(--border2);
    background: var(--bg);
    margin-bottom: 14px;
    font-size: 13px;
    line-height: 1.65;
    color: var(--muted);
  }
  .pathway.low  { border-left-color: var(--low-tx);  background: var(--low-bg); color: #1a5c35; }
  .pathway.medium { border-left-color: var(--amber); background: var(--med-bg); color: var(--med-tx); }
  .pathway.high { border-left-color: var(--danger);  background: var(--high-bg); color: var(--high-tx); }

  .footer-note {
    font-size: 11px;
    color: var(--dim);
    line-height: 1.6;
    padding-top: 12px;
    border-top: 0.5px solid var(--border);
    margin-top: 4px;
  }

  .small {
    font-size: 11px;
    color: var(--dim);
    line-height: 1.55;
  }

  /* ── DISCLAIMER ── */
  .disclaimer {
    font-size: 11px;
    color: var(--dim);
    line-height: 1.7;
    padding: 14px 16px;
    background: var(--card);
    border-radius: 10px;
    border: 0.5px solid var(--border);
    margin-top: 14px;
  }
  .version-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #ccc;
    text-align: right;
    margin-top: 8px;
    letter-spacing: 0.06em;
  }

  @media (max-width: 540px) {
    .grid, .grid-3 { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="wrap">

  <div class="page-header">
    <h1>Appendicitis Risk Pathway</h1>
    <p>Automatic score selection · Adults: Adult Appendicitis Score (AAS) · Children 5–15: Shera score · RIFT Study validated</p>
  </div>

  <!-- Step 1: Patient -->
  <div class="card">
    <p class="section-title">Step 1 — Patient</p>
    <div class="grid">
      <div class="field">
        <label for="age">Age (years)</label>
        <input id="age" type="number" min="1" max="120" placeholder="e.g. 14, 28" />
      </div>
      <div class="field">
        <label for="sex">Sex</label>
        <select id="sex">
          <option value="">Select</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
        </select>
      </div>
    </div>
    <div id="routeBox" class="route hidden"></div>
    <div id="warnBox"  class="warn hidden"></div>
  </div>

  <!-- Adult inputs -->
  <div id="adultCard" class="card hidden">
    <p class="section-title">Step 2 — Adult inputs (AAS)</p>

    <div class="row">
      <div><div class="row-title">Pain in right iliac fossa</div></div>
      <div class="toggle" data-field="adult_rlq_pain">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div><div class="row-title">Pain migrated to right iliac fossa</div></div>
      <div class="toggle" data-field="adult_migration">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div><div class="row-title">Right iliac fossa tenderness</div></div>
      <div class="toggle" data-field="adult_tenderness">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="grid-3" style="margin-top:16px;">
      <div class="field">
        <label for="adult_guarding">Guarding</label>
        <select id="adult_guarding">
          <option value="">Select</option>
          <option value="0">None</option>
          <option value="1">Mild</option>
          <option value="2">Moderate or severe</option>
        </select>
      </div>
      <div class="field">
        <label for="adult_duration">Symptoms before bloods</label>
        <select id="adult_duration">
          <option value="">Select</option>
          <option value="lt24">Under 24 hours</option>
          <option value="gt24">24 hours or more</option>
        </select>
      </div>
      <div class="field">
        <label for="adult_wbc">WBC (×10⁹/L)</label>
        <input id="adult_wbc" type="number" step="0.1" min="0" placeholder="e.g. 12.4" />
      </div>
    </div>

    <div class="grid-3" style="margin-top:12px; align-items:end;">
      <div class="field">
        <label for="adult_neut_mode">Neutrophils entered as</label>
        <select id="adult_neut_mode">
          <option value="anc">Absolute count (×10⁹/L)</option>
          <option value="percent">Percentage (%)</option>
        </select>
      </div>
      <div class="field">
        <label for="adult_neut_val">Neutrophil value</label>
        <input id="adult_neut_val" type="number" step="0.1" min="0" placeholder="e.g. 9.1 or 78" />
      </div>
      <div class="field">
        <label for="adult_crp">CRP (mg/L)</label>
        <input id="adult_crp" type="number" step="1" min="0" placeholder="e.g. 34" />
      </div>
    </div>
  </div>

  <!-- Child inputs -->
  <div id="childCard" class="card hidden">
    <p class="section-title">Step 2 — Child inputs (Shera score)</p>

    <div class="row">
      <div><div class="row-title">Pain migrated to right iliac fossa</div></div>
      <div class="toggle" data-field="child_migration">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div><div class="row-title">Nausea or vomiting</div></div>
      <div class="toggle" data-field="child_nausea">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div><div class="row-title">Loss of appetite</div></div>
      <div class="toggle" data-field="child_anorexia">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div><div class="row-title">Right iliac fossa tenderness</div></div>
      <div class="toggle" data-field="child_tenderness">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="row">
      <div>
        <div class="row-title">Pain on cough, percussion, or hopping</div>
      </div>
      <div class="toggle" data-field="child_cph">
        <button type="button" data-value="1">Yes</button>
        <button type="button" data-value="0">No</button>
      </div>
    </div>

    <div class="grid-3" style="margin-top:16px;">
      <div class="field">
        <label for="child_temp">Temperature (°C)</label>
        <input id="child_temp" type="number" step="0.1" min="34" max="43" placeholder="e.g. 37.8" />
      </div>
      <div class="field">
        <label for="child_wbc">WBC (×10⁹/L)</label>
        <input id="child_wbc" type="number" step="0.1" min="0" placeholder="e.g. 12.2" />
      </div>
      <div class="field">
        <label for="child_neut_mode">Neutrophils entered as</label>
        <select id="child_neut_mode">
          <option value="anc">Absolute count (×10⁹/L)</option>
          <option value="percent">Percentage (%)</option>
        </select>
      </div>
    </div>

    <div class="grid" style="margin-top:12px;">
      <div class="field">
        <label for="child_neut_val">Neutrophil value</label>
        <input id="child_neut_val" type="number" step="0.1" min="0" placeholder="e.g. 8.5 or 78" />
      </div>
      <div class="field" style="justify-content:flex-end;">
        <div class="small" style="padding-bottom:4px;">If absolute count entered, the calculator converts to neutrophil % using the WBC above.</div>
      </div>
    </div>
  </div>

  <!-- Calculate -->
  <div class="card">
    <button id="calcBtn" class="calculate" type="button">Calculate score</button>
  </div>

  <!-- Result -->
  <div id="resultCard" class="card hidden">
    <p class="section-title">Result</p>
    <div id="scoreName" class="small" style="margin-bottom:4px;"></div>
    <div id="scoreValue" class="result-score"></div>
    <div id="riskPill" class="pill"></div>
    <div id="cutoffText" class="cutoff-text"></div>
    <div id="pathwayBox" class="pathway"></div>
    <div id="detailText" class="footer-note"></div>
  </div>

  <!-- Disclaimer -->
  <div class="disclaimer">
    Scores implemented per published algorithms: Adult Appendicitis Score (Sammalkorpi et al., BMC Gastroenterol 2014) and Shera score (paediatric RIFT cohort). Cut-off thresholds are those identified in the RIFT Study (BJS 2020; 107: 73–86). This tool is intended for <strong>research and teaching purposes only</strong>. It does not replace clinical assessment and has not been prospectively validated in this implementation. Patients with clinical concern for serious illness or systemic infection should be assessed and admitted regardless of score.
  </div>
  <p class="version-tag">Hummingbird · Appendicitis Risk · v2.0 · AAS + Shera · RIFT-validated cut-offs · Research &amp; teaching use only</p>

</div>

<script>
  const state = {};

  document.querySelectorAll('.toggle').forEach(group => {
    group.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state[group.dataset.field] = btn.dataset.value;
    });
  });

  document.getElementById('age').addEventListener('input', updateRoute);
  document.getElementById('sex').addEventListener('change', updateRoute);
  document.getElementById('calcBtn').addEventListener('click', calculate);

  function updateRoute() {
    const age = num('age');
    const sex = document.getElementById('sex').value;
    const routeBox  = document.getElementById('routeBox');
    const warnBox   = document.getElementById('warnBox');
    const adultCard = document.getElementById('adultCard');
    const childCard = document.getElementById('childCard');
    routeBox.classList.add('hidden');
    warnBox.classList.add('hidden');
    adultCard.classList.add('hidden');
    childCard.classList.add('hidden');
    document.getElementById('resultCard').classList.add('hidden');

    if (!age || !sex) return;

    if (age < 5) {
      routeBox.textContent = 'Under 5 years — no validated score is built into this tool.';
      routeBox.classList.remove('hidden');
      warnBox.textContent = 'Use clinical assessment, senior review, and imaging as needed. This calculator does not score children under 5.';
      warnBox.classList.remove('hidden');
      return;
    }

    if (age <= 15) {
      routeBox.textContent = 'Routing to: Shera score (children aged 5–15, paediatric RIFT)';
      routeBox.classList.remove('hidden');
      childCard.classList.remove('hidden');
      return;
    }

    routeBox.textContent = 'Routing to: Adult Appendicitis Score (AAS)';
    routeBox.classList.remove('hidden');
    adultCard.classList.remove('hidden');

    if (age > 45) {
      warnBox.textContent = 'Age over 45: AAS was validated in adults aged 16–45. Use as an adjunct only — maintain a low threshold for imaging and senior review.';
      warnBox.classList.remove('hidden');
    }
  }

  function num(id) {
    const v = document.getElementById(id).value;
    return v === '' ? null : Number(v);
  }

  function yn(key) {
    if (!(key in state)) return null;
    return Number(state[key]);
  }

  function neutPercent(modeId, valueId, wbcId) {
    const mode = document.getElementById(modeId).value;
    const val  = num(valueId);
    const wbc  = num(wbcId);
    if (val === null) return null;
    if (mode === 'percent') return val;
    if (!wbc || wbc <= 0) return null;
    return (val / wbc) * 100;
  }

  function sheraLowThreshold(age, sex) {
    if (age >= 5  && age <= 10) return 3;
    if (age >= 11 && age <= 15 && sex === 'female') return 3;
    if (age >= 11 && age <= 15 && sex === 'male')   return 2;
    return null;
  }

  function calculateAdultAAS(age, sex) {
    const rlqPain   = yn('adult_rlq_pain');
    const migration = yn('adult_migration');
    const tenderness= yn('adult_tenderness');
    const guarding  = document.getElementById('adult_guarding').value;
    const duration  = document.getElementById('adult_duration').value;
    const wbc       = num('adult_wbc');
    const crp       = num('adult_crp');
    const neutPct   = neutPercent('adult_neut_mode', 'adult_neut_val', 'adult_wbc');

    const required = [rlqPain, migration, tenderness, guarding, duration, wbc, crp, neutPct];
    if (required.some(v => v === null || v === ''))
      throw new Error('Please complete all adult input fields.');

    let score = 0;

    if (rlqPain === 1)   score += 2;
    if (migration === 1) score += 2;
    if (tenderness === 1) {
      score += (sex === 'female' && age >= 16 && age <= 49) ? 1 : 3;
    }
    if (guarding === '1') score += 2;
    if (guarding === '2') score += 4;

    if      (wbc >= 7.2  && wbc < 10.9) score += 1;
    else if (wbc >= 10.9 && wbc < 14.0) score += 2;
    else if (wbc >= 14.0)               score += 3;

    if      (neutPct >= 62 && neutPct < 75) score += 2;
    else if (neutPct >= 75 && neutPct < 83) score += 3;
    else if (neutPct >= 83)                 score += 4;

    if (duration === 'lt24') {
      if      (crp >= 4   && crp < 11)  score += 2;
      else if (crp >= 11  && crp < 25)  score += 3;
      else if (crp >= 25  && crp < 83)  score += 5;
      else if (crp >= 83)               score += 1;
    } else {
      if      (crp >= 12  && crp < 53)  score += 2;
      else if (crp >= 53  && crp < 152) score += 2;
      else if (crp >= 152)              score += 1;
    }

    const maxScore = (sex === 'female' && age >= 16 && age <= 49) ? 21 : 23;
    let risk, cutoff, pathway;

    if (score <= 10) {
      risk    = 'low';
      cutoff  = `Score ${score} / ${maxScore} — low probability (AAS ≤10)`;
      pathway = 'Low-risk pathway: consider discharge with safety-net advice. If clinical concern persists, ambulatory CT or observation is appropriate before any operative decision.';
    } else if (score >= 16) {
      risk    = 'high';
      cutoff  = `Score ${score} / ${maxScore} — high probability (AAS ≥16)`;
      pathway = 'High-risk pathway: admit and arrange CT. Early senior surgical review. Imaging should usually precede operative decision unless clinical picture is unequivocal.';
    } else {
      risk    = 'medium';
      cutoff  = `Score ${score} / ${maxScore} — intermediate probability (AAS 11–15)`;
      pathway = 'Intermediate-risk pathway: admit and arrange CT. Senior surgical review, serial clinical assessment, and repeat bloods are appropriate.';
    }

    const detail = `Neutrophil % used in scoring: ${neutPct.toFixed(1)}% (entered as ${document.getElementById('adult_neut_mode').value === 'anc' ? 'absolute count — converted using WBC' : 'direct percentage'}).`;
    return { scoreName: 'Adult Appendicitis Score (AAS)', score, max: maxScore, risk, cutoff, pathway, detail };
  }

  function calculateShera(age, sex) {
    const migration  = yn('child_migration');
    const nausea     = yn('child_nausea');
    const anorexia   = yn('child_anorexia');
    const tenderness = yn('child_tenderness');
    const cph        = yn('child_cph');
    const temp       = num('child_temp');
    const wbc        = num('child_wbc');
    const neutPct    = neutPercent('child_neut_mode', 'child_neut_val', 'child_wbc');

    const required = [migration, nausea, anorexia, tenderness, cph, temp, wbc, neutPct];
    if (required.some(v => v === null || v === ''))
      throw new Error('Please complete all child input fields.');

    let score = 0;
    if (migration === 1)  score += 1;
    if (nausea === 1)     score += 1;
    if (anorexia === 1)   score += 1;
    if (tenderness === 1) score += 2;
    if (temp >= 37.3)     score += 1;
    if (cph === 1)        score += 2;
    if (wbc >= 10)        score += 1;
    if (neutPct >= 75)    score += 1;

    const lowCut = sheraLowThreshold(age, sex);
    let risk, cutoff, pathway;

    if (score <= lowCut) {
      risk    = 'low';
      cutoff  = `Score ${score} / 10 — below validated low-risk cut-off of ≤${lowCut} for ${age}-year-old ${sex}`;
      pathway = 'Low-risk pathway: consider discharge with clear safety-net advice. Outpatient ultrasound may be arranged if any clinical concern remains. This does not exclude admission if the child appears systemically unwell.';
    } else if (score >= 7) {
      risk    = 'high';
      cutoff  = `Score ${score} / 10 — above low-risk cut-off of ≤${lowCut}`;
      pathway = 'High-risk pathway: admit and arrange ultrasound. MRI or low-dose CT if ultrasound is equivocal or the child remains clinically concerning. Shera is not validated to direct children to theatre without imaging.';
    } else {
      risk    = 'medium';
      cutoff  = `Score ${score} / 10 — above low-risk cut-off of ≤${lowCut}`;
      pathway = 'Intermediate-risk pathway: admit for observation. Ultrasound imaging is recommended. If ultrasound is inconclusive, MRI (preferred in children) or low-dose CT as per local policy.';
    }

    const detail = `Neutrophil % used in scoring: ${neutPct.toFixed(1)}% (entered as ${document.getElementById('child_neut_mode').value === 'anc' ? 'absolute count — converted using WBC' : 'direct percentage'}).`;
    return { scoreName: 'Shera Score (Paediatric RIFT)', score, max: 10, risk, cutoff, pathway, detail };
  }

  function calculate() {
    try {
      const age = num('age');
      const sex = document.getElementById('sex').value;
      if (!age || !sex) throw new Error('Please enter age and sex first.');
      if (age < 5) throw new Error('This tool does not score children under 5 years.');

      let result;
      if (age <= 15) result = calculateShera(age, sex);
      else           result = calculateAdultAAS(age, sex);

      render(result, age, sex);
    } catch (err) {
      alert(err.message);
    }
  }

  function render(result, age, sex) {
    document.getElementById('resultCard').classList.remove('hidden');
    document.getElementById('scoreName').textContent  = result.scoreName;
    document.getElementById('scoreValue').innerHTML   = `${result.score} <span>/ ${result.max}</span>`;

    const riskPill = document.getElementById('riskPill');
    riskPill.className   = `pill ${result.risk}`;
    riskPill.textContent = result.risk === 'low' ? 'Low risk' : result.risk === 'medium' ? 'Intermediate risk' : 'High risk';

    document.getElementById('cutoffText').textContent = result.cutoff;

    const pathwayBox = document.getElementById('pathwayBox');
    pathwayBox.className   = `pathway ${result.risk}`;
    pathwayBox.textContent = result.pathway;

    let note = result.detail;
    if (age > 45) note += ' In adults over 45, treat this result as an adjunct rather than a stand-alone decision rule.';
    if (age <= 15 && result.risk !== 'low') note += ' In children, Shera supports discharge only in the validated low-risk group — medium and high-risk groups require imaging rather than score-led surgery.';
    document.getElementById('detailText').textContent = note;

    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
</script>
</body>
</html>
"""

components.html(HTML, height=1900, scrolling=True)

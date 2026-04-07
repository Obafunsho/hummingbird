"""
hummingbird/pages/appendicitis.py — Appendicitis Risk Score
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

# ── Minimal CSS override — hide Streamlit chrome, keep tool's own styling ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
.stApp { background:#f5f4f1 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }

/* Module switcher active state */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
  font-size:12px !important;
}
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

/* Switcher: active button styled black via disabled */
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
      style="font-size:10px;color:#bbb;
      text-decoration:underline;cursor:pointer;"
      onmouseover="this.style.color='#c0392b'"
      onmouseout="this.style.color='#bbb'">sign out</a>
  </div>
</div>""", unsafe_allow_html=True)

if st.query_params.get("signout") == "1":
    st.query_params.clear()
    do_logout()

# ── Module switcher ──────────────────────────────────────────────────────────
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

# ── Render HTML tool ───────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hummingbird Appendicitis Risk Score</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Georgia', serif;
    font-size: 15px;
    line-height: 1.6;
    color: #1c1c1a;
    background: #f7f5f0;
    min-height: 100vh;
    padding: 2rem 1rem 4rem;
  }

  .container { max-width: 680px; margin: 0 auto; }

  .header { margin-bottom: 2rem; padding-bottom: 1.25rem; border-bottom: 1px solid #e2dfd8; }
  .header h1 { font-family: 'DM Serif Display', serif; font-size: 22px; font-weight: 400; letter-spacing: -0.01em; color: #1c1c1a; margin-bottom: 3px; }
  .header p { font-size: 13px; color: #888; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

  .step-label {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #aaa;
    margin-bottom: 10px;
  }

  .card {
    background: #fff;
    border-radius: 10px;
    border: 0.5px solid #e2dfd8;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  /* Patient basics */
  .basics-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .field { display: flex; flex-direction: column; gap: 5px; }
  .field label {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 12px; color: #666; font-weight: 500;
  }
  .field select, .field input[type=number] {
    width: 100%; padding: 8px 10px; font-size: 14px;
    border: 0.5px solid #d8d5ce; border-radius: 6px;
    background: #faf9f7; color: #1c1c1a;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23aaa' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 10px center; padding-right: 28px;
  }
  .field input[type=number] { background-image: none; padding-right: 10px; }
  .field select:focus, .field input[type=number]:focus { outline: none; border-color: #a8a49e; background: #fff; }

  /* Score items */
  .score-section-title {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; color: #bbb; margin: 1.25rem 0 0.75rem;
  }
  .score-section-title:first-of-type { margin-top: 0; }

  .item-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 9px 0; border-bottom: 0.5px solid #f0ede8;
    gap: 12px;
  }
  .item-row:last-child { border-bottom: none; padding-bottom: 0; }

  .item-label {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px; color: #333; flex: 1;
  }
  .item-label small {
    display: block; font-size: 11px; color: #aaa; margin-top: 1px;
  }

  .item-controls { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }

  .opt-btn {
    padding: 5px 12px; font-size: 12px;
    border: 0.5px solid #d8d5ce; border-radius: 5px;
    background: #faf9f7; color: #666; cursor: pointer;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    transition: all 0.1s; white-space: nowrap;
  }
  .opt-btn:hover { border-color: #a8a49e; color: #333; }
  .opt-btn.selected { background: #1c1c1a; color: #fff; border-color: #1c1c1a; }

  .pts-badge {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; color: #bbb; min-width: 36px; text-align: right;
  }

  /* WBC / CRP selects inline */
  .inline-select {
    padding: 5px 28px 5px 8px; font-size: 13px;
    border: 0.5px solid #d8d5ce; border-radius: 5px;
    background: #faf9f7; color: #1c1c1a;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    appearance: none; -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%23aaa' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 8px center;
    cursor: pointer;
  }
  .inline-select:focus { outline: none; border-color: #a8a49e; }

  /* Calculate button */
  .calc-btn {
    width: 100%; padding: 13px; font-size: 15px;
    font-family: 'Georgia', serif;
    border: none; border-radius: 8px;
    background: #1c1c1a; color: #f7f5f0;
    cursor: pointer; transition: background 0.15s;
    letter-spacing: 0.01em; margin-top: 0.25rem;
  }
  .calc-btn:hover { background: #333; }
  .calc-btn:active { background: #000; }

  /* Results */
  .results-card { background: #fff; border-radius: 10px; border: 0.5px solid #e2dfd8; padding: 1.5rem; margin-bottom: 1rem; display: none; }

  .primary-result { margin-bottom: 1.5rem; }
  .primary-result .score-name {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #aaa; margin-bottom: 8px;
  }
  .primary-result .score-number {
    font-size: 52px; font-weight: normal; letter-spacing: -0.03em;
    line-height: 1; color: #1c1c1a; margin-bottom: 6px;
  }
  .primary-result .score-number span {
    font-size: 20px; color: #aaa; letter-spacing: 0;
  }

  .risk-pill {
    display: inline-block; padding: 5px 14px; border-radius: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px; font-weight: 500; margin-bottom: 12px;
  }
  .risk-low    { background: #e8f5ee; color: #1a6b3c; }
  .risk-medium { background: #fef3e2; color: #8a5a00; }
  .risk-high   { background: #fdecea; color: #8b1f1f; }

  .cutoff-note {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 12px; color: #999; margin-bottom: 1.25rem;
  }

  .action-box {
    padding: 1rem 1.1rem;
    border-radius: 8px;
    border-left: 3px solid #ccc;
    background: #f7f5f0;
    margin-bottom: 1.25rem;
  }
  .action-box.action-low   { border-left-color: #3aaa6a; background: #f2fbf5; }
  .action-box.action-med   { border-left-color: #e8a020; background: #fffaf0; }
  .action-box.action-high  { border-left-color: #d94040; background: #fff5f5; }
  .action-box p {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px; color: #444; line-height: 1.65;
  }

  .divider-thin { height: 0.5px; background: #eeebe5; margin: 1.25rem 0; }

  .secondary-result { }
  .secondary-result .sec-label {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #ccc; margin-bottom: 8px;
  }
  .alvarado-row {
    display: flex; align-items: baseline; gap: 10px;
  }
  .alvarado-score {
    font-size: 28px; color: #999; letter-spacing: -0.02em;
  }
  .alvarado-interp {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px; color: #aaa;
  }

  .disclaimer {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; color: #aaa; line-height: 1.6;
    padding: 1rem 1.25rem; background: #fff;
    border-radius: 10px; border: 0.5px solid #e2dfd8;
    margin-bottom: 0.75rem;
  }

  .version-tag {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11px; color: #ccc; text-align: right;
  }

  .hidden { display: none; }

  /* Score items shown/hidden by routing */
  .aas-only, .airs-only, .shera-only { display: none; }

  @media (max-width: 480px) {
    .basics-row { grid-template-columns: 1fr 1fr; }
    .item-row { flex-wrap: wrap; }
  }
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <h1>Hummingbird Appendicitis Risk Score</h1>
    <p>Age- and sex-stratified routing to validated scoring models · RIFT Study (adults) · Paediatric RIFT (children)</p>
  </div>

  <!-- Step 1: Patient basics -->
  <div class="card" id="card-basics">
    <p class="step-label">Step 1 — Patient</p>
    <div class="basics-row">
      <div class="field">
        <label>Age (years)</label>
        <input type="number" id="age" min="1" max="120" placeholder="e.g. 14, 28" oninput="onAgeOrSexChange()">
      </div>
      <div class="field">
        <label>Sex</label>
        <select id="sex" onchange="onAgeOrSexChange()">
          <option value="">Select</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
        </select>
      </div>

    </div>
  </div>

  <!-- Routing notice -->
  <div id="routing-notice" class="hidden" style="margin-bottom:1rem; padding: 0.75rem 1rem; background:#fff; border-radius:8px; border:0.5px solid #e2dfd8;">
    <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:13px; color:#555;" id="routing-text"></p>
  </div>

  <!-- Out of range notice -->
  <div id="oor-notice" class="hidden" style="margin-bottom:1rem; padding: 1rem 1.25rem; background:#fff8f0; border-radius:8px; border:0.5px solid #f0d8b8; border-left: 3px solid #e8a020;">
    <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:13px; color:#7a4f00; line-height:1.6;" id="oor-text"></p>
  </div>

  <!-- Step 2: Score items (shown once routing is determined) -->
  <div class="card hidden" id="card-score">
    <p class="step-label" id="score-card-label">Step 2 — Score items</p>

    <!-- SYMPTOMS (all scores) -->
    <p class="score-section-title">Symptoms</p>

    <div class="item-row" id="row-migration">
      <div class="item-label">Migration of pain to RIF<small>Pain that began elsewhere and moved to right iliac fossa</small></div>
      <div class="item-controls">
        <button class="opt-btn" data-group="migration" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="migration" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-migration">— pt</div>
    </div>

    <div class="item-row" id="row-anorexia">
      <div class="item-label">Anorexia / loss of appetite</div>
      <div class="item-controls">
        <button class="opt-btn" data-group="anorexia" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="anorexia" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-anorexia">— pt</div>
    </div>

    <div class="item-row" id="row-nausea">
      <div class="item-label">Nausea / vomiting</div>
      <div class="item-controls">
        <button class="opt-btn" data-group="nausea" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="nausea" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-nausea">— pt</div>
    </div>

    <!-- SIGNS (all scores) -->
    <p class="score-section-title">Examination findings</p>

    <div class="item-row" id="row-tenderness">
      <div class="item-label">RIF tenderness<small>Tenderness on palpation of the right iliac fossa</small></div>
      <div class="item-controls">
        <button class="opt-btn" data-group="tenderness" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="tenderness" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-tenderness">— pt</div>
    </div>

    <div class="item-row" id="row-rebound">
      <div class="item-label">Rebound / guarding<small>Rebound tenderness or muscular guarding</small></div>
      <div class="item-controls">
        <button class="opt-btn" data-group="rebound" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="rebound" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-rebound">— pt</div>
    </div>

    <div class="item-row aas-only" id="row-peritonism">
      <div class="item-label">Peritonism<small>Rigidity, severe guarding (AAS only)</small></div>
      <div class="item-controls">
        <button class="opt-btn" data-group="peritonism" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="peritonism" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-peritonism">— pt</div>
    </div>

    <!-- TEMPERATURE -->
    <p class="score-section-title">Observations</p>

    <div class="item-row" id="row-temp">
      <div class="item-label">Temperature<small>Elevated body temperature</small></div>
      <div class="item-controls">
        <select class="inline-select" id="sel-temp" onchange="selectFromDropdown('temp', this)">
          <option value="">Select</option>
          <option value="0">Normal (&lt;38.5°C)</option>
          <option value="1">38.5–38.9°C</option>
          <option value="2">≥39.0°C (AIRS) / ≥38.5°C (AAS)</option>
        </select>
      </div>
      <div class="pts-badge" id="pts-temp">— pt</div>
    </div>

    <!-- BLOODS -->
    <p class="score-section-title">Blood results</p>

    <div class="item-row" id="row-wbc">
      <div class="item-label">White cell count (×10⁹/L)</div>
      <div class="item-controls">
        <select class="inline-select" id="sel-wbc" onchange="selectFromDropdown('wbc', this)">
          <option value="">Select</option>
          <option value="0">&lt;10.0</option>
          <option value="1">10.0–14.9</option>
          <option value="2">≥15.0</option>
        </select>
      </div>
      <div class="pts-badge" id="pts-wbc">— pt</div>
    </div>

    <div class="item-row" id="row-pmnl">
      <div class="item-label">Polymorphonuclear (PMN) left shift<small>Proportion of neutrophils ≥75% (AIRS) or band cells present</small></div>
      <div class="item-controls">
        <button class="opt-btn" data-group="pmnl" data-val="0" onclick="selectOpt(this)">No</button>
        <button class="opt-btn" data-group="pmnl" data-val="1" onclick="selectOpt(this)">Yes</button>
      </div>
      <div class="pts-badge" id="pts-pmnl">— pt</div>
    </div>

    <div class="item-row airs-only aas-only" id="row-crp">
      <div class="item-label">C-reactive protein (mg/L)<small>AIRS and AAS only</small></div>
      <div class="item-controls">
        <select class="inline-select" id="sel-crp" onchange="selectFromDropdown('crp', this)">
          <option value="">Select</option>
          <option value="0">&lt;10</option>
          <option value="1">10–49</option>
          <option value="2">≥50</option>
        </select>
      </div>
      <div class="pts-badge" id="pts-crp">— pt</div>
    </div>

    <!-- Shera-specific items -->
    <div class="item-row shera-only" id="row-sex-shera">
      <div class="item-label">Sex (Shera score item)<small>Male sex scores 1 point in Shera</small></div>
      <div class="pts-badge" id="pts-sex-shera">— pt</div>
    </div>

    <button class="calc-btn" onclick="calculate()">Calculate score</button>
  </div>

  <!-- Results -->
  <div class="results-card" id="results">
    <p class="step-label">Result</p>

    <div class="primary-result">
      <div class="score-name" id="res-score-name">—</div>
      <div class="score-number" id="res-score-number">—</div>
      <div>
        <span class="risk-pill" id="res-risk-pill">—</span>
      </div>
      <div class="cutoff-note" id="res-cutoff-note"></div>
      <div class="action-box" id="res-action-box">
        <p id="res-action-text"></p>
      </div>
    </div>

    <div class="divider-thin"></div>

    <div class="secondary-result" id="res-alvarado-section">
      <div class="sec-label">Alvarado score (reference only)</div>
      <div class="alvarado-row">
        <div class="alvarado-score" id="res-alvarado-number">—</div>
        <div class="alvarado-interp" id="res-alvarado-interp"></div>
      </div>
      <p style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:11px; color:#bbb; margin-top:6px; line-height:1.5;">
        The Alvarado score is shown for familiarity only. The validated score above should guide clinical decision-making per RIFT Study evidence.
      </p>
    </div>
  </div>

  <div class="disclaimer">
    Scores are implemented per published algorithms: AAS (Sammalkorpi et al., BMC Gastroenterol 2014), AIRS (Andersson &amp; Andersson, World J Surg 2008), Shera score (paediatric RIFT), and Alvarado (Ann Emerg Med 1986). Cut-off thresholds are those identified in the RIFT Study (BJS 2020; 107: 73–86) and the paediatric RIFT cohort. This tool does not replace clinical assessment. Patients with clinical concern for serious illness or markers of systemic infection should be admitted regardless of score.
  </div>
  <p class="version-tag">Hummingbird · Appendicitis Risk · v1.0 · RIFT-validated cut-offs</p>

</div>

<script>
// ---- STATE ----
const vals = {};
let activeScore = null; // 'aas' | 'airs' | 'shera' | null

// ---- ROUTING ----
function onAgeOrSexChange() {
  const age = parseInt(document.getElementById('age').value);
  const sex = document.getElementById('sex').value;

  hideResults();
  document.getElementById('routing-notice').classList.add('hidden');
  document.getElementById('oor-notice').classList.add('hidden');
  document.getElementById('card-score').classList.add('hidden');

  if (!age || !sex) return;

  // Out of validated range
  if (age < 5) {
    showOOR('No validated appendicitis risk prediction model exists for children under 5 years. Clinical assessment and senior surgical review are recommended.');
    return;
  }
  if (age > 45) {
    showOOR('The RIFT Study validated scores in adults aged 16–45 years. For patients over 45, clinical assessment, CT imaging, and senior surgical review are recommended. Risk scoring tools are not validated in this age group.');
    return;
  }

  // Route
  if (age >= 5 && age <= 15) {
    activeScore = 'shera';
    showRoutingNotice(`Age ${age}, ${sex} — routing to <strong>Shera score</strong> (paediatric RIFT validated model). Cut-off: ≤${sheraThreshold(age, sex)} points = low risk.`);
  } else if (age >= 16 && sex === 'female') {
    activeScore = 'aas';
    showRoutingNotice(`Age ${age}, female — routing to <strong>Adult Appendicitis Score (AAS)</strong> (RIFT Study best-performing model for women). Cut-off: ≤8 points = low risk.`);
  } else if (age >= 16 && sex === 'male') {
    activeScore = 'airs';
    showRoutingNotice(`Age ${age}, male — routing to <strong>Appendicitis Inflammatory Response Score (AIRS)</strong> (RIFT Study best-performing model for men). Cut-off: ≤2 points = low risk.`);
  }

  buildScoreItems();
  document.getElementById('card-score').classList.remove('hidden');
}

function sheraThreshold(age, sex) {
  if (age >= 5 && age <= 10) return 3;
  if (age >= 11 && sex === 'female') return 3;
  if (age >= 11 && sex === 'male') return 2;
  return 3;
}

function showRoutingNotice(html) {
  document.getElementById('routing-text').innerHTML = html;
  document.getElementById('routing-notice').classList.remove('hidden');
}

function showOOR(msg) {
  document.getElementById('oor-text').textContent = msg;
  document.getElementById('oor-notice').classList.remove('hidden');
  activeScore = null;
}

// ---- SHOW/HIDE SCORE ROWS ----
function buildScoreItems() {
  // Reset all to hidden then show relevant
  document.querySelectorAll('.aas-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.airs-only').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.shera-only').forEach(el => el.style.display = 'none');

  // Update points badges to reflect current score's weighting
  updatePointsBadges();

  if (activeScore === 'aas') {
    document.querySelectorAll('.aas-only').forEach(el => el.style.display = 'flex');
    document.getElementById('score-card-label').textContent = 'Step 2 — Adult Appendicitis Score (AAS)';
  } else if (activeScore === 'airs') {
    document.querySelectorAll('.airs-only').forEach(el => el.style.display = 'flex');
    document.getElementById('score-card-label').textContent = 'Step 2 — Appendicitis Inflammatory Response Score (AIRS)';
  } else if (activeScore === 'shera') {
    document.querySelectorAll('.shera-only').forEach(el => el.style.display = 'flex');
    document.getElementById('score-card-label').textContent = 'Step 2 — Shera Score';
    // Show sex item auto-scored
    const age = parseInt(document.getElementById('age').value);
    const sex = document.getElementById('sex').value;
    const sheraSex = (sex === 'male') ? 1 : 0;
    vals['sex-shera'] = sheraSex;
    document.getElementById('pts-sex-shera').textContent = sheraSex + ' pt';
  }
}

// Points per item per score
const itemWeights = {
  aas: {
    migration: 1, anorexia: 1, nausea: 1,
    tenderness: 2, rebound: 1, peritonism: 3,
    temp: { '0':0, '1':1, '2':2 },
    wbc: { '0':0, '1':1, '2':2 },
    pmnl: 2,
    crp: { '0':0, '1':1, '2':2 }
  },
  airs: {
    migration: 0, anorexia: 1, nausea: 1,
    tenderness: 2, rebound: 1, peritonism: 0,
    temp: { '0':0, '1':1, '2':1 },
    wbc: { '0':0, '1':1, '2':2 },
    pmnl: 1,
    crp: { '0':0, '1':1, '2':2 }
  },
  shera: {
    migration: 1, anorexia: 1, nausea: 1,
    tenderness: 2, rebound: 1, peritonism: 0,
    temp: { '0':0, '1':1, '2':1 },
    wbc: { '0':0, '1':1, '2':2 },
    pmnl: 1,
    crp: { '0':0, '1':0, '2':0 } // Shera does not use CRP
  }
};

// Labels per temp tier per score
const tempLabels = {
  aas:   { '0':'Normal (<38.5°C)', '1':'38.5–38.9°C', '2':'≥39.0°C' },
  airs:  { '0':'Normal (<38.5°C)', '1':'38.5–38.9°C', '2':'≥39.0°C' },
  shera: { '0':'Normal (<38.5°C)', '1':'38.5–38.9°C', '2':'≥38.5°C' }
};

function updatePointsBadges() {
  if (!activeScore) return;
  const w = itemWeights[activeScore];
  const binary = ['migration','anorexia','nausea','tenderness','rebound','peritonism','pmnl'];
  binary.forEach(k => {
    const el = document.getElementById('pts-' + k);
    if (el) el.textContent = '0–' + w[k] + ' pt';
  });
  ['wbc','crp','temp'].forEach(k => {
    const el = document.getElementById('pts-' + k);
    const wts = w[k];
    const max = Math.max(...Object.values(wts));
    if (el) el.textContent = '0–' + max + ' pt';
  });
}

// ---- INPUT HANDLERS ----
function selectOpt(btn) {
  const group = btn.dataset.group;
  document.querySelectorAll(`[data-group="${group}"]`).forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  vals[group] = parseInt(btn.dataset.val);
  updateLivePts(group);
}

function selectFromDropdown(key, sel) {
  vals[key] = sel.value === '' ? null : sel.value;
  updateLivePts(key);
}

function updateLivePts(key) {
  if (!activeScore) return;
  const w = itemWeights[activeScore];
  const el = document.getElementById('pts-' + key);
  if (!el) return;
  const v = vals[key];
  if (v === null || v === undefined || v === '') { el.textContent = '— pt'; return; }
  let pts;
  if (typeof w[key] === 'object') pts = w[key][String(v)] ?? 0;
  else pts = v * w[key];
  el.textContent = pts + ' pt';
  el.style.color = pts > 0 ? '#1c1c1a' : '#bbb';
}

// ---- CALCULATE ----
function calculate() {
  if (!activeScore) { alert('Please select age and sex first.'); return; }
  const age = parseInt(document.getElementById('age').value);
  const sex = document.getElementById('sex').value;


  const w = itemWeights[activeScore];
  const required = {
    aas:   ['migration','anorexia','nausea','tenderness','rebound','peritonism','temp','wbc','pmnl','crp'],
    airs:  ['anorexia','nausea','tenderness','rebound','temp','wbc','pmnl','crp'],
    shera: ['migration','anorexia','nausea','tenderness','rebound','temp','wbc','pmnl']
  };
  const fields = required[activeScore];
  for (const f of fields) {
    const v = vals[f];
    if (v === null || v === undefined || v === '') {
      alert('Please complete all score items before calculating.'); return;
    }
  }

  // Primary score
  let score = 0;
  fields.forEach(f => {
    const v = vals[f];
    const wt = w[f];
    if (typeof wt === 'object') score += wt[String(v)] ?? 0;
    else score += parseInt(v) * wt;
  });
  // Shera: add sex item
  if (activeScore === 'shera') score += (vals['sex-shera'] || 0);

  // Alvarado (always calculate as reference)
  // Alvarado: migration(1) + anorexia(1) + nausea/vomiting(1) + RIF tenderness(2) + rebound(1) + elevated temp(1) + WBC>10k(2) + left shift(1) = 10
  const alv_temp = (vals['temp'] && vals['temp'] !== '0') ? 1 : 0;
  const alv_wbc  = (vals['wbc']  && vals['wbc']  !== '0') ? 2 : 0;
  const alvarado =
    (parseInt(vals['migration']||0) * 1) +
    (parseInt(vals['anorexia']||0)  * 1) +
    (parseInt(vals['nausea']||0)    * 1) +
    (parseInt(vals['tenderness']||0)* 2) +
    (parseInt(vals['rebound']||0)   * 1) +
    alv_temp + alv_wbc +
    (parseInt(vals['pmnl']||0)      * 1);

  // Risk thresholds
  let riskCategory, cutoffNote, actionClass, actionText;

  if (activeScore === 'aas') {
    // AAS: RIFT cut-off ≤8 = low risk
    if (score <= 8) {
      riskCategory = 'low';
      cutoffNote = `Score ${score} of 16 — below cut-off of ≤8 (RIFT Study, BJS 2020). Failure rate 3.7%, specificity 63.1%.`;
      actionText = 'Low risk of appendicitis. Consider discharge home with safety net advice and ambulatory review if symptoms persist or worsen. If clinical concern remains despite low score, proceed to CT (preferred) before any decision to operate. Ultrasound may be used first if gynaecological pathology is the principal differential.';
    } else if (score <= 12) {
      riskCategory = 'medium';
      cutoffNote = `Score ${score} of 16 — intermediate range.`;
      actionText = 'Intermediate risk. Admit for observation. CT imaging is recommended to clarify diagnosis before operative decision. Serial clinical assessment and repeat bloods are appropriate.';
    } else {
      riskCategory = 'high';
      cutoffNote = `Score ${score} of 16 — high range.`;
      actionText = 'High risk of appendicitis. Senior surgical review and CT imaging before operative decision. Consider early surgery if clinically indicated and CT confirms appendicitis.';
    }
  } else if (activeScore === 'airs') {
    // AIRS: RIFT cut-off ≤2 = low risk
    if (score <= 2) {
      riskCategory = 'low';
      cutoffNote = `Score ${score} of 12 — below cut-off of ≤2 (RIFT Study, BJS 2020). Failure rate 2.4%, specificity 24.7%.`;
      actionText = 'Low risk of appendicitis. Consider discharge with safety net advice. If clinical concern persists, CT imaging is preferred over ultrasound to confirm or exclude appendicitis before any operative decision.';
    } else if (score <= 8) {
      riskCategory = 'medium';
      cutoffNote = `Score ${score} of 12 — intermediate range (AIRS 3–8).`;
      actionText = 'Intermediate risk. Admit for observation. CT imaging is recommended. Serial clinical assessment and repeat bloods are appropriate pending imaging.';
    } else {
      riskCategory = 'high';
      cutoffNote = `Score ${score} of 12 — high range (AIRS ≥9).`;
      actionText = 'High risk of appendicitis. Senior surgical review. CT or direct operative decision as clinically indicated.';
    }
  } else if (activeScore === 'shera') {
    const threshold = sheraThreshold(age, sex);
    if (score <= threshold) {
      riskCategory = 'low';
      cutoffNote = `Score ${score} — below cut-off of ≤${threshold} for ${age}-year-old ${sex} (paediatric RIFT). Failure rate 3.3%, specificity 44.3%.`;
      actionText = 'Low risk of appendicitis. Consider early discharge with clear safety net advice to return if symptoms worsen. Outpatient ultrasound review may be arranged. This score does not exclude the need for admission if the child appears systemically unwell or if clinical concern is high.';
    } else if (score <= 6) {
      riskCategory = 'medium';
      cutoffNote = `Score ${score} — intermediate range.`;
      actionText = 'Intermediate risk. Admit for observation. Ultrasound imaging by an operator trained to assess for appendicitis is recommended. If ultrasound is inconclusive, MRI (preferred in children) or low-dose CT should be considered.';
    } else {
      riskCategory = 'high';
      cutoffNote = `Score ${score} — high range (Shera ≥7).`;
      actionText = 'High risk of appendicitis. Senior surgical review. Imaging to confirm diagnosis before operative decision. CT or MRI as locally available.';
    }
  }

  actionClass = 'action-' + (riskCategory === 'low' ? 'low' : riskCategory === 'medium' ? 'med' : 'high');

  const scoreNames = { aas: 'Adult Appendicitis Score (AAS)', airs: 'Appendicitis Inflammatory Response Score (AIRS)', shera: 'Shera Score (Paediatric)' };
  const scoreMaxes = { aas: '/ 16', airs: '/ 12', shera: '/ 10' };

  document.getElementById('res-score-name').textContent = scoreNames[activeScore];
  document.getElementById('res-score-number').innerHTML = score + ' <span>' + scoreMaxes[activeScore] + '</span>';

  const pill = document.getElementById('res-risk-pill');
  pill.textContent = riskCategory === 'low' ? 'Low risk' : riskCategory === 'medium' ? 'Intermediate risk' : 'High risk';
  pill.className = 'risk-pill risk-' + (riskCategory === 'low' ? 'low' : riskCategory === 'medium' ? 'medium' : 'high');

  document.getElementById('res-cutoff-note').textContent = cutoffNote;
  document.getElementById('res-action-box').className = 'action-box ' + actionClass;
  document.getElementById('res-action-text').textContent = actionText;

  // Alvarado reference
  document.getElementById('res-alvarado-number').textContent = alvarado + ' / 10';
  let alvInterp;
  if (alvarado <= 4) alvInterp = 'Low probability of appendicitis';
  else if (alvarado <= 6) alvInterp = 'Compatible with appendicitis';
  else if (alvarado <= 9) alvInterp = 'Probable appendicitis';
  else alvInterp = 'Very probable appendicitis';
  document.getElementById('res-alvarado-interp').textContent = alvInterp;

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResults() {
  document.getElementById('results').style.display = 'none';
}
</script>
</body>
</html>
"""

components.html(HTML, height=1800, scrolling=True)

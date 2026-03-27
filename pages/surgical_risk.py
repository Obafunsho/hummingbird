"""
hummingbird/pages/surgical_risk.py — Surgical Risk Calculator
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
.stApp { background:#f5f4f1 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
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
      style="font-family:'DM Serif Display',serif;font-size:20px;color:#1a1a1a;
      letter-spacing:.01em;text-decoration:none;"
      onmouseover="this.style.opacity='0.6'" onmouseout="this.style.opacity='1'">Hummingbird</a>
    <span style="font-size:11px;color:#999;letter-spacing:.1em;text-transform:uppercase;">
      Surgical Decisions · Risk Calculator</span>
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
_sw_col1, _sw_col2, _sw_col3, _sw_col4, _sw_col5 = st.columns([5, 1, 1, 1, 1])
with _sw_col2:
    st.markdown('''<div style="height:4px;"></div>''', unsafe_allow_html=True)
    st.markdown('''<div style="font-size:10px;font-weight:600;padding:4px 0;color:#1a1a1a;text-align:center;">Surgical Risk</div>''', unsafe_allow_html=True)
with _sw_col3:
    st.markdown('''<div style="height:4px;"></div>''', unsafe_allow_html=True)
    if st.button("Colorectal", key="sw_col_s", use_container_width=True):
        st.switch_page("pages/colorectal.py")
with _sw_col4:
    st.markdown('''<div style="height:4px;"></div>''', unsafe_allow_html=True)
    if st.button("Upper GI", key="sw_ugi_s", use_container_width=True):
        st.switch_page("pages/upper_gi.py")
with _sw_col5:
    st.markdown('''<div style="height:4px;"></div>''', unsafe_allow_html=True)
    if st.button("Appendicitis", key="sw_app_s", use_container_width=True):
        st.switch_page("pages/appendicitis.py")


# ── Render HTML tool ───────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hummingbird Surgical Risk Calculator</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 15px;
    line-height: 1.6;
    color: #1a1a1a;
    background: #f5f4f1;
    min-height: 100vh;
    padding: 2rem 1rem;
  }

  .container {
    max-width: 700px;
    margin: 0 auto;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h1 {
    font-size: 20px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #1a1a1a;
    margin-bottom: 4px;
  }

  .header p {
    font-size: 13px;
    color: #666;
  }

  .card {
    background: #fff;
    border-radius: 10px;
    border: 0.5px solid #e0ded8;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  .section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 1rem;
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .field label {
    font-size: 12px;
    color: #555;
    font-weight: 500;
  }

  .field select,
  .field input[type=number] {
    width: 100%;
    padding: 8px 10px;
    font-size: 14px;
    border: 0.5px solid #d4d2cc;
    border-radius: 6px;
    background: #fafaf8;
    color: #1a1a1a;
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23999' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 10px center;
    padding-right: 28px;
  }

  .field input[type=number] {
    background-image: none;
    padding-right: 10px;
  }

  .field select:focus,
  .field input[type=number]:focus {
    outline: none;
    border-color: #a0a09a;
    background: #fff;
  }

  .divider {
    height: 0.5px;
    background: #eeece8;
    margin: 1.25rem 0;
  }

  .toggle-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .toggle-btn {
    padding: 6px 13px;
    font-size: 12px;
    border: 0.5px solid #d4d2cc;
    border-radius: 20px;
    background: #fafaf8;
    color: #555;
    cursor: pointer;
    transition: all 0.12s;
    font-family: inherit;
  }

  .toggle-btn:hover {
    border-color: #a0a09a;
    color: #1a1a1a;
  }

  .toggle-btn.active {
    background: #1a1a1a;
    color: #fff;
    border-color: #1a1a1a;
  }

  .calc-btn {
    width: 100%;
    padding: 12px;
    font-size: 14px;
    font-weight: 500;
    border: none;
    border-radius: 8px;
    background: #1a1a1a;
    color: #fff;
    cursor: pointer;
    transition: background 0.15s;
    font-family: inherit;
    margin-top: 0.25rem;
  }

  .calc-btn:hover { background: #333; }
  .calc-btn:active { background: #000; }

  .results-card {
    background: #fff;
    border-radius: 10px;
    border: 0.5px solid #e0ded8;
    padding: 1.5rem;
    margin-bottom: 1rem;
    display: none;
  }

  .results-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 1.25rem;
  }

  .result-item {
    background: #f5f4f1;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
  }

  .result-item .r-label {
    font-size: 11px;
    color: #777;
    margin-bottom: 6px;
    line-height: 1.4;
  }

  .result-item .r-value {
    font-size: 42px;
    font-weight: 500;
    letter-spacing: -0.02em;
    line-height: 1;
    color: #1a1a1a;
  }

  .result-item .r-endpoint {
    font-size: 11px;
    color: #999;
    margin-top: 4px;
  }

  .interpret {
    padding: 1rem 1.1rem;
    background: #f5f4f1;
    border-radius: 8px;
    border-left: 3px solid #ccc;
  }

  .interpret p {
    font-size: 13px;
    color: #444;
    line-height: 1.65;
  }

  .disclaimer {
    font-size: 11px;
    color: #999;
    line-height: 1.6;
    padding: 1rem 1.25rem;
    background: #fff;
    border-radius: 10px;
    border: 0.5px solid #e0ded8;
  }

  .version-tag {
    font-size: 11px;
    color: #bbb;
    text-align: right;
    margin-top: 1rem;
  }

  @media (max-width: 520px) {
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .results-grid { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<div class="container">

  <div class="header">
    <h1>Hummingbird Surgical Risk Calculator</h1>
    <p>Estimated 30-day mortality and major complication risk (Clavien-Dindo III–V)</p>
  </div>

  <div class="card">
    <p class="section-label">Patient variables</p>
    <div class="grid-2">
      <div class="field">
        <label>Age (years)</label>
        <input type="number" id="age" min="16" max="100" placeholder="e.g. 68">
      </div>
      <div class="field">
        <label>ASA grade</label>
        <select id="asa">
          <option value="">Select</option>
          <option value="1">ASA I — healthy</option>
          <option value="2">ASA II — mild systemic disease</option>
          <option value="3">ASA III — severe systemic disease</option>
          <option value="4">ASA IV — life-threatening disease</option>
          <option value="5">ASA V — moribund</option>
        </select>
      </div>
    </div>
    <div class="grid-2">
      <div class="field">
        <label>Operative severity</label>
        <select id="severity">
          <option value="">Select</option>
          <option value="1">Minor (e.g. hernia, excision biopsy)</option>
          <option value="2">Intermediate (e.g. cholecystectomy, appendicectomy)</option>
          <option value="3">Major (e.g. colectomy, hip replacement)</option>
          <option value="4">Major+ (e.g. oesophagectomy, AAA repair)</option>
        </select>
      </div>
      <div class="field">
        <label>Surgical specialty</label>
        <select id="specialty">
          <option value="">Select</option>
          <option value="gen">General surgery</option>
          <option value="col">Colorectal surgery</option>
          <option value="ugi">Upper GI / HPB</option>
          <option value="vasc">Vascular surgery</option>
          <option value="orth">Orthopaedic surgery</option>
          <option value="uro">Urology</option>
          <option value="gyn">Gynaecology</option>
          <option value="thor">Thoracic surgery</option>
          <option value="neuro">Neurosurgery</option>
        </select>
      </div>
    </div>

    <div class="divider"></div>
    <p class="section-label">Comorbidities — select all that apply</p>
    <div class="toggle-row" id="comorbidities">
      <button class="toggle-btn" data-val="cardiac" onclick="toggleCom(this)">Cardiac disease</button>
      <button class="toggle-btn" data-val="resp" onclick="toggleCom(this)">Respiratory disease</button>
      <button class="toggle-btn" data-val="renal" onclick="toggleCom(this)">Renal impairment</button>
      <button class="toggle-btn" data-val="dm" onclick="toggleCom(this)">Diabetes mellitus</button>
      <button class="toggle-btn" data-val="obesity" onclick="toggleCom(this)">Obesity (BMI &gt;35)</button>
      <button class="toggle-btn" data-val="cancer" onclick="toggleCom(this)">Active malignancy</button>
      <button class="toggle-btn" data-val="steroids" onclick="toggleCom(this)">Steroids / immunosuppression</button>
      <button class="toggle-btn" data-val="anaemia" onclick="toggleCom(this)">Anaemia (Hb &lt;100 g/L)</button>
    </div>

    <div class="divider"></div>
    <p class="section-label">Operative context</p>
    <div class="grid-3">
      <div class="field">
        <label>Urgency</label>
        <select id="urgency">
          <option value="">Select</option>
          <option value="elective">Elective</option>
          <option value="expedited">Expedited (days)</option>
          <option value="urgent">Urgent (hours)</option>
          <option value="emergency">Emergency (immediate)</option>
        </select>
      </div>
      <div class="field">
        <label>Operative approach</label>
        <select id="approach">
          <option value="">Select</option>
          <option value="open">Open</option>
          <option value="lap">Laparoscopic</option>
          <option value="robotic">Robotic</option>
          <option value="endo">Endoscopic / percutaneous</option>
        </select>
      </div>
      <div class="field">
        <label>Anaesthetic type</label>
        <select id="anaesthetic">
          <option value="">Select</option>
          <option value="ga">General anaesthesia</option>
          <option value="regional">Regional / spinal</option>
          <option value="local">Local / sedation</option>
        </select>
      </div>
    </div>

    <button class="calc-btn" onclick="calculate()">Calculate risk estimate</button>
  </div>

  <div class="results-card" id="results">
    <p class="section-label">Risk estimates</p>
    <div class="results-grid">
      <div class="result-item">
        <div class="r-label">30-day mortality</div>
        <div class="r-value" id="mort-val">—</div>
        <div class="r-endpoint">% estimated risk</div>
      </div>
      <div class="result-item">
        <div class="r-label">Major complication (Clavien-Dindo III–V)</div>
        <div class="r-value" id="comp-val">—</div>
        <div class="r-endpoint">% estimated risk</div>
      </div>
    </div>
    <div class="interpret">
      <p id="interpret-text"></p>
    </div>
  </div>

  <div class="disclaimer">
    This tool provides an indicative risk estimate for clinical discussion and consent purposes only. It does not replace clinical judgement and has not yet been prospectively validated. Coefficients are derived from published SORT and ACS NSQIP literature and are subject to revision following validation against institutional outcome data. All cases must be reviewed by a responsible clinician before operative consent is obtained.
  </div>

  <p class="version-tag">Hummingbird v0.1 — pre-validation prototype — coefficients subject to change</p>

</div>

<script>
  const selected = new Set();

  function toggleCom(btn) {
    const v = btn.dataset.val;
    if (selected.has(v)) {
      selected.delete(v);
      btn.classList.remove('active');
    } else {
      selected.add(v);
      btn.classList.add('active');
    }
  }

  function sigmoid(x) {
    return 1 / (1 + Math.exp(-x));
  }

  function calculate() {
    const age = parseFloat(document.getElementById('age').value);
    const asa = parseInt(document.getElementById('asa').value);
    const sev = parseInt(document.getElementById('severity').value);
    const spec = document.getElementById('specialty').value;
    const urg = document.getElementById('urgency').value;
    const app = document.getElementById('approach').value;
    const anaes = document.getElementById('anaesthetic').value;

    if (!age || !asa || !sev || !spec || !urg || !app || !anaes) {
      alert('Please complete all fields before calculating.');
      return;
    }

    // ---- MORTALITY MODEL ----
    // Intercept calibrated so elective minor ASA I = ~0.05% mortality
    let lp_mort = -7.5;

    // Age: continuous with non-linear penalty above 65 and 80
    lp_mort += (age - 50) * 0.025;
    if (age > 65) lp_mort += (age - 65) * 0.040;
    if (age > 80) lp_mort += (age - 80) * 0.060;

    // ASA grade
    const asa_mort = [0, 0.0, 0.6, 1.5, 2.8, 4.5];
    lp_mort += asa_mort[asa];

    // Operative severity
    const sev_mort = [0, 0.0, 0.5, 1.2, 2.1];
    lp_mort += sev_mort[sev];

    // Surgical specialty (relative to general surgery = 0)
    const spec_mort = { gen:0.00, col:0.15, ugi:0.40, vasc:0.50, orth:-0.30, uro:-0.20, gyn:-0.25, thor:0.35, neuro:0.30 };
    lp_mort += spec_mort[spec] || 0;

    // Urgency
    const urg_mort = { elective:0.0, expedited:0.4, urgent:0.9, emergency:1.8 };
    lp_mort += urg_mort[urg] || 0;

    // Operative approach
    const app_mort = { open:0.00, lap:-0.40, robotic:-0.35, endo:-0.80 };
    lp_mort += app_mort[app] || 0;

    // Anaesthetic type
    const anaes_mort = { ga:0.00, regional:-0.30, local:-0.70 };
    lp_mort += anaes_mort[anaes] || 0;

    // Comorbidities
    if (selected.has('cardiac'))  lp_mort += 0.70;
    if (selected.has('resp'))     lp_mort += 0.50;
    if (selected.has('renal'))    lp_mort += 0.60;
    if (selected.has('dm'))       lp_mort += 0.30;
    if (selected.has('obesity'))  lp_mort += 0.25;
    if (selected.has('cancer'))   lp_mort += 0.50;
    if (selected.has('steroids')) lp_mort += 0.35;
    if (selected.has('anaemia'))  lp_mort += 0.40;

    const mort = sigmoid(lp_mort) * 100;

    // ---- COMPLICATION MODEL (Clavien-Dindo III-V) ----
    // Intercept calibrated so elective minor ASA I = ~1% complication risk
    let lp_comp = -5.8;

    lp_comp += (age - 50) * 0.018;
    if (age > 65) lp_comp += (age - 65) * 0.025;

    const asa_comp = [0, 0.0, 0.45, 1.1, 2.0, 3.2];
    lp_comp += asa_comp[asa];

    const sev_comp = [0, 0.0, 0.6, 1.4, 2.3];
    lp_comp += sev_comp[sev];

    const spec_comp = { gen:0.00, col:0.20, ugi:0.45, vasc:0.55, orth:0.10, uro:-0.10, gyn:-0.15, thor:0.40, neuro:0.25 };
    lp_comp += spec_comp[spec] || 0;

    const urg_comp = { elective:0.0, expedited:0.35, urgent:0.80, emergency:1.50 };
    lp_comp += urg_comp[urg] || 0;

    const app_comp = { open:0.00, lap:-0.50, robotic:-0.45, endo:-0.90 };
    lp_comp += app_comp[app] || 0;

    const anaes_comp = { ga:0.00, regional:-0.20, local:-0.50 };
    lp_comp += anaes_comp[anaes] || 0;

    if (selected.has('cardiac'))  lp_comp += 0.55;
    if (selected.has('resp'))     lp_comp += 0.60;
    if (selected.has('renal'))    lp_comp += 0.65;
    if (selected.has('dm'))       lp_comp += 0.45;
    if (selected.has('obesity'))  lp_comp += 0.40;
    if (selected.has('cancer'))   lp_comp += 0.40;
    if (selected.has('steroids')) lp_comp += 0.50;
    if (selected.has('anaemia'))  lp_comp += 0.45;

    const comp = sigmoid(lp_comp) * 100;

    // ---- DISPLAY ----
    document.getElementById('mort-val').textContent = mort.toFixed(1) + '%';
    document.getElementById('comp-val').textContent = comp.toFixed(1) + '%';

    const urgLabel  = { elective:'elective', expedited:'expedited', urgent:'urgent', emergency:'emergency' };
    const specLabel = { gen:'general', col:'colorectal', ugi:'upper GI/HPB', vasc:'vascular', orth:'orthopaedic', uro:'urological', gyn:'gynaecological', thor:'thoracic', neuro:'neurosurgical' };
    const nCom = selected.size;

    let interp = `This ${urgLabel[urg]} ${specLabel[spec]} procedure in a ${age}-year-old ASA ${asa} patient carries an estimated 30-day mortality of ${mort.toFixed(1)}% and a major complication risk of ${comp.toFixed(1)}%.`;
    if (nCom > 0) interp += ` ${nCom} comorbidity${nCom > 1 ? ' factors were' : ' factor was'} included in the calculation.`;
    if (mort >= 5 || comp >= 20) {
      interp += ' These estimates indicate high operative risk. Senior clinician review and multidisciplinary discussion are recommended prior to consent.';
    } else if (mort >= 2 || comp >= 10) {
      interp += ' These estimates indicate moderate operative risk and should be discussed explicitly with the patient during the consent process.';
    } else {
      interp += ' These estimates indicate lower operative risk; standard consent and peri-operative planning apply.';
    }

    document.getElementById('interpret-text').textContent = interp;
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
</script>

</body>
</html>
"""

components.html(HTML, height=1400, scrolling=True)

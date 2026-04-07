"""
hummingbird/pages/thyroid.py — Thyroid · Suspected Cancer
Renders Aneel's HTML tool via st.components.v1.html
Auth inherited from app.py via st.navigation()
"""
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from auth import do_logout

# ── Robust path resolution for Streamlit Cloud ────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

html_path = _ROOT / "static" / "hummingbird_thyroid.html"

# Fallback: try relative to cwd if _ROOT resolution fails
if not html_path.exists():
    html_path = Path("static") / "hummingbird_thyroid.html"

if not html_path.exists():
    st.error(f"Could not locate hummingbird_thyroid.html. Tried: {_ROOT / 'static' / 'hummingbird_thyroid.html'}")
    st.stop()

name = st.session_state.get("name", "")

# ── Minimal CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
.stApp { background:#f5f4f1 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
div[data-testid="stHorizontalBlock"] button:disabled {
  background: #1a1a1a !important; border: 0.5px solid #1a1a1a !important;
  color: #fff !important; font-weight: 500 !important;
  opacity: 1 !important; cursor: default !important;
  min-height: unset !important; height: auto !important;
  padding: 9px 14px !important; font-size: 13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Topbar ─────────────────────────────────────────────────────────────────────
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
      Thyroid · Suspected Cancer</span>
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

# ── Module switcher ────────────────────────────────────────────────────────────
_sw_cols = st.columns([3, 1, 1, 1, 1, 1, 1])
with _sw_cols[0]:
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
with _sw_cols[1]:
    if st.button("Colorectal", key="sw_col_thyroid", use_container_width=True):
        st.switch_page("pages/colorectal.py")
with _sw_cols[2]:
    if st.button("Upper GI", key="sw_ugi_thyroid", use_container_width=True):
        st.switch_page("pages/upper_gi.py")
with _sw_cols[3]:
    st.button("Thyroid", key="sw_cur_thyroid", use_container_width=True, disabled=True)
with _sw_cols[4]:
    if st.button("\u2191 More \u2193", key="sw_more_thyroid", use_container_width=True):
        pass

# ── Render HTML tool ───────────────────────────────────────────────────────────
HTML = html_path.read_text(encoding="utf-8")
components.html(HTML, height=1600, scrolling=True)

"""
hummingbird/pages/bladder.py — Bladder · Suspected Cancer
Renders Aneel's HTML tool via st.components.v1.html
Auth inherited from app.py via st.navigation()
"""
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from auth import do_logout

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

name = st.session_state.get("name", "")

# ── Minimal CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');
.stApp { background:#f5f4f1 !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
/* Switcher: active button */
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
      Bladder · Suspected Cancer</span>
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
    if st.button("Colorectal", key="sw_col_bladder", use_container_width=True):
        st.switch_page("pages/colorectal.py")
with _sw_cols[2]:
    if st.button("Upper GI", key="sw_ugi_bladder", use_container_width=True):
        st.switch_page("pages/upper_gi.py")
with _sw_cols[3]:
    st.button("Bladder", key="sw_cur_bladder", use_container_width=True, disabled=True)
with _sw_cols[4]:
    if st.button("↑ More ↓", key="sw_more_bladder", use_container_width=True):
        pass  # TODO: expand cancer module picker

# ── Render HTML tool ───────────────────────────────────────────────────────────
html_path = _ROOT / "static" / "hummingbird_bladder.html"
with open(html_path) as f:
    HTML = f.read()

components.html(HTML, height=1800, scrolling=True)

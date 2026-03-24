"""
hummingbird/app.py — v2.1
Navigation hub and auth gate for Hummingbird multipage app.
"""
import os, sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=False)
sys.path.insert(0, str(Path(__file__).parent))

try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str) and _k not in os.environ:
            os.environ[_k] = _v
except Exception:
    pass

from auth import init_auth, render_login_page

st.set_page_config(page_title="Hummingbird", page_icon="🐦",
                   layout="wide", initial_sidebar_state="collapsed")

# ── AUTH GATE ─────────────────────────────────────────────────────────────────
_, auth_status, username, name = init_auth()
if not auth_status:
    render_login_page()
    st.stop()

# ── NAVIGATION ────────────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/colorectal.py", title="Colorectal — Lower GI",  icon="🎯"),
    st.Page("pages/upper_gi.py",   title="Upper GI — Oesophagogastric", icon="🔬"),
], position="hidden")
pg.run()

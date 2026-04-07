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
                   layout="wide", initial_sidebar_state="expanded")

# ── AUTH GATE ─────────────────────────────────────────────────────────────────
_, auth_status, username, name = init_auth()
if not auth_status:
    render_login_page()
    st.stop()

# ── NAVIGATION ────────────────────────────────────────────────────────────────
pg = st.navigation([
    # ── Hummingbird Cancer ────────────────────────────────────────────────────
    st.Page("pages/colorectal.py",      title="Colorectal — Lower GI",        icon="🎯"),
    st.Page("pages/upper_gi.py",        title="Upper GI — Oesophagogastric",  icon="🔬"),
    st.Page("pages/breast.py",          title="Breast",                        icon="🩺"),
    st.Page("pages/lung.py",            title="Lung",                          icon="🫁"),
    st.Page("pages/bladder.py",         title="Bladder",                       icon="🔵"),
    st.Page("pages/brain_cns.py",       title="Brain & CNS",                   icon="🧠"),
    st.Page("pages/gynaecology.py",     title="Gynaecology",                   icon="🩻"),
    st.Page("pages/haematological.py",  title="Haematological",                icon="🔴"),
    st.Page("pages/head_neck.py",       title="Head & Neck",                   icon="🔷"),
    st.Page("pages/kidney.py",          title="Kidney",                        icon="🫘"),
    st.Page("pages/prostate.py",        title="Prostate",                      icon="🔹"),
    st.Page("pages/sarcoma.py",         title="Sarcoma",                       icon="🦴"),
    st.Page("pages/skin.py",            title="Skin — Melanoma",               icon="🌞"),
    st.Page("pages/thyroid.py",         title="Thyroid",                       icon="🦋"),
    # ── Hummingbird Surgery ───────────────────────────────────────────────────
    st.Page("pages/appendicitis.py",    title="Appendicitis Risk Score",       icon="🏥"),
    st.Page("pages/surgical_risk.py",   title="Surgical Risk Calculator",      icon="⚕️"),
], position="sidebar")
pg.run()

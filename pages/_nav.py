"""
hummingbird/pages/_nav.py
Shared navigation popover for all Hummingbird pages.
"""
import streamlit as st

CANCER_PAGES = [
    ("Colorectal — Lower GI",       "pages/colorectal.py"),
    ("Upper GI — Oesophagogastric", "pages/upper_gi.py"),
    ("Breast",                       "pages/breast.py"),
    ("Lung",                         "pages/lung.py"),
    ("Bladder",                      "pages/bladder.py"),
    ("Brain & CNS",                  "pages/brain_cns.py"),
    ("Gynaecology",                  "pages/gynaecology.py"),
    ("Haematological",               "pages/haematological.py"),
    ("Head & Neck",                  "pages/head_neck.py"),
    ("Kidney",                       "pages/kidney.py"),
    ("Prostate",                     "pages/prostate.py"),
    ("Sarcoma",                      "pages/sarcoma.py"),
    ("Skin — Melanoma",              "pages/skin.py"),
    ("Thyroid",                      "pages/thyroid.py"),
]

SURGICAL_PAGES = [
    ("Appendicitis Risk Score",   "pages/appendicitis.py"),
    ("Surgical Risk Calculator",  "pages/surgical_risk.py"),
]

def render_more_popover(current_slug: str, col):
    """Render the ↑ More ↓ popover in the given column."""
    with col:
        with st.popover("↑ More ↓", use_container_width=True):
            st.markdown(
                '<div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;'
                'color:#999;margin-bottom:8px;font-weight:500;">Cancer referral</div>',
                unsafe_allow_html=True
            )
            for title, path in CANCER_PAGES:
                if path == f"pages/{current_slug}.py":
                    st.markdown(
                        f'<div style="font-size:13px;color:#1a1a1a;font-weight:600;'
                        f'padding:4px 0;">✓ {title}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(title, key=f"nav_{current_slug}_{path}", use_container_width=True):
                        st.switch_page(path)

            st.markdown(
                '<div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;'
                'color:#999;margin-top:12px;margin-bottom:8px;font-weight:500;">Surgical decisions</div>',
                unsafe_allow_html=True
            )
            for title, path in SURGICAL_PAGES:
                if path == f"pages/{current_slug}.py":
                    st.markdown(
                        f'<div style="font-size:13px;color:#1a1a1a;font-weight:600;'
                        f'padding:4px 0;">✓ {title}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(title, key=f"nav_{current_slug}_{path}", use_container_width=True):
                        st.switch_page(path)
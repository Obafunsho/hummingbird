"""
hummingbird/pages/_nav.py
Shared navigation popover for all Hummingbird pages.
Cancer referral pages route internally via st.switch_page.
Surgical decision pages open as standalone public GitHub Pages tools,
with a warning dialog before leaving the authenticated app.
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
    ("Appendicitis Risk Score",  "https://obafunsho.github.io/hummingbird_landing/appendicitis.html"),
    ("Surgical Risk Calculator", "https://obafunsho.github.io/hummingbird_landing/surgical_risk.html"),
]


@st.dialog("Leaving Hummingbird")
def _surgical_warning_dialog(title: str, url: str) -> None:
    st.markdown(
        f'<p style="font-size:14px;color:#1a1a1a;line-height:1.7;margin-bottom:6px;">'
        f'You\'re about to open the <strong>{title}</strong> — a standalone public tool '
        f'that runs outside the Hummingbird cancer referral app.</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="font-size:13px;color:#666;line-height:1.6;">'
        'It will open in a new tab. When you\'re done, close that tab and you\'ll still '
        'be signed in here.</p>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col_go, col_cancel = st.columns(2)
    with col_go:
        st.link_button(
            "Open tool →",
            url=url,
            use_container_width=True,
            type="primary",
        )
    with col_cancel:
        if st.button("Cancel", use_container_width=True, key=f"dlg_cancel_{title}"):
            st.rerun()


def _surgical_button(title: str, url: str, key: str) -> None:
    """Render a button that opens the surgical warning dialog."""
    if st.button(title, key=key, use_container_width=True):
        _surgical_warning_dialog(title, url)


def render_more_popover(current_slug: str, col) -> None:
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
            for title, url in SURGICAL_PAGES:
                _surgical_button(title, url, key=f"surg_{current_slug}_{title}")

"""
hummingbird/auth.py
No cookies. No library widgets. No ghost boxes.
Session state only — user logs in once per browser session.
"""

from pathlib import Path
from typing import Optional, Tuple
import re
import streamlit as st
from streamlit_authenticator.utilities import Hasher
import yaml
from yaml.loader import SafeLoader

CREDENTIALS_FILE = Path(__file__).parent / "credentials.yaml"


def _load_config() -> dict:
    with open(CREDENTIALS_FILE) as f:
        return yaml.load(f, Loader=SafeLoader)


def _save_config(config: dict) -> None:
    with open(CREDENTIALS_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def init_auth() -> Tuple[None, Optional[bool], Optional[str], Optional[str]]:
    """No widgets rendered. Returns (None, auth_status, username, name)."""
    return (
        None,
        st.session_state.get("authentication_status"),
        st.session_state.get("username"),
        st.session_state.get("name"),
    )


def _attempt_login(username: str, password: str) -> bool:
    config   = _load_config()
    creds    = config["credentials"]["usernames"]
    username = username.lower().strip()

    if username not in creds:
        return False
    user     = creds[username]
    attempts = user.get("failed_login_attempts", 0)

    if attempts >= 5:
        st.session_state["login_error"] = "Too many failed attempts. Please contact the study team."
        return False
    if not Hasher.check_pw(password, user["password"]):
        config["credentials"]["usernames"][username]["failed_login_attempts"] = attempts + 1
        _save_config(config)
        return False

    config["credentials"]["usernames"][username]["failed_login_attempts"] = 0
    config["credentials"]["usernames"][username]["logged_in"] = True
    _save_config(config)

    st.session_state["authentication_status"] = True
    st.session_state["username"] = username
    st.session_state["name"]     = f"{user.get('first_name','')} {user.get('last_name','')}".strip()
    st.session_state["email"]    = user.get("email", "")
    return True


def _attempt_register(first: str, last: str, email: str,
                      username: str, password: str) -> Optional[str]:
    config   = _load_config()
    creds    = config["credentials"]["usernames"]
    username = username.lower().strip()
    email    = email.strip()

    if not first.strip():  return "First name is required."
    if not last.strip():   return "Last name is required."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return "Please enter a valid email address."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username may only contain letters, numbers and underscores."
    if len(username) < 2:  return "Username must be at least 2 characters."
    if len(password) < 8:  return "Password must be at least 8 characters."
    if any(u.get("email","").lower() == email.lower() for u in creds.values()):
        return "An account with that email already exists."
    if username in creds:  return "That username is already taken."

    config["credentials"]["usernames"][username] = {
        "email": email, "first_name": first.strip(), "last_name": last.strip(),
        "password": Hasher.hash(password), "logged_in": False,
        "roles": ["clinician"], "failed_login_attempts": 0,
    }
    _save_config(config)
    return None


def do_logout(_=None) -> None:
    username = st.session_state.get("username")
    if username:
        try:
            config = _load_config()
            if username in config["credentials"]["usernames"]:
                config["credentials"]["usernames"][username]["logged_in"] = False
                _save_config(config)
        except Exception:
            pass
    for key in ["authentication_status", "username", "name", "email", "roles"]:
        st.session_state[key] = None
    st.rerun()


# ── CSS ────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --navy:#0B1826; --navy-card:#1A2E42; --navy-tile:#1E3347;
  --teal:#0E9B8A; --teal-b:#12C4AF; --white:#F0F6FA; --muted:#6B8EA8;
  --border:rgba(14,155,138,0.18);
}
*,*::before,*::after { box-sizing:border-box; }
.stApp { background:var(--navy) !important; font-family:'DM Sans',sans-serif !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; max-width:100% !important; }
.stDeployButton { display:none; }
/* Grid texture */
.stApp::before {
  content:''; position:fixed; inset:0;
  background-image:
    linear-gradient(rgba(14,155,138,0.03) 1px,transparent 1px),
    linear-gradient(90deg,rgba(14,155,138,0.03) 1px,transparent 1px);
  background-size:52px 52px; pointer-events:none; z-index:0;
}
/* Inputs */
.stTextInput input {
  background:var(--navy-tile) !important;
  border:1.5px solid rgba(240,244,248,0.1) !important;
  border-radius:8px !important; color:var(--white) !important;
  font-size:14px !important; padding:11px 14px !important;
  font-family:'DM Sans',sans-serif !important; transition:border-color 0.15s !important;
}
.stTextInput input:focus { border-color:var(--teal) !important; outline:none !important; }
.stTextInput input::placeholder { color:rgba(240,244,248,0.25) !important; }
.stTextInput label {
  color:var(--muted) !important; font-size:13px !important;
  font-weight:500 !important; font-family:'DM Sans',sans-serif !important;
}
/* Primary button */
.hb-primary .stButton > button {
  background:linear-gradient(135deg,#0E9B8A,#12C4AF) !important;
  border:none !important; border-radius:10px !important; color:white !important;
  font-size:15px !important; font-weight:600 !important;
  padding:14px 24px !important; width:100% !important;
  box-shadow:0 4px 24px rgba(14,155,138,0.4) !important; transition:all 0.2s !important;
}
.hb-primary .stButton > button:hover {
  transform:translateY(-1px) !important;
  box-shadow:0 6px 28px rgba(14,155,138,0.5) !important;
}
/* Secondary button */
.hb-secondary .stButton > button {
  background:transparent !important; border:1px solid var(--border) !important;
  border-radius:10px !important; color:var(--muted) !important;
  font-size:14px !important; font-weight:400 !important;
  padding:13px 24px !important; width:100% !important; transition:all 0.15s !important;
}
.hb-secondary .stButton > button:hover {
  border-color:var(--teal) !important; color:var(--teal-b) !important;
  background:rgba(14,155,138,0.06) !important;
}
.stAlert { border-radius:10px !important; font-size:13px !important; }
</style>
"""

def _orbs():
    st.markdown("""
    <div style="position:fixed;border-radius:50%;pointer-events:none;z-index:0;
      width:500px;height:500px;background:rgba(14,155,138,0.07);
      filter:blur(120px);top:-180px;left:-120px;"></div>
    <div style="position:fixed;border-radius:50%;pointer-events:none;z-index:0;
      width:350px;height:350px;background:rgba(14,155,138,0.05);
      filter:blur(120px);bottom:5%;right:-80px;"></div>""", unsafe_allow_html=True)

def _wordmark():
    st.markdown("""
    <div style="text-align:center;margin-bottom:36px;position:relative;z-index:1;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
        width:48px;height:48px;background:linear-gradient(135deg,#0E9B8A,#12C4AF);
        border-radius:14px;font-size:22px;margin-bottom:16px;">🐦</div>
      <div style="font-family:'DM Serif Display',serif;font-size:32px;
        color:#F0F6FA;letter-spacing:0.01em;margin-bottom:6px;">Hummingbird</div>
      <div style="font-size:12px;font-weight:400;color:#6B8EA8;
        letter-spacing:0.12em;text-transform:uppercase;">
        Colorectal Cancer · Lower GI · Decision Support</div>
    </div>""", unsafe_allow_html=True)

def _divider(text="or"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin:18px 0;">
      <span style="flex:1;height:1px;background:rgba(255,255,255,0.06);"></span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:10px;
        color:rgba(107,142,168,0.6);letter-spacing:0.1em;text-transform:uppercase;">{text}</span>
      <span style="flex:1;height:1px;background:rgba(255,255,255,0.06);"></span>
    </div>""", unsafe_allow_html=True)

def _footer():
    st.markdown("""
    <div style="text-align:center;margin-top:32px;font-size:11px;
      color:rgba(107,142,168,0.5);line-height:1.8;">
      Hummingbird v2.1 · Clinician-authored decision support<br>
      NICE NG12 compliant · Not prospectively validated<br>
      Configured by Prof Aneel Bhangu, Consultant Colorectal Surgeon
    </div>""", unsafe_allow_html=True)


def render_login_page(_=None) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    _orbs()
    if "hb_page" not in st.session_state:
        st.session_state.hb_page = "login"
    _, centre, _ = st.columns([1, 1.05, 1])
    with centre:
        st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
        _wordmark()
        if st.session_state.hb_page == "login":
            _page_login()
        else:
            _page_register()
        _footer()


def _page_login():
    # Card
    st.markdown("""<div style="background:#1A2E42;border:1px solid rgba(14,155,138,0.18);
      border-radius:16px;padding:36px 32px;margin-bottom:14px;">""", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:24px;">
      <div style="font-family:'DM Serif Display',serif;font-size:24px;
        color:#F0F6FA;margin-bottom:6px;">Sign in</div>
      <div style="font-size:13px;color:#6B8EA8;">Welcome back. Enter your credentials to continue.</div>
    </div>""", unsafe_allow_html=True)

    username = st.text_input("Username", key="li_user", placeholder="your_username")
    password = st.text_input("Password", type="password", key="li_pass", placeholder="••••••••")

    if st.session_state.get("login_error"):
        st.error(st.session_state.pop("login_error"))

    st.markdown('<div class="hb-primary" style="margin-top:8px;">', unsafe_allow_html=True)
    if st.button("Sign in", key="li_submit", use_container_width=True):
        if not username or not password:
            st.session_state["login_error"] = "Please enter your username and password."
        else:
            ok = _attempt_login(username, password)
            if not ok and not st.session_state.get("login_error"):
                st.session_state["login_error"] = "Incorrect username or password."
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close card

    _divider("new to hummingbird")
    st.markdown('<div class="hb-secondary">', unsafe_allow_html=True)
    if st.button("Create account →", key="li_to_reg", use_container_width=True):
        st.session_state.hb_page = "register"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _page_register():
    st.markdown("""<div style="background:#1A2E42;border:1px solid rgba(14,155,138,0.18);
      border-radius:16px;padding:36px 32px;margin-bottom:14px;">""", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:24px;">
      <div style="font-family:'DM Serif Display',serif;font-size:24px;
        color:#F0F6FA;margin-bottom:6px;">Create account</div>
      <div style="font-size:13px;color:#6B8EA8;">Sign in immediately after registration.</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: first = st.text_input("First name",  key="rg_fn", placeholder="Jane")
    with c2: last  = st.text_input("Last name",   key="rg_ln", placeholder="Smith")
    email    = st.text_input("Email address",      key="rg_em", placeholder="jane@hospital.nhs.uk")
    username = st.text_input("Username",           key="rg_un",
                              placeholder="jane_smith  (letters, numbers, underscores)")
    password = st.text_input("Password", type="password", key="rg_pw", placeholder="Min. 8 characters")
    confirm  = st.text_input("Confirm password", type="password", key="rg_cf", placeholder="••••••••")

    if st.session_state.get("reg_error"):
        st.error(st.session_state.pop("reg_error"))

    st.markdown('<div class="hb-primary" style="margin-top:8px;">', unsafe_allow_html=True)
    if st.button("Create account →", key="rg_submit", use_container_width=True):
        if password != confirm:
            st.session_state["reg_error"] = "Passwords do not match."
        else:
            err = _attempt_register(first, last, email, username, password)
            if err:
                st.session_state["reg_error"] = err
            else:
                st.session_state["reg_success"] = True
                st.session_state.hb_page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close card

    if st.session_state.pop("reg_success", False):
        st.success("Account created. Please sign in.")

    _divider("already have an account")
    st.markdown('<div class="hb-secondary">', unsafe_allow_html=True)
    if st.button("← Back to sign in", key="rg_to_li", use_container_width=True):
        st.session_state.hb_page = "login"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

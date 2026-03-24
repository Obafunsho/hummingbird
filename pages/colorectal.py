"""
hummingbird/pages/colorectal.py
Wrapper — imports and runs the main colorectal app logic.
The main app.py becomes the home page; this page is the explicit colorectal route.
"""
# This file intentionally re-executes app.py logic by importing it.
# Streamlit pages are independent scripts — shared state lives in st.session_state.
import runpy, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
runpy.run_path(str(Path(__file__).parent.parent / "app.py"), run_name="__main__")

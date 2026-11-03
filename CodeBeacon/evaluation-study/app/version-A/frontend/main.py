import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from frontend.api_client import ApiClient, ApiError, ConfigurationError, load_settings
from frontend.views.account import (
    clear_session, handle_authenticated_error, render_settings, render_sign_in,
    require_session,
)
from frontend.views.dashboard import render_dashboard

st.set_page_config(page_title="Room monitor", page_icon=":material/device_thermostat:", layout="wide")
st.title("Room monitor")
st.session_state.setdefault("auth", None)

notice = st.session_state.pop("notice", None)
if notice:
    st.info(notice)

try:
    settings = load_settings()
except ConfigurationError as error:
    st.error(str(error))
    st.caption("Check the project's local API settings, then refresh this page.")
    st.stop()

if not st.session_state["auth"]:
    with ApiClient(settings) as client:
        render_sign_in(client)
    st.stop()

auth = require_session()
with ApiClient(settings, auth["access_token"]) as client:
    with st.sidebar:
        st.text(f"Signed in as {auth['account']['username']}")
        page = st.radio("Workspace", ["Dashboard", "Account settings"], key="workspace")
        st.button("Sign out", on_click=clear_session, width="stretch")
    try:
        auth["account"] = client.current_account()
    except ApiError as error:
        handle_authenticated_error(error)
        st.stop()
    if page == "Account settings":
        render_settings(client)
    else:
        render_dashboard(client, settings)

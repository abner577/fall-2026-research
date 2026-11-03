import time

import streamlit as st

from frontend.api_client import ApiClient, ApiError


def clear_session(message: str | None = None) -> None:
    for key in list(st.session_state):
        del st.session_state[key]
    if message:
        st.session_state["notice"] = message


def save_session(response: dict) -> None:
    st.session_state["auth"] = {
        "access_token": response["access_token"],
        "expires_at": time.monotonic() + response["expires_in"],
        "account": response["account"],
    }


def require_session() -> dict:
    auth = st.session_state.get("auth")
    if not auth or time.monotonic() >= auth["expires_at"]:
        clear_session("Your session has expired. Sign in again.")
        st.rerun(scope="app")
    return auth


def show_api_error(error: ApiError) -> None:
    st.error(str(error))
    if error.retry_after is not None:
        st.caption(f"Try again in {error.retry_after} seconds.")


def handle_authenticated_error(error: ApiError) -> None:
    if error.status_code == 401:
        clear_session("Your session is no longer valid. Sign in again.")
        st.rerun(scope="app")
    show_api_error(error)


def render_sign_in(client: ApiClient) -> None:
    st.caption("Monitor room temperatures and manage your devices.")
    mode = st.segmented_control("Account access", ["Sign in", "Create account"], default="Sign in", key="access_mode")
    registering = mode == "Create account"
    with st.form("account_access", clear_on_submit=True):
        st.subheader("Create account" if registering else "Sign in")
        username = st.text_input("Username", max_chars=32, key="login_username")
        password = st.text_input("Password", type="password", max_chars=128, key="login_password")
        confirmation = st.text_input("Confirm password", type="password", max_chars=128, key="register_confirmation") if registering else None
        if registering:
            st.caption("Use 3–32 letters, numbers, or underscores for your username and 15–128 characters for your password.")
        submitted = st.form_submit_button("Create account" if registering else "Sign in", type="primary", width="stretch")
    if not submitted:
        return
    if not username.strip() or not password:
        st.error("Enter your username and password.")
        return
    if registering and password != confirmation:
        st.error("Passwords do not match.")
        return
    try:
        if registering:
            client.register(username, password)
            st.success("Account created. Sign in to continue.")
        else:
            response = client.login(username, password)
            clear_session()
            save_session(response)
            st.rerun()
    except ApiError as error:
        show_api_error(error)


def render_settings(client: ApiClient) -> None:
    st.header("Account settings")
    st.text(f"Username: {st.session_state['auth']['account']['username']}")
    with st.form("change_password", clear_on_submit=True):
        st.subheader("Change password")
        current = st.text_input("Current password", type="password", max_chars=128, key="current_password")
        new = st.text_input("New password", type="password", max_chars=128, key="new_password")
        confirmation = st.text_input("Confirm new password", type="password", max_chars=128, key="confirm_new_password")
        submitted = st.form_submit_button("Update password", type="primary")
    if submitted:
        if not current or not new:
            st.error("Enter your current and new passwords.")
        elif new != confirmation:
            st.error("Passwords do not match.")
        else:
            try:
                save_session(client.change_password(current, new))
                st.success("Password updated. Other account sessions have been signed out.")
            except ApiError as error:
                show_api_error(error)

from datetime import datetime, timezone

import altair as alt
import pandas as pd
import streamlit as st

from frontend.api_client import ApiClient, ApiError, Settings
from frontend.views.account import handle_authenticated_error, require_session


def _dismiss_credentials() -> None:
    st.session_state.pop("enrollment", None)
    st.session_state.pop("issued_device_token", None)


def _render_enrollment(client: ApiClient) -> None:
    with st.expander("Register a device"):
        with st.form("enroll_device", clear_on_submit=True):
            name = st.text_input("Device name", max_chars=100, key="device_name")
            submitted = st.form_submit_button("Register device", disabled=bool(st.session_state.get("enrollment")))
        if submitted:
            if not name.strip():
                st.error("Enter a name for your device.")
            else:
                try:
                    enrollment = client.enroll_device(name.strip())
                    st.session_state["enrollment"] = enrollment
                    st.session_state["selected_device"] = enrollment["device"]["id"]
                    st.session_state.pop("issued_device_token", None)
                    st.rerun()
                except ApiError as error:
                    handle_authenticated_error(error)
    enrollment = st.session_state.get("enrollment")
    if enrollment:
        with st.container(border=True):
            st.success("Device registered. Save its credentials before dismissing this panel.")
            st.caption("Set DEVICE_ID and DEVICE_TOKEN in the device's local configuration. The token cannot be retrieved again.")
            st.text(f"Device ID: {enrollment['device']['id']}")
            st.text_input("Device token", value=enrollment["device_token"], type="password", key="issued_device_token")
            st.button("I have saved these credentials", on_click=_dismiss_credentials)


def render_dashboard(client: ApiClient, settings: Settings) -> None:
    st.header("Your devices")
    _render_enrollment(client)
    try:
        devices = client.list_devices()
    except ApiError as error:
        handle_authenticated_error(error)
        return
    if not devices:
        st.info("Register your first device to start monitoring a room.")
        return
    by_id = {device["id"]: device for device in devices}
    if st.session_state.get("selected_device") not in by_id:
        st.session_state["selected_device"] = devices[0]["id"]
    device_id = st.selectbox(
        "Device", list(by_id), key="selected_device",
        format_func=lambda identifier: f"{by_id[identifier]['name']} · {identifier}",
    )
    if len(devices) == 200:
        st.caption("Showing the 200 most recently registered devices.")
    st.caption("Updates every 5 seconds while this page is open. Times are shown in UTC.")
    _render_device(settings, device_id)


@st.fragment(run_every="5s")
def _render_device(settings: Settings, device_id: str) -> None:
    auth = require_session()
    st.button("Refresh readings", key="refresh_readings", icon=":material/refresh:")
    with ApiClient(settings, auth["access_token"]) as client:
        try:
            detail = client.device_detail(device_id)
            readings = client.readings(device_id)
            commands = client.commands(device_id)
        except ApiError as error:
            handle_authenticated_error(error)
            return

        latest = detail["latest_reading"]
        if latest:
            recorded_at = datetime.fromisoformat(latest["recorded_at"])
            received_at = datetime.fromisoformat(latest["received_at"])
            stale = (datetime.now(timezone.utc) - received_at).total_seconds() > 30
            with st.container(horizontal=True):
                st.metric("Temperature", f"{latest['temperature_c']:.1f} °C", border=True)
                st.metric("Reported fan", latest["fan_state"].capitalize(), border=True)
                st.metric("Reading status", "Stale" if stale else "Recent", border=True)
            st.caption(f"Latest measurement: {recorded_at.astimezone(timezone.utc):%Y-%m-%d %H:%M:%S} UTC")
            if stale:
                st.warning("No reading received in the last 30 seconds. Check the device connection.")
        else:
            st.info("Waiting for the device's first reading. Configure its credentials and start the device client.")

        with st.container(border=True):
            st.subheader("Fan control")
            st.caption("Requests are queued. The reported fan state changes after the device sends a new reading.")
            with st.form(f"fan_control_{device_id}"):
                target = st.segmented_control("Requested fan state", ["on", "off"], default="off", format_func=str.capitalize)
                submitted = st.form_submit_button("Send fan command", type="primary")
            if submitted:
                try:
                    command = client.request_fan(device_id, target)
                    commands = [command, *commands][:100]
                    st.success("Fan command queued. Waiting for device acknowledgment.")
                except ApiError as error:
                    handle_authenticated_error(error)

        with st.container(border=True):
            st.subheader("Temperature history")
            if readings:
                frame = pd.DataFrame(readings)[["recorded_at", "temperature_c", "fan_state"]]
                frame["recorded_at"] = pd.to_datetime(frame["recorded_at"], utc=True)
                frame = frame.sort_values("recorded_at").rename(columns={
                    "recorded_at": "Recorded at (UTC)", "temperature_c": "Temperature (°C)", "fan_state": "Reported fan",
                })
                chart = alt.Chart(frame).mark_line(color="#147D92", point=True).encode(
                    x=alt.X("Recorded at (UTC):T", scale=alt.Scale(type="utc")),
                    y=alt.Y("Temperature (°C):Q", scale=alt.Scale(zero=False)),
                    tooltip=[alt.Tooltip("Recorded at (UTC):T", format="%Y-%m-%d %H:%M:%S", timeUnit="utcyearmonthdatehoursminutesseconds"), "Temperature (°C):Q"],
                )
                st.altair_chart(chart, alt="Room temperature over time")
                st.dataframe(frame.iloc[::-1], hide_index=True, alt="Recent temperature readings and reported fan states")
                st.caption("Up to 100 most recent readings.")
            else:
                st.caption("Temperature history will appear when the device sends readings.")

        with st.container(border=True):
            st.subheader("Command history")
            if commands:
                rows = [{
                    "Requested at (UTC)": command["created_at"],
                    "Fan request": command["fan_state"].capitalize(),
                    "Status": "Acknowledged" if command["acknowledged_at"] else "Pending",
                    "Acknowledged at (UTC)": command["acknowledged_at"],
                    "Command ID": command["id"],
                } for command in commands]
                frame = pd.DataFrame(rows)
                for column in ("Requested at (UTC)", "Acknowledged at (UTC)"):
                    frame[column] = pd.to_datetime(frame[column], utc=True)
                st.dataframe(frame, hide_index=True, alt="Recent fan commands and device acknowledgments")
                st.caption("Up to 100 most recent commands. Pending commands remain queued until acknowledged.")
            else:
                st.caption("No fan commands have been requested for this device.")

import streamlit as st
from ui_map import render_map_and_controls

def member_dashboard():
    st.sidebar.markdown('<p class="sidebar-title">👷 Team Panel</p>', unsafe_allow_html=True)
    st.sidebar.write("🗺 My Operations")
    st.sidebar.write("⚠ Issues & Nearby Alerts")

    st.title("👷 Rescue Unit Dashboard")

    tabs = st.tabs(["🗺 My Operation Map", "⚠ Alerts Near Me"])

    with tabs[0]:
        # Map is fullscreen by default
        st.markdown("<style>iframe {height: 85vh !important;}</style>", unsafe_allow_html=True)
        st.info("🤖 **Automatic System Active** - Watch live rescue operations on the map. Units deploy automatically to alerts.")
        render_map_and_controls(admin=False, env=st.session_state.get("env"))

    with tabs[1]:
        st.subheader("🔔 Personal Alerts and Messages")
        key = f"user_{st.session_state.get('username')}"
        notes = st.session_state.get("personal_notifications", {}).get(key, [])
        if not notes:
            st.info("No nearby alerts yet.")
        else:
            for n in notes[-10:]:
                st.warning(f"{n['time']} – {n['msg']}")

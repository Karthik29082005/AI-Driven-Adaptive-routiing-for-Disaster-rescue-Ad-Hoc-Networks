import os
import streamlit as st
from login import login_screen
from admin_dashboard import admin_dashboard
from env_demo import DemoEnv
from movement import init_movement_state
from routing.qlearning import QLearningRouter
from auto_system import run_automatic_system

import importlib
import sys
# Force reload modules that have been recently updated to bypass Streamlit caching bugs
if "commentary" in sys.modules:
    importlib.reload(sys.modules["commentary"])
if "auto_system" in sys.modules:
    importlib.reload(sys.modules["auto_system"])
if "ui_alert" in sys.modules:
    importlib.reload(sys.modules["ui_alert"])

st.set_page_config(layout="wide", page_title="AI-Driven Disaster Rescue Routing")

# Inject custom CSS (resolve path relative to this file)
_src_dir = os.path.dirname(os.path.abspath(__file__))
_style_path = os.path.join(_src_dir, "style.css")
if os.path.exists(_style_path):
    with open(_style_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Initialize base layout
# Login gate - show FIRST, completely bypassing heavy environment initialization 
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ----- USER IS LOGGED IN Past this point -----

# Now perform heavy initialization (OSRM API calls)
if "env" not in st.session_state:
    with st.spinner("Initializing geographical network map... this may take up to a minute."):
        env = DemoEnv()
        st.session_state["env"] = env

        init_movement_state()
        units = {}
        for nid, node in env.nodes.items():
            uid = f"unit_{nid}"
            units[uid] = {
                "id": uid,
                "sim_id": nid,
                "type": node.type,
                "x": node.x,
                "y": node.y,
                "status": "idle",
                "route": [],
                "route_index": 0,
                "assigned_to": None,
            }
        st.session_state["unit_positions"] = units
        st.session_state["ql_router"] = QLearningRouter(env)

env = st.session_state.get("env")
if env:
    run_automatic_system(env)

# Context bar: state + user
role = st.session_state.get("role", "member")
state_name = "Unknown"
if env and hasattr(env, "state"):
    state_name = env.state.get("name", "Unknown")
elif env and hasattr(env, "district"):
    state_name = env.district.get("name", "Unknown")

st.markdown(f"""
<div class="top-bar">
    <div style="display: flex; align-items: center; gap: 15px;">
        <span class="user-info"> {st.session_state.get('full_name', 'User')} <span class="role-badge">{role.upper()}</span></span>
    </div>
    <div style="display: flex; align-items: center; gap: 15px;">
        <span style="color: var(--accent-cyan); font-weight: 500;">🎯 {state_name}</span>
        <span style="color: var(--success); font-weight: 500; display: flex; align-items: center; gap: 6px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 8px var(--success);"></span> System Online
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

col_blank, col_logout = st.columns([5, 1])
with col_logout:
    if st.button("Log out", use_container_width=True):
        env = st.session_state.get("env")
        ql = st.session_state.get("ql_router")
        st.session_state.clear()
        st.session_state["env"] = env
        st.session_state["ql_router"] = ql
        st.rerun()
st.markdown("---")


if role == "admin":
    admin_dashboard()
else:
    st.error("Access Denied. Only admin accounts can access the dashboard.")
    st.stop()

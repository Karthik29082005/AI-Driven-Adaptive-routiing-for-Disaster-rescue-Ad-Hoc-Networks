import os
import streamlit as st
from login import login_screen
from admin_dashboard import admin_dashboard
from member_dashboard import member_dashboard
from env_demo import DemoEnv
from movement import init_movement_state
from routing.qlearning import QLearningRouter
from auto_system import run_automatic_system

st.set_page_config(layout="wide", page_title="AI-Driven Disaster Rescue Routing")

# Inject custom CSS
style_path = os.path.join("src", "style.css")
if os.path.exists(style_path):
    with open(style_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<div class="app-header">🚁 AI-Driven Disaster Rescue Routing System</div>', unsafe_allow_html=True)

# Initialize environment and units once
if "env" not in st.session_state:
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

# Display selected state information
env = st.session_state.get("env")
if env and hasattr(env, "state"):
    state = env.state
    st.info(f"🎯 **Rescue Operations Active in:** {state['name']} State | 🤖 **Automatic Mode: ON**")
elif env and hasattr(env, "district"):
    # Backward compatibility
    district = env.district
    st.info(f"🎯 **Rescue Operations Active in:** {district.get('name', 'Unknown')} | 🤖 **Automatic Mode: ON**")

# Login gate
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# Run automatic alert generation and deployment system
if env:
    run_automatic_system(env)

role = st.session_state.get("role", "member")

top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.write(f"Logged in as **{st.session_state.get('full_name','User')}** ({role})")
with top_col2:
    if st.button("Logout"):
        env = st.session_state.get("env")
        ql = st.session_state.get("ql_router")
        st.session_state.clear()
        st.session_state["env"] = env
        st.session_state["ql_router"] = ql
        st.rerun()


if role == "admin":
    admin_dashboard()
else:
    member_dashboard()

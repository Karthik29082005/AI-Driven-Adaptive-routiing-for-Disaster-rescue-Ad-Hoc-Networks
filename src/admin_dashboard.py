import streamlit as st
import pandas as pd
from ui_map import render_map_and_controls
from ui_alert import dispatch_ui
from rl_graph import show_rl_performance_graph
from admin_user_mgmt import admin_user_management
from db_logs import fetch_all

def show_reports():
    st.header("📊 Operational Reports")

    report_type = st.selectbox(
        "Select Report Type",
        ["Alerts", "Assignments", "Failures", "AI Performance"]
    )
    table_map = {
        "Alerts": "alerts",
        "Assignments": "assignments",
        "Failures": "failures",
        "AI Performance": "rl_metrics"
    }
    rows = fetch_all(table_map[report_type])
    if not rows:
        st.info("No records found for this report.")
        return

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False),
        file_name=f"{table_map[report_type]}_report.csv"
    )

def admin_dashboard():
    st.sidebar.markdown('<p class="sidebar-title">☑ Admin Menu</p>', unsafe_allow_html=True)
    st.sidebar.write("📌 Live Map")
    st.sidebar.write("🚨 Alerts")
    st.sidebar.write("📈 AI Performance")
    st.sidebar.write("🧑‍🤝‍🧑 Team")
    st.sidebar.write("📊 Reports")

    st.title("🚁 Command & Control Dashboard")

    tabs = st.tabs([
        "🗺 Live Map",
        "🚨 Alerts & Deployment",
        "📈 AI Performance",
        "🧑‍🤝‍🧑 Team Management",
        "📊 Reports"
    ])

    with tabs[0]:
        # Map is fullscreen by default
        st.markdown("<style>iframe {height: 85vh !important;}</style>", unsafe_allow_html=True)
        st.info("🤖 **Automatic System Active** - Alerts are generated automatically every 30-60 seconds. Units deploy automatically.")
        render_map_and_controls(admin=True, env=st.session_state.get("env"))

    with tabs[1]:
        st.info("🤖 **Automatic Mode**: The system automatically generates alerts and deploys units. Manual alerts below are optional.")
        dispatch_ui(env=st.session_state.get("env"))
        
        # Show active automatic alerts
        st.markdown("### 📊 Active Automatic Alerts")
        active_alerts = st.session_state.get("active_alerts", [])
        if active_alerts:
            import time
            current_time = time.time()
            for alert in active_alerts[-5:]:  # Show last 5
                age = int(current_time - alert.get("time", 0))
                st.write(f"🚨 **{alert.get('severity', 'Unknown')}** severity at ({alert['lat']:.4f}, {alert['lon']:.4f}) - {age}s ago")
        else:
            st.info("No active alerts. New alerts will be generated automatically.")

    with tabs[2]:
        show_rl_performance_graph()

    with tabs[3]:
        admin_user_management()

    with tabs[4]:
        show_reports()

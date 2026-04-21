import streamlit as st
import pandas as pd
from ui_map import render_map_and_controls
from ui_alert import dispatch_ui
from rl_graph import show_rl_performance_graph
from admin_user_mgmt import admin_user_management
from db_logs import fetch_all
from commentary import get_commentary_entries, clear_commentary
from routing_comparison import render_routing_comparison_dashboard

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

def render_live_commentary():
    """Render the live commentary panel in the sidebar."""
    st.sidebar.markdown('<p class="sidebar-title">📻 Live Disaster Commentary</p>', unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear", key="clear_comm", use_container_width=True):
            clear_commentary()
            st.rerun()
    with col2:
        if st.button("🔄 Refresh", key="refresh_comm", use_container_width=True):
            st.rerun()
    st.sidebar.caption("Live feed of disaster events")
    st.sidebar.markdown("---")
    
    # Get commentary entries
    entries = get_commentary_entries(limit=50)
    
    if not entries:
        st.sidebar.info("📡 **Waiting for disaster events...**\n\nCommentary will appear here as rescue operations begin.")
        return
    
    # Create a scrollable container for commentary
    st.sidebar.markdown("### 📝 Real-Time Updates")
    st.sidebar.markdown(f"*Showing {len(entries)} recent events*")
    st.sidebar.markdown("---")
    
    # Display commentary entries (newest first) in a scrollable container
    commentary_container = st.sidebar.container()
    
    with commentary_container:
        for i, entry in enumerate(entries):
            timestamp = entry.get("timestamp", "00:00:00")
            text = entry.get("text", "")
            event_type = entry.get("event_type", "")
            
            # Style based on event type with different colors
            if "alert" in event_type or "emergency" in text.lower() or "🚨" in text:
                st.markdown(f"""
                <div class="comm-notif comm-alert">
                    <span class="comm-time">{timestamp}</span>
                    <span class="comm-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)
            elif "failed" in event_type or "failure" in text.lower() or "❌" in text:
                st.markdown(f"""
                <div class="comm-notif comm-fail">
                    <span class="comm-time">{timestamp}</span>
                    <span class="comm-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)
            elif "arrived" in event_type or "success" in text.lower() or "✅" in text:
                st.markdown(f"""
                <div class="comm-notif comm-success">
                    <span class="comm-time">{timestamp}</span>
                    <span class="comm-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)
            elif "ai" in event_type.lower() or "🤖" in text or "🧠" in text:
                st.markdown(f"""
                <div class="comm-notif comm-ai">
                    <span class="comm-time">{timestamp}</span>
                    <span class="comm-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="comm-notif comm-info">
                    <span class="comm-time">{timestamp}</span>
                    <span class="comm-text">{text}</span>
                </div>
                """, unsafe_allow_html=True)

def admin_dashboard():
    render_live_commentary()

    st.markdown("## Command & Control Dashboard")
    st.caption("Use the tabs below to view the live map, manage alerts, monitor AI performance, and run reports.")

    tabs = st.tabs([
        "🗺 Live Map",
        "🚨 Alerts & Deployment",
        "📈 AI Performance",
        "🔄 Routing Comparison",
        "🧑‍🤝‍🧑 Team Management",
        "📊 Reports"
    ])

    with tabs[0]:
        st.markdown("### 📍 Live Map")
        st.markdown("Real-time view of rescue units, alerts, and routes. Alerts are generated automatically every 30–60 seconds.")
        st.markdown("<style>iframe {height: 75vh !important;}</style>", unsafe_allow_html=True)
        render_map_and_controls(admin=True, env=st.session_state.get("env"))

    with tabs[1]:
        st.markdown("### 🚨 Active Alerts")
        st.markdown("Units are deployed automatically to new alerts.")
        dispatch_ui(env=st.session_state.get("env"))
        st.markdown("---")
        st.markdown("**Active automatic alerts**")
        active_alerts = st.session_state.get("active_alerts", [])
        if active_alerts:
            import time
            current_time = time.time()
            for alert in active_alerts[-5:]:
                age = int(current_time - alert.get("time", 0))
                st.write(f"🚨 **{alert.get('severity', 'Unknown')}** at ({alert['lat']:.4f}, {alert['lon']:.4f}) — *{age}s ago*")
        else:
            st.info("No active alerts. New alerts will appear here when generated.")

    with tabs[2]:
        st.markdown("### 📈 AI Performance")
        st.markdown("Q-Learning router performance over time.")
        show_rl_performance_graph()

    with tabs[3]:
        st.markdown("### 🔄 Routing Comparison")
        st.markdown("Compare rerouting time: Q-Learning vs Dijkstra when a node fails.")
        render_routing_comparison_dashboard()

    with tabs[4]:
        st.markdown("### Team Management")
        st.markdown("Add and manage team members and their assignments.")
        admin_user_management()

    with tabs[5]:
        st.markdown("### 📊 Reports")
        st.markdown("View and download operational data (alerts, assignments, failures, AI metrics).")
        show_reports()

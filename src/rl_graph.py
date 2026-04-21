"""
RL Performance Graph - Enhanced UI with multiple visualizations
"""
import streamlit as st
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import numpy as np
from db_logs import fetch_all

def show_rl_performance_graph():
    st.markdown("### 📈 Q-Learning Performance Analysis")
    st.caption("Track how the AI router improves over time as it learns from rerouting events.")
    
    # Check if Q-Learning router exists
    ql_router = st.session_state.get("ql_router")
    if not ql_router:
        st.warning("Q-Learning router not initialized. Please refresh the page.")
        return
    
    # Get logs from session state
    logs = st.session_state.get("rl_logs", [])
    
    # Also try to get from database
    db_logs = fetch_all("rl_metrics")
    
    # Combine and deduplicate
    all_logs = []
    seen_episodes = set()
    
    # Add session logs
    for log in logs:
        ep = log.get("episode", 0)
        if ep not in seen_episodes:
            all_logs.append({
                "episode": ep,
                "time": log.get("time", 0),
                "improvement": log.get("improvement", 0)
            })
            seen_episodes.add(ep)
    
    # Add database logs (if not already in session logs)
    for db_log in db_logs:
        ep = db_log[1] if len(db_log) > 1 else 0  # episode is second column
        if ep not in seen_episodes:
            all_logs.append({
                "episode": ep,
                "time": db_log[2] if len(db_log) > 2 else 0,  # time_taken
                "improvement": db_log[3] if len(db_log) > 3 else 0  # improvement
            })
            seen_episodes.add(ep)
    
    # Sort by episode
    all_logs.sort(key=lambda x: x.get("episode", 0))
    
    if len(all_logs) < 1:
        st.info("""
        **No rerouting data yet.** 
        
        To generate RL learning data:
        1. Go to the **Live Map** tab
        2. Click **"Simulate unit failure"** to trigger a rerouting event
        3. The AI will reroute using Q-Learning and data will appear here
        
        The graph will show how the AI improves its rerouting speed over time.
        """)
        
        # Option to train the Q-Learning router
        st.markdown("---")
        st.markdown("**Pre-train Q-Learning Router**")
        st.caption("Train the router on random paths to improve initial performance.")
        if st.button("Train Q-Learning Router (50 episodes)", type="primary"):
            with st.spinner("Training Q-Learning router... This may take a moment."):
                ql_router.train(episodes=50)
            st.success("✅ Q-Learning router trained! Now simulate failures to see performance.")
        return
    
    if len(all_logs) < 2:
        st.info(f"""
        **Only {len(all_logs)} rerouting event recorded.** 
        
        Need at least 2 events to show learning trends. 
        Simulate more unit failures in the **Live Map** tab to see the graph.
        """)
        
        # Show single data point
        if all_logs:
            log = all_logs[0]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Episode", log.get("episode", 0))
            with col2:
                st.metric("Rerouting Time", f"{log.get('time', 0)*1000:.2f} ms")
            with col3:
                st.metric("Improvement", f"{log.get('improvement', 0):.1f}%")
        return
    
    # Statistics summary
    episodes = [log.get("episode", 0) for log in all_logs]
    times = [log.get("time", 0) * 1000 for log in all_logs]  # Convert to ms
    improvements = [log.get("improvement", 0) for log in all_logs]
    
    st.markdown("#### 📊 Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Episodes", len(all_logs))
    with col2:
        avg_time = np.mean(times) if times else 0
        st.metric("Avg Reroute Time", f"{avg_time:.2f} ms")
    with col3:
        best_time = min(times) if times else 0
        st.metric("Best Time", f"{best_time:.2f} ms")
    with col4:
        if len(times) > 1 and max(times) > 0:
            total_improvement = ((max(times) - min(times)) / max(times)) * 100.0
            st.metric("Total Improvement", f"{total_improvement:.1f}%")
        else:
            st.metric("Total Improvement", "N/A")
    
    st.markdown("---")
    
    # Create visualizations
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Chart 1: Rerouting Time Over Episodes
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(episodes, times, marker='o', linewidth=2.5, markersize=6, 
             color='#1976d2', label='Rerouting Time', zorder=3)
    ax1.fill_between(episodes, times, alpha=0.2, color='#1976d2')
    ax1.set_xlabel('Episode (Rerouting Event)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Time (milliseconds)', fontsize=11, fontweight='bold')
    ax1.set_title('⚡ Q-Learning Rerouting Performance', fontsize=12, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=10)
    
    # Add trend line
    if len(episodes) > 2:
        z = np.polyfit(episodes, times, 1)
        p = np.poly1d(z)
        ax1.plot(episodes, p(episodes), "r--", alpha=0.5, linewidth=1.5, label='Trend')
        ax1.legend(fontsize=10)
    
    # Chart 2: Improvement Percentage
    ax2 = fig.add_subplot(gs[0, 1])
    colors = ['#4caf50' if imp >= 0 else '#f44336' for imp in improvements]
    ax2.bar(episodes, improvements, color=colors, alpha=0.7, width=0.6)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Episode', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Improvement (%)', fontsize=11, fontweight='bold')
    ax2.set_title('📈 Improvement per Episode', fontsize=12, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Chart 3: Time Distribution Histogram
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.hist(times, bins=min(10, len(times)), color='#ff9800', alpha=0.7, edgecolor='black')
    ax3.axvline(avg_time, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_time:.2f}ms')
    ax3.set_xlabel('Rerouting Time (ms)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax3.set_title('📊 Time Distribution', fontsize=12, fontweight='bold', pad=10)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Chart 4: Cumulative Improvement
    ax4 = fig.add_subplot(gs[1, 1])
    cumulative_improvement = []
    running_min = float('inf')
    for t in times:
        running_min = min(running_min, t)
        if len(times) > 0 and max(times) > 0:
            cum_imp = ((max(times) - running_min) / max(times)) * 100
            cumulative_improvement.append(cum_imp)
        else:
            cumulative_improvement.append(0)
    
    ax4.plot(episodes, cumulative_improvement, marker='s', linewidth=2.5, 
             markersize=6, color='#9c27b0', label='Cumulative Improvement')
    ax4.fill_between(episodes, cumulative_improvement, alpha=0.2, color='#9c27b0')
    ax4.set_xlabel('Episode', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Cumulative Improvement (%)', fontsize=11, fontweight='bold')
    ax4.set_title(' Learning Progress', fontsize=12, fontweight='bold', pad=10)
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.legend(fontsize=10)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Performance insights
    st.markdown("---")
    st.markdown("#### 💡 Performance Insights")
    
    if len(times) > 1:
        best_idx = times.index(min(times))
        worst_idx = times.index(max(times))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"""
            **Best Performance** (Episode {episodes[best_idx]})
            - Time: {min(times):.2f} ms
            - Improvement: {improvements[best_idx]:.1f}%
            """)
        
        with col2:
            if worst_idx != best_idx:
                st.info(f"""
                **Worst Performance** (Episode {episodes[worst_idx]})
                - Time: {max(times):.2f} ms
                - Improvement: {improvements[worst_idx]:.1f}%
                """)
        
        # Trend analysis
        if len(times) >= 3:
            recent_avg = np.mean(times[-3:])
            early_avg = np.mean(times[:3])
            trend = "improving" if recent_avg < early_avg else "degrading" if recent_avg > early_avg else "stable"
            trend_icon = "📈" if trend == "improving" else "📉" if trend == "degrading" else "➡️"
            
            st.markdown(f"""
            **Trend Analysis:** {trend_icon} The router is **{trend}**.
            - Early episodes average: {early_avg:.2f} ms
            - Recent episodes average: {recent_avg:.2f} ms
            """)
    
    # Data table
    st.markdown("---")
    st.markdown("#### 📋 Detailed Data")
    
    import pandas as pd
    df_data = []
    for log in all_logs:
        df_data.append({
            "Episode": log.get("episode", 0),
            "Time (ms)": f"{log.get('time', 0)*1000:.2f}",
            "Improvement (%)": f"{log.get('improvement', 0):.1f}"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Performance Data (CSV)",
        data=csv,
        file_name=f"rl_performance_{len(all_logs)}_episodes.csv",
        mime="text/csv"
    )

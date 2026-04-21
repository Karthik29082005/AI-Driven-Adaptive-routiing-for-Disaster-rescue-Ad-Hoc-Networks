"""
Routing Comparison Dashboard
Compares Q-Learning vs Dijkstra's algorithm rerouting performance.
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Streamlit
import matplotlib.pyplot as plt
import numpy as np

def get_comparison_data():
    """Get routing comparison data from session state."""
    return st.session_state.get("routing_comparison_logs", [])

def render_routing_comparison_dashboard():
    """Render the routing comparison dashboard."""
    st.markdown("### 🔄 Q-Learning vs Dijkstra Rerouting Comparison")
    
    comparison_logs = get_comparison_data()
    
    if not comparison_logs:
        st.info("📊 **No rerouting comparisons yet.**\n\nComparisons will appear here when units fail and rerouting occurs.")
        return
    
    # Get latest comparison
    latest = comparison_logs[-1]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ql_time = latest.get("ql_time", 0) * 1000  # Convert to milliseconds
        st.metric("Q-Learning Time", f"{ql_time:.2f} ms")
    
    with col2:
        dijkstra_time = latest.get("dijkstra_time", 0)
        if dijkstra_time is not None:
            dijkstra_time_ms = dijkstra_time * 1000
            st.metric("Dijkstra Time", f"{dijkstra_time_ms:.2f} ms")
        else:
            st.metric("Dijkstra Time", "N/A")
    
    with col3:
        time_diff = latest.get("time_difference", 0)
        if time_diff is not None:
            time_diff_ms = time_diff * 1000
            if time_diff > 0:
                st.metric("Time Difference", f"⚡ {time_diff_ms:.2f} ms faster", delta=f"{time_diff_ms:.2f} ms")
            else:
                st.metric("Time Difference", f"⚠️ {abs(time_diff_ms):.2f} ms slower", delta=f"{time_diff_ms:.2f} ms")
        else:
            st.metric("Time Difference", "N/A")
    
    with col4:
        speedup = latest.get("speedup_factor", 0)
        if speedup is not None and speedup > 0:
            st.metric("Speedup Factor", f"{speedup:.2f}x")
        else:
            st.metric("Speedup Factor", "N/A")
    
    st.markdown("---")
    
    # Statistics from all comparisons
    if len(comparison_logs) > 1:
        st.markdown("#### 📊 Overall Statistics")
        
        # Filter valid comparisons (where both times exist)
        valid_comparisons = [
            c for c in comparison_logs 
            if c.get("dijkstra_time") is not None and c.get("ql_time") is not None
        ]
        
        if valid_comparisons:
            ql_times = [c["ql_time"] * 1000 for c in valid_comparisons]
            dijkstra_times = [c["dijkstra_time"] * 1000 for c in valid_comparisons]
            time_diffs = [c["time_difference"] * 1000 for c in valid_comparisons if c.get("time_difference") is not None]
            speedups = [c["speedup_factor"] for c in valid_comparisons if c.get("speedup_factor") is not None]
            
            stat_cols = st.columns(4)
            
            with stat_cols[0]:
                st.metric("Avg Q-Learning Time", f"{np.mean(ql_times):.2f} ms")
                st.caption(f"Min: {np.min(ql_times):.2f} ms | Max: {np.max(ql_times):.2f} ms")
            
            with stat_cols[1]:
                st.metric("Avg Dijkstra Time", f"{np.mean(dijkstra_times):.2f} ms")
                st.caption(f"Min: {np.min(dijkstra_times):.2f} ms | Max: {np.max(dijkstra_times):.2f} ms")
            
            with stat_cols[2]:
                if time_diffs:
                    avg_diff = np.mean(time_diffs)
                    st.metric("Avg Time Difference", f"{avg_diff:.2f} ms")
                    faster_count = sum(1 for d in time_diffs if d > 0)
                    st.caption(f"Q-Learning faster: {faster_count}/{len(time_diffs)} times")
            
            with stat_cols[3]:
                if speedups:
                    avg_speedup = np.mean(speedups)
                    st.metric("Avg Speedup", f"{avg_speedup:.2f}x")
                    st.caption(f"Best: {np.max(speedups):.2f}x")
                else:
                    st.metric("Avg Speedup", "N/A")
            
            st.markdown("---")
            
            # Visualization
            if len(valid_comparisons) >= 1:
                st.markdown("#### 📈 Performance Comparison Chart")
            
            fig, axes = plt.subplots(2, 1, figsize=(12, 8))
            
            # Time comparison chart
            episodes = list(range(1, len(valid_comparisons) + 1))
            ax1 = axes[0]
            ax1.plot(episodes, ql_times, 'o-', label='Q-Learning', color='#17a2b8', linewidth=2, markersize=6)
            ax1.plot(episodes, dijkstra_times, 's-', label="Dijkstra's", color='#dc3545', linewidth=2, markersize=6)
            ax1.set_xlabel('Rerouting Episode', fontsize=12)
            ax1.set_ylabel('Time (ms)', fontsize=12)
            ax1.set_title('Rerouting Time Comparison: Q-Learning vs Dijkstra', fontsize=14, fontweight='bold')
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3)
            
            
            # Time difference chart
            if time_diffs:
                ax2 = axes[1]
                colors = ['#28a745' if d > 0 else '#dc3545' for d in time_diffs]
                ax2.bar(episodes[:len(time_diffs)], time_diffs, color=colors, alpha=0.7)
                ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
                ax2.set_xlabel('Rerouting Episode', fontsize=12)
                ax2.set_ylabel('Time Difference (ms)', fontsize=12)
                ax2.set_title('Time Difference: Positive = Q-Learning Faster, Negative = Dijkstra Faster', fontsize=12, fontweight='bold')
                ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            st.markdown("---")
            
            # Speedup factor chart
            if speedups:
                st.markdown("#### ⚡ Speedup Factor Over Time")
                fig2, ax3 = plt.subplots(figsize=(12, 5))
                ax3.plot(episodes[:len(speedups)], speedups, 'o-', color='#ffc107', linewidth=2, markersize=6)
                ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=1, label='No speedup (1x)')
                ax3.set_xlabel('Rerouting Episode', fontsize=12)
                ax3.set_ylabel('Speedup Factor (x)', fontsize=12)
                ax3.set_title('Q-Learning Speedup Factor vs Dijkstra', fontsize=14, fontweight='bold')
                ax3.legend(fontsize=11)
                ax3.grid(True, alpha=0.3)
                st.pyplot(fig2)
    
    st.markdown("---")
    
    # Recent comparisons table
    st.markdown("#### 📋 Recent Rerouting Comparisons")
    
    if comparison_logs:
        # Prepare data for table
        table_data = []
        for comp in comparison_logs[-10:]:  # Show last 10
            timestamp = datetime.fromtimestamp(comp.get("timestamp", time.time())).strftime("%H:%M:%S")
            ql_t = comp.get("ql_time", 0) * 1000
            dijk_t = comp.get("dijkstra_time", 0)
            dijk_t_ms = dijk_t * 1000 if dijk_t is not None else None
            diff = comp.get("time_difference", 0)
            diff_ms = diff * 1000 if diff is not None else None
            speedup = comp.get("speedup_factor", 0)
            
            table_data.append({
                "Episode": comp.get("episode", 0),
                "Time": timestamp,
                "Q-Learning (ms)": f"{ql_t:.2f}",
                "Dijkstra (ms)": f"{dijk_t_ms:.2f}" if dijk_t_ms is not None else "N/A",
                "Difference (ms)": f"{diff_ms:.2f}" if diff_ms is not None else "N/A",
                "Speedup": f"{speedup:.2f}x" if speedup and speedup > 0 else "N/A",
                "QL Route Length": comp.get("ql_route_length", 0),
                "Dijkstra Route Length": comp.get("dijkstra_route_length", 0) or "N/A"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Comparison Data (CSV)",
            data=csv,
            file_name=f"routing_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def render_quick_comparison_summary():
    """Render a quick summary widget for the main dashboard."""
    comparison_logs = get_comparison_data()
    
    if not comparison_logs:
        return
    
    valid_comparisons = [
        c for c in comparison_logs 
        if c.get("dijkstra_time") is not None and c.get("ql_time") is not None
    ]
    
    if not valid_comparisons:
        return
    
    latest = valid_comparisons[-1]
    
    st.markdown("#### 🔄 Latest Rerouting Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ql_time = latest.get("ql_time", 0) * 1000
        st.metric("Q-Learning", f"{ql_time:.2f} ms", delta=None)
    
    with col2:
        dijkstra_time = latest.get("dijkstra_time", 0) * 1000
        st.metric("Dijkstra", f"{dijkstra_time:.2f} ms", delta=None)
    
    time_diff = latest.get("time_difference", 0) * 1000
    speedup = latest.get("speedup_factor", 0)
    
    if time_diff > 0:
        st.success(f"⚡ Q-Learning is {time_diff:.2f} ms faster ({speedup:.2f}x speedup)")
    elif time_diff < 0:
        st.warning(f"⚠️ Dijkstra is {abs(time_diff):.2f} ms faster")
    else:
        st.info("⏱️ Both methods took the same time")

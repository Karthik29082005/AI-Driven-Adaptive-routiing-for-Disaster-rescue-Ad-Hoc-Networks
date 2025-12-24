import streamlit as st
import matplotlib.pyplot as plt

def show_rl_performance_graph():
    logs = st.session_state.get("rl_logs", [])
    if len(logs) < 2:
        st.info("Need more reroute events to show RL learning graph.")
        return

    episodes = [log["episode"] for log in logs]
    times = [log["time"] for log in logs]

    plt.figure(figsize=(7, 4))
    plt.plot(episodes, times, marker="o", lw=2, color="#007bff")
    plt.xlabel("Episode (Failure Event)")
    plt.ylabel("Rerouting Time (sec)")
    plt.title("⚡ RL Performance – Rerouting Time per Episode")
    plt.grid(True)
    st.pyplot(plt)

    if max(times) > 0:
        improvement = ((max(times) - min(times)) / max(times)) * 100.0
        st.success(f"⚡ RL Routing Speed Improvement: {improvement:.1f}%")

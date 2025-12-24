import random
import time
from collections import defaultdict
import streamlit as st
from db_logs import save_rl_metric

class QLearningRouter:
    def __init__(self, env, alpha=0.6, gamma=0.8, epsilon=0.2):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.episode_count = 0

    def get_state(self, node_id):
        node = self.env.nodes[node_id]
        deg = self.env.G.degree[node_id] if node_id in self.env.G else 0
        return (round(node.x, 2), round(node.y, 2), deg)

    def choose_action(self, node_id):
        neighbors = list(self.env.G.neighbors(node_id)) if node_id in self.env.G else []
        if not neighbors:
            return None
        state = self.get_state(node_id)
        if random.random() < self.epsilon:
            return random.choice(neighbors)
        return max(neighbors, key=lambda nxt: self.q_table[state][nxt])

    def train(self, episodes=50):
        node_ids = list(self.env.nodes.keys())
        for ep in range(episodes):
            src = random.choice(node_ids)
            dst = random.choice(node_ids)
            if src == dst:
                continue
            current = src
            steps = 0
            while current != dst and steps < 25:
                state = self.get_state(current)
                action = self.choose_action(current)
                if action is None:
                    break
                if action == dst:
                    r = 10.0
                else:
                    r = -1.0
                next_state = self.get_state(action)
                future = 0.0
                neighbors_next = list(self.env.G.neighbors(action)) if action in self.env.G else []
                if neighbors_next:
                    future = max(self.q_table[next_state][nxt] for nxt in neighbors_next)
                old_q = self.q_table[state][action]
                self.q_table[state][action] = old_q + self.alpha * (r + self.gamma * future - old_q)
                current = action
                steps += 1
        st.session_state["ql_trained"] = True

    def reroute_on_failure(self, start_id, goal_id):
        self.episode_count += 1
        start_time = time.time()
        route = [start_id]
        current = start_id
        steps = 0
        while current != goal_id and steps < 30:
            action = self.choose_action(current)
            if action is None or action in route:
                break
            route.append(action)
            current = action
            steps += 1
        elapsed = time.time() - start_time

        st.session_state.setdefault("rl_logs", [])
        logs = st.session_state["rl_logs"]
        prev_time = logs[-1]["time"] if logs else None
        if prev_time is not None and prev_time > 0:
            improvement = ((prev_time - elapsed) / prev_time) * 100.0
        else:
            improvement = 0.0

        logs.append({
            "episode": self.episode_count,
            "time": elapsed,
            "route": route,
            "improvement": improvement
        })

        save_rl_metric(self.episode_count, elapsed, improvement)

        popup = (
            f"⚡ Q-Learning Rerouting Completed!\n"
            f"⏱ Time Taken: {elapsed:.2f} seconds\n"
            f"📈 Improvement: {improvement:.1f}% vs last reroute"
        )
        st.session_state.setdefault("notifications", []).append({"type": "rl", "text": popup})
        st.success(popup)

        return route, elapsed

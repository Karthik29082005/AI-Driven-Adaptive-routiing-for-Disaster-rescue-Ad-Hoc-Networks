import random
import time
from collections import defaultdict
import streamlit as st
from db_logs import save_rl_metric
from commentary import add_commentary
import networkx as nx

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

    def dijkstra_reroute(self, start_id, goal_id):
        """Calculate reroute using Dijkstra's algorithm for comparison."""
        try:
            start_time = time.time()
            if start_id not in self.env.G or goal_id not in self.env.G:
                return None, None
            
            # Use NetworkX shortest path (Dijkstra)
            path = nx.shortest_path(self.env.G, start_id, goal_id, weight="weight")
            elapsed = time.time() - start_time
            return path, elapsed
        except (nx.NetworkXNoPath, nx.NodeNotFound, KeyError):
            return None, None

    def reroute_on_failure(self, start_id, goal_id):
        self.episode_count += 1
        
        # Q-Learning rerouting
        ql_start_time = time.time()
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
        ql_elapsed = time.time() - ql_start_time

        # Dijkstra rerouting for comparison
        dijkstra_route, dijkstra_time = self.dijkstra_reroute(start_id, goal_id)
        
        # Calculate comparison metrics
        time_difference = None
        speedup_factor = None
        if dijkstra_time is not None:
            time_difference = dijkstra_time - ql_elapsed
            if dijkstra_time > 0:
                speedup_factor = (dijkstra_time / ql_elapsed) if ql_elapsed > 0 else None

        # Store comparison data
        comparison_data = {
            "episode": self.episode_count,
            "ql_time": ql_elapsed,
            "dijkstra_time": dijkstra_time,
            "time_difference": time_difference,
            "speedup_factor": speedup_factor,
            "ql_route_length": len(route),
            "dijkstra_route_length": len(dijkstra_route) if dijkstra_route else None,
            "timestamp": time.time()
        }
        
        # Initialize comparison logs if not exists
        if "routing_comparison_logs" not in st.session_state:
            st.session_state["routing_comparison_logs"] = []
        
        st.session_state["routing_comparison_logs"].append(comparison_data)
        
        # Keep only last 100 comparisons
        if len(st.session_state["routing_comparison_logs"]) > 100:
            st.session_state["routing_comparison_logs"] = st.session_state["routing_comparison_logs"][-100:]

        st.session_state.setdefault("rl_logs", [])
        logs = st.session_state["rl_logs"]
        prev_time = logs[-1]["time"] if logs else None
        if prev_time is not None and prev_time > 0:
            improvement = ((prev_time - ql_elapsed) / prev_time) * 100.0
        else:
            improvement = 0.0

        logs.append({
            "episode": self.episode_count,
            "time": ql_elapsed,
            "route": route,
            "improvement": improvement
        })

        save_rl_metric(self.episode_count, ql_elapsed, improvement)
        
        # Add commentary for AI rerouting with comparison info
        if dijkstra_time is not None and time_difference is not None:
            if time_difference > 0:
                add_commentary("ai_reroute",
                              improvement=f"{time_difference*1000:.1f}ms faster than Dijkstra")
            else:
                add_commentary("ai_reroute",
                              improvement=f"{abs(time_difference)*1000:.1f}ms slower than Dijkstra")
        else:
            add_commentary("ai_reroute",
                          improvement=f"{improvement:.1f}% improvement over previous route")

        popup = (
            f"⚡ Q-Learning Rerouting Completed!\n"
            f"⏱ Q-Learning Time: {ql_elapsed*1000:.2f}ms"
        )
        if dijkstra_time is not None:
            popup += f"\n⏱ Dijkstra Time: {dijkstra_time*1000:.2f}ms"
            if time_difference is not None:
                if time_difference > 0:
                    popup += f"\n🚀 Q-Learning is {time_difference*1000:.2f}ms faster ({speedup_factor:.2f}x speedup)"
                else:
                    popup += f"\n⚠️ Q-Learning is {abs(time_difference)*1000:.2f}ms slower"
        
        st.session_state.setdefault("notifications", []).append({"type": "rl", "text": popup})
        st.success(popup)

        return route, ql_elapsed

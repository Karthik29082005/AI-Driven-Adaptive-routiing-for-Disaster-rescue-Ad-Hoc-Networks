import math
import time
import streamlit as st

SPEED_PROFILE_KMPH = {
    "drone": 25.0,
    "van": 70.0,
    "ambulance": 100.0,
    "rescue_team": 6.0,
    "fire_truck": 60.0,
    "police": 80.0,
}

def init_movement_state():
    if "last_move_ts" not in st.session_state:
        st.session_state["last_move_ts"] = time.time()
    if "unit_positions" not in st.session_state:
        st.session_state["unit_positions"] = {}

def update_movements():
    init_movement_state()
    now = time.time()
    dt = now - st.session_state["last_move_ts"]
    if dt <= 0:
        return
    st.session_state["last_move_ts"] = now

    units = st.session_state["unit_positions"]

    for uid, u in units.items():
        status = u.get("status", "idle")
        if status not in ("moving", "en_route"):
            continue
        route = u.get("route") or []
        idx = u.get("route_index", 0)
        if len(route) == 0 or idx >= len(route):
            u["status"] = "idle"
            u["route_index"] = 0
            continue

        cx, cy = u["x"], u["y"]
        tx, ty = route[idx]

        dx_km = (tx - cx) * 111.0
        dy_km = (ty - cy) * 111.0
        dist_km = math.hypot(dx_km, dy_km)

        if dist_km < 0.01:
            u["x"], u["y"] = tx, ty
            u["route_index"] = idx + 1
            if u["route_index"] >= len(route):
                u["status"] = "arrived"
            continue

        speed = SPEED_PROFILE_KMPH.get(u["type"], 30.0)
        step_km = speed * (dt / 3600.0)

        if step_km >= dist_km:
            u["x"], u["y"] = tx, ty
            u["route_index"] = idx + 1
            if u["route_index"] >= len(route):
                u["status"] = "arrived"
            continue

        frac = step_km / dist_km
        new_lon = cx + (tx - cx) * frac
        new_lat = cy + (ty - cy) * frac

        u["x"], u["y"] = new_lon, new_lat
        u["route_index"] = idx

def assign_route_to_unit(uid: str, route_nodes, env):
    if "unit_positions" not in st.session_state:
        return
    u = st.session_state["unit_positions"].get(uid)
    if not u:
        return
    waypoints = []
    for nid in route_nodes:
        node = env.nodes[nid]
        waypoints.append((node.x, node.y))  # (lon, lat)
    u["route"] = waypoints
    u["route_index"] = 0
    u["status"] = "moving"

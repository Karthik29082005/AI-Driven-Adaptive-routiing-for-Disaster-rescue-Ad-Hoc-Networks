import math
import datetime
import streamlit as st
from db_logs import save_failure

BROKEN_ICONS = {
    "drone": "models/drone_broken.png",
    "ambulance": "models/ambulance_broken.png",
    "van": "models/van_broken.png",
    "fire_truck": "models/fire_truck_broken.png",
    "police": "models/police_broken.png",
}

def handle_unit_failure(unit_id, reason, env=None):
    if "unit_positions" not in st.session_state:
        return None

    units = st.session_state["unit_positions"]
    unit = units.get(unit_id)
    if not unit:
        return None

    unit["status"] = "failed"
    unit["route"] = []
    unit["route_index"] = 0

    lat = unit["y"]
    lon = unit["x"]
    utype = unit["type"]

    event = {
        "unit_id": unit_id,
        "unit_type": utype,
        "lat": lat,
        "lon": lon,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reason": reason,
        "message": f"{utype.capitalize()} {unit_id} failed at ({lat:.4f},{lon:.4f}) – {reason}"
    }

    st.session_state.setdefault("unit_failures", []).append(event)
    st.session_state.setdefault("notifications", []).append(event)

    save_failure(unit_id, reason, lat, lon)

    if env is not None:
        try:
            env.break_connections(unit.get("sim_id"))
        except Exception:
            pass

    notify_nearby_units(unit_id, lat, lon, radius_km=10.0)
    trigger_ai_reroute(unit_id, env)

    return event

def notify_nearby_units(failed_id, lat, lon, radius_km=10.0):
    st.session_state.setdefault("personal_notifications", {})
    positions = st.session_state.get("unit_positions", {})

    for uid, u in positions.items():
        if uid == failed_id or u.get("status") == "failed":
            continue
        dx = (u["x"] - lon) * 111.0
        dy = (u["y"] - lat) * 111.0
        dist_km = math.hypot(dx, dy)
        if dist_km <= radius_km:
            msg = {
                "time": datetime.datetime.now().strftime("%H:%M"),
                "msg": f"Nearby failure: {failed_id} at {dist_km:.1f} km"
            }
            key = f"user_{u.get('assigned_to', 'none')}"
            st.session_state["personal_notifications"].setdefault(key, []).append(msg)

def trigger_ai_reroute(failed_uid, env):
    qlr = st.session_state.get("ql_router")
    if not qlr or not env:
        return

    positions = st.session_state.get("unit_positions", {})
    failed_unit = positions.get(failed_uid)
    if not failed_unit:
        return

    best_uid = None
    best_dist = 1e9
    for uid, u in positions.items():
        if uid == failed_uid or u.get("status") == "failed":
            continue
        dx = (u["x"] - failed_unit["x"]) * 111.0
        dy = (u["y"] - failed_unit["y"]) * 111.0
        d = math.hypot(dx, dy)
        if d < best_dist:
            best_dist = d
            best_uid = uid

    if best_uid is None:
        return

    goal_node = None
    if "nearest_hospital_node" in st.session_state:
        goal_node = st.session_state["nearest_hospital_node"]
    elif "nearest_shelter_node" in st.session_state:
        goal_node = st.session_state["nearest_shelter_node"]

    if goal_node is None:
        return

    start_sim = positions[best_uid]["sim_id"]
    qlr.reroute_on_failure(start_sim, goal_node)

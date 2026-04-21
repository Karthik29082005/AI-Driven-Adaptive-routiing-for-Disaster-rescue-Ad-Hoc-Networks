import math
import datetime
import random
import networkx as nx
import streamlit as st
from db_logs import save_failure
from commentary import add_commentary
from movement import assign_route_to_unit

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
    
    # Add commentary for unit failure
    add_commentary("unit_failed",
                  unit_type=utype,
                  unit_id=unit_id,
                  lat=lat,
                  lon=lon,
                  reason=reason)

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

    potential_goal = None
    if "nearest_hospital_node" in st.session_state:
        potential_goal = st.session_state["nearest_hospital_node"]
    elif "nearest_shelter_node" in st.session_state:
        potential_goal = st.session_state["nearest_shelter_node"]

    start_sim = positions[best_uid]["sim_id"]
    
    # -------------------------------------------------------------
    # TOPOLOGICAL CONSTRAINT: Ensure goal_node is actually REACHABLE! 
    # If the user destroyed too much of the map via failures, islands form.
    # -------------------------------------------------------------
    reachable_nodes = list(nx.node_connected_component(env.G, start_sim)) if start_sim in env.G else []
    
    # Is the user's hospital/target actually on the same surviving island as the rescue vehicle?
    if potential_goal is not None and potential_goal in reachable_nodes:
        goal_node = potential_goal
    else:
        # Fallback to ANY reachable random geographic node so the algorithm trains
        available_nodes = [node for node in reachable_nodes if node != start_sim]
        
        if available_nodes:
            goal_node = random.choice(available_nodes)
        else:
            # The unit is completely marooned!
            st.warning(f"⚠️ {best_uid} is completely geographically isolated due to network damage. AI routing impossible.")
            return

    start_sim = positions[best_uid]["sim_id"]
    route_nodes, comp_time = qlr.reroute_on_failure(start_sim, goal_node)
    
    if route_nodes:
        # Move destination logic to substitution unit
        substitute_unit = positions[best_uid]
        substitute_unit["target_type"] = failed_unit.get("target_type")
        substitute_unit["target_location"] = failed_unit.get("target_location")
        substitute_unit["is_rerouted"] = True
        
        # Apply the route and wake the unit up so Folium renders its line!
        assign_route_to_unit(best_uid, route_nodes, env)
        
        # Append exact raw coordinates to the route array for precise tracing
        if substitute_unit.get("target_location"):
            t_lat, t_lon = substitute_unit["target_location"]
            from movement import fetch_osrm_curve
            last_pt = substitute_unit["route"][-1] if substitute_unit.get("route") else (substitute_unit["x"], substitute_unit["y"])
            curve = fetch_osrm_curve(last_pt[0], last_pt[1], t_lon, t_lat)
            if curve:
                substitute_unit["route"].extend(curve[1:] if len(curve) > 1 else curve)
            else:
                substitute_unit["route"].append((t_lon, t_lat))
            
        st.session_state.setdefault("notifications", []).append(
            {"time": datetime.datetime.now().strftime("%H:%M:%S"), 
             "msg": f"AI recalculated path. {best_uid} is taking over mission!"
            })

import time
import math
import streamlit as st
from movement import assign_route_to_unit
from db_logs import save_alert, save_assignment
from admin_user_mgmt import get_team_members
from commentary import add_commentary

def get_district_hospitals(env):
    """Get hospitals for the selected state."""
    if env and hasattr(env, "state"):
        return env.state.get("hospitals", [])
    elif env and hasattr(env, "district"):
        # Backward compatibility
        return env.district.get("hospitals", [])
    # Fallback to default hospitals
    return [
        {"name": "AIIMS Delhi", "loc": (28.5672, 77.2100)},
        {"name": "KIMS Hyderabad", "loc": (17.4158, 78.4294)},
        {"name": "Apollo Chennai", "loc": (13.0391, 80.2090)},
    ]

def get_district_shelters(env):
    """Get shelters for the selected state."""
    if env and hasattr(env, "state"):
        return env.state.get("shelters", [])
    elif env and hasattr(env, "district"):
        # Backward compatibility
        return env.district.get("shelters", [])
    # Fallback to default shelters
    return [
        {"name": "Shelter Hub Delhi", "loc": (28.6200, 77.2300)},
        {"name": "Shelter Hub Mumbai", "loc": (19.0760, 72.8777)},
        {"name": "Shelter Hub Bengaluru", "loc": (12.9716, 77.5946)},
    ]

def distance_km(lat1, lon1, lat2, lon2):
    return math.hypot((lon2 - lon1) * 111.0, (lat2 - lat1) * 111.0)

def get_closest_node(env, dest_lat, dest_lon):
    best_id = None
    best_d = 1e9
    for nid, node in env.nodes.items():
        if nid not in env.G:
            continue
        d = distance_km(dest_lat, dest_lon, node.y, node.x)
        if d < best_d:
            best_d = d
            best_id = nid
    return best_id

def dispatch_ui(env=None):
    pass


def assign_rescue_units(lat, lon, env, alert_id):
    units = st.session_state.get("unit_positions", {})
    team_members = get_team_members()
    if not units:
        st.error("No units available.")
        return
    if not team_members:
        st.error("No team members registered.")
        return

    candidates = []
    for uid, u in units.items():
        status = u.get("status", "idle")
        if status in ("idle", "arrived") and status != "failed":
            d = distance_km(lat, lon, u["y"], u["x"])
            candidates.append((d, uid, u))
    
    if not candidates:
        st.warning("No idle units available to dispatch.")
        return
        
    candidates.sort(key=lambda x: x[0])

    dispatch_units = candidates[:3]
    st.info(f"Dispatching {len(dispatch_units)} nearest available units...")

    member_idx = 0
    for _, uid, u in dispatch_units:
        member = team_members[member_idx]
        assigned_email = member[1] if len(member) > 1 else member[0]  # username
        u["assigned_to"] = assigned_email
        u["active_alert_id"] = alert_id
        member_idx = (member_idx + 1) % len(team_members)
        save_assignment(uid, assigned_email, alert_id)
        
        # Add commentary for unit assignment
        add_commentary("unit_assigned",
                      unit_type=u["type"],
                      unit_id=uid,
                      team_member=assigned_email)
        
        dispatch_unit_to_target(uid, lat, lon, env)
        st.success(f"{u['type'].capitalize()} {uid} assigned to {assigned_email}")

def dispatch_unit_to_target(uid, alert_lat, alert_lon, env):
    u = st.session_state["unit_positions"][uid]
    
    alert_node = get_closest_node(env, alert_lat, alert_lon)
    if alert_node is not None:
        try:
            route_nodes = env.shortest_path(u["sim_id"], alert_node)
            if route_nodes:
                assign_route_to_unit(uid, route_nodes, env)
                from movement import fetch_osrm_curve
                last_pt = u["route"][-1] if u.get("route") else (u["x"], u["y"])
                curve = fetch_osrm_curve(last_pt[0], last_pt[1], alert_lon, alert_lat)
                if curve: u["route"].extend(curve[1:] if len(curve) > 1 else curve)
                u["status"] = "moving"
                u["target_type"] = "alert"
                u["target_location"] = (alert_lat, alert_lon)
                
                # Add commentary for unit deployment
                add_commentary("unit_deployed",
                              unit_type=u["type"],
                              unit_id=uid,
                              lat=alert_lat,
                              lon=alert_lon)
                
                st.toast(f"🚨 {uid} moving towards Alert Location", icon="🚑")
        except Exception as e:
            st.error(f"Cannot dispatch {uid}: {str(e)}")
    else:
        st.error(f"Cannot dispatch {uid}: Target area is unreachable due to network damage.")

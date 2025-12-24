import math
import streamlit as st
from movement import assign_route_to_unit
from db_logs import save_alert, save_assignment
from admin_user_mgmt import get_team_members

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
        d = distance_km(dest_lat, dest_lon, node.y, node.x)
        if d < best_d:
            best_d = d
            best_id = nid
    return best_id

def dispatch_ui(env=None):
    st.subheader("🚨 Disaster Alert Trigger")
    
    # Get state information for default coordinates and bounds
    if env and hasattr(env, "state"):
        state = env.state
        center_lat, center_lon = state["center"]
        bounds = state["bounds"]
        st.info(f"📍 Operating in: **{state['name']} State**")
        
        # Set default to state center and limit inputs to state bounds
        lat = st.number_input(
            "Alert Latitude", 
            value=float(center_lat),
            min_value=float(bounds["min_lat"]),
            max_value=float(bounds["max_lat"]),
            step=0.001
        )
        lon = st.number_input(
            "Alert Longitude", 
            value=float(center_lon),
            min_value=float(bounds["min_lon"]),
            max_value=float(bounds["max_lon"]),
            step=0.001
        )
    elif env and hasattr(env, "district"):
        # Backward compatibility
        district = env.district
        center_lat, center_lon = district["center"]
        bounds = district["bounds"]
        st.info(f"📍 Operating in: **{district.get('name', 'Unknown')}**")
        
        lat = st.number_input(
            "Alert Latitude", 
            value=float(center_lat),
            min_value=float(bounds["min_lat"]),
            max_value=float(bounds["max_lat"]),
            step=0.001
        )
        lon = st.number_input(
            "Alert Longitude", 
            value=float(center_lon),
            min_value=float(bounds["min_lon"]),
            max_value=float(bounds["max_lon"]),
            step=0.001
        )
    else:
        lat = st.number_input("Alert Latitude", value=19.0760)
        lon = st.number_input("Alert Longitude", value=72.8777)
    
    severity = st.selectbox("Severity", ["Low", "Moderate", "High"])

    if st.button("Trigger Alert"):
        st.session_state["alert_active"] = True
        st.session_state["alert_location"] = (lat, lon)
        alert_id = save_alert(lat, lon, severity)
        st.session_state["current_alert_id"] = alert_id
        st.success("Alert saved and raised!")
        assign_rescue_units(lat, lon, env, alert_id)

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
        if u.get("status") == "failed":
            continue
        d = distance_km(lat, lon, u["y"], u["x"])
        candidates.append((d, uid, u))
    candidates.sort(key=lambda x: x[0])

    dispatch_units = candidates[:6]
    st.info(f"Dispatching {len(dispatch_units)} nearest units...")

    member_idx = 0
    for _, uid, u in dispatch_units:
        member = team_members[member_idx]
        assigned_email = member[1]  # username
        u["assigned_to"] = assigned_email
        member_idx = (member_idx + 1) % len(team_members)
        save_assignment(uid, assigned_email, alert_id)
        dispatch_unit_to_target(uid, lat, lon, env)
        st.success(f"{u['type'].capitalize()} {uid} assigned to {assigned_email}")

def dispatch_unit_to_target(uid, alert_lat, alert_lon, env):
    u = st.session_state["unit_positions"][uid]
    
    # Use district-specific hospitals and shelters
    hospitals = get_district_hospitals(env)
    shelters = get_district_shelters(env)
    
    if u["type"] == "ambulance":
        target = min(hospitals, key=lambda h: distance_km(alert_lat, alert_lon, *h["loc"]))
        dest_lat, dest_lon = target["loc"]
        st.session_state["nearest_hospital_node"] = get_closest_node(env, dest_lat, dest_lon)
    else:
        target = min(shelters, key=lambda h: distance_km(alert_lat, alert_lon, *h["loc"]))
        dest_lat, dest_lon = target["loc"]
        st.session_state["nearest_shelter_node"] = get_closest_node(env, dest_lat, dest_lon)

    dest_node = get_closest_node(env, dest_lat, dest_lon)
    route_nodes = env.shortest_path(u["sim_id"], dest_node)
    assign_route_to_unit(uid, route_nodes, env)
    st.toast(f"🚨 {uid} moving towards {target['name']}", icon="🚑")

import streamlit as st
import folium
import os
import time
from folium import PolyLine, Rectangle
from streamlit_folium import st_folium
from movement import update_movements
from failures import handle_unit_failure, BROKEN_ICONS


def resolve_icon_path(icon_ref: str):
    # icon_ref may be a relative path like 'models/drone.png' or just a name.
    # Try to find an existing file in the repository's top-level `models/` directory.
    repo_models = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "models"))
    # consider basename candidates (strip any leading path)
    base = os.path.basename(icon_ref)
    candidates = [base, base + ".png", base + ".png.png"]
    # also consider the original reference if it already contains a path
    if os.path.sep in icon_ref:
        candidates.insert(0, os.path.basename(icon_ref))

    for name in candidates:
        p = os.path.join(repo_models, name)
        if os.path.exists(p):
            return p
    # fallback: return the original reference (let folium handle error if any)
    return icon_ref

def render_map_and_controls(admin: bool, env=None):
    st.subheader("📍 Disaster Routing Map - Live Operations")

    update_movements()

    # Center map on the selected state
    if env is not None and hasattr(env, "state"):
        state = env.state
        center_lat, center_lon = state["center"]
        base_location = [center_lat, center_lon]
        zoom_start = 7  # State-level view (wider than district)
    elif env is not None and hasattr(env, "district"):
        # Backward compatibility
        district = env.district
        center_lat, center_lon = district["center"]
        base_location = [center_lat, center_lon]
        zoom_start = 11
    else:
        base_location = [20.5937, 78.9629]  # Fallback to India center
        zoom_start = 5
    
    m = folium.Map(location=base_location, zoom_start=zoom_start)

    units = st.session_state.get("unit_positions", {})

    # Draw state boundary if available
    if env is not None and hasattr(env, "state"):
        state = env.state
        bounds = state["bounds"]
        Rectangle(
            bounds=[[bounds["min_lat"], bounds["min_lon"]], 
                   [bounds["max_lat"], bounds["max_lon"]]],
            color="#ff7800",
            fill=True,
            fillColor="#ff7800",
            fillOpacity=0.1,
            weight=2,
            popup=f"Operational Area: {state['name']} State"
        ).add_to(m)
    elif env is not None and hasattr(env, "district"):
        # Backward compatibility
        district = env.district
        bounds = district["bounds"]
        Rectangle(
            bounds=[[bounds["min_lat"], bounds["min_lon"]], 
                   [bounds["max_lat"], bounds["max_lon"]]],
            color="#ff7800",
            fill=True,
            fillColor="#ff7800",
            fillOpacity=0.1,
            weight=2,
            popup=f"Operational Area: {district.get('name', 'Unknown')}"
        ).add_to(m)

    # Communication links
    if env is not None and hasattr(env, "G"):
        for u, v in env.G.edges():
            n1 = env.nodes[u]
            n2 = env.nodes[v]
            PolyLine(
                locations=[(n1.y, n1.x), (n2.y, n2.x)],
                weight=1.5,
                color="#00bcd4",
                opacity=0.6
            ).add_to(m)

    # Planned routes
    for uid, u in units.items():
        route = u.get("route") or []
        if len(route) >= 2:
            latlon_route = [(lat, lon) for (lon, lat) in route]
            PolyLine(
                locations=latlon_route,
                weight=3,
                color="#4caf50" if u.get("status") != "failed" else "#f44336",
                opacity=0.8
            ).add_to(m)

    # Unit markers
    for uid, u in units.items():
        lat, lon = u["y"], u["x"]
        status = u.get("status", "idle")
        base_icon = f"models/{u['type']}.png"
        icon_file = BROKEN_ICONS.get(u["type"], base_icon) if status == "failed" else base_icon
        resolved_icon = resolve_icon_path(icon_file)

        folium.Marker(
            location=(lat, lon),
            popup=f"{u['type']} ({uid}) — {status}",
            icon=folium.CustomIcon(resolved_icon, icon_size=(50, 50))
        ).add_to(m)

        if status == "failed":
            folium.Circle(
                location=(lat, lon),
                radius=400,
                color="red",
                fill=True,
                fill_opacity=0.25
            ).add_to(m)

    # Show hospitals and shelters on map
    if env is not None and hasattr(env, "state"):
        state = env.state
        hospitals = state.get("hospitals", [])
        shelters = state.get("shelters", [])
    elif env is not None and hasattr(env, "district"):
        # Backward compatibility
        district = env.district
        hospitals = district.get("hospitals", [])
        shelters = district.get("shelters", [])
    else:
        hospitals = []
        shelters = []
        
        # Add hospital markers
        for hospital in hospitals:
            lat, lon = hospital["loc"]
            hospital_icon = resolve_icon_path("models/hospital.png")
            folium.Marker(
                location=(lat, lon),
                popup=f"🏥 {hospital['name']}",
                tooltip="Hospital",
                icon=folium.CustomIcon(hospital_icon, icon_size=(40, 40))
            ).add_to(m)
        
        # Add shelter markers
        for shelter in shelters:
            lat, lon = shelter["loc"]
            shelter_icon = resolve_icon_path("models/shelter.png")
            folium.Marker(
                location=(lat, lon),
                popup=f"🏠 {shelter['name']}",
                tooltip="Shelter",
                icon=folium.CustomIcon(shelter_icon, icon_size=(40, 40))
            ).add_to(m)

    # Show team members on map (at their assigned unit locations)
    from admin_user_mgmt import get_team_members
    team_members = get_team_members()
    team_member_icon = resolve_icon_path("models/team_member.png")
    
    # Group units by assigned team member
    units_by_member = {}
    for uid, u in units.items():
        assigned_to = u.get("assigned_to")
        if assigned_to:
            if assigned_to not in units_by_member:
                units_by_member[assigned_to] = []
            units_by_member[assigned_to].append(u)
    
    # Show team member markers at their unit locations
    for member_email, member_units in units_by_member.items():
        if member_units:
            # Use the first unit's location for the team member marker
            first_unit = member_units[0]
            lat, lon = first_unit["y"], first_unit["x"]
            
            # Find team member name
            member_name = member_email
            for member in team_members:
                if len(member) > 1 and member[1] == member_email:
                    if len(member) > 3:
                        member_name = member[3] or member_email
                    break
            
            folium.Marker(
                location=(lat, lon),
                popup=f"👤 {member_name} ({len(member_units)} units)",
                tooltip=f"Team Member: {member_name}",
                icon=folium.CustomIcon(team_member_icon, icon_size=(35, 35))
            ).add_to(m)

    # Show active alerts with alert icon
    active_alerts = st.session_state.get("active_alerts", [])
    current_time = time.time()
    
    for alert in active_alerts:
        if current_time - alert.get("time", 0) < 300:  # Show alerts for 5 minutes
            lat, lon = alert["lat"], alert["lon"]
            alert_icon = resolve_icon_path("models/alert.png")
            
            # Alert marker
            folium.Marker(
                location=(lat, lon),
                popup=f"🚨 Alert - {alert.get('severity', 'Unknown')} Severity",
                tooltip=f"Disaster Alert ({alert.get('severity', 'Unknown')})",
                icon=folium.CustomIcon(alert_icon, icon_size=(50, 50))
            ).add_to(m)
            
            # Alert pulse circle
            folium.Circle(
                location=(lat, lon),
                radius=800,
                color="red",
                fill=True,
                weight=2,
                fill_opacity=0.3,
                popup=f"Alert Zone - {alert.get('severity', 'Unknown')}"
            ).add_to(m)
    
    # Show alert notification only once per new alert (fix continuous toast)
    alert_active = st.session_state.get("alert_active", False)
    if alert_active and active_alerts:
        latest_alert = max(active_alerts, key=lambda x: x.get("time", 0))
        alert_key = f"alert_{latest_alert.get('id', 0)}"
        
        if alert_key not in st.session_state.get("alert_notifications_shown", set()):
            st.session_state.setdefault("alert_notifications_shown", set()).add(alert_key)
            st.toast(f"🚨 New Disaster Alert - {latest_alert.get('severity', 'Unknown')} Severity — Routing rescue teams!", icon="⚠️")

    # Controls
    if admin:
        st.markdown("### 🔧 Admin Controls")
        if st.button("Simulate Random Failure (first unit)"):
            if units:
                first_uid = list(units.keys())[0]
                handle_unit_failure(first_uid, "Simulated by Admin", env)
    else:
        st.markdown("### 🚨 Team Member Controls")
        my_email = st.session_state.get("username")
        my_units = [uid for uid, u in units.items() if u.get("assigned_to") == my_email]
        if my_units:
            selected = st.selectbox("My Units", my_units)
            if st.button("⚠ Report Problem for selected"):
                handle_unit_failure(selected, "Reported by team", env)
                st.warning("Problem reported to Admin.")
        else:
            st.info("No units assigned to you yet.")

    # Fullscreen map by default
    st_folium(m, width=1400, height=750)

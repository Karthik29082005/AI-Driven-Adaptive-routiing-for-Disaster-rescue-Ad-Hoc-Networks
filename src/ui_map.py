import streamlit as st
import folium
import os
import time
from folium import PolyLine, Rectangle
from folium.plugins import AntPath
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
    update_movements()

    # Center map on the selected state
    if env is not None and hasattr(env, "state"):
        state = env.state
        center_lat, center_lon = state["center"]
        base_location = [center_lat, center_lon]
        zoom_start = 12  # City/District-level view
    elif env is not None and hasattr(env, "district"):
        # Backward compatibility
        district = env.district
        center_lat, center_lon = district["center"]
        base_location = [center_lat, center_lon]
        zoom_start = 12
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

    # Communication links / Road network
    if env is not None and hasattr(env, "G"):
        for u, v in env.G.edges():
            geom = env.G[u][v].get('geometry')
            if not geom:
                n1, n2 = env.nodes[u], env.nodes[v]
                geom = [(n1.y, n1.x), (n2.y, n2.x)]
            PolyLine(
                locations=geom,
                weight=2,
                color="#00ff00",
                opacity=0.8,
                dash_array="5, 5"
            ).add_to(m)

    # Planned routes (Animated)
    for uid, u in units.items():
        my_email = st.session_state.get("username", "").strip()
        assigned_email = u.get("assigned_to", "")
        if assigned_email:
            assigned_email = assigned_email.strip()
            
        if not admin and assigned_email != my_email:
            continue
            
        route = u.get("route") or []
        if len(route) >= 2:
            latlon_route = [(lat, lon) for (lon, lat) in route]
            
            if u.get("status") == "failed":
                route_color = "#f44336"
                pulse_color = "#ffffff"
            elif u.get("is_rerouted"): # New rule for AI rerouted paths
                route_color = "#9c27b0"
                pulse_color = "#ffffff"
            elif u.get("target_type") == "alert":
                route_color = "#ff9800"
                pulse_color = "#ffffff"
            else:
                route_color = "#2196f3"
                pulse_color = "#ffffff"
                
            AntPath(
                locations=latlon_route,
                weight=4,
                color=route_color,
                pulse_color=pulse_color,
                delay=800,
                opacity=0.8
            ).add_to(m)

    # Unit markers
    for uid, u in units.items():
        my_email = st.session_state.get("username", "").strip()
        assigned_email = u.get("assigned_to", "")
        if assigned_email:
            assigned_email = assigned_email.strip()
            
        if not admin and assigned_email != my_email:
            continue
            
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
        if not admin and member_email != st.session_state.get("username"):
            continue
            
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
    
    # Pre-calculate assigned alerts for members
    my_alert_ids = set()
    if not admin:
        my_email = st.session_state.get("username", "").strip()
        my_units = [u for uid, u in units.items() if (u.get("assigned_to", "") or "").strip() == my_email]
        my_alert_ids = {u.get("active_alert_id") for u in my_units if u.get("active_alert_id")}
    
    for alert in active_alerts:
        if not admin and alert["id"] not in my_alert_ids:
            continue
            
        if current_time - alert.get("time", 0) < 300:  # Show alerts for 5 minutes
            lat, lon = alert["lat"], alert["lon"]
            alert_icon = resolve_icon_path("models/alert.png")
            
            # Highlight nearby nodes in orange
            if env is not None and hasattr(env, "nodes"):
                import math
                for nid, node in env.nodes.items():
                    d = math.hypot((node.x - lon) * 111.0, (node.y - lat) * 111.0)
                    if d <= 2.0: # 2km radius
                        folium.CircleMarker(
                            location=(node.y, node.x),
                            radius=3,
                            color="orange",
                            fill=True,
                            fill_opacity=0.6,
                            tooltip="Nearby Node"
                        ).add_to(m)

            # Alert marker
            folium.Marker(
                location=(lat, lon),
                popup=f"🚨 Alert - {alert.get('severity', 'Unknown')} Severity",
                tooltip=f"Disaster Alert ({alert.get('severity', 'Unknown')})",
                icon=folium.CustomIcon(alert_icon, icon_size=(50, 50))
            ).add_to(m)

    # Legend
    with st.expander("📋 Map legend", expanded=False):
        st.markdown("""
        - **Orange animated routes** = Routing towards alert
        - **Blue animated routes** = Routing towards hospital/shelter
        - **Purple animated routes** = AI Rerouted path
        - **Red animated routes** = Failed unit
        - **Alert marker** = Disaster alert location
        - **Green dotted lines** = Ordinary node connections (Roads)
        - Click markers for unit/alert details
        """)

    # Controls
    if admin:
        st.markdown("**Admin:** Simulate a unit failure to test AI rerouting.")
        # Only show units that are actually doing something (idle or moving) 
        active_units = [uid for uid, u in units.items() if u.get("status") in ("moving", "idle", "en_route")]
        
        if active_units:
            selected_fail_unit = st.selectbox("Select active unit to simulate failure:", active_units)
            if st.button("Simulate unit failure", type="secondary"):
                handle_unit_failure(selected_fail_unit, "Simulated by Admin", env)
                st.success(f"Failure simulated for {selected_fail_unit}. Check the Routing Comparison tab for Q-Learning vs Dijkstra times.")
        else:
            st.info("No active units available to fail.")
    else:
        st.markdown("**Your units** — Report a problem if your unit cannot continue.")
        my_email = st.session_state.get("username", "").strip()
        my_units = [uid for uid, u in units.items() if (u.get("assigned_to", "") or "").strip() == my_email]
        if my_units:
            selected = st.selectbox("Select unit", my_units, help="Choose the unit to report")
            if st.button("Report problem for this unit", type="secondary"):
                handle_unit_failure(selected, "Reported by team", env)
                st.warning("Problem reported. Admin will be notified.")
        else:
            st.info("No units assigned to you yet. They will appear here when assigned.")

    st_folium(m, width=1400, height=700, returned_objects=[])

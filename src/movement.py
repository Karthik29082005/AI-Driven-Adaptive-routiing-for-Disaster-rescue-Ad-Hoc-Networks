import math
import time
import requests
import streamlit as st
from commentary import add_commentary

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
        previous_status = u.get("status", "idle")
        status = previous_status
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
                # Bind the new physical location to the routing node so future trips start here
                from ui_alert import get_closest_node 
                closest_node = get_closest_node(st.session_state["env"], u["y"], u["x"])
                if closest_node is not None:
                    u["sim_id"] = closest_node
                
                # Clear any AI reroute tagging now that the mission is over
                u["is_rerouted"] = False
                
                # Check if this is arrival at alert or destination
                target_type = u.get("target_type")
                if target_type == "alert":
                    add_commentary("unit_arrived_alert",
                                  unit_type=u["type"],
                                  unit_id=uid)
                elif target_type == "destination":
                    destination_type = "hospital" if u["type"] == "ambulance" else "shelter"
                    add_commentary("unit_arrived_destination",
                                  unit_type=u["type"],
                                  unit_id=uid,
                                  destination_type=destination_type)
            continue

        speed = SPEED_PROFILE_KMPH.get(u["type"], 30.0)
        step_km = speed * (dt / 3600.0)

        if step_km >= dist_km:
            u["x"], u["y"] = tx, ty
            u["route_index"] = idx + 1
            if u["route_index"] >= len(route):
                u["status"] = "arrived"
                # Bind the new physical location to the routing node so future trips start here
                from ui_alert import get_closest_node 
                closest_node = get_closest_node(st.session_state["env"], u["y"], u["x"])
                if closest_node is not None:
                    u["sim_id"] = closest_node
                    
                # Clear any AI reroute tagging now that the mission is over
                u["is_rerouted"] = False
                    
                # Check if this is arrival at alert or destination
                target_type = u.get("target_type")
                if target_type == "alert":
                    add_commentary("unit_arrived_alert",
                                  unit_type=u["type"],
                                  unit_id=uid)
                elif target_type == "destination":
                    destination_type = "hospital" if u["type"] == "ambulance" else "shelter"
                    add_commentary("unit_arrived_destination",
                                  unit_type=u["type"],
                                  unit_id=uid,
                                  destination_type=destination_type)
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
    if len(route_nodes) == 1:
        node = env.nodes[route_nodes[0]]
        waypoints.append((node.y, node.x))  # lat, lon
    else:
        for i in range(len(route_nodes) - 1):
            n1 = route_nodes[i]
            n2 = route_nodes[i+1]
            if env.G.has_edge(n1, n2):
                geom = env.G[n1][n2].get("geometry", [])
                # geometry lists are [ (lat, lon), ... ]
                # if n1 is the start of the geom, extend directly.
                # if reversed, reverse the geometry.
                if geom:
                    dist_normal = math.hypot(geom[0][0] - env.nodes[n1].y, geom[0][1] - env.nodes[n1].x)
                    dist_reversed = math.hypot(geom[-1][0] - env.nodes[n1].y, geom[-1][1] - env.nodes[n1].x)
                    if dist_reversed < dist_normal:
                        waypoints.extend(geom[::-1])
                    else:
                        waypoints.extend(geom)
                else:
                    waypoints.extend([(env.nodes[n1].y, env.nodes[n1].x), (env.nodes[n2].y, env.nodes[n2].x)])
            else:
                waypoints.extend([(env.nodes[n1].y, env.nodes[n1].x), (env.nodes[n2].y, env.nodes[n2].x)])
                
    # remove duplicate consecutive points
    clean_waypoints = []
    for w in waypoints:
        if not clean_waypoints or w != clean_waypoints[-1]:
            clean_waypoints.append(w)
            
    # convert to (lon, lat) for internal routing system standard
    u["route"] = [(lon, lat) for (lat, lon) in clean_waypoints]
    u["route_index"] = 0
    u["status"] = "moving"

def fetch_osrm_curve(lon1, lat1, lon2, lat2):
    """Fetch realistic road curve between two exact coordinates."""
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?geometries=geojson&overview=full"
        resp = requests.get(url, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == "Ok":
                coords = data["routes"][0]["geometry"]["coordinates"]
                return coords
    except Exception:
        pass
    return [(lon1, lat1), (lon2, lat2)]


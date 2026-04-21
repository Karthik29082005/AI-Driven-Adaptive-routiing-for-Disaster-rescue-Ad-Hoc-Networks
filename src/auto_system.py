"""
Automatic alert generation and deployment system.
Generates alerts automatically and deploys rescue units without admin intervention.
"""
import random
import time
import math
import streamlit as st
from ui_alert import assign_rescue_units, get_district_hospitals, get_district_shelters, distance_km, get_closest_node
from movement import assign_route_to_unit
from db_logs import save_alert, save_assignment
from admin_user_mgmt import get_team_members
from commentary import add_commentary

def generate_random_alert_in_district(env):
    """Generate a random alert within the state boundaries."""
    if not env:
        return None
    
    # Check for state first, then district for backward compatibility
    if hasattr(env, "state"):
        state = env.state
        bounds = state["bounds"]
        area_name = state["name"]
    elif hasattr(env, "district"):
        district = env.district
        bounds = district["bounds"]
        area_name = district.get("name", "Unknown")
    else:
        return None
    
    # Generate random coordinates within state/district
    lat = random.uniform(bounds["min_lat"], bounds["max_lat"])
    lon = random.uniform(bounds["min_lon"], bounds["max_lon"])
    
    # Random severity
    severity = random.choice(["Low", "Moderate", "High"])
    
    return {
        "lat": lat,
        "lon": lon,
        "severity": severity,
        "area": area_name
    }

def should_generate_new_alert():
    """Check if we should generate a new alert based on timing."""
    if "last_alert_time" not in st.session_state:
        return True
    
    # Generate new alert every 30-60 seconds
    time_since_last = time.time() - st.session_state["last_alert_time"]
    return time_since_last >= random.uniform(30, 60)

def get_available_units():
    """Get units that are available for deployment (strictly idle and unassigned to targets)."""
    units = st.session_state.get("unit_positions", {})
    available = []
    for uid, u in units.items():
        status = u.get("status", "idle")
        target_type = u.get("target_type")
        if status in ("idle", "arrived") and status != "failed" and target_type is None:
            available.append((uid, u))
    return available

def auto_deploy_units_to_alert(alert_lat, alert_lon, env, alert_id):
    """Automatically deploy available units to an alert."""
    units = st.session_state.get("unit_positions", {})
    team_members = get_team_members()
    
    if not units:
        return
    
    if not team_members:
        # Create dummy team members if none exist
        team_members = [("Dummy", "team@rescue.com")]
    
    # Find available units using the proper filter
    available_units = get_available_units()
    candidates = []
    for uid, u in available_units:
        d = distance_km(alert_lat, alert_lon, u["y"], u["x"])
        candidates.append((d, uid, u))
    
    if not candidates:
        return
    
    candidates.sort(key=lambda x: x[0])
    
    # Deploy top 3 nearest available units per alert
    dispatch_units = candidates[:3]
    
    # Add commentary for multiple units deployment
    if len(dispatch_units) > 1:
        add_commentary("multiple_units_deployed",
                      count=len(dispatch_units),
                      severity=st.session_state.get("active_alerts", [{}])[-1].get("severity", "Unknown") if st.session_state.get("active_alerts") else "Unknown")
    
    member_idx = 0
    for _, uid, u in dispatch_units:
        member = team_members[member_idx % len(team_members)]
        assigned_email = member[1] if len(member) > 1 else member[0]
        u["assigned_to"] = assigned_email
        u["active_alert_id"] = alert_id
        save_assignment(uid, assigned_email, alert_id)
        
        # Add commentary for unit assignment
        add_commentary("unit_assigned",
                      unit_type=u["type"],
                      unit_id=uid,
                      team_member=assigned_email)
        
        member_idx += 1
        auto_dispatch_unit_to_alert(uid, alert_lat, alert_lon, env)

def auto_dispatch_unit_to_alert(uid, alert_lat, alert_lon, env):
    """Dispatch a unit to the alert location, then to appropriate destination."""
    u = st.session_state["unit_positions"][uid]
    
    # First go to alert location
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
        except Exception as e:
            # If a unit cannot find a path to the alert, report it to the UI instead of silently failing
            print(f"Routing error for {uid}: {e}")
            st.toast(f"⚠️ {uid} cannot find a route to the alert: Network Island", icon="❌")

def check_and_handle_arrivals(env):
    """Check if units have arrived and route them to final destinations."""
    units = st.session_state.get("unit_positions", {})
    hospitals = get_district_hospitals(env)
    shelters = get_district_shelters(env)
    
    for uid, u in units.items():
        if u.get("status") == "arrived" and u.get("target_type") == "alert":
            # Unit arrived at alert, now route to hospital/shelter
            alert_lat, alert_lon = u.get("target_location", (u["y"], u["x"]))
            
            try:
                if u["type"] == "ambulance":
                    target = min(hospitals, key=lambda h: distance_km(alert_lat, alert_lon, *h["loc"]))
                    dest_lat, dest_lon = target["loc"]
                    destination_type = "hospital"
                else:
                    target = min(shelters, key=lambda h: distance_km(alert_lat, alert_lon, *h["loc"]))
                    dest_lat, dest_lon = target["loc"]
                    destination_type = "shelter"
                
                dest_node = get_closest_node(env, dest_lat, dest_lon)
                if dest_node is not None:
                    route_nodes = env.shortest_path(u["sim_id"], dest_node)
                    if route_nodes:
                        assign_route_to_unit(uid, route_nodes, env)
                        from movement import fetch_osrm_curve
                        last_pt = u["route"][-1] if u.get("route") else (u["x"], u["y"])
                        curve = fetch_osrm_curve(last_pt[0], last_pt[1], dest_lon, dest_lat)
                        if curve: u["route"].extend(curve[1:] if len(curve) > 1 else curve)
                        u["status"] = "moving"
                        u["target_type"] = "destination"
                        u["target_location"] = (dest_lat, dest_lon)
                        
                        # Add commentary for routing to destination
                        add_commentary("unit_routing_destination",
                                      unit_type=u["type"],
                                      unit_id=uid,
                                      destination_type=destination_type)
            except Exception:
                # If routing fails, mark as idle
                u["status"] = "idle"
                u["target_type"] = None
        
        # When units finish the entire sequence (arrive at hospital/shelter)
        elif u.get("status") == "arrived" and u.get("target_type") == "destination":
            u["status"] = "idle"
            u["target_type"] = None
            u["target_location"] = None
            u["assigned_to"] = None
            u["active_alert_id"] = None
            
            # Dynamically update the unit's sim_id (spawn node) to the hospital/shelter node
            # so future routing computes paths from its current physical location, not original base
            closest_node = get_closest_node(env, u["y"], u["x"])
            if closest_node is not None:
                u["sim_id"] = closest_node
                
            u.pop("route", None)
            
            # Since the mission is completely done, we can mark the alert as resolved 
            # by clearing `active_alerts` if this was the final unit related to it.
            # Simplified approach: Once ANY unit successfully returns, count alert as resolved
            if "active_alerts" in st.session_state and st.session_state["active_alerts"]:
                st.session_state["active_alerts"].clear()
                st.session_state["alert_active"] = False
                
                # Add commentary for alert resolution
                add_commentary("mission_accomplished",
                              unit_type=u["type"],
                              unit_id=uid)
                st.toast("✅ Unit returned to base. Alert fully resolved!", icon="🎉")

def run_automatic_system(env):
    """Main function to run automatic alert generation and deployment."""
    # Initialize alert tracking
    if "active_alerts" not in st.session_state:
        st.session_state["active_alerts"] = []
    
    if "alert_notifications_shown" not in st.session_state:
        st.session_state["alert_notifications_shown"] = set()
    
    # Check if we should generate a new alert
    if should_generate_new_alert():
        alert_data = generate_random_alert_in_district(env)
        if alert_data:
            # Save alert to database
            alert_id = save_alert(alert_data["lat"], alert_data["lon"], alert_data["severity"])
            
            # Add to active alerts
            alert_info = {
                "id": alert_id,
                "lat": alert_data["lat"],
                "lon": alert_data["lon"],
                "severity": alert_data["severity"],
                "time": time.time(),
                "deployed": False # Important: not deployed yet
            }
            st.session_state["active_alerts"].append(alert_info)
            st.session_state["last_alert_time"] = time.time()
            
            # Set as current alert
            st.session_state["alert_active"] = True
            st.session_state["alert_location"] = (alert_data["lat"], alert_data["lon"])
            st.session_state["current_alert_id"] = alert_id
            
            # Add commentary for alert generation
            add_commentary("alert_generated",
                          severity=alert_data["severity"],
                          lat=alert_data["lat"],
                          lon=alert_data["lon"],
                          area=alert_data["area"])
    
    # Continuously attempt to deploy available units to unsettled alerts
    for alert in st.session_state["active_alerts"]:
        if not alert.get("deployed"):
            # Check if any units are available to take it
            available_units = get_available_units()
            if available_units:
                auto_deploy_units_to_alert(alert["lat"], alert["lon"], env, alert["id"])
                # Only mark deployed if at least one unit was actually assigned and starts moving
                deployed_success = False
                for uid, u in st.session_state.get("unit_positions", {}).items():
                    if u.get("target_type") == "alert" and u.get("target_location") == (alert["lat"], alert["lon"]):
                        deployed_success = True
                        break
                
                if deployed_success:
                    alert["deployed"] = True
        
    # Handle unit arrivals and route to final destinations
    check_and_handle_arrivals(env)
    
    # Clean up old alerts (older than 5 minutes)
    current_time = time.time()
    st.session_state["active_alerts"] = [
        a for a in st.session_state["active_alerts"]
        if current_time - a["time"] < 300  # 5 minutes
    ]
    
    # Update alert_active based on recent alerts
    if st.session_state["active_alerts"]:
        latest_alert = max(st.session_state["active_alerts"], key=lambda x: x["time"])
        if current_time - latest_alert["time"] < 180:  # Active for 3 minutes
            st.session_state["alert_active"] = True
            st.session_state["alert_location"] = (latest_alert["lat"], latest_alert["lon"])
        else:
            st.session_state["alert_active"] = False
    else:
        st.session_state["alert_active"] = False


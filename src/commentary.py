"""
Live commentary system for disaster rescue operations.
Generates natural language descriptions of all events happening during disaster response.
"""
import datetime
import random
import streamlit as st

# Commentary templates for different event types
COMMENTARY_TEMPLATES = {
    "alert_generated": [
        "🚨 Emergency alert detected! A {severity}-level disaster has been reported at coordinates ({lat:.4f}, {lon:.4f}) in {area}.",
        "⚠️ New disaster alert: {severity} severity incident confirmed at location ({lat:.4f}, {lon:.4f}) within {area}.",
        "🔴 Critical alert: {severity} severity emergency situation identified at ({lat:.4f}, {lon:.4f}) in the {area} region.",
        "📢 Disaster alert: {severity}-level emergency reported at coordinates ({lat:.4f}, {lon:.4f}) in {area}.",
    ],
    "unit_deployed": [
        "🚁 {unit_type_cap} {unit_id} has been dispatched to the disaster site at ({lat:.4f}, {lon:.4f}).",
        "🚑 Emergency response unit {unit_id} ({unit_type_cap}) is now en route to the alert location ({lat:.4f}, {lon:.4f}).",
        "⚡ {unit_type_cap} {unit_id} mobilized and heading towards the disaster zone at ({lat:.4f}, {lon:.4f}).",
        "🏃 {unit_type_cap} {unit_id} deployed and moving towards emergency location ({lat:.4f}, {lon:.4f}).",
    ],
    "unit_moving": [
        "{unit_type_cap} {unit_id} is currently in transit, making steady progress towards the disaster site.",
        "📍 {unit_type_cap} {unit_id} is on the move, navigating through the affected area.",
        "🚗 {unit_type_cap} {unit_id} continues its journey, maintaining optimal speed towards the emergency location.",
        "🛣️ {unit_type_cap} {unit_id} is traveling along the designated route to reach the disaster zone.",
    ],
    "unit_arrived_alert": [
        "✅ {unit_type_cap} {unit_id} has successfully arrived at the disaster site. Rescue operations are now commencing.",
        "🎯 {unit_type_cap} {unit_id} reached the emergency location. Team is assessing the situation and preparing for rescue operations.",
        "📍 {unit_type_cap} {unit_id} has arrived at the scene. Emergency response activities are being initiated immediately.",
        "🏁 {unit_type_cap} {unit_id} completed its journey to the disaster site. Rescue team is now on the ground.",
    ],
    "unit_routing_destination": [
        "🏥 {unit_type_cap} {unit_id} has completed rescue operations at the site and is now routing to the nearest {destination_type} for medical care and shelter.",
        "🚑 {unit_type_cap} {unit_id} is transporting rescued individuals to the nearest {destination_type} facility.",
        "📍 {unit_type_cap} {unit_id} has left the disaster site and is heading towards the {destination_type} with survivors.",
        "🏃 {unit_type_cap} {unit_id} is en route to the {destination_type} after completing initial rescue operations.",
    ],
    "unit_arrived_destination": [
        "✅ {unit_type_cap} {unit_id} has successfully reached the {destination_type}. Survivors are being transferred for medical care and shelter.",
        "🏥 {unit_type_cap} {unit_id} arrived at the {destination_type}. All rescued individuals are now receiving proper care.",
        "🎯 {unit_type_cap} {unit_id} completed its mission, delivering survivors safely to the {destination_type}.",
        "📍 {unit_type_cap} {unit_id} has reached the {destination_type}. Rescue mission successfully completed.",
    ],
    "unit_failed": [
        "❌ Critical: {unit_type_cap} {unit_id} has encountered a failure at location ({lat:.4f}, {lon:.4f}). Reason: {reason}. Backup units are being notified.",
        "⚠️ Emergency: {unit_type_cap} {unit_id} is out of service at ({lat:.4f}, {lon:.4f}) due to {reason}. Alternative response units are being mobilized.",
        "🔴 Alert: {unit_type_cap} {unit_id} has failed at coordinates ({lat:.4f}, {lon:.4f}) - {reason}. AI rerouting system is activating backup units.",
        "🚨 System failure: {unit_type_cap} {unit_id} is non-operational at ({lat:.4f}, {lon:.4f}) because of {reason}. Emergency protocols are being initiated.",
    ],
    "ai_reroute": [
        "🤖 AI rerouting system activated! The Q-Learning algorithm has calculated an alternative route. Result: {improvement}.",
        "🧠 Artificial intelligence system has optimized the rescue route. Performance: {improvement}.",
        "⚡ Smart routing engaged: AI has found a new path. Outcome: {improvement}.",
        "🎯 Q-Learning router has successfully rerouted units. Analysis: {improvement}.",
    ],
    "multiple_units_deployed": [
        "🚁 Multiple rescue units ({count} units) have been simultaneously deployed to handle the emergency.",
        "⚡ Emergency response team mobilized: {count} rescue units dispatched to the disaster site to provide comprehensive coverage.",
        "🏃 Large-scale deployment initiated: {count} units are now en route to the emergency location to ensure maximum rescue capacity.",
        "🚑 Mass deployment: {count} rescue units have been activated and are heading towards the disaster zone.",
    ],
    "unit_assigned": [
        "👤 {unit_type_cap} {unit_id} has been assigned to team member {team_member} for this rescue operation.",
        "📋 {unit_type_cap} {unit_id} is now under the command of {team_member} for the emergency response mission.",
        "👷 {team_member} has taken control of {unit_type_cap} {unit_id} to coordinate rescue efforts.",
        "🎯 {unit_type_cap} {unit_id} assigned to {team_member}. Team coordination established for effective response.",
    ],
    "mission_accomplished": [
        "🎉 Mission accomplished! {unit_type_cap} {unit_id} has completed all tasks and returned to base. Alert fully resolved.",
        "✅ Alert resolved: {unit_type_cap} {unit_id} successfully finished its mission and is now standing by.",
        "🏁 Operation successful! Alert handled completely after {unit_type_cap} {unit_id} completed its drop-off.",
        "🌟 Outstanding work! The emergency has been fully addressed, and {unit_type_cap} {unit_id} is idle again.",
    ],
}

def add_commentary(event_type, **kwargs):
    """
    Add a commentary entry to the live commentary feed.
    
    Args:
        event_type: Type of event (e.g., 'alert_generated', 'unit_deployed')
        **kwargs: Event-specific parameters for template formatting
    """
    if event_type not in COMMENTARY_TEMPLATES:
        return
    
    templates = COMMENTARY_TEMPLATES[event_type]
    template = random.choice(templates)
    
    # Provide unit_type_cap natively
    if "unit_type" in kwargs and isinstance(kwargs["unit_type"], str):
        kwargs["unit_type_cap"] = kwargs["unit_type"].capitalize()
    
    try:
        commentary_text = template.format(**kwargs)
    except (KeyError, ValueError) as e:
        # If template formatting fails, create a fallback message with all kwargs
        error_msg = f"COMMENTARY FORMAT ERROR: {e} with template {template} and kwargs {kwargs}"
        print(error_msg)
        st.error(error_msg)
        commentary_text = f"Event: {event_type} - {', '.join([f'{k}={v}' for k, v in kwargs.items()])}"
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    commentary_entry = {
        "timestamp": timestamp,
        "text": commentary_text,
        "event_type": event_type,
        "time": datetime.datetime.now()
    }
    
    # Initialize commentary list if it doesn't exist
    if "live_commentary" not in st.session_state:
        st.session_state["live_commentary"] = []
    
    # Add to commentary (keep last 100 entries)
    st.session_state["live_commentary"].append(commentary_entry)
    if len(st.session_state["live_commentary"]) > 100:
        st.session_state["live_commentary"] = st.session_state["live_commentary"][-100:]

def get_commentary_entries(limit=50):
    """Get recent commentary entries, most recent first."""
    if "live_commentary" not in st.session_state:
        return []
    
    entries = st.session_state["live_commentary"]
    return entries[-limit:][::-1]  # Reverse to show newest first

def clear_commentary():
    """Clear all commentary entries."""
    if "live_commentary" in st.session_state:
        st.session_state["live_commentary"] = []

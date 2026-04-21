"""
Indian states data with coordinates and boundaries.
Each state has a center point and approximate boundaries.
Rescue operations are randomly selected at the state level.
"""
import random

# State-level data with aggregated boundaries and resources
STATES = [
    {
        "name": "Bangalore",
        "center": (12.9716, 77.5946),  # Bangalore (lat, lon)
        "bounds": {
            "min_lat": 12.85, "max_lat": 13.05,
            "min_lon": 77.45, "max_lon": 77.75
        },
        "hospitals": [
            {"name": "Bangalore Medical College", "loc": (12.9716, 77.5946)},
            {"name": "Apollo Hospital Bangalore", "loc": (12.9352, 77.6245)},
            {"name": "Victoria Hospital", "loc": (12.9634, 77.5755)},
            {"name": "Nimhans", "loc": (12.9385, 77.5941)},
        ],
        "shelters": [
            {"name": "Bangalore Central Shelter", "loc": (12.9716, 77.5946)},
            {"name": "North Bangalore Shelter", "loc": (13.0350, 77.5973)},
            {"name": "Jayanagar Relief Camp", "loc": (12.9308, 77.5838)},
            {"name": "Indiranagar Camp", "loc": (12.9784, 77.6408)},
        ]
    },
    {
        "name": "Delhi",
        "center": (28.6139, 77.2090), # New Delhi
        "bounds": {
            "min_lat": 28.50, "max_lat": 28.75,
            "min_lon": 77.05, "max_lon": 77.35
        },
        "hospitals": [
            {"name": "AIIMS Delhi", "loc": (28.5672, 77.2100)},
            {"name": "Safdarjung Hospital", "loc": (28.5600, 77.2000)},
            {"name": "RML Hospital", "loc": (28.6268, 77.2016)},
            {"name": "Max Hospital Saket", "loc": (28.5276, 77.2131)},
        ],
        "shelters": [
            {"name": "Delhi Central Shelter", "loc": (28.6139, 77.2090)},
            {"name": "North Delhi Shelter", "loc": (28.6900, 77.1500)},
            {"name": "South Delhi Shelter", "loc": (28.5500, 77.2000)},
            {"name": "East Delhi Shelter", "loc": (28.6300, 77.2900)},
        ]
    },
    {
        "name": "Hyderabad",
        "center": (17.3850, 78.4867),  # Hyderabad
        "bounds": {
            "min_lat": 17.25, "max_lat": 17.50,
            "min_lon": 78.35, "max_lon": 78.60
        },
        "hospitals": [
            {"name": "KIMS Hyderabad", "loc": (17.4326, 78.4864)},
            {"name": "Apollo Jubilee Hills", "loc": (17.4158, 78.4116)},
            {"name": "Osmania Hospital", "loc": (17.3751, 78.4716)},
            {"name": "Care Hospital", "loc": (17.4172, 78.4485)},
        ],
        "shelters": [
            {"name": "Hyderabad Central Shelter", "loc": (17.3850, 78.4867)},
            {"name": "Secunderabad Shelter", "loc": (17.4399, 78.4983)},
            {"name": "Madhapur Camp", "loc": (17.4491, 78.3908)},
            {"name": "Charminar Shelter", "loc": (17.3616, 78.4747)},
        ]
    },
    {
        "name": "Pune",
        "center": (18.5204, 73.8567),
        "bounds": {
            "min_lat": 18.40, "max_lat": 18.65,
            "min_lon": 73.70, "max_lon": 74.00
        },
        "hospitals": [
            {"name": "Ruby Hall Clinic", "loc": (18.5303, 73.8778)},
            {"name": "Jehangir Hospital", "loc": (18.5298, 73.8767)},
            {"name": "Sahyadri Hospital", "loc": (18.5173, 73.8347)},
            {"name": "Sassoon General Hospital", "loc": (18.5255, 73.8732)},
        ],
        "shelters": [
            {"name": "Pune Central Shelter", "loc": (18.5204, 73.8567)},
            {"name": "Pune Camp Shelter", "loc": (18.5113, 73.8797)},
            {"name": "Kothrud Relief Camp", "loc": (18.5074, 73.8077)},
            {"name": "Viman Nagar Shelter", "loc": (18.5679, 73.9143)},
        ]
    },
    {
        "name": "Kurnool",
        "center": (15.8281, 78.0373),
        "bounds": {
            "min_lat": 15.75, "max_lat": 15.90,
            "min_lon": 77.95, "max_lon": 78.15
        },
        "hospitals": [
            {"name": "Government General Hospital", "loc": (15.8200, 78.0300)},
            {"name": "KIMS Kurnool", "loc": (15.8450, 78.0350)},
            {"name": "Gowri Gopal Hospital", "loc": (15.8300, 78.0400)},
            {"name": "Medicover Hospital", "loc": (15.8320, 78.0420)},
        ],
        "shelters": [
            {"name": "Kurnool Central Shelter", "loc": (15.8281, 78.0373)},
            {"name": "Old City Relief Camp", "loc": (15.8250, 78.0350)},
            {"name": "Venkatramana Colony Camp", "loc": (15.8150, 78.0450)},
            {"name": "B-Camp Shelter", "loc": (15.8100, 78.0200)},
        ]
    }
]

# Legacy support - keep districts for backward compatibility
DISTRICTS = [
    {
        "name": "Bangalore Urban",
        "state": "Karnataka",
        "center": (12.9716, 77.5946),
        "bounds": {
            "min_lat": 12.7, "max_lat": 13.2,
            "min_lon": 77.3, "max_lon": 77.9
        },
        "hospitals": [
            {"name": "Bangalore Medical College", "loc": (12.9716, 77.5946)},
            {"name": "Apollo Hospital Bangalore", "loc": (12.9352, 77.6245)},
        ],
        "shelters": [
            {"name": "Bangalore Central Shelter", "loc": (12.9716, 77.5946)},
            {"name": "North Bangalore Shelter", "loc": (13.0350, 77.5973)},
        ]
    },
]

def get_random_state():
    """Randomly select a state for rescue operations."""
    return random.choice(STATES)

def get_state_by_name(name):
    """Get a state by its name."""
    for state in STATES:
        if state["name"] == name:
            return state
    return None

def generate_points_in_state(state, num_points=10):
    """Generate random points within a state's boundaries."""
    bounds = state["bounds"]
    points = []
    for i in range(num_points):
        lat = random.uniform(bounds["min_lat"], bounds["max_lat"])
        lon = random.uniform(bounds["min_lon"], bounds["max_lon"])
        points.append((lon, lat))  # (lon, lat) format for consistency
    return points

# Legacy functions for backward compatibility
def get_random_district():
    """Legacy function - now returns a state instead of district."""
    return get_random_state()

def get_district_by_name(name):
    """Legacy function - now searches states."""
    return get_state_by_name(name)

def generate_points_in_district(district_or_state, num_points=10):
    """Legacy function - works with both districts and states."""
    return generate_points_in_state(district_or_state, num_points)

"""
Indian states data with coordinates and boundaries.
Each state has a center point and approximate boundaries.
Rescue operations are randomly selected at the state level.
"""
import random

# State-level data with aggregated boundaries and resources
STATES = [
    {
        "name": "Karnataka",
        "center": (12.9716, 77.5946),  # Bangalore (lat, lon)
        "bounds": {
            "min_lat": 11.5, "max_lat": 18.5,
            "min_lon": 74.0, "max_lon": 78.5
        },
        "hospitals": [
            {"name": "Bangalore Medical College", "loc": (12.9716, 77.5946)},
            {"name": "Apollo Hospital Bangalore", "loc": (12.9352, 77.6245)},
            {"name": "Mysore Medical College", "loc": (12.2958, 76.6394)},
            {"name": "Mangalore Hospital", "loc": (12.9141, 74.8560)},
        ],
        "shelters": [
            {"name": "Bangalore Central Shelter", "loc": (12.9716, 77.5946)},
            {"name": "North Karnataka Shelter", "loc": (15.3173, 75.7139)},
            {"name": "Mysore Shelter", "loc": (12.2958, 76.6394)},
            {"name": "Hubli Shelter", "loc": (15.3647, 75.1240)},
        ]
    },
    {
        "name": "Maharashtra",
        "center": (19.0760, 72.8777),  # Mumbai
        "bounds": {
            "min_lat": 15.5, "max_lat": 22.0,
            "min_lon": 72.5, "max_lon": 80.5
        },
        "hospitals": [
            {"name": "KEM Hospital Mumbai", "loc": (19.0760, 72.8777)},
            {"name": "Jaslok Hospital", "loc": (18.9500, 72.8100)},
            {"name": "Pune General Hospital", "loc": (18.5204, 73.8567)},
            {"name": "Nagpur Medical College", "loc": (21.1458, 79.0882)},
        ],
        "shelters": [
            {"name": "Mumbai Central Shelter", "loc": (19.0760, 72.8777)},
            {"name": "South Mumbai Shelter", "loc": (18.9400, 72.8300)},
            {"name": "Pune Central Shelter", "loc": (18.5204, 73.8567)},
            {"name": "Nashik Shelter", "loc": (19.9975, 73.7898)},
        ]
    },
    {
        "name": "Delhi",
        "center": (28.7041, 77.1025),
        "bounds": {
            "min_lat": 28.4, "max_lat": 28.9,
            "min_lon": 76.8, "max_lon": 77.4
        },
        "hospitals": [
            {"name": "AIIMS Delhi", "loc": (28.5672, 77.2100)},
            {"name": "Safdarjung Hospital", "loc": (28.5600, 77.2000)},
            {"name": "Delhi General Hospital", "loc": (28.7041, 77.1025)},
            {"name": "Max Hospital Delhi", "loc": (28.6000, 77.2500)},
        ],
        "shelters": [
            {"name": "Delhi Central Shelter", "loc": (28.7041, 77.1025)},
            {"name": "North Delhi Shelter", "loc": (28.7500, 77.1000)},
            {"name": "South Delhi Shelter", "loc": (28.5500, 77.2000)},
            {"name": "East Delhi Shelter", "loc": (28.6500, 77.3000)},
        ]
    },
    {
        "name": "Tamil Nadu",
        "center": (13.0827, 80.2707),  # Chennai
        "bounds": {
            "min_lat": 8.0, "max_lat": 13.5,
            "min_lon": 76.0, "max_lon": 80.5
        },
        "hospitals": [
            {"name": "Apollo Chennai", "loc": (13.0391, 80.2090)},
            {"name": "Chennai General Hospital", "loc": (13.0827, 80.2707)},
            {"name": "Madurai Medical College", "loc": (9.9252, 78.1198)},
            {"name": "Coimbatore Medical College", "loc": (11.0168, 76.9558)},
        ],
        "shelters": [
            {"name": "Chennai Central Shelter", "loc": (13.0827, 80.2707)},
            {"name": "South Chennai Shelter", "loc": (13.0000, 80.2500)},
            {"name": "Coimbatore Shelter", "loc": (11.0168, 76.9558)},
            {"name": "Trichy Shelter", "loc": (10.7905, 78.7047)},
        ]
    },
    {
        "name": "Telangana",
        "center": (17.3850, 78.4867),  # Hyderabad
        "bounds": {
            "min_lat": 15.5, "max_lat": 19.5,
            "min_lon": 77.0, "max_lon": 81.0
        },
        "hospitals": [
            {"name": "KIMS Hyderabad", "loc": (17.4158, 78.4294)},
            {"name": "Apollo Hyderabad", "loc": (17.3850, 78.4867)},
            {"name": "Osmania Hospital", "loc": (17.4000, 78.5000)},
            {"name": "Nizam's Institute", "loc": (17.4200, 78.4500)},
        ],
        "shelters": [
            {"name": "Hyderabad Central Shelter", "loc": (17.3850, 78.4867)},
            {"name": "Secunderabad Shelter", "loc": (17.4500, 78.5000)},
            {"name": "Warangal Shelter", "loc": (18.0000, 79.5833)},
            {"name": "Karimnagar Shelter", "loc": (18.4333, 79.1500)},
        ]
    },
    {
        "name": "West Bengal",
        "center": (22.5726, 88.3639),  # Kolkata
        "bounds": {
            "min_lat": 21.5, "max_lat": 27.0,
            "min_lon": 86.0, "max_lon": 89.5
        },
        "hospitals": [
            {"name": "Kolkata Medical College", "loc": (22.5726, 88.3639)},
            {"name": "Apollo Kolkata", "loc": (22.5500, 88.3500)},
            {"name": "Durgapur Hospital", "loc": (23.5204, 87.3219)},
            {"name": "Siliguri Hospital", "loc": (26.7271, 88.3953)},
        ],
        "shelters": [
            {"name": "Kolkata Central Shelter", "loc": (22.5726, 88.3639)},
            {"name": "North Kolkata Shelter", "loc": (22.6000, 88.3800)},
            {"name": "Howrah Shelter", "loc": (22.5958, 88.2636)},
            {"name": "Asansol Shelter", "loc": (23.6739, 86.9524)},
        ]
    },
    {
        "name": "Gujarat",
        "center": (23.0225, 72.5714),  # Ahmedabad
        "bounds": {
            "min_lat": 20.0, "max_lat": 24.5,
            "min_lon": 68.0, "max_lon": 74.5
        },
        "hospitals": [
            {"name": "Ahmedabad Civil Hospital", "loc": (23.0225, 72.5714)},
            {"name": "Apollo Ahmedabad", "loc": (23.0000, 72.5500)},
            {"name": "Surat General Hospital", "loc": (21.1702, 72.8311)},
            {"name": "Rajkot Hospital", "loc": (22.3039, 70.8022)},
        ],
        "shelters": [
            {"name": "Ahmedabad Central Shelter", "loc": (23.0225, 72.5714)},
            {"name": "Ahmedabad East Shelter", "loc": (23.0500, 72.6000)},
            {"name": "Vadodara Shelter", "loc": (22.3072, 73.1812)},
            {"name": "Gandhinagar Shelter", "loc": (23.2156, 72.6369)},
        ]
    },
    {
        "name": "Rajasthan",
        "center": (26.9124, 75.7873),  # Jaipur
        "bounds": {
            "min_lat": 23.0, "max_lat": 30.5,
            "min_lon": 69.5, "max_lon": 78.5
        },
        "hospitals": [
            {"name": "SMS Hospital Jaipur", "loc": (26.9124, 75.7873)},
            {"name": "Apollo Jaipur", "loc": (26.9000, 75.8000)},
            {"name": "Jodhpur Medical College", "loc": (26.2389, 73.0243)},
            {"name": "Bikaner Hospital", "loc": (28.0229, 73.3119)},
        ],
        "shelters": [
            {"name": "Jaipur Central Shelter", "loc": (26.9124, 75.7873)},
            {"name": "Jaipur North Shelter", "loc": (26.9500, 75.7500)},
            {"name": "Udaipur Shelter", "loc": (24.5854, 73.7125)},
            {"name": "Ajmer Shelter", "loc": (26.4499, 74.6399)},
        ]
    },
    {
        "name": "Uttar Pradesh",
        "center": (26.8467, 80.9462),  # Lucknow
        "bounds": {
            "min_lat": 24.0, "max_lat": 30.5,
            "min_lon": 77.0, "max_lon": 84.5
        },
        "hospitals": [
            {"name": "King George Medical College", "loc": (26.8467, 80.9462)},
            {"name": "Apollo Lucknow", "loc": (26.8500, 80.9500)},
            {"name": "Agra Medical College", "loc": (27.1767, 78.0081)},
            {"name": "Varanasi Hospital", "loc": (25.3176, 82.9739)},
        ],
        "shelters": [
            {"name": "Lucknow Central Shelter", "loc": (26.8467, 80.9462)},
            {"name": "Lucknow East Shelter", "loc": (26.8600, 81.0000)},
            {"name": "Kanpur Shelter", "loc": (26.4499, 80.3319)},
            {"name": "Allahabad Shelter", "loc": (25.4358, 81.8463)},
        ]
    },
    {
        "name": "Punjab",
        "center": (30.7333, 76.7794),  # Chandigarh
        "bounds": {
            "min_lat": 29.5, "max_lat": 32.5,
            "min_lon": 73.5, "max_lon": 77.0
        },
        "hospitals": [
            {"name": "PGI Chandigarh", "loc": (30.7333, 76.7794)},
            {"name": "Amritsar Medical College", "loc": (31.6340, 74.8560)},
            {"name": "Ludhiana Hospital", "loc": (30.9010, 75.8573)},
            {"name": "Jalandhar Hospital", "loc": (31.3260, 75.5762)},
        ],
        "shelters": [
            {"name": "Chandigarh Central Shelter", "loc": (30.7333, 76.7794)},
            {"name": "Amritsar Shelter", "loc": (31.6340, 74.8560)},
            {"name": "Ludhiana Shelter", "loc": (30.9010, 75.8573)},
            {"name": "Patiala Shelter", "loc": (30.3398, 76.3869)},
        ]
    },
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

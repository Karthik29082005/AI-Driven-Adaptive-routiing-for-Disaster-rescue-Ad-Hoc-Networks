import networkx as nx
from districts import get_random_state, generate_points_in_state

class Node:
    def __init__(self, nid, x, y, ntype):
        self.id = nid
        self.x = x  # longitude
        self.y = y  # latitude
        self.type = ntype

class DemoEnv:
    """
    Simple demo MANET graph over a randomly selected Indian state.
    """
    def __init__(self):
        self.G = nx.Graph()
        self.nodes = {}
        # Randomly select a state for rescue operations
        self.state = get_random_state()
        # Keep 'district' for backward compatibility
        self.district = self.state
        self._create_demo_nodes()
        self._connect_nodes()

    def _create_demo_nodes(self):
        # Create 4 units of each type (5 types × 4 = 20 units)
        unit_types = ["drone", "ambulance", "van", "fire_truck", "police"]
        units_per_type = 4
        
        # We assume self.district is set to a small area instead of a whole state
        self.district = self.state  # backward compat
        center_lat, center_lon = self.district["center"]
        base_coords = [(center_lon, center_lat)]
        
        additional_points = generate_points_in_state(self.district, num_points=units_per_type * len(unit_types) - 1)
        base_coords.extend(additional_points)
        
        node_id = 0
        for unit_type in unit_types:
            for _ in range(units_per_type):
                if node_id < len(base_coords):
                    lon, lat = base_coords[node_id]
                    node = Node(node_id, lon, lat, unit_type)
                    self.nodes[node_id] = node
                    self.G.add_node(node_id)
                    node_id += 1

    def _connect_nodes(self, k=2):
        import requests
        import time
        import streamlit as st
        
        def dist_km(a, b):
            return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5 * 111.0

        ids = list(self.nodes.keys())
        # Connect to k nearest neighbors
        
        # We need a small delay between requests to avoid hitting the public OSRM rate limit
        # The public API is very strict. If we hit 429 Too Many Requests, it falls back to straight lines
        total_requests = 0
        osrm_available = True
        
        for i in ids:
            n1 = self.nodes[i]
            # Find k nearest
            others = [j for j in ids if j != i]
            others.sort(key=lambda j: dist_km(n1, self.nodes[j]))
            nearest = others[:k]
            
            for j in nearest:
                if not self.G.has_edge(i, j):
                    n2 = self.nodes[j]
                    
                    if osrm_available:
                        # Fetch OSRM route using a more reliable public endpoint from openstreetmap.de
                        url = f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{n1.x},{n1.y};{n2.x},{n2.y}?geometries=geojson&overview=full"
                        try:
                            # Respect OSM terms of use
                            if total_requests > 0:
                                time.sleep(0.2)
                            total_requests += 1
                            
                            headers = {'User-Agent': 'DisasterRescueAI/1.0 (test@example.com)'}
                            resp = requests.get(url, headers=headers, timeout=5.0)
                            
                            if resp.status_code == 429:
                                # If rate limited, just raise exception to fallback to straight lines instantly
                                raise Exception("OSRM Rate Limited (429)! Falling back.")
                                
                            resp.raise_for_status() # Raise exception for bad status codes
                            
                            data = resp.json()
                            if data.get("code") == "Ok":
                                route = data["routes"][0]
                                dist = route["distance"] / 1000.0  # km
                                coords = route["geometry"]["coordinates"]
                                geom = [(lat, lon) for (lon, lat) in coords]
                                self.G.add_edge(i, j, weight=dist, geometry=geom)
                            else:
                                d = dist_km(n1, n2)
                                self.G.add_edge(i, j, weight=d, geometry=[(n1.y, n1.x), (n2.y, n2.x)])
                        except Exception as e:
                            print(f"OSRM Error ({n1.id}->{n2.id}) - Disabling OSRM and falling back to straight distances: {e}")
                            osrm_available = False
                            # Fallback to straight line if OSRM is slow/down
                            d = dist_km(n1, n2)
                            self.G.add_edge(i, j, weight=d, geometry=[(n1.y, n1.x), (n2.y, n2.x)])
                    else:
                        # OSRM is unavailable, skip request entirely
                        d = dist_km(n1, n2)
                        self.G.add_edge(i, j, weight=d, geometry=[(n1.y, n1.x), (n2.y, n2.x)])

    def shortest_path(self, src, dst):
        try:
            return nx.shortest_path(self.G, src, dst, weight="weight")
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def break_connections(self, node_id):
        if node_id in self.G:
            self.G.remove_node(node_id)

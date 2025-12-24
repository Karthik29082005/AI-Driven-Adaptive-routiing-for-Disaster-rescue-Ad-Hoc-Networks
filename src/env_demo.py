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
        # Create 3-4 units of each type (5 types × 4 = 20 units)
        unit_types = ["drone", "ambulance", "van", "fire_truck", "police"]
        units_per_type = 4  # 4 units of each type
        
        # Generate nodes within the selected state
        # Use state center as one point, then generate others nearby
        center_lat, center_lon = self.state["center"]
        base_coords = [(center_lon, center_lat)]  # Start with state center
        
        # Generate enough points for all units (20 units)
        additional_points = generate_points_in_state(self.state, num_points=units_per_type * len(unit_types) - 1)
        base_coords.extend(additional_points)
        
        node_id = 0
        # Create 4 units of each type
        for unit_type in unit_types:
            for _ in range(units_per_type):
                if node_id < len(base_coords):
                    lon, lat = base_coords[node_id]
                    node = Node(node_id, lon, lat, unit_type)
                    self.nodes[node_id] = node
                    self.G.add_node(node_id)
                    node_id += 1

    def _connect_nodes(self, max_dist_km=200.0):
        def dist_km(a, b):
            return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5 * 111.0

        ids = list(self.nodes.keys())
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                n1 = self.nodes[ids[i]]
                n2 = self.nodes[ids[j]]
                d = dist_km(n1, n2)
                if d <= max_dist_km:
                    self.G.add_edge(n1.id, n2.id, weight=d)

    def shortest_path(self, src, dst):
        return nx.shortest_path(self.G, src, dst, weight="weight")

    def break_connections(self, node_id):
        if node_id in self.G:
            self.G.remove_node(node_id)

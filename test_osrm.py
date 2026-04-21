import sys
import os

# add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from env_demo import DemoEnv

print("Creating DemoEnv to test OSRM queries...")
try:
    env = DemoEnv()
    print(f"Graph initialized with {env.G.number_of_nodes()} nodes and {env.G.number_of_edges()} edges.")
    has_geom = 0
    for u, v, data in env.G.edges(data=True):
        if "geometry" in data and len(data["geometry"]) > 2:
            has_geom += 1
    print(f"Edges with OSRM geometries: {has_geom}")
    print("Success!")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("Failed")

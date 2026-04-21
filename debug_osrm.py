import requests

# Test a simple route between two coordinates in India
lon1, lat1 = 77.2090, 28.6139 # Delhi
lon2, lat2 = 77.0266, 28.4595 # Gurgaon

url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?geometries=geojson&overview=full"
print(f"Requesting: {url}")
try:
    resp = requests.get(url, timeout=10)
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == "Ok":
            route = data["routes"][0]
            dist = route["distance"] / 1000.0  # km
            coords = route["geometry"]["coordinates"]
            print(f"Success! Route distance: {dist:.2f} km")
            print(f"Number of coordinates in geometry: {len(coords)}")
        else:
            print(f"API Returned Code: {data.get('code')}")
            print(data)
    else:
        print(f"Error Response: {resp.text}")
except Exception as e:
    print(f"Request failed with exception: {e}")

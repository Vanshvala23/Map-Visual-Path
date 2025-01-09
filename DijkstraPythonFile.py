import requests
import folium
import webbrowser
import os
import random

# Your TomTom API key
API_KEY = "IdImQLwJMrB88pnVWZZnAVZmQ7CsqmxH"

# Rajkot center coordinates
CENTER_LAT = 22.3039
CENTER_LON = 70.8022

# Function to generate random locations within a given range around Rajkot
def generate_random_nodes(num_nodes=200, lat_range=1.5, lon_range=1.5):
    nodes = []
    for i in range(num_nodes):
        lat_offset = random.uniform(-lat_range, lat_range)
        lon_offset = random.uniform(-lon_range, lon_range)
        nodes.append({
            "label": f"Node {i + 1}",
            "lat": CENTER_LAT + lat_offset,
            "lon": CENTER_LON + lon_offset
        })
    return nodes

# Generate 200 random nodes (increase as per need)
nodes = generate_random_nodes()

# Function to calculate a route
def get_route(start, end):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    params = {
        "key": API_KEY,
        "traffic": "true",
        "routeType": "fastest"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function to build a map with nodes
def build_node_map():
    # Center map on Rajkot
    center = (CENTER_LAT, CENTER_LON)  # Rajkot coordinates
    node_map = folium.Map(location=center, zoom_start=12)

    # Add nodes as markers
    for node in nodes:
        folium.Marker(
            location=(node["lat"], node["lon"]),
            popup=node["label"],
            tooltip="Click to select",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(node_map)

    return node_map

# Function to build a route map
def build_route_map(route_data):
    # Center on the first point of the route
    first_point = route_data["routes"][0]["legs"][0]["points"][0]
    route_map = folium.Map(location=[first_point["latitude"], first_point["longitude"]], zoom_start=14)

    # Draw route
    for leg in route_data["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="blue", popup="Route").add_to(route_map)

    return route_map

# Function to open HTML map in browser
def open_html_map(filename):
    url = f"file://{os.path.realpath(filename)}"
    webbrowser.open(url, new=2)

# Main Execution
if __name__ == "__main__":
    # Build and save map with nodes
    node_map = build_node_map()
    node_map.save("NodeMap.html")
    open_html_map("NodeMap.html")
    print("Node map saved as NodeMap.html. Open it to view nodes.")

    # Prompt user to select start and end nodes
    print("\nAvailable Nodes:")
    for idx, node in enumerate(nodes):
        print(f"{idx + 1}. {node['label']} ({node['lat']}, {node['lon']})")

    start_idx = int(input("\nSelect start node (enter number): ")) - 1
    end_idx = int(input("Select end node (enter number): ")) - 1

    start = f"{nodes[start_idx]['lat']},{nodes[start_idx]['lon']}"
    end = f"{nodes[end_idx]['lat']},{nodes[end_idx]['lon']}"

    # Fetch and display the route
    route_data = get_route(start, end)
    route_map = build_route_map(route_data)
    route_map.save("RouteMap.html")
    open_html_map("RouteMap.html")
    print("Route map saved as RouteMap.html. Open it to view the route.")

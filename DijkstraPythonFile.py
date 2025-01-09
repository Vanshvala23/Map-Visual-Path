import requests
import folium
import webbrowser
import os
import random
import json

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
def get_route(start, end, route_type="fastest"):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    params = {
        "key": API_KEY,
        "traffic": "true",
        "routeType": route_type,  # Use route type to get different kinds of routes
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function to get multiple routes
def get_multiple_routes(start, end):
    # Fetch different route types (fastest, shortest, etc.)
    fastest_route = get_route(start, end, "fastest")
    shortest_route = get_route(start, end, "shortest")
    
    # You can also fetch a route with no traffic
    no_traffic_route = get_route(start, end, "fastest")  # No traffic route

    return fastest_route, shortest_route, no_traffic_route

# Function to find the shortest and longest route from multiple alternatives
def get_shortest_and_longest_route(route_data):
    # Sort the routes by distance (legs[0].distance)
    routes = route_data
    sorted_routes = sorted(routes, key=lambda x: x["routes"][0]["summary"]["lengthInMeters"])

    shortest_route = sorted_routes[0]  # The shortest route
    longest_route = sorted_routes[-1]  # The longest route

    return shortest_route, longest_route

# Function to build a route map with multiple routes (shortest and longest)
def build_route_map(route_data, shortest_route, longest_route):
    # Center on the first point of the shortest route
    first_point = shortest_route["routes"][0]["legs"][0]["points"][0]
    route_map = folium.Map(location=[first_point["latitude"], first_point["longitude"]], zoom_start=14)

    # Draw shortest route (blue)
    for leg in shortest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="blue", popup="Shortest Route").add_to(route_map)

    # Draw longest route (red)
    for leg in longest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="red", popup="Longest Route").add_to(route_map)

    return route_map

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

# Function to open HTML map in browser
def open_html_map(filename):
    url = f"file://{os.path.realpath(filename)}"
    webbrowser.open(url, new=2)

# Save the route information in a JSON file
def save_route_info(shortest_route, longest_route):
    route_info = {
        "shortest_route": shortest_route["routes"][0]["summary"],
        "longest_route": longest_route["routes"][0]["summary"]
    }
    with open("route_info.json", "w") as json_file:
        json.dump(route_info, json_file, indent=4)

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

    # Fetch multiple route alternatives
    route_data = get_multiple_routes(start, end)

    # Get shortest and longest route
    shortest_route, longest_route = get_shortest_and_longest_route(route_data)

    # Build and save the shortest and longest route map
    route_map = build_route_map(route_data, shortest_route, longest_route)
    route_map.save("RouteMap.html")
    open_html_map("RouteMap.html")
    print("Route map saved as RouteMap.html. Open it to view both the shortest and longest routes.")

    # Save route information in a JSON file
    save_route_info(shortest_route, longest_route)
    print("Route information saved as route_info.json.")

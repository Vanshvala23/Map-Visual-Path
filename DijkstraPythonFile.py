import requests
import folium
import webbrowser
import os
import random
import json

API_KEY = "IdImQLwJMrB88pnVWZZnAVZmQ7CsqmxH"
CENTER_LAT = 22.3039
CENTER_LON = 70.8022

def generate_random_nodes(num_nodes=200, lat_range=0.5, lon_range=0.5):
    nodes = []
    for i in range(num_nodes):
        lat_offset = random.uniform(-lat_range, lat_range)
        lon_offset = random.uniform(-lon_range, lon_range)
        lat = CENTER_LAT + lat_offset
        lon = CENTER_LON + lon_offset
        if lat > 20.5 and lat < 24.0 and lon > 69.5 and lon < 72.5:
            nodes.append({"label": f"Node {i + 1}", "lat": lat, "lon": lon})
    return nodes

nodes = generate_random_nodes()

def get_route(start, end, route_type="fastest"):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    params = {
        "key": API_KEY,
        "traffic": "true",  # Real-time traffic data
        "routeType": route_type,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_multiple_routes(start, end):
    fastest_route = get_route(start, end, "fastest")
    shortest_route = get_route(start, end, "shortest")
    no_traffic_route = get_route(start, end, "fastest")
    return fastest_route, shortest_route, no_traffic_route

def get_shortest_and_longest_route(route_data):
    routes = route_data
    sorted_routes = sorted(routes, key=lambda x: x["routes"][0]["summary"]["lengthInMeters"])
    shortest_route = sorted_routes[0]
    longest_route = sorted_routes[-1]
    return shortest_route, longest_route

def build_route_map(route_data, shortest_route, longest_route):
    first_point = shortest_route["routes"][0]["legs"][0]["points"][0]
    route_map = folium.Map(location=[first_point["latitude"], first_point["longitude"]], zoom_start=14)

    # Shortest route in purple
    for leg in shortest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="blue", popup="Shortest Route").add_to(route_map)

    # Longest route in green
    for leg in longest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="red", popup="Longest Route").add_to(route_map)

    # Adding a tile layer with proper attribution (Stamen Terrain)
    folium.TileLayer(
        tiles="Stamen Terrain", 
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    ).add_to(route_map)

    return route_map

def build_node_map():
    center = (CENTER_LAT, CENTER_LON)
    node_map = folium.Map(location=center, zoom_start=12)
    for node in nodes:
        folium.Marker(
            location=(node["lat"], node["lon"]),
            popup=node["label"],
            tooltip="Click to select",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(node_map)
    return node_map

def open_html_map(filename):
    url = f"file://{os.path.realpath(filename)}"
    webbrowser.open(url, new=2)

def save_route_info(shortest_route, longest_route):
    route_info = {
        "shortest_route": shortest_route["routes"][0]["summary"],
        "longest_route": longest_route["routes"][0]["summary"]
    }
    with open("route_info.json", "w") as json_file:
        json.dump(route_info, json_file, indent=4)

if __name__ == "__main__":
    node_map = build_node_map()
    node_map.save("NodeMap.html")
    open_html_map("NodeMap.html")
    print("Node map saved as NodeMap.html. Open it to view nodes.")

    print("\nAvailable Nodes:")
    for idx, node in enumerate(nodes):
        print(f"{idx + 1}. {node['label']} ({node['lat']}, {node['lon']})")

    start_idx = int(input("\nSelect start node (enter number): ")) - 1
    end_idx = int(input("Select end node (enter number): ")) - 1

    start = f"{nodes[start_idx]['lat']},{nodes[start_idx]['lon']}"
    end = f"{nodes[end_idx]['lat']},{nodes[end_idx]['lon']}"

    route_data = get_multiple_routes(start, end)

    shortest_route, longest_route = get_shortest_and_longest_route(route_data)

    route_map = build_route_map(route_data, shortest_route, longest_route)
    route_map.save("RouteMap.html")
    open_html_map("RouteMap.html")
    print("Route map saved as RouteMap.html. Open it to view both the shortest and longest routes.")

    save_route_info(shortest_route, longest_route)
    print("Route information saved as route_info.json.")
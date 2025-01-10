from flask import Flask, render_template, request, jsonify
import requests
import folium
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
        if 20.5 < lat < 24.0 and 69.5 < lon < 72.5:
            nodes.append({"label": f"Node {i + 1}", "lat": lat, "lon": lon})
    return nodes

def get_route(start, end, route_type="fastest"):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    params = {
        "key": API_KEY,
        "traffic": "true",
        "routeType": route_type,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_multiple_routes(start, end):
    fastest_route = get_route(start, end, "fastest")
    shortest_route = get_route(start, end, "shortest")
    return [fastest_route, shortest_route]

def get_shortest_and_longest_route(route_data):
    sorted_routes = sorted(route_data, key=lambda x: x["routes"][0]["summary"]["lengthInMeters"])
    return sorted_routes[0], sorted_routes[-1]

def build_route_map(route_data, shortest_route, longest_route):
    first_point = shortest_route["routes"][0]["legs"][0]["points"][0]
    route_map = folium.Map(location=[first_point["latitude"], first_point["longitude"]], zoom_start=14)

    for leg in shortest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="blue", popup="Shortest Route").add_to(route_map)

    for leg in longest_route["routes"][0]["legs"]:
        points = [(point["latitude"], point["longitude"]) for point in leg["points"]]
        folium.PolyLine(points, weight=5, color="red", popup="Longest Route").add_to(route_map)

    folium.TileLayer(
        tiles="Stamen Terrain",
        attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
    ).add_to(route_map)

    return route_map

def save_route_info(shortest_route, longest_route):
    route_info = {
        "shortest_route": shortest_route["routes"][0]["summary"],
        "longest_route": longest_route["routes"][0]["summary"]
    }
    with open("route_info.json", "w") as json_file:
        json.dump(route_info, json_file, indent=4)

app = Flask(__name__)
nodes = generate_random_nodes()

@app.route("/")
def index():
    return render_template("index.html", nodes=nodes)

@app.route("/generate_routes", methods=["POST"])
def generate_routes():
    try:
        data = request.json
        start_idx = int(data["start_node"])
        end_idx = int(data["end_node"])

        if start_idx == end_idx:
            return jsonify({"error": "Start and end nodes must be different."}), 400

        start = f"{nodes[start_idx]['lat']},{nodes[start_idx]['lon']}"
        end = f"{nodes[end_idx]['lat']},{nodes[end_idx]['lon']}"

        route_data = get_multiple_routes(start, end)
        shortest_route, longest_route = get_shortest_and_longest_route(route_data)

        route_map = build_route_map(route_data, shortest_route, longest_route)
        route_map.save("static/RouteMap.html")

        save_route_info(shortest_route, longest_route)

        return jsonify({"message": "Routes generated successfully.", "map_url": "/static/RouteMap.html"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

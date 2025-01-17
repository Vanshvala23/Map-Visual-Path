from flask import Flask, render_template, request, jsonify
import requests
import folium
import os
import json

API_KEY = "IdImQLwJMrB88pnVWZZnAVZmQ7CsqmxH"

app = Flask(__name__, static_folder="static")

def get_coordinates(location_name):
    url = f"https://api.tomtom.com/search/2/geocode/{location_name}.json"
    params = {"key": API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    if results.get("results"):
        position = results["results"][0]["position"]
        return position["lat"], position["lon"]
    raise ValueError(f"No coordinates found for {location_name}")

def get_route(start, end, route_type="fastest"):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{end}/json"
    params = {"key": API_KEY, "routeType": route_type}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def build_route_map(route, map_name, color):
    points = [
        (point["latitude"], point["longitude"])
        for leg in route["routes"][0]["legs"]
        for point in leg["points"]
    ]
    map_center = points[0]
    route_map = folium.Map(location=map_center, zoom_start=12)
    folium.PolyLine(points, color=color, weight=5, popup=f"{map_name} Route").add_to(route_map)
    map_path = os.path.join("static", f"{map_name}RouteMap.html")
    route_map.save(map_path)
    return map_path

@app.route("/")
def index():
    return render_template("index.html", locations=default_location_names)

@app.route("/generate_routes", methods=["POST"])
def generate_routes():
    data = request.get_json()
    start_idx = int(data["start_node"])
    end_idx = int(data["end_node"])
    if start_idx == end_idx:
        return jsonify({"error": "Start and end nodes must be different."}), 400
    start_coords = f"{coordinates[start_idx][0]},{coordinates[start_idx][1]}"
    end_coords = f"{coordinates[end_idx][0]},{coordinates[end_idx][1]}"
    fastest_route = get_route(start_coords, end_coords, "fastest")
    shortest_route = get_route(start_coords, end_coords, "shortest")
    shortest_map_path = build_route_map(shortest_route, "Shortest", "blue")
    longest_map_path = build_route_map(fastest_route, "Longest", "red")
    return jsonify({
        "shortest_map_url": "/" + shortest_map_path,
        "longest_map_url": "/" + longest_map_path
    })

default_location_names = [
    "Gujarat, India","Mumbai, India","Bangalore, India","Delhi, India"
]
coordinates = [get_coordinates(loc) for loc in default_location_names]

if __name__ == "__main__":
    app.run(debug=True)

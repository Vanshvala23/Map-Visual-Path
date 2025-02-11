from flask import Flask, render_template, request, jsonify
import requests

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
    params = {"key": API_KEY, "routeType": route_type, "traffic": "true"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@app.route("/")
def index():
    return render_template("index.html", locations=default_location_names)
@app.route("/generate_routes", methods=["POST"])
def generate_routes():
    data = request.get_json()
    print("Received data:", data)  # Debugging line

    if not data or "start_node" not in data or "end_node" not in data:
        return jsonify({"error": "Missing start_node or end_node in request body."}), 400

    start_idx = int(data["start_node"])
    end_idx = int(data["end_node"])

    if start_idx == end_idx:
        return jsonify({"error": "Start and end locations must be different."}), 400

    start_coords = f"{coordinates[start_idx][0]},{coordinates[start_idx][1]}"
    end_coords = f"{coordinates[end_idx][0]},{coordinates[end_idx][1]}"

    fastest_route = get_route(start_coords, end_coords, "fastest")
    shortest_route = get_route(start_coords, end_coords, "shortest")

    def extract_route_data(route):
        legs = route["routes"][0]["legs"][0]
        distance_km = legs["summary"]["lengthInMeters"] / 1000  
        duration_min = legs["summary"]["travelTimeInSeconds"] / 60  
        traffic_delay = legs["summary"].get("trafficDelayInSeconds", 0) / 60  
        return {
            "distance": round(distance_km, 2),
            "duration": round(duration_min, 2),
            "traffic_delay": round(traffic_delay, 2),
            "coordinates": [(p["latitude"], p["longitude"]) for p in legs["points"]]
        }

    fastest_data = extract_route_data(fastest_route)
    shortest_data = extract_route_data(shortest_route)

    return jsonify({
        "fastest_route": fastest_data,
        "shortest_route": shortest_data
    })

default_location_names = [
    "Gujarat, India", "Mumbai, India", "Bangalore, India", "Delhi, India"
]
coordinates = [get_coordinates(loc) for loc in default_location_names]

if __name__ == "__main__":
    app.run(debug=True)

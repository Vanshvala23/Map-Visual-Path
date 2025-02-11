document.addEventListener("DOMContentLoaded", function () {
    const map = L.map("map").setView([22.9734, 78.6569], 5); // Default to India

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const generateRoutesBtn = document.getElementById("generateRoutes");
    let fastestRouteLayer, shortestRouteLayer;
    let fastestDot, shortestDot;
    let fastestAnimation, shortestAnimation;

    generateRoutesBtn.addEventListener("click", function () {
        const startIndex = document.getElementById("start").value;
        const endIndex = document.getElementById("end").value;

        fetch("/generate_routes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ start_node: startIndex, end_node: endIndex }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            // Clear previous routes & markers
            if (fastestRouteLayer) map.removeLayer(fastestRouteLayer);
            if (shortestRouteLayer) map.removeLayer(shortestRouteLayer);
            if (fastestDot) map.removeLayer(fastestDot);
            if (shortestDot) map.removeLayer(shortestDot);
            if (fastestAnimation) clearInterval(fastestAnimation);
            if (shortestAnimation) clearInterval(shortestAnimation);

            // Convert coordinates
            const fastestCoords = data.fastest_route.coordinates.map(c => [c[0], c[1]]);
            const shortestCoords = data.shortest_route.coordinates.map(c => [c[0], c[1]]);

            // Draw routes
            fastestRouteLayer = L.polyline(fastestCoords, { color: "red", weight: 5 }).addTo(map);
            shortestRouteLayer = L.polyline(shortestCoords, { color: "blue", weight: 5 }).addTo(map);

            // Fit map to route bounds
            const bounds = L.latLngBounds(fastestCoords.concat(shortestCoords));
            map.fitBounds(bounds);

            // Display Route Details
            document.getElementById("route-details").innerHTML = `
                <div class="text-lg">
                    <p><span class="text-red-400 font-bold cursor-pointer" id="longestRoute">🔴 Longest Route:</span> ${data.fastest_route.distance} km, ${data.fastest_route.duration} min, Traffic Delay: ${data.fastest_route.traffic_delay} min</p>
                    <p><span class="text-blue-400 font-bold cursor-pointer" id="shortestRoute">🔵 Shortest Route:</span> ${data.shortest_route.distance} km, ${data.shortest_route.duration} min</p>
                </div>
            `;

            // Initialize Dot Markers
            fastestDot = L.circleMarker(fastestCoords[0], {
                radius: 6, // Size of the dot
                color: "red",
                fillColor: "red",
                fillOpacity: 1
            }).addTo(map);

            shortestDot = L.circleMarker(shortestCoords[0], {
                radius: 6,
                color: "blue",
                fillColor: "blue",
                fillOpacity: 1
            }).addTo(map);

            // Animate Dots
            animateDot(fastestCoords, fastestDot, 50); // Red Route Animation
            animateDot(shortestCoords, shortestDot, 80); // Blue Route Animation

            // Handle Route Click Events
            document.getElementById("longestRoute").addEventListener("click", () => {
                map.fitBounds(fastestRouteLayer.getBounds());
            });

            document.getElementById("shortestRoute").addEventListener("click", () => {
                map.fitBounds(shortestRouteLayer.getBounds());
            });

        })
        .catch(error => console.error("Error:", error));
    });

    function animateDot(routeCoords, dot, speed) {
        let index = 0;
        function moveDot() {
            if (index < routeCoords.length) {
                dot.setLatLng(routeCoords[index]);
                index++;
            } else {
                clearInterval(dot.animation);
            }
        }
        dot.animation = setInterval(moveDot, speed);
    }
});

// Include Turf.js via CDN
const turfScript = document.createElement("script");
turfScript.src = "https://cdnjs.cloudflare.com/ajax/libs/Turf.js/6.5.0/turf.min.js";
document.body.appendChild(turfScript);

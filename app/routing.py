"""Real routing on actual OpenStreetMap road data via the free public OSRM
demo server — genuine driving/walking distance and duration, no invented
numbers. The public demo server is rate-limited and meant for light/
prototype use; self-host OSRM or use a paid router for production traffic.
"""
import httpx

OSRM_URL = "https://router.project-osrm.org/route/v1"

OSRM_PROFILE = {
    "driving": "driving",
    "walking": "foot",
    "boda": "driving",
    "matatu": "driving",
    "danfo": "driving",
}


async def get_route(origin: dict, destination: dict, mode: str) -> dict:
    profile = OSRM_PROFILE.get(mode, "driving")
    coords = f"{origin['lng']},{origin['lat']};{destination['lng']},{destination['lat']}"
    url = f"{OSRM_URL}/{profile}/{coords}"

    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(url, params={"overview": "full", "geometries": "geojson"})
        res.raise_for_status()
        data = res.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("No route found between those points")

    route = data["routes"][0]

    # OSRM gives [lng, lat] pairs; Leaflet (the map library) wants [lat, lng] —
    # this swaps them so the frontend can use it directly.
    geometry = [[lat, lng] for lng, lat in route["geometry"]["coordinates"]]

    return {
        "distance_km": route["distance"] / 1000,
        "base_duration_minutes": route["duration"] / 60,
        "route_geometry": geometry,
    }
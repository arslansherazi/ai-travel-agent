from fastmcp import FastMCP
from mcp.servers.places.service import PlacesService
import os

server = FastMCP("Places Server")

# Initialize the places service with API key from environment
places_service = PlacesService(api_key=os.getenv("GOOGLE_PLACES_API_KEY"))

@server.tool()
def search_places(
    location: str,
    place_type: str = None,
    radius: int = 5000,
    limit: int = 20,
    min_rating: float = None,
    price_level: str = None
) -> str:
    """
    Search for places based on location and criteria

    :param location: location to search (city name, address, etc.) or coordinates as "lat,lng"
    :param place_type: type of place (restaurant, tourist_attraction, museum, etc.)
    :param radius: search radius in meters (default: 5000, max: 50000)
    :param limit: maximum number of results (default: 20, max: 60)
    :param min_rating: minimum rating filter (0-5)
    :param price_level: price level (free, inexpensive, moderate, expensive, very_expensive)
    :return: formatted list of places matching the criteria
    """
    # Handle coordinate input
    if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
        try:
            lat, lng = map(float, location.split(","))
            location = (lat, lng)
        except ValueError:
            pass  # Keep as string if parsing fails
    
    return places_service.search_places(location, place_type, radius, limit, min_rating, price_level)


@server.tool()
def recommend_places_by_weather(
    location: str,
    weather_condition: str,
    max_distance: int = 5000,
    limit: int = 20
) -> str:
    """
    Recommend places based on current weather conditions

    :param location: location to search (city name, address, etc.) or coordinates as "lat,lng"
    :param weather_condition: weather condition (sunny, rainy, cloudy, snowy, windy, hot, cold)
    :param max_distance: maximum distance to search in meters (default: 5000)
    :param limit: maximum number of recommendations (default: 20)
    :return: weather-appropriate place recommendations
    """
    # Handle coordinate input
    if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
        try:
            lat, lng = map(float, location.split(","))
            location = (lat, lng)
        except ValueError:
            pass  # Keep as string if parsing fails
    
    return places_service.recommend_places_by_weather(location, weather_condition, max_distance, limit)


@server.tool()
def recommend_places_by_distance(
    location: str,
    travel_mode: str = "walking",
    limit: int = 20
) -> str:
    """
    Recommend places based on travel distance and mode

    :param location: location to search (city name, address, etc.) or coordinates as "lat,lng"
    :param travel_mode: travel mode (walking, short_drive, day_trip, extended)
    :param limit: maximum number of recommendations (default: 20)
    :return: distance-appropriate place recommendations
    """
    # Handle coordinate input
    if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
        try:
            lat, lng = map(float, location.split(","))
            location = (lat, lng)
        except ValueError:
            pass  # Keep as string if parsing fails
    
    return places_service.recommend_places_by_distance(location, travel_mode, limit) 
"""
Places server tools for tourist attraction discovery using OpenTripMap API
Provides human-readable, user-friendly tools for finding attractions
"""

from fastmcp import FastMCP
from _mcp.servers.places.service import PlacesService
import os

server = FastMCP("Places Server")
places_service = PlacesService(api_key=os.getenv("OPENTRIPMAP_API_KEY"))


@server.tool()
def search_attractions(
    location: str,
    category: str = None,
    distance_km: int = 10,
    max_results: int = 20,
    language: str = "en"
) -> str:
    """
    Search for tourist attractions and points of interest near a location

    :param location: city, address, or landmark name (e.g., "Rome", "Eiffel Tower", "Times Square New York")
    :param category: type of attraction (natural, cultural, museums, architecture, amusements, sport, etc.)
    :param distance_km: search distance in kilometers from location (default: 10, max: 50)
    :param max_results: maximum number of results to return (default: 20, max: 100)
    :param language: language for results (en, de, fr, es, it, pt, ru, zh, ja, ar, hi)
    :return: formatted list of tourist attractions with descriptions and distances
    """
    try:
        # Convert km to meters for API and validate limits
        radius_meters = min(distance_km * 1000, 50000)
        max_results = min(max_results, 100)
        
        # Get coordinates for the location using base service
        lat, lng = places_service.get_coordinates(location)
        if not lat or not lng:
            return f"Could not find coordinates for location: {location}. Please try a more specific location name."
        
        location_str = f"{lat},{lng}"
        
        return places_service.search_places(location_str, category, radius_meters, max_results, language)
    except Exception as e:
        return f"Error searching attractions: {str(e)}"


@server.tool()
def find_attractions_by_name(
    attraction_name: str,
    near_location: str = None,
    language: str = "en"
) -> str:
    """
    Find specific attractions by name, optionally near a location

    :param attraction_name: name of the attraction to find (e.g., "Colosseum", "Statue of Liberty")
    :param near_location: optional city or area to search near (e.g., "Rome", "New York")
    :param language: language for results (en, de, fr, es, it, pt, ru, zh, ja, ar, hi)
    :return: formatted details about the specific attraction(s) found
    """
    try:
        # Build search query
        search_query = attraction_name
        if near_location:
            search_query = f"{attraction_name} {near_location}"
        
        return places_service.autocomplete_places(search_query, language)
    except Exception as e:
        return f"Error finding attraction: {str(e)}"


@server.tool()
def explore_area_attractions(
    location: str,
    area_size: str = "city",
    category: str = None,
    max_results: int = 50,
    language: str = "en"
) -> str:
    """
    Explore all attractions in a city, neighborhood, or region

    :param location: city, neighborhood, or region name (e.g., "Rome", "Manhattan", "Tuscany")
    :param area_size: size of area to explore ("neighborhood", "city", "region")
    :param category: type of attractions to focus on (natural, cultural, museums, etc.)
    :param max_results: maximum number of results (default: 50, max: 100)
    :param language: language for results (en, de, fr, es, it, pt, ru, zh, ja, ar, hi)
    :return: comprehensive list of attractions in the specified area
    """
    try:
        max_results = min(max_results, 100)
        
        # Map area size to search radius
        radius_mapping = {
            "neighborhood": 2,  # 2km
            "city": 15,         # 15km  
            "region": 50        # 50km
        }
        radius_km = radius_mapping.get(area_size.lower(), 15)
        
        # Get coordinates for the location using base service
        lat, lng = places_service.get_coordinates(location)
        if not lat or not lng:
            return f"Could not find coordinates for location: {location}. Please try a more specific location name."
        
        location_str = f"{lat},{lng}"
        radius_meters = radius_km * 1000
        
        return places_service.search_places(location_str, category, radius_meters, max_results, language)
    except Exception as e:
        return f"Error exploring area: {str(e)}"


@server.tool()
def get_attraction_suggestions(
    partial_name: str,
    language: str = "en"
) -> str:
    """
    Get suggestions for attraction names as you type

    :param partial_name: partial attraction name (e.g., "Eiffel", "Statue of")
    :param language: language for suggestions (en, de, fr, es, it, pt, ru, zh, ja, ar, hi)
    :return: formatted list of matching attraction name suggestions
    """
    try:
        return places_service.autocomplete_places(partial_name, language)
    except Exception as e:
        return f"Error getting suggestions: {str(e)}"


@server.tool()
def find_weather_appropriate_attractions(
    location: str,
    weather: str,
    distance_km: int = 15,
    max_results: int = 30
) -> str:
    """
    Find attractions suitable for specific weather conditions

    :param location: city or area name (e.g., "Rome", "Central Park New York")
    :param weather: current weather condition (sunny, rainy, cloudy, snowy, windy)
    :param distance_km: search distance in kilometers (default: 15, max: 50)
    :param max_results: maximum results per category (default: 30)
    :return: formatted list of attractions perfect for the current weather
    """
    try:
        distance_km = min(distance_km, 50)
        
        # Get coordinates for the location using base service
        lat, lng = places_service.get_coordinates(location)
        if not lat or not lng:
            return f"Could not find coordinates for location: {location}. Please try a more specific location name."
        
        location_str = f"{lat},{lng}"
        radius_meters = distance_km * 1000
        
        return places_service.get_places_by_weather(location_str, weather, radius_meters, max_results)
    except Exception as e:
        return f"Error finding weather-appropriate attractions: {str(e)}"


@server.tool()
def get_attraction_categories() -> str:
    """
    Get list of available tourist attraction categories for filtering

    :return: organized list of attraction categories you can use in searches
    """
    try:
        from _mcp.servers.places.constants import PLACE_CATEGORIES
        
        result = "🗺️ Available Tourist Attraction Categories:\n\n"
        
        # Group categories by type for better readability
        categories = {
            "🏞️ Natural Features": ["natural", "beaches", "geological_formations", "islands", "mountains", "volcanoes", "caves", "national_parks", "nature_reserves", "water"],
            "🏛️ Cultural Heritage": ["cultural", "archaeological_sites", "fortifications", "architecture", "monuments_and_memorials", "museums", "churches", "historic", "palaces", "castles"],
            "🎠 Entertainment": ["amusements", "theatres_and_entertainments", "cinemas", "zoos", "aquariums", "theme_parks", "festivals_and_events"],
            "⚽ Sports & Recreation": ["sport", "climbing", "golf", "diving", "skiing", "surfing", "water_sports", "winter_sports"],
            "🏙️ Urban Attractions": ["interesting_places", "view_points", "bridges", "towers", "lighthouses", "skyscrapers", "industrial_facilities"],
            "🏨 Tourism Facilities": ["accomodations", "foods", "shops", "tourist_facilities"]
        }
        
        for group, cats in categories.items():
            result += f"{group}:\n"
            for cat in cats:
                if cat in PLACE_CATEGORIES:
                    display_name = cat.replace('_', ' ').title()
                    result += f"   • {display_name}\n"
            result += "\n"
        
        result += "💡 Usage Tips:\n"
        result += "   • Use these category names in the 'category' parameter\n"
        result += "   • Leave category empty to search all attraction types\n"
        result += "   • Combine with weather searches for perfect recommendations"
        
        return result
        
    except Exception as e:
        return f"Error listing categories: {str(e)}"


@server.tool()
def get_walking_distance_attractions(
    location: str,
    category: str = None,
    max_walking_minutes: int = 15,
    language: str = "en"
) -> str:
    """
    Find attractions within comfortable walking distance

    :param location: starting location (hotel, landmark, address)
    :param category: type of attractions (museums, restaurants, shops, etc.)
    :param max_walking_minutes: maximum walking time in minutes (5-30 minutes)
    :param language: language for results (en, de, fr, es, it, pt, ru, zh, ja, ar, hi)
    :return: formatted list of nearby attractions you can walk to
    """
    try:
        # Convert walking time to distance (assuming 5 km/h walking speed)
        max_walking_minutes = min(max_walking_minutes, 30)
        distance_km = (max_walking_minutes / 60) * 5  # 5 km/h walking speed
        radius_meters = int(distance_km * 1000)
        
        # Get coordinates for the location using base service
        lat, lng = places_service.get_coordinates(location)
        if not lat or not lng:
            return f"Could not find coordinates for location: {location}. Please try a more specific location name."
        
        location_str = f"{lat},{lng}"
        
        result = places_service.search_places(location_str, category, radius_meters, 20, language)
        
        # Add walking time context to the result
        if not result.startswith("Error") and not result.startswith("No places"):
            walking_context = f"🚶 Attractions within {max_walking_minutes} minutes walk from {location}:\n\n"
            result = walking_context + result
        
        return result
    except Exception as e:
        return f"Error finding walking distance attractions: {str(e)}"

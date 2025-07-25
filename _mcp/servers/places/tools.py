from fastmcp import FastMCP
from _mcp.servers.places.service import PlacesService

server = FastMCP("Places Server")

places_service = PlacesService()

@server.tool()
def search_places(
    location: str,
    place_type: str = None,
    radius: int = 10,
    limit: int = 20,
    language: str = "en"
) -> str:
    """
    Search for places based on location and criteria using Photon API (OpenStreetMap data)

    :param location: location to search (city name, address, etc.) or coordinates as "lat,lng"
    :param place_type: type of place (restaurant, hotel, museum, tourist_attraction, etc.)
    :param radius: search radius in kilometers (default: 10, max: 100)
    :param limit: maximum number of results (default: 20, max: 50)
    :param language: language code for results (default: en)
    :return: formatted list of places matching the criteria
    """
    return places_service.search_places(location, place_type, radius, limit, language)

@server.tool()
def geocode_location(
    location: str,
    language: str = "en",
    limit: int = 10
) -> str:
    """
    Geocode a location string to get coordinates and detailed information

    :param location: location to geocode (city name, address, etc.)
    :param language: language code for results (default: en)
    :param limit: maximum number of results (default: 10)
    :return: geocoding results with coordinates and place details
    """
    result = places_service.geocode_location(location, language, limit)
    if isinstance(result, str):  # Error case
        return result
    
    if not result:
        return f"No results found for location: {location}"
    
    formatted_result = f"Geocoding results for '{location}':\n\n"
    for i, feature in enumerate(result, 1):
        properties = feature.get("properties", {})
        coordinates = feature.get("geometry", {}).get("coordinates", [])
        
        name = properties.get("name", "N/A")
        city = properties.get("city", "")
        country = properties.get("country", "")
        postcode = properties.get("postcode", "")
        
        # Build address
        address_parts = []
        if city:
            address_parts.append(city)
        if postcode:
            address_parts.append(postcode)
        if country:
            address_parts.append(country)
        address = ", ".join(address_parts) if address_parts else "N/A"
        
        formatted_result += f"{i}. {name}\n"
        formatted_result += f"   Address: {address}\n"
        if len(coordinates) == 2:
            formatted_result += f"   Coordinates: {coordinates[1]:.6f}, {coordinates[0]:.6f}\n"
        formatted_result += f"   OSM ID: {properties.get('osm_id', 'N/A')}\n\n"
    
    return formatted_result

@server.tool()
def reverse_geocode(
    latitude: float,
    longitude: float,
    language: str = "en"
) -> str:
    """
    Reverse geocode coordinates to get place information

    :param latitude: latitude coordinate
    :param longitude: longitude coordinate
    :param language: language code for results (default: en)
    :return: place information for the given coordinates
    """
    result = places_service.reverse_geocode(latitude, longitude, language)
    if isinstance(result, str):  # Error case
        return result
    
    properties = result.get("properties", {})
    coordinates = result.get("geometry", {}).get("coordinates", [])
    
    name = properties.get("name", "N/A")
    city = properties.get("city", "")
    country = properties.get("country", "")
    postcode = properties.get("postcode", "")
    street = properties.get("street", "")
    housenumber = properties.get("housenumber", "")
    
    # Build address
    address_parts = []
    if housenumber and street:
        address_parts.append(f"{housenumber} {street}")
    elif street:
        address_parts.append(street)
    if city:
        address_parts.append(city)
    if postcode:
        address_parts.append(postcode)
    if country:
        address_parts.append(country)
    
    address = ", ".join(address_parts) if address_parts else "N/A"
    
    formatted_result = f"Reverse geocoding results for ({latitude}, {longitude}):\n\n"
    formatted_result += f"Name: {name}\n"
    formatted_result += f"Address: {address}\n"
    if len(coordinates) == 2:
        formatted_result += f"Exact Coordinates: {coordinates[1]:.6f}, {coordinates[0]:.6f}\n"
    formatted_result += f"OSM ID: {properties.get('osm_id', 'N/A')}\n"
    
    return formatted_result

@server.tool()
def recommend_places_by_weather(
    location: str,
    weather_condition: str,
    max_distance: int = 10,
    limit: int = 20
) -> str:
    """
    Recommend places based on current weather conditions

    :param location: location to search (city name, address, etc.) or coordinates as "lat,lng"
    :param weather_condition: weather condition (sunny, rainy, cloudy, snowy, windy, hot, cold)
    :param max_distance: maximum distance to search in kilometers (default: 10)
    :param limit: maximum number of recommendations (default: 20)
    :return: weather-appropriate place recommendations
    """
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
    return places_service.recommend_places_by_distance(location, travel_mode, limit)

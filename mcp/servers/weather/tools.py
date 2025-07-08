from fastmcp import FastMCP
from .service import WeatherService

server = FastMCP("Weather Server")

# Initialize the weather service
weather_service = WeatherService()

@server.tool()
def check_weather(location: str) -> str:
    """
    Check the weather in a location

    :param location: location to check
    :return: weather report
    """
    return weather_service.get_current_weather(location)


@server.tool()
def get_best_trip_days(location: str) -> str:
    """
    Find the best days for a trip based on weather conditions

    :param location: location to check
    :return: recommended days for a trip
    """
    return weather_service.get_trip_recommendations(location)


@server.tool()
def get_weather_events(location: str) -> str:
    """
    Get severe weather events for a location

    :param location: location to check
    :return: list of weather events
    """
    return weather_service.get_severe_weather_events(location)

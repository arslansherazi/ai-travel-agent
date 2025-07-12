from fastmcp import FastMCP
from _mcp.servers.trip_planner.service import TripPlannerService
import os

server = FastMCP("Trip Planner Server")

# Initialize the trip planner service with API keys from environment
trip_planner_service = TripPlannerService(
    places_api_key=os.getenv("GOOGLE_PLACES_API_KEY"),
    booking_api_key=os.getenv("BOOKING_API_KEY")
)

@server.tool()
def plan_complete_trip(
    location: str,
    start_date: str = None,
    duration: str = "3",
    trip_style: str = "balanced",
    budget: str = "mid_range",
    include_accommodation: bool = True
) -> str:
    """
    Plan a complete trip with activities, itinerary, and optionally accommodation

    :param location: destination location (city name, address, etc.) or coordinates as "lat,lng"
    :param start_date: trip start date in YYYY-MM-DD format (optional - if not provided, optimizes based on weather)
    :param duration: trip duration as number of days or preset (weekend, short, week, extended, month)
    :param trip_style: trip style (relaxed, balanced, adventure, cultural, food_focused)
    :param budget: budget category (budget, mid_range, luxury)
    :param include_accommodation: whether to include accommodation suggestions
    :return: comprehensive trip plan with daily itinerary and accommodation
    """
    # Handle coordinate input
    if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
        try:
            lat, lng = map(float, location.split(","))
            location = (lat, lng)
        except ValueError:
            pass  # Keep as string if parsing fails
    
    return trip_planner_service.plan_trip(
        location=location,
        start_date=start_date,
        duration=duration,
        trip_style=trip_style,
        budget=budget,
        include_accommodation=include_accommodation
    )


@server.tool()
def plan_weather_optimized_trip(
    location: str,
    weather_condition: str,
    duration: str = "3",
    trip_style: str = "balanced"
) -> str:
    """
    Plan a trip specifically optimized for certain weather conditions

    :param location: destination location (city name, address, etc.) or coordinates as "lat,lng"
    :param weather_condition: desired weather condition (clear, sunny, partly_cloudy, cloudy, overcast, rainy, snowy)
    :param duration: trip duration as number of days or preset (weekend, short, week, extended)
    :param trip_style: trip style preference (relaxed, balanced, adventure, cultural, food_focused)
    :return: weather-optimized trip plan with activities perfect for the specified conditions
    """
    # Handle coordinate input
    if "," in location and location.replace(",", "").replace(".", "").replace("-", "").replace(" ", "").isdigit():
        try:
            lat, lng = map(float, location.split(","))
            location = (lat, lng)
        except ValueError:
            pass  # Keep as string if parsing fails
    
    return trip_planner_service.plan_weather_based_trip(
        location=location,
        weather_condition=weather_condition,
        duration=duration,
        trip_style=trip_style
    ) 
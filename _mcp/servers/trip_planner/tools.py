"""
Trip planner server tools for comprehensive travel planning
Integrates attractions, weather, and booking services for complete trip planning
"""

from fastmcp import FastMCP
from _mcp.servers.trip_planner.service import TripPlannerService
import os

server = FastMCP("Trip Planner Server")

# Initialize the trip planner service with API keys from environment
trip_planner_service = TripPlannerService(
    booking_api_key=os.getenv("BOOKING_API_KEY"),
    places_api_key=os.getenv("OPENTRIPMAP_API_KEY")
)

@server.tool()
def plan_complete_trip(
    destination: str,
    start_date: str,
    end_date: str,
    budget: str = "moderate",
    interests: str = "cultural,natural",
    group_size: int = 2,
    accommodation_type: str = "hotel"
) -> str:
    """
    Plan a complete trip with activities, itinerary, and accommodation suggestions

    :param destination: destination city or location name (e.g., "Rome", "Paris", "Tokyo")
    :param start_date: trip start date in YYYY-MM-DD format
    :param end_date: trip end date in YYYY-MM-DD format
    :param budget: budget category ("budget", "moderate", "luxury")
    :param interests: comma-separated interests (e.g., "cultural,natural,entertainment")
    :param group_size: number of people in the group
    :param accommodation_type: type of accommodation preferred ("hotel", "hostel", "apartment")
    :return: comprehensive trip plan with daily itinerary and accommodation options
    """
    try:
        # Parse interests string into list
        interests_list = [interest.strip() for interest in interests.split(',')] if interests else ["cultural", "natural"]
        
        return trip_planner_service.plan_trip(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            interests=interests_list,
            group_size=group_size,
            accommodation_type=accommodation_type
        )
    except Exception as e:
        return f"Error planning trip: {str(e)}"

@server.tool()
def suggest_daily_activities(
    destination: str,
    date: str,
    weather_condition: str = None,
    interests: str = "cultural,natural",
    duration_hours: int = 8
) -> str:
    """
    Suggest activities for a specific day based on weather and interests

    :param destination: destination city or location name
    :param date: specific date in YYYY-MM-DD format
    :param weather_condition: current weather condition (sunny, rainy, cloudy, snowy, windy)
    :param interests: comma-separated interests (e.g., "cultural,natural,entertainment")
    :param duration_hours: total hours to plan activities for (4-12 hours)
    :return: formatted activity suggestions for the day
    """
    try:
        # Parse interests string into list
        interests_list = [interest.strip() for interest in interests.split(',')] if interests else ["cultural", "natural"]
        
        return trip_planner_service.suggest_activities(
            destination=destination,
            date=date,
            weather_condition=weather_condition,
            interests=interests_list,
            duration_hours=duration_hours
        )
    except Exception as e:
        return f"Error suggesting activities: {str(e)}"

@server.tool()
def find_nearby_amenities(
    location: str,
    amenity_type: str = "restaurants",
    distance_km: int = 2
) -> str:
    """
    Find nearby amenities like restaurants, shops, or transport

    :param location: current location name (hotel, landmark, address)
    :param amenity_type: type of amenity to find (restaurants, shops, transport, hotels)
    :param distance_km: search radius in kilometers (1-10 km)
    :return: formatted list of nearby amenities with distances
    """
    try:
        return trip_planner_service.find_nearby_amenities(
            location=location,
            amenity_type=amenity_type,
            distance_km=distance_km
        )
    except Exception as e:
        return f"Error finding amenities: {str(e)}"

@server.tool()
def get_weather_based_recommendations(
    destination: str,
    weather_condition: str,
    duration_hours: int = 6,
    interests: str = "cultural,natural"
) -> str:
    """
    Get activity recommendations based on current weather conditions

    :param destination: destination city or location name
    :param weather_condition: current weather (sunny, rainy, cloudy, snowy, windy)
    :param duration_hours: hours of activities to plan (2-12 hours)
    :param interests: comma-separated interests for filtering recommendations
    :return: weather-appropriate activity recommendations
    """
    try:
        # Parse interests string into list
        interests_list = [interest.strip() for interest in interests.split(',')] if interests else ["cultural", "natural"]
        
        return trip_planner_service.suggest_activities(
            destination=destination,
            date=None,  # Current day
            weather_condition=weather_condition,
            interests=interests_list,
            duration_hours=duration_hours
        )
    except Exception as e:
        return f"Error getting weather-based recommendations: {str(e)}" 
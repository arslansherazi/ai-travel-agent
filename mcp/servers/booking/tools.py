from fastmcp import FastMCP
from mcp.servers.booking.service import BookingService
import os

server = FastMCP("Booking Server")

# Initialize the booking service with API key from environment
booking_service = BookingService(api_key=os.getenv("BOOKING_API_KEY"))

@server.tool()
def search_availability(
    location: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
    rooms: int = 1,
    rows: int = 20
) -> str:
    """
    Search for accommodation availability based on location and dates

    :param location: location to search (city name, address, etc.)
    :param checkin: check-in date in YYYY-MM-DD format
    :param checkout: checkout date in YYYY-MM-DD format
    :param adults: number of adults (default: 2)
    :param rooms: number of rooms (default: 1)
    :param rows: number of results to return (default: 20, max: 100)
    :return: formatted list of available accommodations
    """
    return booking_service.search_accommodations(location, checkin, checkout, adults, rooms, rows)


@server.tool()
def search_specific_accommodations(
    location: str,
    checkin: str,
    checkout: str,
    star_rating: int = None,
    price_min: float = None,
    price_max: float = None,
    accommodation_type: str = None,
    adults: int = 2,
    rooms: int = 1,
    rows: int = 20
) -> str:
    """
    Search for accommodations with specific criteria like star rating, price range, and type

    :param location: location to search (city name, address, etc.)
    :param checkin: check-in date in YYYY-MM-DD format
    :param checkout: checkout date in YYYY-MM-DD format
    :param star_rating: hotel star rating (1-5 stars)
    :param price_min: minimum price per night
    :param price_max: maximum price per night
    :param accommodation_type: type of accommodation (hotel, apartment, resort, villa, hostel, bed_and_breakfast, guesthouse)
    :param adults: number of adults (default: 2)
    :param rooms: number of rooms (default: 1)
    :param rows: number of results to return (default: 20, max: 100)
    :return: formatted list of accommodations matching the criteria
    """
    return booking_service.search_specific_accommodations(
        location, checkin, checkout, star_rating, price_min, price_max, 
        accommodation_type, adults, rooms, rows
    )


@server.tool()
def get_accommodation_details(hotel_id: str) -> str:
    """
    Get detailed information about a specific accommodation including photos, reviews, contact details, and booking URLs

    :param hotel_id: unique hotel identifier from search results
    :return: detailed accommodation information including photos, reviews, contact info, amenities, and booking URL
    """
    return booking_service.get_accommodation_details(hotel_id) 
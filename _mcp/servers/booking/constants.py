"""Booking service constants"""

# API URLs
BOOKING_API_BASE_URL = "https://demandapi.booking.com/3.1"

# API Endpoints
ENDPOINTS = {
    "search": "/accommodations/search",
    "availability": "/accommodations/availability",
    "bulk_availability": "/accommodations/bulk-availability",
    "details": "/accommodations/details",
    "reviews": "/accommodations/reviews",
    "locations_cities": "/common/locations/cities",
    "locations_countries": "/common/locations/countries",
    "currencies": "/common/payments/currencies"
}

# Search Parameters
SEARCH_EXTRAS = [
    "extra_charges",
    "products"
]

ACCOMMODATION_TYPES = {
    "hotel": 204,
    "apartment": 201,
    "resort": 219,
    "villa": 212,
    "hostel": 203,
    "bed_and_breakfast": 202,
    "guesthouse": 216
}

MEAL_PLANS = [
    "all_inclusive",
    "breakfast_included", 
    "full_board",
    "half_board"
]

CANCELLATION_TYPES = [
    "free_cancellation",
    "non_refundable"
]

PLATFORMS = [
    "android",
    "desktop", 
    "ios",
    "mobile",
    "tablet"
]

TRAVEL_PURPOSES = [
    "business",
    "leisure"
]

# Rating Constants
STAR_RATINGS = {
    "1_star": 1,
    "2_star": 2,
    "3_star": 3,
    "4_star": 4,
    "5_star": 5
}

# Default Values
DEFAULT_PLATFORM = "desktop"
DEFAULT_COUNTRY = "us"
DEFAULT_CURRENCY = "USD"
DEFAULT_ADULTS = 2
DEFAULT_ROOMS = 1
DEFAULT_ROWS = 20
DEFAULT_STAY_DURATION = 1
MAX_ROWS = 100
MIN_ROWS = 10

# Date Constraints
MAX_DAYS_IN_FUTURE = 500
MAX_STAY_DURATION = 90

# Price Range Limits
MIN_PRICE = 0
MAX_PRICE = 10000 
"""Places service constants for OpenTripMap API (opentripmap.io)"""

# API URLs - Using OpenTripMap API (Tourist attractions and POI service)
OPENTRIPMAP_API_BASE_URL = "https://api.opentripmap.com"

# API Endpoints
ENDPOINTS = {
    "places_by_location": "/0.1/en/places/radius",
    "places_by_bbox": "/0.1/en/places/bbox", 
    "place_details": "/0.1/en/places/xid",
    "place_autocomplete": "/0.1/en/places/autosuggest"
}

# OpenTripMap place categories (tourism-focused from OpenStreetMap)
PLACE_CATEGORIES = {
    # Natural features
    "natural": "natural",
    "beaches": "beaches",
    "geological_formations": "geological_formations",
    "islands": "islands",
    "mountains": "mountains",
    "volcanoes": "volcanoes",
    "caves": "caves",
    "national_parks": "national_parks",
    "nature_reserves": "nature_reserves",
    "water": "water",
    
    # Cultural heritage
    "cultural": "cultural", 
    "archaeological_sites": "archaeological_sites",
    "fortifications": "fortifications",
    "architecture": "architecture",
    "monuments_and_memorials": "monuments_and_memorials",
    "museums": "museums",
    "churches": "churches",
    "historic": "historic",
    "palaces": "palaces",
    "castles": "castles",
    
    # Entertainment
    "amusements": "amusements",
    "theatres_and_entertainments": "theatres_and_entertainments",
    "cinemas": "cinemas",
    "zoos": "zoos",
    "aquariums": "aquariums",
    "theme_parks": "theme_parks",
    "festivals_and_events": "festivals_and_events",
    
    # Sports and recreation
    "sport": "sport",
    "climbing": "climbing",
    "golf": "golf",
    "diving": "diving",
    "skiing": "skiing",
    "surfing": "surfing",
    "water_sports": "water_sports",
    "winter_sports": "winter_sports",
    
    # Urban infrastructure  
    "interesting_places": "interesting_places",
    "view_points": "view_points",
    "bridges": "bridges",
    "towers": "towers",
    "lighthouses": "lighthouses",
    "skyscrapers": "skyscrapers",
    "industrial_facilities": "industrial_facilities",
    
    # Tourism facilities
    "accomodations": "accomodations",
    "foods": "foods",
    "shops": "shops",
    "tourist_facilities": "tourist_facilities"
}

# Search parameters
DEFAULT_RADIUS = 10000  # 10km in meters (OpenTripMap uses meters)
MAX_RADIUS = 50000     # 50km maximum
MIN_RADIUS = 100       # 100m minimum

DEFAULT_RESULTS_LIMIT = 20
MAX_RESULTS_LIMIT = 500
MIN_RESULTS_LIMIT = 1

# Rate limiting parameters
DEFAULT_RATE_LIMIT = 5000  # requests per day for free tier
DEFAULT_FORMAT = "json"

# Language codes supported by OpenTripMap
SUPPORTED_LANGUAGES = [
    "en", "de", "fr", "es", "it", "pt", "ru", "zh", "ja", "ar", "hi"
]
DEFAULT_LANGUAGE = "en"

# Distance categories for results
DISTANCE_CATEGORIES = {
    "very_close": (0, 500),      # Within 500m
    "close": (500, 2000),        # 500m - 2km  
    "nearby": (2000, 10000),     # 2km - 10km
    "far": (10000, 25000),       # 10km - 25km
    "very_far": (25000, 50000)   # 25km - 50km
}

# Place importance/kind mapping for filtering
PLACE_IMPORTANCE = {
    1: "international",  # Places of international importance
    2: "national",      # Places of national importance  
    3: "regional",      # Places of regional importance
    4: "local",         # Places of local importance
    5: "neighborhood",  # Neighborhood attractions
    6: "other"          # Other places
}

# Weather to place category mapping for trip planning
WEATHER_PLACE_MAPPING = {
    "sunny": ["beaches", "view_points", "natural", "sport", "water_sports"],
    "rainy": ["museums", "cultural", "theatres_and_entertainments", "shops", "churches"],
    "cloudy": ["architecture", "historic", "monuments_and_memorials", "interesting_places"],
    "snowy": ["winter_sports", "skiing", "museums", "cultural"],
    "windy": ["sport", "water_sports", "view_points", "lighthouses"]
} 
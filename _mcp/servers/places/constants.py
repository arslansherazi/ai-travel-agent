"""Places service constants"""

# API URLs - Using Google Places API as primary source
GOOGLE_PLACES_API_BASE_URL = "https://maps.googleapis.com/maps/api/place"
FOURSQUARE_API_BASE_URL = "https://api.foursquare.com/v3/places"

# API Endpoints
ENDPOINTS = {
    "nearby_search": "/nearbysearch/json",
    "text_search": "/textsearch/json", 
    "place_details": "/details/json",
    "place_photos": "/photo",
    "foursquare_search": "/search",
    "foursquare_nearby": "/nearby"
}

# Place Types (Google Places API categories)
PLACE_TYPES = {
    # Attractions & Entertainment
    "tourist_attraction": "tourist_attraction",
    "amusement_park": "amusement_park",
    "aquarium": "aquarium",
    "art_gallery": "art_gallery",
    "museum": "museum",
    "zoo": "zoo",
    "casino": "casino",
    "movie_theater": "movie_theater",
    "night_club": "night_club",
    
    # Food & Dining
    "restaurant": "restaurant",
    "cafe": "cafe",
    "bar": "bar",
    "bakery": "bakery",
    "meal_takeaway": "meal_takeaway",
    
    # Shopping
    "shopping_mall": "shopping_mall",
    "store": "store",
    "clothing_store": "clothing_store",
    "book_store": "book_store",
    
    # Accommodation
    "lodging": "lodging",
    
    # Transportation
    "airport": "airport",
    "bus_station": "bus_station",
    "subway_station": "subway_station",
    "train_station": "train_station",
    
    # Nature & Outdoor
    "park": "park",
    "campground": "campground",
    "rv_park": "rv_park",
    
    # Religious & Cultural
    "church": "church",
    "hindu_temple": "hindu_temple",
    "mosque": "mosque",
    "synagogue": "synagogue",
    
    # Health & Services
    "hospital": "hospital",
    "pharmacy": "pharmacy",
    "bank": "bank",
    "atm": "atm",
    "gas_station": "gas_station"
}

# Search Radius Options (in meters)
SEARCH_RADIUS = {
    "very_close": 500,      # 0.5 km
    "close": 1000,          # 1 km  
    "nearby": 5000,         # 5 km
    "moderate": 10000,      # 10 km
    "far": 25000,           # 25 km
    "very_far": 50000       # 50 km
}

# Default Values
DEFAULT_RADIUS = SEARCH_RADIUS["nearby"]  # 5km
DEFAULT_RESULTS_LIMIT = 20
MAX_RESULTS_LIMIT = 60
MIN_RESULTS_LIMIT = 5

# Price Levels (Google Places API standard)
PRICE_LEVELS = {
    "free": 0,
    "inexpensive": 1,
    "moderate": 2,
    "expensive": 3,
    "very_expensive": 4
}

# Rating Thresholds
RATING_THRESHOLDS = {
    "excellent": 4.5,
    "very_good": 4.0,
    "good": 3.5,
    "fair": 3.0,
    "poor": 2.0
}

# Weather-based Place Recommendations
WEATHER_PLACE_MAPPING = {
    "sunny": ["park", "tourist_attraction", "zoo", "amusement_park", "beach"],
    "rainy": ["museum", "art_gallery", "shopping_mall", "movie_theater", "aquarium"],
    "cloudy": ["tourist_attraction", "museum", "restaurant", "cafe"],
    "snowy": ["museum", "shopping_mall", "restaurant", "cafe", "art_gallery"],
    "windy": ["museum", "shopping_mall", "restaurant", "cafe"],
    "hot": ["aquarium", "museum", "shopping_mall", "movie_theater", "cafe"],
    "cold": ["museum", "restaurant", "shopping_mall", "movie_theater", "bar"]
}

# Distance-based Recommendations
DISTANCE_CATEGORIES = {
    "walking": {"max_distance": 2000, "types": ["restaurant", "cafe", "store", "park"]},
    "short_drive": {"max_distance": 10000, "types": ["tourist_attraction", "museum", "shopping_mall"]},
    "day_trip": {"max_distance": 50000, "types": ["amusement_park", "zoo", "tourist_attraction", "park"]},
    "extended": {"max_distance": 100000, "types": ["tourist_attraction", "lodging", "airport"]}
}

# Photo size options
PHOTO_SIZES = {
    "small": 200,
    "medium": 400, 
    "large": 800,
    "extra_large": 1600
}

# Language codes for international support
SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar", "hi"
]

DEFAULT_LANGUAGE = "en" 
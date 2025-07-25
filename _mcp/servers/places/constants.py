"""Places service constants for Photon API"""

# API URLs - Using Photon API (OpenStreetMap geocoding service)
PHOTON_API_BASE_URL = "https://photon.komoot.io"

# API Endpoints
ENDPOINTS = {
    "search": "/api",
    "reverse": "/reverse"
}

# OpenStreetMap place types (simplified from OSM tags)
PLACE_TYPES = {
    # Amenities
    "restaurant": "restaurant",
    "cafe": "cafe", 
    "bar": "bar",
    "pub": "pub",
    "fast_food": "fast_food",
    "food_court": "food_court",
    
    # Tourism
    "tourist_attraction": "attraction",
    "museum": "museum",
    "gallery": "gallery",
    "viewpoint": "viewpoint",
    "theme_park": "theme_park",
    
    # Accommodation
    "hotel": "hotel",
    "hostel": "hostel",
    "guest_house": "guest_house",
    "camping": "camp_site",
    
    # Shopping
    "shop": "shop",
    "supermarket": "supermarket",
    "mall": "mall",
    "market": "marketplace",
    
    # Transportation
    "airport": "aerodrome",
    "train_station": "railway",
    "bus_station": "bus_station",
    "subway": "subway",
    
    # Entertainment
    "cinema": "cinema",
    "theatre": "theatre",
    "casino": "casino",
    
    # Nature & Recreation
    "park": "park",
    "garden": "garden",
    "beach": "beach",
    "forest": "forest",
    
    # Religious
    "church": "place_of_worship",
    "mosque": "place_of_worship", 
    "temple": "place_of_worship",
    "synagogue": "place_of_worship",
    
    # Services
    "hospital": "hospital",
    "pharmacy": "pharmacy",
    "bank": "bank",
    "atm": "atm",
    "fuel": "fuel"
}

# Search parameters
DEFAULT_RESULTS_LIMIT = 20
MAX_RESULTS_LIMIT = 50
MIN_RESULTS_LIMIT = 1

# Supported languages for Photon API
SUPPORTED_LANGUAGES = [
    "en", "de", "fr", "it", "es", "pt", "pl", "ru", "ar", "ja", "ko", "zh"
]

DEFAULT_LANGUAGE = "en"

# Search radius for geographic filtering (in km)
SEARCH_RADIUS = {
    "very_close": 1,      # 1 km
    "close": 5,           # 5 km  
    "nearby": 10,         # 10 km
    "moderate": 25,       # 25 km
    "far": 50,            # 50 km
    "very_far": 100       # 100 km
}

DEFAULT_RADIUS = SEARCH_RADIUS["nearby"]  # 10km

# Weather-based place suggestions (simplified for geocoding)
WEATHER_PLACE_MAPPING = {
    "sunny": ["park", "beach", "tourist_attraction", "viewpoint"],
    "rainy": ["museum", "gallery", "mall", "cinema"],
    "cloudy": ["tourist_attraction", "museum", "restaurant", "cafe"],
    "snowy": ["museum", "mall", "restaurant", "cafe"],
    "windy": ["museum", "mall", "restaurant", "cafe"],
    "hot": ["museum", "mall", "cinema", "cafe"],
    "cold": ["museum", "restaurant", "mall", "cinema"]
}

# Distance-based recommendations  
DISTANCE_CATEGORIES = {
    "walking": {
        "radius": 2,
        "types": ["restaurant", "cafe", "shop", "park"]
    },
    "short_drive": {
        "radius": 15, 
        "types": ["tourist_attraction", "museum", "mall"]
    },
    "day_trip": {
        "radius": 50,
        "types": ["theme_park", "tourist_attraction", "park", "beach"]
    },
    "extended": {
        "radius": 100,
        "types": ["tourist_attraction", "hotel", "airport"]
    }
} 
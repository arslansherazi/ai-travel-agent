"""
Trip planner service constants
"""

# Trip Duration Presets (in days)
TRIP_DURATIONS = {
    "weekend": 2,
    "short": 3,
    "week": 7,
    "extended": 14,
    "month": 30
}

# Default trip settings
DEFAULT_TRIP_DURATION = 3  # days
MIN_TRIP_DURATION = 1
MAX_TRIP_DURATION = 30

# Activities per day based on trip style
TRIP_STYLES = {
    "relaxed": {
        "activities_per_day": 2,
        "travel_radius": 10000,  # 10km
        "pace": "slow",
        "preferred_types": ["restaurant", "cafe", "park", "museum", "spa"]
    },
    "balanced": {
        "activities_per_day": 3,
        "travel_radius": 15000,  # 15km
        "pace": "moderate",
        "preferred_types": ["tourist_attraction", "restaurant", "museum", "park", "shopping_mall"]
    },
    "adventure": {
        "activities_per_day": 4,
        "travel_radius": 25000,  # 25km
        "pace": "fast",
        "preferred_types": ["tourist_attraction", "amusement_park", "zoo", "park", "sport_center"]
    },
    "cultural": {
        "activities_per_day": 3,
        "travel_radius": 20000,  # 20km
        "pace": "moderate",
        "preferred_types": ["museum", "art_gallery", "church", "tourist_attraction", "restaurant"]
    },
    "food_focused": {
        "activities_per_day": 4,
        "travel_radius": 15000,  # 15km
        "pace": "moderate",
        "preferred_types": ["restaurant", "cafe", "bakery", "bar", "market"]
    }
}

# Weather-based activity recommendations for trip planning
WEATHER_ACTIVITY_MAPPING = {
    "clear": {
        "morning": ["park", "tourist_attraction", "zoo"],
        "afternoon": ["amusement_park", "tourist_attraction", "park"],
        "evening": ["restaurant", "bar", "night_market"]
    },
    "sunny": {
        "morning": ["park", "tourist_attraction", "beach"],
        "afternoon": ["zoo", "amusement_park", "outdoor_activity"],
        "evening": ["restaurant", "rooftop_bar", "outdoor_dining"]
    },
    "partly_cloudy": {
        "morning": ["museum", "tourist_attraction", "park"],
        "afternoon": ["shopping_mall", "tourist_attraction", "cafe"],
        "evening": ["restaurant", "movie_theater", "bar"]
    },
    "cloudy": {
        "morning": ["museum", "art_gallery", "shopping_mall"],
        "afternoon": ["tourist_attraction", "cafe", "indoor_activity"],
        "evening": ["restaurant", "bar", "entertainment"]
    },
    "overcast": {
        "morning": ["museum", "shopping_mall", "art_gallery"],
        "afternoon": ["cafe", "indoor_attraction", "shopping"],
        "evening": ["restaurant", "movie_theater", "indoor_entertainment"]
    },
    "rainy": {
        "morning": ["museum", "shopping_mall", "art_gallery"],
        "afternoon": ["movie_theater", "aquarium", "indoor_activity"],
        "evening": ["restaurant", "bar", "spa"]
    },
    "snowy": {
        "morning": ["museum", "shopping_mall", "indoor_attraction"],
        "afternoon": ["cafe", "art_gallery", "indoor_activity"],
        "evening": ["restaurant", "bar", "indoor_entertainment"]
    }
}

# Time of day activity preferences
TIME_BASED_ACTIVITIES = {
    "morning": {
        "early": ["cafe", "bakery", "park"],  # 6-9 AM
        "mid": ["museum", "tourist_attraction", "shopping_mall"]  # 9-12 PM
    },
    "afternoon": {
        "early": ["restaurant", "tourist_attraction", "park"],  # 12-3 PM
        "mid": ["museum", "shopping_mall", "cafe"],  # 3-6 PM
        "late": ["bar", "restaurant", "entertainment"]  # 6-9 PM
    },
    "evening": {
        "early": ["restaurant", "bar", "entertainment"],  # 6-9 PM
        "late": ["bar", "night_club", "late_night_food"]  # 9 PM+
    }
}

# Budget-based recommendations
BUDGET_CATEGORIES = {
    "budget": {
        "accommodation_price": "inexpensive",
        "dining_price": "inexpensive",
        "activity_focus": ["park", "free_attraction", "walking_tour"],
        "daily_budget": 50
    },
    "mid_range": {
        "accommodation_price": "moderate",
        "dining_price": "moderate",
        "activity_focus": ["tourist_attraction", "museum", "restaurant"],
        "daily_budget": 150
    },
    "luxury": {
        "accommodation_price": "expensive",
        "dining_price": "expensive",
        "activity_focus": ["fine_dining", "premium_attraction", "spa"],
        "daily_budget": 500
    }
}

# Season-based recommendations
SEASONAL_ACTIVITIES = {
    "spring": ["park", "garden", "outdoor_market", "tourist_attraction"],
    "summer": ["beach", "amusement_park", "zoo", "outdoor_activity"],
    "autumn": ["museum", "art_gallery", "scenic_drive", "restaurant"],
    "winter": ["museum", "shopping_mall", "indoor_entertainment", "spa"]
}

# Trip planning priorities
PLANNING_PRIORITIES = {
    "weather_weight": 0.5,
    "distance_weight": 0.4,
    "budget_weight": 0.1
    # Note: rating_weight removed - OpenTripMap API focuses on POI data rather than ratings
}

# Accommodation search parameters
ACCOMMODATION_SEARCH = {
    "search_radius": 5000,  # 5 km from city center
    "nights_offset": 0  # How many days before trip to search
    # Note: min_rating removed - OpenTripMap focuses on attractions, use booking service for accommodations
}

# Default values
DEFAULT_TRIP_STYLE = "balanced"
DEFAULT_BUDGET = "mid_range"
DEFAULT_ACTIVITIES_PER_DAY = 3
MAX_ACTIVITIES_PER_DAY = 6

# Error messages
ERROR_MESSAGES = {
    "no_weather_data": "Could not retrieve weather data for the specified location and dates",
    "no_places_found": "No suitable places found for the specified criteria",
    "no_accommodation": "No accommodation found matching the criteria",
    "invalid_dates": "Invalid date format or date range",
    "location_not_found": "Could not find the specified location"
} 
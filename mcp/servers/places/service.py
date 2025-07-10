"""
Places service module containing the PlacesService utils
"""

import math
from typing import List, Dict, Optional, Union, Tuple
from mcp.servers.base_service import BaseService
from mcp.servers.places.constants import (
    GOOGLE_PLACES_API_BASE_URL,
    ENDPOINTS,
    PLACE_TYPES,
    SEARCH_RADIUS,
    DEFAULT_RADIUS,
    DEFAULT_RESULTS_LIMIT,
    MAX_RESULTS_LIMIT,
    MIN_RESULTS_LIMIT,
    PRICE_LEVELS,
    WEATHER_PLACE_MAPPING,
    DISTANCE_CATEGORIES,
    DEFAULT_LANGUAGE
)


class PlacesService(BaseService):
    """
    Service class for places-related operations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the places service
        
        :param api_key: Google Places API key
        """
        self.api_key = api_key
        self.base_url = GOOGLE_PLACES_API_BASE_URL
    
    def search_places(
        self,
        location: Union[str, Tuple[float, float]],
        place_type: Optional[str] = None,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT,
        min_rating: Optional[float] = None,
        price_level: Optional[str] = None
    ) -> str:
        """
        Search for places based on location and criteria
        
        :param location: location string or (lat, lng) tuple
        :param place_type: type of place to search for
        :param radius: search radius in meters
        :param limit: maximum number of results
        :param min_rating: minimum rating filter
        :param price_level: price level filter
        :return: formatted search results
        """
        places_data = self.search_places_data(location, place_type, radius, limit, min_rating, price_level)
        if isinstance(places_data, str):  # Error case
            return places_data
        
        return self._format_places_results(location, places_data, place_type)

    def search_places_data(
        self,
        location: Union[str, Tuple[float, float]],
        place_type: Optional[str] = None,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT,
        min_rating: Optional[float] = None,
        price_level: Optional[str] = None
    ) -> List[Dict] | str:
        """
        Search for places and return structured data (for use by other services)
        
        :param location: location string or (lat, lng) tuple
        :param place_type: type of place to search for
        :param radius: search radius in meters
        :param limit: maximum number of results
        :param min_rating: minimum rating filter
        :param price_level: price level filter
        :return: list of place data or error string
        """
        api_key_error = self.check_api_key_required(self.api_key, "Google Places API")
        if api_key_error:
            return api_key_error
        
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = self.get_coordinates(location)
            if not lat or not lng:
                return f"Could not find coordinates for {location}"
        else:
            lat, lng = location
        
        # Validate inputs
        validation_error = self._validate_search_params(place_type, radius, limit, min_rating, price_level)
        if validation_error:
            return validation_error
        
        # Prepare search parameters
        params = {
            "location": f"{lat},{lng}",
            "radius": min(radius, SEARCH_RADIUS["very_far"]),
            "key": self.api_key,
            "language": DEFAULT_LANGUAGE
        }
        
        # Add optional filters
        if place_type and place_type in PLACE_TYPES:
            params["type"] = PLACE_TYPES[place_type]
        
        if min_rating:
            params["minprice"] = 0
        
        if price_level and price_level in PRICE_LEVELS:
            params["maxprice"] = PRICE_LEVELS[price_level]
            params["minprice"] = 0
        
        try:
            url = f"{self.base_url}{ENDPOINTS['nearby_search']}"
            response = self.make_api_request(url, params=params)
            
            if response.get("error"):
                return self.format_error_response(response["error"], "places search")
            
            # Filter results by rating if specified
            places = response.get("results", [])
            if min_rating:
                places = [place for place in places if place.get("rating", 0) >= min_rating]
            
            # Limit results
            places = places[:limit]
            
            return places
            
        except Exception as e:
            return self.format_error_response(str(e), "places search")

    def recommend_places_by_weather(
        self,
        location: Union[str, Tuple[float, float]],
        weather_condition: str,
        max_distance: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> str:
        """
        Recommend places based on weather conditions
        
        :param location: location string or (lat, lng) tuple
        :param weather_condition: weather condition (sunny, rainy, cloudy, etc.)
        :param max_distance: maximum distance to search
        :param limit: maximum number of recommendations
        :return: formatted recommendations
        """
        recommendations_data = self.recommend_places_by_weather_data(location, weather_condition, max_distance, limit)
        if isinstance(recommendations_data, str):  # Error case
            return recommendations_data
        
        return self._format_weather_recommendations(location, recommendations_data, weather_condition)

    def recommend_places_by_weather_data(
        self,
        location: Union[str, Tuple[float, float]],
        weather_condition: str,
        max_distance: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> List[Dict] | str:
        """
        Recommend places based on weather conditions and return structured data
        
        :param location: location string or (lat, lng) tuple
        :param weather_condition: weather condition (sunny, rainy, cloudy, etc.)
        :param max_distance: maximum distance to search
        :param limit: maximum number of recommendations
        :return: list of place data or error string
        """
        api_key_error = self.check_api_key_required(self.api_key, "Google Places API")
        if api_key_error:
            return api_key_error
        
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = self.get_coordinates(location)
            if not lat or not lng:
                return f"Could not find coordinates for {location}"
        else:
            lat, lng = location
        
        # Get recommended place types for weather condition
        weather_key = weather_condition.lower()
        if weather_key not in WEATHER_PLACE_MAPPING:
            available_conditions = ", ".join(WEATHER_PLACE_MAPPING.keys())
            return f"Weather condition '{weather_condition}' not supported. Available: {available_conditions}"
        
        recommended_types = WEATHER_PLACE_MAPPING[weather_key]
        all_recommendations = []
        
        # Search for each recommended place type
        for place_type in recommended_types:
            try:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": max_distance,
                    "type": place_type,
                    "key": self.api_key,
                    "language": DEFAULT_LANGUAGE
                }
                
                url = f"{self.base_url}{ENDPOINTS['nearby_search']}"
                response = self.make_api_request(url, params=params)
                
                if not response.get("error"):
                    places = response.get("results", [])[:3]  # Top 3 per category
                    for place in places:
                        place["recommended_for"] = weather_condition
                        place["category"] = place_type
                    all_recommendations.extend(places)
                    
            except Exception:
                continue
        
        # Sort by rating and limit results
        all_recommendations.sort(key=lambda x: x.get("rating", 0), reverse=True)
        final_recommendations = all_recommendations[:limit]
        
        return final_recommendations

    def recommend_places_by_distance(
        self,
        location: Union[str, Tuple[float, float]],
        travel_mode: str = "walking",
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> str:
        """
        Recommend places based on distance categories
        
        :param location: location string or (lat, lng) tuple
        :param travel_mode: travel mode (walking, short_drive, day_trip, extended)
        :param limit: maximum number of recommendations
        :return: formatted recommendations
        """
        recommendations_data = self.recommend_places_by_distance_data(location, travel_mode, limit)
        if isinstance(recommendations_data, str):  # Error case
            return recommendations_data
        
        return self._format_distance_recommendations(location, recommendations_data, travel_mode)

    def recommend_places_by_distance_data(
        self,
        location: Union[str, Tuple[float, float]],
        travel_mode: str = "walking",
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> List[Dict] | str:
        """
        Recommend places based on distance categories and return structured data
        
        :param location: location string or (lat, lng) tuple
        :param travel_mode: travel mode (walking, short_drive, day_trip, extended)
        :param limit: maximum number of recommendations
        :return: list of place data or error string
        """
        api_key_error = self.check_api_key_required(self.api_key, "Google Places API")
        if api_key_error:
            return api_key_error
        
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = self.get_coordinates(location)
            if not lat or not lng:
                return f"Could not find coordinates for {location}"
        else:
            lat, lng = location
        
        # Get distance configuration
        if travel_mode not in DISTANCE_CATEGORIES:
            available_modes = ", ".join(DISTANCE_CATEGORIES.keys())
            return f"Travel mode '{travel_mode}' not supported. Available: {available_modes}"
        
        distance_config = DISTANCE_CATEGORIES[travel_mode]
        search_radius = distance_config["radius"]
        recommended_types = distance_config["types"]
        
        all_recommendations = []
        
        # Search for each recommended place type
        for place_type in recommended_types:
            try:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": search_radius,
                    "type": place_type,
                    "key": self.api_key,
                    "language": DEFAULT_LANGUAGE
                }
                
                url = f"{self.base_url}{ENDPOINTS['nearby_search']}"
                response = self.make_api_request(url, params=params)
                
                if not response.get("error"):
                    places = response.get("results", [])[:2]  # Top 2 per category
                    for place in places:
                        place["travel_mode"] = travel_mode
                        place["category"] = place_type
                        # Calculate actual distance
                        place_lat = place.get("geometry", {}).get("location", {}).get("lat", lat)
                        place_lng = place.get("geometry", {}).get("location", {}).get("lng", lng)
                        place["distance_km"] = self._calculate_distance(lat, lng, place_lat, place_lng)
                    all_recommendations.extend(places)
                    
            except Exception:
                continue
        
        # Sort by rating and limit results
        all_recommendations.sort(key=lambda x: x.get("rating", 0), reverse=True)
        final_recommendations = all_recommendations[:limit]
        
        return final_recommendations
    
    @staticmethod
    def _validate_search_params(
        place_type: Optional[str],
        radius: int,
        limit: int,
        min_rating: Optional[float],
        price_level: Optional[str]
    ) -> Optional[str]:
        """
        Validate search parameters
        
        :param place_type: place type
        :param radius: search radius
        :param limit: results limit
        :param min_rating: minimum rating
        :param price_level: price level
        :return: error message if validation fails, None otherwise
        """
        if place_type and place_type not in PLACE_TYPES:
            available_types = ", ".join(PLACE_TYPES.keys())
            return f"Invalid place type '{place_type}'. Available types: {available_types}"
        
        if radius < 0 or radius > SEARCH_RADIUS["very_far"]:
            return f"Radius must be between 0 and {SEARCH_RADIUS['very_far']} meters"
        
        if limit < MIN_RESULTS_LIMIT or limit > MAX_RESULTS_LIMIT:
            return f"Limit must be between {MIN_RESULTS_LIMIT} and {MAX_RESULTS_LIMIT}"
        
        if min_rating is not None and (min_rating < 0 or min_rating > 5):
            return "Minimum rating must be between 0 and 5"
        
        if price_level and price_level not in PRICE_LEVELS:
            available_levels = ", ".join(PRICE_LEVELS.keys())
            return f"Invalid price level '{price_level}'. Available levels: {available_levels}"
        
        return None
    
    @staticmethod
    def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        
        :param lat1: latitude of first point
        :param lng1: longitude of first point
        :param lat2: latitude of second point
        :param lng2: longitude of second point
        :return: distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius = 6371.0
        distance = earth_radius * c
        
        return distance
    
    @staticmethod
    def _format_places_results(
        location: Union[str, Tuple[float, float]],
        places: List[Dict],
        place_type: Optional[str]
    ) -> str:
        """
        Format places search results
        
        :param location: search location
        :param places: list of places
        :param place_type: place type filter
        :return: formatted results
        """
        if isinstance(location, tuple):
            location_str = f"coordinates ({location[0]:.4f}, {location[1]:.4f})"
        else:
            location_str = location
        
        type_filter = f" ({place_type})" if place_type else ""
        result = f"Places search results for {location_str}{type_filter}:\n\n"
        
        if not places:
            return f"No places found for {location_str}{type_filter}"
        
        for i, place in enumerate(places, 1):
            name = place.get("name", "N/A")
            rating = place.get("rating", "N/A")
            price_level = place.get("price_level", "N/A")
            address = place.get("vicinity", "N/A")
            types = ", ".join(place.get("types", [])[:3])  # Show first 3 types
            
            result += f"{i}. {name}\n"
            result += f"   Rating: {rating}/5.0\n"
            result += f"   Price Level: {price_level}/4\n"
            result += f"   Address: {address}\n"
            result += f"   Types: {types}\n"
            result += f"   Place ID: {place.get('place_id', 'N/A')}\n\n"
        
        return result
    
    @staticmethod
    def _format_weather_recommendations(
        location: Union[str, Tuple[float, float]],
        recommendations: List[Dict],
        weather_condition: str
    ) -> str:
        """
        Format weather-based recommendations
        
        :param location: search location
        :param recommendations: list of recommended places
        :param weather_condition: weather condition
        :return: formatted recommendations
        """
        if isinstance(location, tuple):
            location_str = f"coordinates ({location[0]:.4f}, {location[1]:.4f})"
        else:
            location_str = location
        
        result = f"Places recommended for {weather_condition} weather in {location_str}:\n\n"
        
        if not recommendations:
            return f"No places found for {weather_condition} weather in {location_str}"
        
        current_category = None
        place_count = 0
        
        for rec in recommendations:
            category = rec.get("category", "").replace("_", " ").title()
            
            if category != current_category:
                if current_category is not None:
                    result += "\n"
                result += f"📍 {category}:\n"
                current_category = category
                place_count = 0
            
            place_count += 1
            name = rec.get("name", "N/A")
            rating = rec.get("rating", "N/A")
            address = rec.get("vicinity", "N/A")
            
            result += f"  {place_count}. {name} (Rating: {rating}/5.0)\n"
            result += f"     {address}\n"
        
        return result
    
    @staticmethod
    def _format_distance_recommendations(
        location: Union[str, Tuple[float, float]],
        recommendations: List[Dict],
        travel_mode: str
    ) -> str:
        """
        Format distance-based recommendations
        
        :param location: search location
        :param recommendations: list of recommended places
        :param travel_mode: travel mode
        :return: formatted recommendations
        """
        if isinstance(location, tuple):
            location_str = f"coordinates ({location[0]:.4f}, {location[1]:.4f})"
        else:
            location_str = location
        
        mode_display = travel_mode.replace("_", " ").title()
        result = f"Places recommended for {mode_display} from {location_str}:\n\n"
        
        if not recommendations:
            return f"No places found for {mode_display} from {location_str}"
        
        current_category = None
        place_count = 0
        
        for rec in recommendations:
            category = rec.get("category", "").replace("_", " ").title()
            
            if category != current_category:
                if current_category is not None:
                    result += "\n"
                result += f"📍 {category}:\n"
                current_category = category
                place_count = 0
            
            place_count += 1
            name = rec.get("name", "N/A")
            rating = rec.get("rating", "N/A")
            distance = rec.get("distance_km", "N/A")
            address = rec.get("vicinity", "N/A")
            
            result += f"  {place_count}. {name} (Rating: {rating}/5.0, Distance: {distance}km)\n"
            result += f"     {address}\n"
        
        return result 
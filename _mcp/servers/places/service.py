"""
Places service module containing the PlacesService utils for Photon API
"""

import math
import requests
from typing import List, Dict, Optional, Union, Tuple
from _mcp.servers.places.constants import (
    PHOTON_API_BASE_URL,
    ENDPOINTS,
    PLACE_TYPES,
    SEARCH_RADIUS,
    DEFAULT_RADIUS,
    DEFAULT_RESULTS_LIMIT,
    MAX_RESULTS_LIMIT,
    MIN_RESULTS_LIMIT,
    WEATHER_PLACE_MAPPING,
    DISTANCE_CATEGORIES,
    DEFAULT_LANGUAGE
)


class PlacesService:
    """
    Service class for places-related operations using Photon API
    """
    
    def __init__(self):
        """
        Initialize the places service
        Note: Photon API doesn't require an API key
        """
        self.base_url = PHOTON_API_BASE_URL
    
    def search_places(
        self,
        location: Union[str, Tuple[float, float]],
        place_type: Optional[str] = None,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT,
        language: str = DEFAULT_LANGUAGE
    ) -> str:
        """
        Search for places based on location and criteria
        
        :param location: location string or (lat, lng) tuple
        :param place_type: type of place to search for
        :param radius: search radius in kilometers
        :param limit: maximum number of results
        :param language: preferred language for results
        :return: formatted search results
        """
        places_data = self.search_places_data(location, place_type, radius, limit, language)
        if isinstance(places_data, str):  # Error case
            return places_data
        
        return self._format_places_results(location, places_data, place_type)

    def search_places_data(
        self,
        location: Union[str, Tuple[float, float]],
        place_type: Optional[str] = None,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT,
        language: str = DEFAULT_LANGUAGE
    ) -> List[Dict] | str:
        """
        Search for places and return structured data
        
        :param location: location string or (lat, lng) tuple
        :param place_type: type of place to search for
        :param radius: search radius in kilometers
        :param limit: maximum number of results
        :param language: preferred language for results
        :return: list of place data or error string
        """
        # Validate inputs
        validation_error = self._validate_search_params(place_type, radius, limit)
        if validation_error:
            return validation_error
        
        # If location is coordinates, search nearby
        if isinstance(location, tuple):
            lat, lng = location
            return self._search_nearby(lat, lng, place_type, radius, limit, language)
        
        # If location is a string, first geocode it then search nearby
        geocode_result = self.geocode_location(location, language)
        if isinstance(geocode_result, str):  # Error case
            return geocode_result
        
        if not geocode_result:
            return f"Could not find location: {location}"
        
        # Get the first result's coordinates
        first_result = geocode_result[0]
        coordinates = first_result.get("geometry", {}).get("coordinates", [])
        if len(coordinates) != 2:
            return f"Invalid coordinates for location: {location}"
        
        lng, lat = coordinates  # GeoJSON uses [lng, lat] format
        
        # Search for places near the geocoded location
        return self._search_nearby(lat, lng, place_type, radius, limit, language)

    def geocode_location(
        self,
        location: str,
        language: str = DEFAULT_LANGUAGE,
        limit: int = 10
    ) -> List[Dict] | str:
        """
        Geocode a location string to get coordinates and place information
        
        :param location: location string to geocode
        :param language: preferred language for results
        :param limit: maximum number of results
        :return: list of geocoding results or error string
        """
        try:
            params = {
                "q": location,
                "limit": limit,
                "lang": language
            }
            
            url = f"{self.base_url}{ENDPOINTS['search']}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("type") != "FeatureCollection":
                return "Invalid response format from geocoding service"
            
            features = data.get("features", [])
            return features
            
        except requests.exceptions.RequestException as e:
            return f"Error geocoding location: {str(e)}"
        except Exception as e:
            return f"Unexpected error during geocoding: {str(e)}"

    def reverse_geocode(
        self,
        lat: float,
        lng: float,
        language: str = DEFAULT_LANGUAGE
    ) -> Dict | str:
        """
        Reverse geocode coordinates to get place information
        
        :param lat: latitude
        :param lng: longitude  
        :param language: preferred language for results
        :return: place information or error string
        """
        try:
            params = {
                "lat": lat,
                "lon": lng,
                "lang": language
            }
            
            url = f"{self.base_url}{ENDPOINTS['reverse']}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("type") != "FeatureCollection":
                return "Invalid response format from reverse geocoding service"
            
            features = data.get("features", [])
            if not features:
                return f"No place found at coordinates ({lat}, {lng})"
            
            return features[0]  # Return the first (most relevant) result
            
        except requests.exceptions.RequestException as e:
            return f"Error reverse geocoding: {str(e)}"
        except Exception as e:
            return f"Unexpected error during reverse geocoding: {str(e)}"

    def _search_nearby(
        self,
        lat: float,
        lng: float,
        place_type: Optional[str],
        radius: int,
        limit: int,
        language: str
    ) -> List[Dict] | str:
        """
        Search for places near given coordinates
        Note: Photon API is primarily geocoding, so this simulates nearby search
        by searching for place types in the area
        
        :param lat: latitude
        :param lng: longitude
        :param place_type: type of place to search for
        :param radius: search radius in kilometers
        :param limit: maximum number of results
        :param language: preferred language
        :return: list of places or error string
        """
        try:
            # Since Photon doesn't have a true "nearby search", we'll search for
            # place types with geographic bounds
            search_terms = []
            
            if place_type and place_type in PLACE_TYPES:
                search_terms.append(PLACE_TYPES[place_type])
            else:
                # Search for common place types
                search_terms = ["restaurant", "hotel", "shop", "attraction", "museum"]
            
            all_places = []
            
            for term in search_terms:
                try:
                    # Calculate bounding box for the search
                    lat_delta = radius / 111.0  # Rough conversion: 1 degree lat ≈ 111km
                    lng_delta = radius / (111.0 * math.cos(math.radians(lat)))
                    
                    # Create a search query that includes the place type and location context
                    query = f"{term} near {lat},{lng}"
                    
                    params = {
                        "q": query,
                        "limit": min(limit, 20),
                        "lang": language,
                        "lat": lat,
                        "lon": lng
                    }
                    
                    url = f"{self.base_url}{ENDPOINTS['search']}"
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        features = data.get("features", [])
                        
                        # Filter by distance
                        filtered_features = []
                        for feature in features:
                            coords = feature.get("geometry", {}).get("coordinates", [])
                            if len(coords) == 2:
                                place_lng, place_lat = coords
                                distance = self._calculate_distance(lat, lng, place_lat, place_lng)
                                if distance <= radius:
                                    feature["distance_km"] = distance
                                    feature["search_term"] = term
                                    filtered_features.append(feature)
                        
                        all_places.extend(filtered_features)
                
                except Exception:
                    continue
            
            # Remove duplicates and sort by distance
            unique_places = []
            seen_names = set()
            
            for place in all_places:
                name = place.get("properties", {}).get("name", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_places.append(place)
            
            # Sort by distance and limit results
            unique_places.sort(key=lambda x: x.get("distance_km", float('inf')))
            return unique_places[:limit]
            
        except Exception as e:
            return f"Error searching nearby places: {str(e)}"

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
        :param weather_condition: weather condition
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
        :param weather_condition: weather condition
        :param max_distance: maximum distance to search
        :param limit: maximum number of recommendations
        :return: list of place data or error string
        """
        # Get coordinates if location is a string
        if isinstance(location, str):
            geocode_result = self.geocode_location(location)
            if isinstance(geocode_result, str) or not geocode_result:
                return f"Could not find location: {location}"
            
            coordinates = geocode_result[0].get("geometry", {}).get("coordinates", [])
            if len(coordinates) != 2:
                return f"Invalid coordinates for location: {location}"
            lng, lat = coordinates
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
            places = self._search_nearby(lat, lng, place_type, max_distance, 5, DEFAULT_LANGUAGE)
            if isinstance(places, list):
                for place in places:
                    place["recommended_for"] = weather_condition
                    place["category"] = place_type
                all_recommendations.extend(places)
        
        # Sort by distance and limit results
        all_recommendations.sort(key=lambda x: x.get("distance_km", float('inf')))
        return all_recommendations[:limit]

    def recommend_places_by_distance(
        self,
        location: Union[str, Tuple[float, float]],
        travel_mode: str = "walking",
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> str:
        """
        Recommend places based on distance categories
        
        :param location: location string or (lat, lng) tuple
        :param travel_mode: travel mode
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
        :param travel_mode: travel mode
        :param limit: maximum number of recommendations
        :return: list of place data or error string
        """
        # Get coordinates if location is a string
        if isinstance(location, str):
            geocode_result = self.geocode_location(location)
            if isinstance(geocode_result, str) or not geocode_result:
                return f"Could not find location: {location}"
            
            coordinates = geocode_result[0].get("geometry", {}).get("coordinates", [])
            if len(coordinates) != 2:
                return f"Invalid coordinates for location: {location}"
            lng, lat = coordinates
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
            places = self._search_nearby(lat, lng, place_type, search_radius, 3, DEFAULT_LANGUAGE)
            if isinstance(places, list):
                for place in places:
                    place["travel_mode"] = travel_mode
                    place["category"] = place_type
                all_recommendations.extend(places)
        
        # Sort by distance and limit results
        all_recommendations.sort(key=lambda x: x.get("distance_km", float('inf')))
        return all_recommendations[:limit]
    
    @staticmethod
    def _validate_search_params(
        place_type: Optional[str],
        radius: int,
        limit: int
    ) -> Optional[str]:
        """
        Validate search parameters
        
        :param place_type: place type
        :param radius: search radius
        :param limit: results limit
        :return: error message if validation fails, None otherwise
        """
        if place_type and place_type not in PLACE_TYPES:
            available_types = ", ".join(PLACE_TYPES.keys())
            return f"Invalid place type '{place_type}'. Available types: {available_types}"
        
        if radius < 0 or radius > SEARCH_RADIUS["very_far"]:
            return f"Radius must be between 0 and {SEARCH_RADIUS['very_far']} km"
        
        if limit < MIN_RESULTS_LIMIT or limit > MAX_RESULTS_LIMIT:
            return f"Limit must be between {MIN_RESULTS_LIMIT} and {MAX_RESULTS_LIMIT}"
        
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
        
        return round(distance, 2)
    
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
            properties = place.get("properties", {})
            geometry = place.get("geometry", {})
            coordinates = geometry.get("coordinates", [])
            
            name = properties.get("name", "N/A")
            city = properties.get("city", "")
            country = properties.get("country", "")
            postcode = properties.get("postcode", "")
            street = properties.get("street", "")
            housenumber = properties.get("housenumber", "")
            distance = place.get("distance_km", "N/A")
            
            # Build address
            address_parts = []
            if housenumber and street:
                address_parts.append(f"{housenumber} {street}")
            elif street:
                address_parts.append(street)
            if city:
                address_parts.append(city)
            if postcode:
                address_parts.append(postcode)
            if country:
                address_parts.append(country)
            
            address = ", ".join(address_parts) if address_parts else "N/A"
            
            result += f"{i}. {name}\n"
            result += f"   Address: {address}\n"
            if distance != "N/A":
                result += f"   Distance: {distance} km\n"
            if len(coordinates) == 2:
                result += f"   Coordinates: {coordinates[1]:.4f}, {coordinates[0]:.4f}\n"
            result += f"   OSM ID: {properties.get('osm_id', 'N/A')}\n\n"
        
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
            properties = rec.get("properties", {})
            name = properties.get("name", "N/A")
            distance = rec.get("distance_km", "N/A")
            city = properties.get("city", "")
            
            location_info = f" in {city}" if city else ""
            distance_info = f" ({distance}km)" if distance != "N/A" else ""
            
            result += f"  {place_count}. {name}{location_info}{distance_info}\n"
        
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
            properties = rec.get("properties", {})
            name = properties.get("name", "N/A")
            distance = rec.get("distance_km", "N/A")
            city = properties.get("city", "")
            
            location_info = f" in {city}" if city else ""
            distance_info = f" ({distance}km)" if distance != "N/A" else ""
            
            result += f"  {place_count}. {name}{location_info}{distance_info}\n"
        
        return result 
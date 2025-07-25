"""
Places service module for OpenTripMap API integration
Handles tourist attraction and POI discovery with geocoding support
"""

import math
from typing import List, Dict, Optional, Union, Tuple
from _mcp.servers.base_service import BaseService
from _mcp.servers.places.constants import (
    OPENTRIPMAP_API_BASE_URL,
    ENDPOINTS,
    PLACE_CATEGORIES,
    DEFAULT_RADIUS,
    MAX_RADIUS,
    MIN_RADIUS,
    DEFAULT_RESULTS_LIMIT,
    MAX_RESULTS_LIMIT,
    MIN_RESULTS_LIMIT,
    WEATHER_PLACE_MAPPING,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    DEFAULT_FORMAT
)


class PlacesService(BaseService):
    """
    Service class for places-related operations using OpenTripMap API
    Provides tourist attraction discovery with natural language location support
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the places service with optional API key

        :param api_key: OpenTripMap API key (optional - required for higher rate limits)
        """
        self.api_key = api_key
        self.base_url = OPENTRIPMAP_API_BASE_URL
    
    def search_places(
        self,
        location: str,
        category: str = None,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT,
        language: str = DEFAULT_LANGUAGE
    ) -> str:
        """
        Search for tourist attractions and POIs using OpenTripMap API

        :param location: location as "lat,lng" coordinates or place name (will geocode first)
        :param category: place category from PLACE_CATEGORIES constants
        :param radius: search radius in meters (default: 10000, max: 50000)
        :param limit: maximum number of results (default: 20, max: 500)
        :param language: language code for results (default: en)
        :return: formatted search results or error message string
        """
        try:
            # Parse location
            lat, lng = self._parse_location(location)
            if lat is None or lng is None:
                return self.format_error_response(f"Invalid location: {location}", "location parsing")
            
            # Validate parameters
            radius = max(MIN_RADIUS, min(radius, MAX_RADIUS))
            limit = max(MIN_RESULTS_LIMIT, min(limit, MAX_RESULTS_LIMIT))
            language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
            
            # Build API parameters
            params = {
                'radius': radius,
                'lon': lng,
                'lat': lat,
                'format': DEFAULT_FORMAT,
                'limit': limit,
                'lang': language
            }
            
            # Add API key if available
            if self.api_key:
                params['apikey'] = self.api_key
            
            # Add category filter if specified
            if category and category in PLACE_CATEGORIES:
                params['kinds'] = PLACE_CATEGORIES[category]
            
            # Make API request
            endpoint = f"{self.base_url}{ENDPOINTS['places_by_location']}"
            data = self.make_api_request(endpoint, params=params)
            
            if data.get("error"):
                return self.format_error_response(data["error"], "OpenTripMap API")
            
            return self._format_places_response(data, lat, lng)
            
        except Exception as e:
            return self.format_error_response(str(e), "search")
    
    def get_place_details(self, place_id: str, language: str = DEFAULT_LANGUAGE) -> str:
        """
        Get detailed information about a specific place

        :param place_id: OpenTripMap place ID (xid)
        :param language: language code for details (default: en)
        :return: formatted place details or error message string
        """
        try:
            language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
            
            params = {
                'lang': language,
                'format': DEFAULT_FORMAT
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            endpoint = f"{self.base_url}{ENDPOINTS['place_details']}/{place_id}"
            data = self.make_api_request(endpoint, params=params)
            
            if data.get("error"):
                return self.format_error_response(data["error"], "place details")
            
            return self._format_place_details(data)
            
        except Exception as e:
            return self.format_error_response(str(e), "place details")
    
    def autocomplete_places(self, query: str, language: str = DEFAULT_LANGUAGE) -> str:
        """
        Get place suggestions for autocomplete functionality

        :param query: search query string
        :param language: language code for suggestions (default: en)
        :return: formatted suggestions or error message string
        """
        try:
            language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
            
            params = {
                'name': query,
                'lang': language,
                'format': DEFAULT_FORMAT
            }
            
            if self.api_key:
                params['apikey'] = self.api_key
            
            endpoint = f"{self.base_url}{ENDPOINTS['place_autocomplete']}"
            data = self.make_api_request(endpoint, params=params)
            
            if data.get("error"):
                return self.format_error_response(data["error"], "autocomplete")
            
            return self._format_autocomplete_response(data)
            
        except Exception as e:
            return self.format_error_response(str(e), "autocomplete")
    
    def get_places_by_weather(
        self,
        location: str,
        weather_condition: str,
        radius: int = DEFAULT_RADIUS,
        limit: int = DEFAULT_RESULTS_LIMIT
    ) -> str:
        """
        Get places suitable for specific weather conditions

        :param location: location as "lat,lng" coordinates
        :param weather_condition: weather condition (sunny, rainy, cloudy, snowy, windy)
        :param radius: search radius in meters (default: 10000)
        :param limit: maximum number of results (default: 20)
        :return: formatted results or error message string
        """
        try:
            if weather_condition not in WEATHER_PLACE_MAPPING:
                return self.format_error_response(f"Unknown weather condition: {weather_condition}", "weather filtering")
            
            suitable_categories = WEATHER_PLACE_MAPPING[weather_condition]
            all_results = []
            
            for category in suitable_categories:
                result = self.search_places(location, category, radius, limit // len(suitable_categories))
                if not result.startswith("Error"):
                    all_results.append(f"=== {category.replace('_', ' ').title()} ===\n{result}")
            
            if not all_results:
                return f"No places found suitable for {weather_condition} weather"
            
            return f"Places suitable for {weather_condition} weather:\n\n" + "\n\n".join(all_results)
            
        except Exception as e:
            return self.format_error_response(str(e), "weather-based search")
    
    def _parse_location(self, location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse location string to lat/lng coordinates

        :param location: location as "lat,lng" coordinates or place name
        :return: tuple of (lat, lng) or (None, None) if invalid
        """
        try:
            # Try to parse as coordinates first
            if ',' in location:
                parts = location.strip().split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lng = float(parts[1].strip())
                    
                    # Validate coordinate ranges using base service method
                    if self.validate_coordinates(lat, lng):
                        return lat, lng
            
            # If not coordinates, try to geocode the location name using base service
            lat, lng = self.get_coordinates(location)
            return lat, lng
            
        except (ValueError, IndexError):
            return None, None
    
    def _format_places_response(self, data: Union[Dict, List], center_lat: float, center_lng: float) -> str:
        """
        Format the API response into a readable string

        :param data: API response data (dict or list)
        :param center_lat: center latitude for distance calculation
        :param center_lng: center longitude for distance calculation
        :return: formatted string with places information
        """
        try:
            # Handle different response formats
            places = data if isinstance(data, list) else data.get('features', [])
            
            if not places:
                return "No places found in the specified area."
            
            result = f"Found {len(places)} tourist attractions and points of interest:\n\n"
            
            for i, place in enumerate(places, 1):
                name = place.get('properties', {}).get('name', 'Unknown Place')
                xid = place.get('properties', {}).get('xid', '')
                kinds = place.get('properties', {}).get('kinds', '')
                
                # Get coordinates for distance calculation
                coords = place.get('geometry', {}).get('coordinates', [])
                if len(coords) >= 2:
                    place_lng, place_lat = coords[0], coords[1]
                    distance = self._calculate_distance(center_lat, center_lng, place_lat, place_lng)
                    distance_text = f" ({distance:.1f}km away)"
                else:
                    distance_text = ""
                
                # Format kinds/categories
                categories = kinds.replace(',', ', ').replace('_', ' ').title() if kinds else 'General Attraction'
                
                result += f"{i}. {name}{distance_text}\n"
                result += f"   Categories: {categories}\n"
                if xid:
                    result += f"   ID: {xid}\n"
                result += "\n"
            
            return result.strip()
            
        except Exception as e:
            return self.format_error_response(str(e), "response formatting")
    
    def _format_place_details(self, data: Dict) -> str:
        """
        Format place details into a readable string

        :param data: place details data dictionary
        :return: formatted string with place details
        """
        try:
            name = data.get('name', 'Unknown Place')
            kinds = data.get('kinds', '')
            address = data.get('address', {})
            wikipedia = data.get('wikipedia', '')
            image = data.get('image', '')
            
            result = f"=== {name} ===\n\n"
            
            if kinds:
                categories = kinds.replace(',', ', ').replace('_', ' ').title()
                result += f"Categories: {categories}\n"
            
            if address:
                addr_parts = []
                for key in ['house_number', 'road', 'city', 'state', 'country']:
                    if key in address and address[key]:
                        addr_parts.append(address[key])
                if addr_parts:
                    result += f"Address: {', '.join(addr_parts)}\n"
            
            if wikipedia:
                result += f"Wikipedia: {wikipedia}\n"
            
            if image:
                result += f"Image: {image}\n"
            
            return result.strip()
            
        except Exception as e:
            return self.format_error_response(str(e), "place details formatting")
    
    def _format_autocomplete_response(self, data: Union[Dict, List]) -> str:
        """
        Format autocomplete suggestions into a readable string

        :param data: autocomplete response data (dict or list)
        :return: formatted string with suggestions
        """
        try:
            suggestions = data if isinstance(data, list) else data.get('features', [])
            
            if not suggestions:
                return "No suggestions found."
            
            result = "Suggestions:\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                name = suggestion.get('properties', {}).get('name', 'Unknown')
                country = suggestion.get('properties', {}).get('country', '')
                
                result += f"{i}. {name}"
                if country:
                    result += f" ({country})"
                result += "\n"
            
            return result.strip()
            
        except Exception as e:
            return self.format_error_response(str(e), "suggestions formatting")
    
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
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r 
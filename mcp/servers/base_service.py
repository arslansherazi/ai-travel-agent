"""Base service module containing common functionality for all services"""

import requests
from typing import Tuple, Optional, Dict, Any
from abc import ABC

from mcp.servers.constants import GEOCODING_API_URL, DEFAULT_TIMEOUT


class BaseService(ABC):
    """
    Base service class with common functionality for all services
    """
    
    @staticmethod
    def get_coordinates(location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Get latitude and longitude for a location using Open-Meteo Geocoding API
        
        :param location: location name (city, address, etc.)
        :return: tuple of (latitude, longitude) or (None, None) if not found
        """
        params = {
            "name": location,
            "count": 1,  # Get only the top result
            "language": "en",
            "format": "json"
        }
        
        try:
            response = requests.get(GEOCODING_API_URL, params=params)
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                return None, None
            
            # Return the coordinates of the first result
            return results[0].get("latitude"), results[0].get("longitude")
            
        except Exception as e:
            print(f"Error in geocoding: {e}")
            return None, None
    
    @staticmethod
    def make_api_request(
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        method: str = "GET",
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Make an API request with error handling
        
        :param url: API endpoint URL
        :param params: request parameters
        :param headers: request headers
        :param method: HTTP method (GET, POST, etc.)
        :param timeout: request timeout in seconds
        :return: API response data or error dict
        """
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers, timeout=timeout)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}

            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP error {response.status_code}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    @staticmethod
    def validate_coordinates(lat: Optional[float], lng: Optional[float]) -> bool:
        """
        Validate latitude and longitude coordinates
        
        :param lat: latitude
        :param lng: longitude
        :return: True if coordinates are valid, False otherwise
        """
        if lat is None or lng is None:
            return False
        
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @staticmethod
    def format_error_response(error_message: str, context: str = "") -> str:
        """
        Format error messages consistently
        
        :param error_message: the error message
        :param context: additional context about where the error occurred
        :return: formatted error string
        """
        if context:
            return f"Error in {context}: {error_message}"
        return f"Error: {error_message}"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
        """
        Truncate text to a maximum length
        
        :param text: text to truncate
        :param max_length: maximum length
        :param suffix: suffix to add when truncating
        :return: truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def check_api_key_required(api_key: Optional[str], service_name: str) -> Optional[str]:
        """
        Check if API key is required and return error message if missing
        
        :param api_key: API key to check
        :param service_name: name of the service (e.g., "Booking.com", "Weather")

        :return: error message if API key is missing, None otherwise
        """
        if not api_key:
            return f"API key is required for {service_name} operations. Please configure your {service_name} API key."
        return None
 
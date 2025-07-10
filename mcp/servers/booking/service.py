"""
Booking service module containing the BookingService utils
"""

from typing import Tuple, Dict, Optional, Union
from datetime import datetime, timedelta
from mcp.servers.base_service import BaseService
from mcp.servers.booking.constants import (
    BOOKING_API_BASE_URL,
    ENDPOINTS,
    SEARCH_EXTRAS,
    ACCOMMODATION_TYPES,
    DEFAULT_PLATFORM,
    DEFAULT_COUNTRY,
    DEFAULT_CURRENCY,
    DEFAULT_ADULTS,
    DEFAULT_ROOMS,
    DEFAULT_ROWS,
    MAX_ROWS,
    MIN_ROWS,
    MAX_DAYS_IN_FUTURE,
    MAX_STAY_DURATION,
    MIN_PRICE,
    MAX_PRICE, DEFAULT_STAY_DURATION
)


class BookingService(BaseService):
    """
    Service class for booking-related operations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the booking service
        
        :param api_key: Booking.com API key
        """
        self.api_key = api_key
        self.base_url = BOOKING_API_BASE_URL
    
    def search_accommodations(
        self,
        location: str | Tuple[float, float],
        checkin: str = datetime.now().strftime("%Y-%m-%d"),
        checkout: str = (datetime.now() + timedelta(days=DEFAULT_STAY_DURATION)).strftime("%Y-%m-%d"),
        adults: int = DEFAULT_ADULTS,
        rooms: int = DEFAULT_ROOMS,
        rows: int = DEFAULT_ROWS
    ) -> str:
        """
        Search for accommodations based on location and dates
        
        :param location: location string or (lat, lng) tuple
        :param checkin: check-in date (YYYY-MM-DD)
        :param checkout: checkout date (YYYY-MM-DD)
        :param adults: number of adults
        :param rooms: number of rooms
        :param rows: number of results to return
        :return: formatted search results
        """
        accommodations_data = self.search_accommodations_data(location, checkin, checkout, adults, rooms, rows)
        if isinstance(accommodations_data, str):  # Error case
            return accommodations_data
        
        return self._format_search_results(location, {"results": accommodations_data})

    def search_accommodations_data(
        self,
        location: str | Tuple[float, float],
        checkin: str = datetime.now().strftime("%Y-%m-%d"),
        checkout: str = (datetime.now() + timedelta(days=DEFAULT_STAY_DURATION)).strftime("%Y-%m-%d"),
        adults: int = DEFAULT_ADULTS,
        rooms: int = DEFAULT_ROOMS,
        rows: int = DEFAULT_ROWS
    ) -> list[Dict] | str:
        """
        Search for accommodations and return structured data (for use by other services)
        
        :param location: location string or (lat, lng) tuple
        :param checkin: check-in date (YYYY-MM-DD)
        :param checkout: checkout date (YYYY-MM-DD)
        :param adults: number of adults
        :param rooms: number of rooms
        :param rows: number of results to return
        :return: list of accommodation data or error string
        """
        api_key_error = self.check_api_key_required(self.api_key, "Booking.com")
        if api_key_error:
            return api_key_error
        
        # Validate dates
        validation_error = self._validate_dates(checkin, checkout)
        if validation_error:
            return validation_error
        
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = BaseService.get_coordinates(location)
            if not lat or not lng:
                return f"Could not find coordinates for {location}"
        else:
            lat, lng = location
        
        # Prepare search parameters
        params = {
            "latitude": lat,
            "longitude": lng,
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "rooms": rooms,
            "rows": min(max(rows, MIN_ROWS), MAX_ROWS),
            "extras": ",".join(SEARCH_EXTRAS),
            "platform": DEFAULT_PLATFORM,
            "country": DEFAULT_COUNTRY,
            "currency": DEFAULT_CURRENCY
        }
        
        try:
            response = self._make_api_request(ENDPOINTS["search"], params)
            if response.get("error"):
                return f"Error searching accommodations: {response['error']}"
            
            return response.get("results", [])
            
        except Exception as e:
            return f"Error occurred during search: {str(e)}"

    def search_specific_accommodations(
        self,
        location: Union[str, Tuple[float, float]],
        checkin: str,
        checkout: str,
        star_rating: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        accommodation_type: Optional[str] = None,
        adults: int = DEFAULT_ADULTS,
        rooms: int = DEFAULT_ROOMS,
        rows: int = DEFAULT_ROWS
    ) -> str:
        """
        Search for accommodations with specific criteria
        
        :param location: location string or (lat, lng) tuple
        :param checkin: check-in date (YYYY-MM-DD)
        :param checkout: checkout date (YYYY-MM-DD)
        :param star_rating: hotel star rating (1-5)
        :param price_min: minimum price per night
        :param price_max: maximum price per night
        :param accommodation_type: type of accommodation (hotel, apartment, etc.)
        :param adults: number of adults
        :param rooms: number of rooms
        :param rows: number of results to return
        :return: formatted search results
        """
        accommodations_data = self.search_specific_accommodations_data(
            location, checkin, checkout, star_rating, price_min, price_max, 
            accommodation_type, adults, rooms, rows
        )
        if isinstance(accommodations_data, str):  # Error case
            return accommodations_data
        
        return self._format_specific_search_results(
            location, {"results": accommodations_data}, star_rating, price_min, price_max, accommodation_type
        )

    def search_specific_accommodations_data(
        self,
        location: Union[str, Tuple[float, float]],
        checkin: str,
        checkout: str,
        star_rating: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        accommodation_type: Optional[str] = None,
        adults: int = DEFAULT_ADULTS,
        rooms: int = DEFAULT_ROOMS,
        rows: int = DEFAULT_ROWS
    ) -> list[Dict] | str:
        """
        Search for accommodations with specific criteria and return structured data
        
        :param location: location string or (lat, lng) tuple
        :param checkin: check-in date (YYYY-MM-DD)
        :param checkout: checkout date (YYYY-MM-DD)
        :param star_rating: hotel star rating (1-5)
        :param price_min: minimum price per night
        :param price_max: maximum price per night
        :param accommodation_type: type of accommodation (hotel, apartment, etc.)
        :param adults: number of adults
        :param rooms: number of rooms
        :param rows: number of results to return
        :return: list of accommodation data or error string
        """
        api_key_error = self.check_api_key_required(self.api_key, "Booking.com")
        if api_key_error:
            return api_key_error
        
        # Validate inputs
        validation_error = self._validate_specific_search_params(
            checkin, checkout, star_rating, price_min, price_max, accommodation_type
        )
        if validation_error:
            return validation_error
        
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = BaseService.get_coordinates(location)
            if not lat or not lng:
                return f"Could not find coordinates for {location}"
        else:
            lat, lng = location
        
        # Prepare search parameters
        params = {
            "latitude": lat,
            "longitude": lng,
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "rooms": rooms,
            "rows": min(max(rows, MIN_ROWS), MAX_ROWS),
            "extras": ",".join(SEARCH_EXTRAS),
            "platform": DEFAULT_PLATFORM,
            "country": DEFAULT_COUNTRY,
            "currency": DEFAULT_CURRENCY
        }
        
        # Add specific filters
        if star_rating:
            params["star_rating"] = star_rating
        if price_min:
            params["price_min"] = price_min
        if price_max:
            params["price_max"] = price_max
        if accommodation_type and accommodation_type.lower() in ACCOMMODATION_TYPES:
            params["accommodation_type"] = ACCOMMODATION_TYPES[accommodation_type.lower()]
        
        try:
            response = self._make_api_request(ENDPOINTS["search"], params)
            if response.get("error"):
                return f"Error searching accommodations: {response['error']}"
            
            return response.get("results", [])
            
        except Exception as e:
            return f"Error occurred during search: {str(e)}"
    
    def get_accommodation_details(self, hotel_id: str) -> str:
        """
        Get detailed information about a specific accommodation
        
        :param hotel_id: unique hotel identifier
        :return: formatted accommodation details
        """
        api_key_error = self.check_api_key_required(self.api_key, "Booking.com")
        if api_key_error:
            return api_key_error
        
        params = {
            "hotel_id": hotel_id,
            "platform": DEFAULT_PLATFORM,
            "country": DEFAULT_COUNTRY,
            "currency": DEFAULT_CURRENCY
        }
        
        try:
            # Get accommodation details
            details_response = self._make_api_request(ENDPOINTS["details"], params)
            if details_response.get("error"):
                return f"Error fetching accommodation details: {details_response['error']}"
            
            # Get reviews
            reviews_response = self._make_api_request(ENDPOINTS["reviews"], params)
            
            return self._format_accommodation_details(details_response, reviews_response)
            
        except Exception as e:
            return f"Error occurred while fetching details: {str(e)}"
    
    def _make_api_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Make API request to Booking.com
        
        :param endpoint: API endpoint
        :param params: request parameters
        :return: API response data
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        return BaseService.make_api_request(url, params=params, headers=headers)
    
    @staticmethod
    def _validate_dates(checkin: str, checkout: str) -> Optional[str]:
        """
        Validate check-in and checkout dates
        
        :param checkin: check-in date string
        :param checkout: checkout date string
        :return: error message if validation fails, None otherwise
        """
        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
            today = datetime.now()
            
            # Check if dates are in the past
            if checkin_date.date() < today.date():
                return "Check-in date cannot be in the past"
            
            if checkout_date.date() <= checkin_date.date():
                return "Checkout date must be after check-in date"
            
            # Check if dates are too far in the future
            max_future_date = today + timedelta(days=MAX_DAYS_IN_FUTURE)
            if checkin_date > max_future_date:
                return f"Check-in date cannot be more than {MAX_DAYS_IN_FUTURE} days in the future"
            
            # Check stay duration
            stay_duration = (checkout_date - checkin_date).days
            if stay_duration > MAX_STAY_DURATION:
                return f"Stay duration cannot exceed {MAX_STAY_DURATION} days"
            
            return None
            
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD format"
    
    @staticmethod
    def _validate_specific_search_params(
        checkin: str,
        checkout: str,
        star_rating: Optional[int],
        price_min: Optional[float],
        price_max: Optional[float],
        accommodation_type: Optional[str]
    ) -> Optional[str]:
        """
        Validate specific search parameters
        
        :param checkin: check-in date
        :param checkout: checkout date
        :param star_rating: star rating
        :param price_min: minimum price
        :param price_max: maximum price
        :param accommodation_type: accommodation type
        :return: error message if validation fails, None otherwise
        """
        # Validate dates first
        date_error = BookingService._validate_dates(checkin, checkout)
        if date_error:
            return date_error
        
        # Validate star rating
        if star_rating is not None and (star_rating < 1 or star_rating > 5):
            return "Star rating must be between 1 and 5"
        
        # Validate price range
        if price_min is not None and (price_min < MIN_PRICE or price_min > MAX_PRICE):
            return f"Minimum price must be between {MIN_PRICE} and {MAX_PRICE}"
        
        if price_max is not None and (price_max < MIN_PRICE or price_max > MAX_PRICE):
            return f"Maximum price must be between {MIN_PRICE} and {MAX_PRICE}"
        
        if price_min is not None and price_max is not None and price_min >= price_max:
            return "Minimum price must be less than maximum price"
        
        # Validate accommodation type
        if accommodation_type is not None and accommodation_type.lower() not in ACCOMMODATION_TYPES:
            available_types = ", ".join(ACCOMMODATION_TYPES.keys())
            return f"Invalid accommodation type. Available types: {available_types}"
        
        return None
    
    @staticmethod
    def _format_search_results(location: Union[str, Tuple[float, float]], response: Dict) -> str:
        """
        Format search results into a readable report
        
        :param location: search location
        :param response: API response data
        :return: formatted search results
        """
        location_str = location
        if isinstance(location, tuple):
            location_str = f"coordinates ({location[0]:.4f}, {location[1]:.4f})"
        
        result = f"Accommodation search results for {location_str}:\n\n"
        
        accommodations = response.get("results", [])
        if not accommodations:
            return f"No accommodations found for {location_str}"
        
        for i, accommodation in enumerate(accommodations[:10], 1):
            name = accommodation.get("name", "N/A")
            star_rating = accommodation.get("star_rating", "N/A")
            price = accommodation.get("price", {})
            currency = price.get("currency", "")
            amount = price.get("amount", "N/A")
            
            result += f"{i}. {name}\n"
            result += f"   Star Rating: {star_rating} stars\n"
            result += f"   Price: {amount} {currency} per night\n"
            result += f"   Hotel ID: {accommodation.get('hotel_id', 'N/A')}\n\n"
        
        total_results = response.get("total_results", len(accommodations))
        if total_results > 10:
            result += f"... and {total_results - 10} more results\n"
        
        return result
    
    @staticmethod
    def _format_specific_search_results(
        location: Union[str, Tuple[float, float]],
        response: Dict,
        star_rating: Optional[int],
        price_min: Optional[float],
        price_max: Optional[float],
        accommodation_type: Optional[str]
    ) -> str:
        """
        Format specific search results into a readable report
        
        :param location: search location
        :param response: API response data
        :param star_rating: star rating filter
        :param price_min: minimum price filter
        :param price_max: maximum price filter
        :param accommodation_type: accommodation type filter
        :return: formatted search results
        """
        if isinstance(location, tuple):
            location_str = f"coordinates ({location[0]:.4f}, {location[1]:.4f})"
        else:
            location_str = location
        
        # Build filter description
        filters = []
        if star_rating:
            filters.append(f"{star_rating} stars")
        if price_min:
            filters.append(f"min price: ${price_min}")
        if price_max:
            filters.append(f"max price: ${price_max}")
        if accommodation_type:
            filters.append(f"type: {accommodation_type}")
        
        filter_str = f" (filters: {', '.join(filters)})" if filters else ""
        
        result = f"Specific accommodation search results for {location_str}{filter_str}:\n\n"
        
        accommodations = response.get("results", [])
        if not accommodations:
            return f"No accommodations found for {location_str} with the specified criteria"
        
        for i, accommodation in enumerate(accommodations[:10], 1):
            name = accommodation.get("name", "N/A")
            star_rating_result = accommodation.get("star_rating", "N/A")
            price = accommodation.get("price", {})
            currency = price.get("currency", "")
            amount = price.get("amount", "N/A")
            acc_type = accommodation.get("accommodation_type_name", "N/A")
            
            result += f"{i}. {name}\n"
            result += f"   Type: {acc_type}\n"
            result += f"   Star Rating: {star_rating_result} stars\n"
            result += f"   Price: {amount} {currency} per night\n"
            result += f"   Hotel ID: {accommodation.get('hotel_id', 'N/A')}\n\n"
        
        total_results = response.get("total_results", len(accommodations))
        if total_results > 10:
            result += f"... and {total_results - 10} more results\n"
        
        return result
    
    @staticmethod
    def _format_accommodation_details(details_response: Dict, reviews_response: Optional[Dict] = None) -> str:
        """
        Format accommodation details into a readable report
        
        :param details_response: accommodation details API response
        :param reviews_response: reviews API response
        :return: formatted accommodation details
        """
        accommodation = details_response.get("result", {})
        
        if not accommodation:
            return "No accommodation details found"
        
        result = f"Accommodation Details:\n\n"
        result += f"Name: {accommodation.get('name', 'N/A')}\n"
        result += f"Star Rating: {accommodation.get('star_rating', 'N/A')} stars\n"
        result += f"Type: {accommodation.get('accommodation_type_name', 'N/A')}\n"
        
        # Address information
        address = accommodation.get("address", {})
        if address:
            result += f"Address: {address.get('address_line_1', '')}, "
            result += f"{address.get('city', '')}, {address.get('country', '')}\n"
        
        # Contact information
        contact = accommodation.get("contact", {})
        if contact:
            phone = contact.get("phone")
            if phone:
                result += f"Phone: {phone}\n"
        
        # Description
        description = accommodation.get("description", {}).get("short_description")
        if description:
            result += f"Description: {description}\n"
        
        # Amenities
        amenities = accommodation.get("amenities", [])
        if amenities:
            result += f"Amenities: {', '.join([amenity.get('name', '') for amenity in amenities[:10]])}\n"
        
        # Photos
        photos = accommodation.get("photos", [])
        if photos:
            result += f"Photos: {len(photos)} photos available\n"
            result += f"Photo URLs:\n"
            for i, photo in enumerate(photos[:5], 1):
                url = photo.get("url_original")
                if url:
                    result += f"  {i}. {url}\n"
        
        # Booking information
        booking_url = accommodation.get("url")
        if booking_url:
            result += f"Booking URL: {booking_url}\n"
        
        # Reviews
        if reviews_response and reviews_response.get("result"):
            reviews = reviews_response["result"]
            avg_score = reviews.get("average_score")
            review_count = reviews.get("review_count")
            
            if avg_score and review_count:
                result += f"Reviews: {avg_score}/10 based on {review_count} reviews\n"
            
            # Sample reviews
            review_list = reviews.get("reviews", [])
            if review_list:
                result += f"Recent Reviews:\n"
                for i, review in enumerate(review_list[:3], 1):
                    score = review.get("score", "N/A")
                    comment = review.get("positive", "")[:200]
                    if comment:
                        result += f"  {i}. Score: {score}/10 - {comment}...\n"
        
        return result 
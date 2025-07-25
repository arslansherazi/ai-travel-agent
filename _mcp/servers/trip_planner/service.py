"""
Trip planning service using OpenTripMap for attractions, weather data, and booking integration
Provides comprehensive trip planning with daily itineraries and activity recommendations
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from _mcp.servers.base_service import BaseService
from _mcp.servers.places.service import PlacesService
from _mcp.servers.booking.service import BookingService
from _mcp.servers.weather.service import WeatherService


class TripPlannerService(BaseService):
    """
    Service for comprehensive trip planning using attractions, weather, and booking data
    Integrates multiple services to create complete travel itineraries
    """
    
    def __init__(self, booking_api_key: Optional[str] = None, places_api_key: Optional[str] = None):
        """
        Initialize trip planner with required services

        :param booking_api_key: API key for booking service (optional)
        :param places_api_key: API key for OpenTripMap places service (optional)
        """
        self.places_service = PlacesService(api_key=places_api_key)
        self.booking_service = BookingService(api_key=booking_api_key)
        self.weather_service = WeatherService()
    
    def plan_trip(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: str = "moderate",
        interests: List[str] = None,
        group_size: int = 2,
        accommodation_type: str = "hotel"
    ) -> str:
        """
        Generate a comprehensive trip plan with daily itineraries

        :param destination: city or location name (e.g., "Rome", "Paris", "Tokyo")
        :param start_date: start date in YYYY-MM-DD format
        :param end_date: end date in YYYY-MM-DD format
        :param budget: budget category (budget, moderate, luxury)
        :param interests: list of interest categories (cultural, natural, entertainment, etc.)
        :param group_size: number of people in the group
        :param accommodation_type: type of accommodation preferred
        :return: formatted comprehensive trip plan
        """
        try:
            # Validate inputs
            if not self._validate_trip_inputs(destination, start_date, end_date):
                return self.format_error_response("Invalid trip parameters", "input validation")
            
            trip_data = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "interests": interests or ["cultural", "natural"],
                "group_size": group_size,
                "accommodation_type": accommodation_type
            }
            
            # Get weather information
            weather_data = self._get_weather_forecast(destination, start_date, end_date)
            
            # Find accommodations
            accommodation_data = self._find_accommodations(destination, start_date, end_date, group_size)
            
            # Generate daily itineraries
            daily_plans = self._generate_daily_itineraries(trip_data, weather_data)
            
            # Create packing suggestions
            packing_list = self._generate_packing_list(weather_data)
            
            # Generate final trip plan
            return self._format_complete_trip_plan(trip_data, daily_plans, accommodation_data, packing_list)
            
        except Exception as e:
            return self.format_error_response(str(e), "trip planning")
    
    def suggest_activities(
        self,
        destination: str,
        date: str = None,
        weather_condition: str = None,
        interests: List[str] = None,
        duration_hours: int = 6
    ) -> str:
        """
        Suggest activities for a specific day and weather condition

        :param destination: location name
        :param date: date in YYYY-MM-DD format (optional)
        :param weather_condition: current weather (sunny, rainy, cloudy, snowy, windy)
        :param interests: list of activity preferences
        :param duration_hours: number of hours to plan activities for
        :return: formatted activity suggestions
        """
        try:
            if not weather_condition and date:
                # Get weather for the date
                weather_data = self._get_weather_forecast(destination, date, date)
                weather_condition = weather_data.get(date, {}).get('condition', 'cloudy')
            
            # Search for weather-appropriate attractions
            if weather_condition:
                attractions = self.places_service.get_places_by_weather(
                    destination, weather_condition, 15000, 20
                )
            else:
                # Default search using human-readable location
                attractions = self.places_service.search_places(
                    destination, None, 15000, 20
                )
            
            return self._format_activity_suggestions(attractions, weather_condition, duration_hours)
            
        except Exception as e:
            return self.format_error_response(str(e), "activity suggestions")
    
    def find_nearby_amenities(
        self,
        location: str,
        amenity_type: str = "restaurants",
        distance_km: int = 2
    ) -> str:
        """
        Find nearby amenities like restaurants, shops, transport

        :param location: current location name
        :param amenity_type: type of amenity (restaurants, shops, transport, hotels)
        :param distance_km: search radius in kilometers
        :return: formatted list of nearby amenities
        """
        try:
            # Map amenity types to OpenTripMap categories
            amenity_mapping = {
                "restaurants": "foods",
                "food": "foods",
                "dining": "foods",
                "shops": "shops",
                "shopping": "shops",
                "transport": "tourist_facilities",
                "hotels": "accomodations",
                "accommodation": "accomodations"
            }
            
            category = amenity_mapping.get(amenity_type.lower(), amenity_type)
            
            # Search for places using the places service with location name
            results = self.places_service.search_places(
                location, category, distance_km * 1000, 15
            )
            
            return f"🔍 {amenity_type.title()} near {location}:\n\n{results}"
            
        except Exception as e:
            return self.format_error_response(str(e), "amenity search")
    
    def _validate_trip_inputs(self, destination: str, start_date: str, end_date: str) -> bool:
        """
        Validate trip planning inputs for correctness

        :param destination: destination location name
        :param start_date: start date string
        :param end_date: end date string
        :return: True if inputs are valid, False otherwise
        """
        try:
            # Check if destination is provided
            if not destination or len(destination.strip()) < 2:
                return False
            
            # Parse and validate dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Check if dates are logical
            if end <= start:
                return False
            
            # Check if trip is not too long (reasonable limit)
            if (end - start).days > 30:
                return False
            
            return True
            
        except ValueError:
            return False
    
    def _get_weather_forecast(self, destination: str, start_date: str, end_date: str) -> Dict:
        """
        Get weather forecast for the trip period using coordinates

        :param destination: destination location name
        :param start_date: start date string
        :param end_date: end date string
        :return: dictionary of weather data by date
        """
        try:
            # Get coordinates for the destination using base service
            lat, lng = self.get_coordinates(destination)
            if not lat or not lng:
                return {}
            
            # Get weather forecast
            weather_result = self.weather_service.get_weather_forecast(lat, lng, 7)
            
            # Parse weather data into a more usable format
            weather_by_date = {}
            
            if isinstance(weather_result, str) and not weather_result.startswith("Error"):
                # Simple parsing - extract weather conditions from response
                lines = weather_result.split('\n')
                current_date = None
                
                for line in lines:
                    if 'Date:' in line:
                        # Extract date from the line
                        current_date = line.split('Date:')[1].strip()
                    elif 'Condition:' in line and current_date:
                        condition = line.split('Condition:')[1].strip().lower()
                        weather_by_date[current_date] = {'condition': condition}
            
            return weather_by_date
            
        except Exception:
            return {}
    
    def _find_accommodations(self, destination: str, start_date: str, end_date: str, group_size: int) -> Dict:
        """
        Find accommodation options for the destination and dates

        :param destination: destination location name
        :param start_date: check-in date
        :param end_date: check-out date
        :param group_size: number of people
        :return: dictionary with accommodation data
        """
        try:
            # Search for accommodations using booking service
            accommodations = self.booking_service.search_accommodations(
                destination, start_date, end_date, group_size
            )
            
            return {"accommodations": accommodations}
            
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_daily_itineraries(self, trip_data: Dict, weather_data: Dict) -> List[Dict]:
        """
        Generate day-by-day itineraries for the trip

        :param trip_data: trip information dictionary
        :param weather_data: weather forecast data
        :return: list of daily plan dictionaries
        """
        try:
            daily_plans = []
            start_date = datetime.strptime(trip_data["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(trip_data["end_date"], "%Y-%m-%d")
            
            current_date = start_date
            day_number = 1
            
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Get weather for this day
                weather_condition = weather_data.get(date_str, {}).get('condition', 'cloudy')
                
                # Generate activities for this day
                activities = self._plan_single_day(
                    trip_data["destination"],
                    date_str,
                    weather_condition,
                    trip_data["interests"]
                )
                
                daily_plans.append({
                    "day": day_number,
                    "date": date_str,
                    "weather": weather_condition,
                    "activities": activities
                })
                
                current_date += timedelta(days=1)
                day_number += 1
            
            return daily_plans
            
        except Exception:
            return []
    
    def _plan_single_day(self, destination: str, date: str, weather: str, interests: List[str]) -> List[Dict]:
        """
        Plan activities for a single day

        :param destination: destination location name
        :param date: date string
        :param weather: weather condition
        :param interests: list of user interests
        :return: list of activity dictionaries
        """
        try:
            activities = []
            time_slots = ["morning", "afternoon", "evening"]
            
            for time_slot in time_slots:
                activity = self._find_activity_for_time_slot(destination, time_slot, weather, interests)
                if activity:
                    activities.append(activity)
            
            return activities
            
        except Exception:
            return []
    
    def _find_activity_for_time_slot(self, destination: str, time_slot: str, weather: str, interests: List[str]) -> Optional[Dict]:
        """
        Find appropriate activity for a specific time slot

        :param destination: destination location name
        :param time_slot: time period (morning, afternoon, evening)
        :param weather: weather condition
        :param interests: list of user interests
        :return: activity dictionary or None
        """
        try:
            # Select category based on interests and time slot
            if time_slot == "morning" and "cultural" in interests:
                category = "museums"
            elif time_slot == "afternoon" and "natural" in interests:
                category = "natural" if weather == "sunny" else "museums"
            elif time_slot == "evening":
                category = "foods"  # Dining/entertainment
            else:
                category = None
            
            # Search for attractions using location name directly
            results = self.places_service.search_places(
                destination, category, 15000, 5
            )
            
            if results and not results.startswith("Error") and not results.startswith("No places"):
                # Parse the first result
                lines = results.split('\n')
                for line in lines:
                    if line.strip() and '. ' in line and not line.startswith('Found'):
                        name = line.split('. ', 1)[1].split(' (')[0] if ' (' in line else line.split('. ', 1)[1]
                        return {
                            "name": name,
                            "time_slot": time_slot,
                            "category": category or "general",
                            "weather_suitable": weather
                        }
            
            return None
            
        except Exception:
            return None
    
    def _format_activity_suggestions(self, attractions: str, weather: str, duration_hours: int) -> str:
        """
        Format activity suggestions with context

        :param attractions: attractions string
        :param weather: weather condition
        :param duration_hours: planned duration
        :return: formatted activity suggestions
        """
        result = f"🎯 Activity Suggestions for {weather} weather ({duration_hours} hours):\n\n"
        result += attractions
        return result
    
    @staticmethod
    def _generate_packing_list(weather_data: Dict) -> List[str]:
        """
        Generate packing suggestions based on weather

        :param weather_data: weather forecast data
        :return: list of packing suggestions
        """
        packing_list = [
            "📱 Phone charger and adapters",
            "📄 Travel documents and copies",
            "💳 Credit cards and cash",
            "🧴 Personal hygiene items"
        ]
        
        # Add weather-specific items
        weather_conditions = set()
        for day_weather in weather_data.values():
            weather_conditions.add(day_weather.get('condition', 'cloudy'))
        
        if 'rainy' in weather_conditions:
            packing_list.extend(["☂️ Umbrella or rain jacket", "👟 Waterproof shoes"])
        
        if 'sunny' in weather_conditions:
            packing_list.extend(["🕶️ Sunglasses", "🧴 Sunscreen", "👒 Hat"])
        
        if 'cold' in weather_conditions or 'snowy' in weather_conditions:
            packing_list.extend(["🧥 Warm jacket", "🧤 Gloves", "🧣 Scarf"])
        
        return packing_list
    
    def _format_complete_trip_plan(self, trip_data: Dict, daily_plans: List[Dict], accommodation_data: Dict, packing_list: List[str]) -> str:
        """
        Format the complete trip plan into a readable string

        :param trip_data: trip information dictionary
        :param daily_plans: list of daily plan dictionaries
        :param accommodation_data: accommodation information
        :param packing_list: list of packing suggestions
        :return: formatted complete trip plan
        """
        result = f"🌟 Complete Trip Plan for {trip_data['destination']}\n"
        result += f"📅 {trip_data['start_date']} to {trip_data['end_date']}\n"
        result += f"👥 Group size: {trip_data['group_size']}\n"
        result += f"💰 Budget: {trip_data['budget']}\n\n"
        
        # Daily itineraries
        result += "📋 Daily Itineraries:\n\n"
        for day_plan in daily_plans:
            result += f"Day {day_plan['day']} - {day_plan['date']} (Weather: {day_plan['weather']})\n"
            for activity in day_plan['activities']:
                result += f"  • {activity['time_slot'].title()}: {activity['name']} ({activity['category']})\n"
            result += "\n"
        
        # Accommodations
        if accommodation_data.get('accommodations'):
            result += "🏨 Accommodation Options:\n"
            result += accommodation_data['accommodations']
            result += "\n\n"
        
        # Packing list
        result += "🎒 Packing Checklist:\n"
        for item in packing_list:
            result += f"  {item}\n"
        
        return result 
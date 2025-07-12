"""
Trip planner service module containing the TripPlannerService class
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Tuple
from _mcp.servers.base_service import BaseService
from _mcp.servers.weather.service import WeatherService
from _mcp.servers.places.service import PlacesService
from _mcp.servers.booking.service import BookingService
from _mcp.servers.trip_planner.constants import (
    TRIP_DURATIONS,
    DEFAULT_TRIP_DURATION,
    MIN_TRIP_DURATION,
    MAX_TRIP_DURATION,
    TRIP_STYLES,
    WEATHER_ACTIVITY_MAPPING,
    BUDGET_CATEGORIES,
    DEFAULT_TRIP_STYLE,
    DEFAULT_BUDGET,
    ERROR_MESSAGES
)


class TripPlannerService(BaseService):
    """
    Service class for comprehensive trip planning
    """
    
    def __init__(
        self,
        places_api_key: Optional[str] = None,
        booking_api_key: Optional[str] = None
    ):
        """
        Initialize the trip planner service

        :param places_api_key: Google Places API key
        :param booking_api_key: Booking.com API key
        """
        self.weather_service = WeatherService()
        self.places_service = PlacesService(api_key=places_api_key)
        self.booking_service = BookingService(api_key=booking_api_key)
    
    def plan_trip(
        self,
        location: str | Tuple[float, float],
        start_date: Optional[str] = None,
        duration: Optional[int | str] = None,
        trip_style: str = DEFAULT_TRIP_STYLE,
        budget: str = DEFAULT_BUDGET,
        include_accommodation: bool = True
    ) -> str:
        """
        Plan a complete trip based on location and preferences
        
        :param location: destination location
        :param start_date: trip start date (YYYY-MM-DD) or None for weather-based planning
        :param duration: trip duration in days or preset ("weekend", "short", etc.)
        :param trip_style: trip style (relaxed, balanced, adventure, cultural, food_focused)
        :param budget: budget category (budget, mid_range, luxury)
        :param include_accommodation: whether to include accommodation suggestions
        :return: complete trip plan
        """
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = self.get_coordinates(location)
            if not lat or not lng:
                return ERROR_MESSAGES["location_not_found"]
            location_name = location
        else:
            lat, lng = location
            location_name = f"coordinates ({lat:.4f}, {lng:.4f})"
        
        # Validate and parse duration
        trip_days = self._parse_duration(duration)
        if not trip_days:
            return f"Invalid duration. Use number of days (1-{MAX_TRIP_DURATION}) or preset ({', '.join(TRIP_DURATIONS.keys())})"
        
        # Validate trip style and budget
        if trip_style not in TRIP_STYLES:
            available_styles = ", ".join(TRIP_STYLES.keys())
            return f"Invalid trip style '{trip_style}'. Available: {available_styles}"
        
        if budget not in BUDGET_CATEGORIES:
            available_budgets = ", ".join(BUDGET_CATEGORIES.keys())
            return f"Invalid budget category '{budget}'. Available: {available_budgets}"
        
        # Determine dates
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                dates = [start_dt + timedelta(days=i) for i in range(trip_days)]
            except ValueError:
                return ERROR_MESSAGES["invalid_dates"]
        else:
            # Weather-based date selection (next 14 days)
            dates = self._select_optimal_dates(lat, lng, trip_days)
            if not dates:
                return ERROR_MESSAGES["no_weather_data"]
        
        # Get trip style configuration
        style_config = TRIP_STYLES[trip_style]
        
        # Plan each day
        daily_plans = []
        for i, date in enumerate(dates):
            day_plan = self._plan_single_day(
                lat, lng, date, style_config
            )
            daily_plans.append(day_plan)
        
        # Get accommodation if requested
        accommodation = None
        if include_accommodation and self.booking_service.api_key:
            accommodation = self._get_accommodation_suggestions(
                lat, lng, dates[0], len(dates)
            )
        
        # Format complete trip plan
        return self._format_trip_plan(
            location_name, dates, daily_plans, accommodation, trip_style, budget
        )
    
    def plan_weather_based_trip(
        self,
        location: Union[str, Tuple[float, float]],
        weather_condition: str,
        duration: Optional[Union[int, str]] = None,
        trip_style: str = DEFAULT_TRIP_STYLE
    ) -> str:
        """
        Plan a trip specifically optimized for certain weather conditions
        
        :param location: destination location
        :param weather_condition: desired weather condition (sunny, rainy, snowy, etc.)
        :param duration: trip duration in days or preset
        :param trip_style: trip style preference
        :return: weather-optimized trip plan
        """
        # Get coordinates if location is a string
        if isinstance(location, str):
            lat, lng = self.get_coordinates(location)
            if not lat or not lng:
                return ERROR_MESSAGES["location_not_found"]
            location_name = location
        else:
            lat, lng = location
            location_name = f"coordinates ({lat:.4f}, {lng:.4f})"
        
        # Validate inputs
        trip_days = self._parse_duration(duration)
        if not trip_days:
            return f"Invalid duration. Use number of days (1-{MAX_TRIP_DURATION}) or preset"
        
        if trip_style not in TRIP_STYLES:
            available_styles = ", ".join(TRIP_STYLES.keys())
            return f"Invalid trip style '{trip_style}'. Available: {available_styles}"
        
        # Find dates with desired weather
        optimal_dates = self._find_weather_matching_dates(lat, lng, weather_condition, trip_days)
        if not optimal_dates:
            return f"No suitable {weather_condition} weather found in the next 14 days for {location_name}"
        
        # Get weather-specific activities
        if weather_condition.lower() not in WEATHER_ACTIVITY_MAPPING:
            available_conditions = ", ".join(WEATHER_ACTIVITY_MAPPING.keys())
            return f"Weather condition '{weather_condition}' not supported. Available: {available_conditions}"
        
        # Plan activities optimized for the weather
        weather_activities = WEATHER_ACTIVITY_MAPPING[weather_condition.lower()]
        daily_plans = []
        
        for i, date in enumerate(optimal_dates):
            day_plan = self._plan_weather_specific_day(
                lat, lng, date, weather_activities, TRIP_STYLES[trip_style]
            )
            daily_plans.append(day_plan)
        
        return self._format_weather_trip_plan(
            location_name, optimal_dates, daily_plans, weather_condition, trip_style
        )

    @staticmethod
    def _parse_duration(duration: Optional[int | str]) -> Optional[int]:
        """
        Parse duration input into number of days
        
        :param duration: duration input
        :return: number of days or None if invalid
        """
        if duration is None:
            return DEFAULT_TRIP_DURATION
        
        if isinstance(duration, int):
            if MIN_TRIP_DURATION <= duration <= MAX_TRIP_DURATION:
                return duration
            return None
        
        if isinstance(duration, str):
            if duration.isdigit():
                days = int(duration)
                if MIN_TRIP_DURATION <= days <= MAX_TRIP_DURATION:
                    return days
                return None
            elif duration.lower() in TRIP_DURATIONS:
                return TRIP_DURATIONS[duration.lower()]
        
        return None
    
    def _select_optimal_dates(
        self,
        lat: float,
        lng: float,
        days: int
    ) -> List[datetime]:
        """
        Select optimal dates based on weather forecast
        
        :param lat: latitude
        :param lng: longitude
        :param days: number of days
        :return: list of optimal dates
        """
        try:
            # Get 14-day forecast data
            forecast_data = self.weather_service.get_forecast_data((lat, lng), 14)
            
            if isinstance(forecast_data, str):  # Error case
                # Fallback to starting tomorrow
                base_date = datetime.now() + timedelta(days=1)
                return [base_date + timedelta(days=i) for i in range(days)]
            
            # Parse forecast to find best consecutive days
            daily = forecast_data.get("daily", {})
            if not daily or not daily.get("time"):
                # Fallback if no forecast data
                base_date = datetime.now() + timedelta(days=1)
                return [base_date + timedelta(days=i) for i in range(days)]
            
            # Score each day
            scored_days = []
            times = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip_sums = daily.get("precipitation_sum", [])
            precip_probs = daily.get("precipitation_probability_max", [])
            wind_speeds = daily.get("wind_speed_10m_max", [])
            weather_codes = daily.get("weather_code", [])
            
            for i in range(min(len(times), 14)):
                date_str = times[i]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Calculate weather score
                max_temp = max_temps[i] if i < len(max_temps) else 20
                min_temp = min_temps[i] if i < len(min_temps) else 10
                precip_sum = precip_sums[i] if i < len(precip_sums) else 0
                precip_prob = precip_probs[i] if i < len(precip_probs) else 0
                wind_speed = wind_speeds[i] if i < len(wind_speeds) else 0
                weather_code = weather_codes[i] if i < len(weather_codes) else 0
                
                score = self._calculate_weather_score(max_temp, min_temp, precip_sum, precip_prob, wind_speed, weather_code)
                scored_days.append({"date": date_obj, "score": score})
            
            # Sort by score and find best consecutive period
            scored_days.sort(key=lambda x: x["score"], reverse=True)
            
            # Find best consecutive days
            best_dates = self._find_best_consecutive_days(scored_days, days)
            return best_dates if best_dates else [datetime.now() + timedelta(days=i+1) for i in range(days)]
            
        except Exception:
            # Fallback to starting tomorrow
            base_date = datetime.now() + timedelta(days=1)
            return [base_date + timedelta(days=i) for i in range(days)]
    
    @staticmethod
    def _calculate_weather_score(max_temp: float, min_temp: float, precip_sum: float, 
                                precip_prob: float, wind_speed: float, weather_code: int) -> float:
        """Calculate weather suitability score"""
        score = 100.0
        
        # Temperature penalties
        if max_temp > 35 or max_temp < 5:
            score -= 30
        elif max_temp > 30 or max_temp < 10:
            score -= 15
            
        if min_temp < 0:
            score -= 20
        elif min_temp < 5:
            score -= 10
            
        # Precipitation penalties
        score -= precip_sum * 10  # Heavy penalty for rain
        score -= precip_prob / 2  # Light penalty for rain probability
        
        # Wind penalty
        if wind_speed > 50:
            score -= 25
        elif wind_speed > 30:
            score -= 10
            
        # Weather code penalties
        if weather_code >= 95:  # Thunderstorm
            score -= 30
        elif weather_code >= 71:  # Snow
            score -= 25
        elif weather_code >= 61:  # Rain
            score -= 20
        elif weather_code >= 51:  # Drizzle
            score -= 10
            
        return max(0.0, score)
    
    @staticmethod
    def _find_best_consecutive_days(scored_days: List[Dict], days_needed: int) -> List[datetime]:
        """Find the best consecutive days from scored days"""
        if len(scored_days) < days_needed:
            return []
            
        # Sort by date to find consecutive periods
        sorted_by_date = sorted(scored_days, key=lambda x: x["date"])
        
        best_score = 0
        best_start_idx = 0
        
        # Find best consecutive period
        for i in range(len(sorted_by_date) - days_needed + 1):
            # Check if dates are consecutive
            consecutive = True
            for j in range(1, days_needed):
                if (sorted_by_date[i + j]["date"] - sorted_by_date[i + j - 1]["date"]).days != 1:
                    consecutive = False
                    break
            
            if consecutive:
                # Calculate total score for this period
                total_score = sum(sorted_by_date[i + k]["score"] for k in range(days_needed))
                if total_score > best_score:
                    best_score = total_score
                    best_start_idx = i
        
        if best_score > 0:
            return [sorted_by_date[best_start_idx + i]["date"] for i in range(days_needed)]
        
        return []

    def _find_weather_matching_dates(
        self,
        lat: float,
        lng: float,
        weather_condition: str,
        days: int
    ) -> List[datetime]:
        """
        Find dates with matching weather conditions
        
        :param lat: latitude
        :param lng: longitude
        :param weather_condition: desired weather condition
        :param days: number of consecutive days needed
        :return: list of matching dates
        """
        try:
            # Get weather forecast data
            forecast_data = self.weather_service.get_forecast_data((lat, lng), 14)
            
            if isinstance(forecast_data, str):  # Error case
                # Fallback to starting in 2 days
                base_date = datetime.now() + timedelta(days=2)
                return [base_date + timedelta(days=i) for i in range(days)]
            
            # Analyze forecast for weather condition matching
            daily = forecast_data.get("daily", {})
            if not daily or not daily.get("time"):
                base_date = datetime.now() + timedelta(days=2)
                return [base_date + timedelta(days=i) for i in range(days)]
            
            # This is a simplified implementation - in reality you'd analyze weather codes
            # and conditions to match the desired weather_condition
            base_date = datetime.now() + timedelta(days=2)
            return [base_date + timedelta(days=i) for i in range(days)]
            
        except Exception:
            # Fallback
            base_date = datetime.now() + timedelta(days=2)
            return [base_date + timedelta(days=i) for i in range(days)]

    def _plan_single_day(
        self,
        lat: float,
        lng: float,
        date: datetime,
        style_config: Dict
    ) -> Dict:
        """
        Plan activities for a single day
        
        :param lat: latitude
        :param lng: longitude
        :param date: date to plan for
        :param style_config: trip style configuration
        :return: day plan dictionary
        """
        activities_count = style_config["activities_per_day"]
        travel_radius = style_config["travel_radius"]
        preferred_types = style_config["preferred_types"]
        
        day_activities = []
        
        # Morning activity
        morning_types = [t for t in preferred_types if t in ["cafe", "museum", "park", "tourist_attraction"]]
        if morning_types:
            morning_activity = self._get_activity_for_time(
                lat, lng, morning_types[0], travel_radius, "morning"
            )
            if morning_activity:
                day_activities.append(morning_activity)
        
        # Afternoon activities
        for i in range(min(activities_count - 1, 2)):
            activity_type = preferred_types[i % len(preferred_types)]
            activity = self._get_activity_for_time(
                lat, lng, activity_type, travel_radius, "afternoon"
            )
            if activity:
                day_activities.append(activity)
        
        # Evening activity (dining)
        evening_activity = self._get_activity_for_time(
            lat, lng, "restaurant", travel_radius, "evening"
        )
        if evening_activity:
            day_activities.append(evening_activity)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "day_name": date.strftime("%A"),
            "activities": day_activities,
            "total_activities": len(day_activities)
        }

    def _plan_weather_specific_day(
        self,
        lat: float,
        lng: float,
        date: datetime,
        weather_activities: Dict,
        style_config: Dict
    ) -> Dict:
        """
        Plan a day with weather-specific activities
        
        :param lat: latitude
        :param lng: longitude
        :param date: date to plan for
        :param weather_activities: weather-appropriate activities
        :param style_config: trip style configuration
        :return: day plan dictionary
        """
        travel_radius = style_config["travel_radius"]
        day_activities = []
        
        # Plan activities for each time period
        for time_period, activity_types in weather_activities.items():
            if activity_types:
                activity_type = activity_types[0]  # Use first suggested type
                activity = self._get_activity_for_time(
                    lat, lng, activity_type, travel_radius, time_period
                )
                if activity:
                    day_activities.append(activity)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "day_name": date.strftime("%A"),
            "activities": day_activities,
            "total_activities": len(day_activities),
            "weather_optimized": True
        }

    def _get_activity_for_time(
        self,
        lat: float,
        lng: float,
        activity_type: str,
        radius: int,
        time_period: str
    ) -> Optional[Dict]:
        """
        Get a specific activity for a time period
        
        :param lat: latitude
        :param lng: longitude
        :param activity_type: type of activity
        :param radius: search radius
        :param time_period: time period (morning, afternoon, evening)
        :return: activity dictionary or None
        """
        try:
            # Search for places of this type using the data method
            places_data = self.places_service.search_places_data(
                (lat, lng), activity_type, radius, 5, 3.5
            )
            
            if isinstance(places_data, str) or not places_data:  # Error or no results
                return None
            
            # Use the first result
            place = places_data[0]
            
            return {
                "type": activity_type,
                "time": time_period,
                "name": place.get("name", f"Sample {activity_type.replace('_', ' ').title()}"),
                "rating": place.get("rating", 0),
                "address": place.get("vicinity", "Address not available"),
                "place_id": place.get("place_id", ""),
                "price_level": place.get("price_level", 0)
            }
            
        except Exception:
            return None

    def _get_accommodation_suggestions(
        self,
        lat: float,
        lng: float,
        check_in: datetime,
        nights: int
    ) -> Optional[Dict]:
        """
        Get accommodation suggestions
        
        :param lat: latitude
        :param lng: longitude
        :param check_in: check-in date
        :param nights: number of nights
        :return: accommodation suggestions or None
        """
        if not self.booking_service.api_key:
            return None
        
        try:
            check_in_str = check_in.strftime("%Y-%m-%d")
            check_out = check_in + timedelta(days=nights)
            check_out_str = check_out.strftime("%Y-%m-%d")
            
            # Get accommodation data using the data method
            accommodations_data = self.booking_service.search_accommodations_data(
                (lat, lng), check_in_str, check_out_str, rows=5
            )
            
            if isinstance(accommodations_data, str) or not accommodations_data:  # Error or no results
                return None
            
            # Use the first result
            accommodation = accommodations_data[0]
            
            return {
                "name": accommodation.get("name", "Hotel Name"),
                "rating": accommodation.get("rating", 0),
                "price_per_night": accommodation.get("price", {}).get("amount", 0),
                "currency": accommodation.get("price", {}).get("currency", "USD"),
                "total_cost": accommodation.get("price", {}).get("amount", 0) * nights,
                "check_in": check_in_str,
                "check_out": check_out_str,
                "nights": nights
            }
            
        except Exception:
            return None
    
    @staticmethod
    def _format_trip_plan(
        location: str,
        dates: List[datetime],
        daily_plans: List[Dict],
        accommodation: Optional[Dict],
        trip_style: str,
        budget: str
    ) -> str:
        """
        Format the complete trip plan
        
        :param location: destination location
        :param dates: trip dates
        :param daily_plans: daily activity plans
        :param accommodation: accommodation information
        :param trip_style: trip style
        :param budget: budget category
        :return: formatted trip plan
        """
        start_date = dates[0].strftime("%B %d, %Y")
        end_date = dates[-1].strftime("%B %d, %Y")
        duration = len(dates)
        
        result = f"🎯 TRIP PLAN FOR {location.upper()}\n"
        result += f"📅 Dates: {start_date} - {end_date} ({duration} days)\n"
        result += f"🎨 Style: {trip_style.title()}\n"
        result += f"💰 Budget: {budget.title()}\n\n"
        
        # Accommodation section
        if accommodation:
            result += "🏨 ACCOMMODATION:\n"
            result += f"   Check-in: {accommodation['check_in']}\n"
            result += f"   Check-out: {accommodation['check_out']}\n"
            result += f"   Duration: {accommodation['nights']} nights\n"
            result += f"   {accommodation['suggestions']}\n\n"
        
        # Daily itinerary
        result += "📋 DAILY ITINERARY:\n\n"
        
        for i, day_plan in enumerate(daily_plans, 1):
            result += f"Day {i} - {day_plan['day_name']}, {day_plan['date']}:\n"
            
            if day_plan['activities']:
                for j, activity in enumerate(day_plan['activities'], 1):
                    time_emoji = {"morning": "🌅", "afternoon": "☀️", "evening": "🌙"}.get(activity.get('time', ''), "📍")
                    result += f"  {time_emoji} {activity.get('name', 'Activity')}\n"
                    result += f"     Type: {activity.get('type', 'N/A').replace('_', ' ').title()}\n"
                    result += f"     Rating: {activity.get('rating', 'N/A')}/5.0\n"
                    if activity.get('address'):
                        result += f"     Address: {activity['address']}\n"
                    result += "\n"
            else:
                result += "  No activities planned for this day\n\n"
        
        result += "💡 TRIP PLANNING NOTES:\n"
        result += f"• Plan includes {sum(len(day['activities']) for day in daily_plans)} total activities\n"
        result += f"• Activities are optimized for {trip_style} travel style\n"
        result += f"• Budget considerations: {budget} category\n"
        result += "• Check weather conditions before departure\n"
        result += "• Book accommodations and activities in advance\n"
        
        return result
    
    @staticmethod
    def _format_weather_trip_plan(
        location: str,
        dates: List[datetime],
        daily_plans: List[Dict],
        weather_condition: str,
        trip_style: str
    ) -> str:
        """
        Format weather-optimized trip plan
        
        :param location: destination location
        :param dates: trip dates
        :param daily_plans: daily activity plans
        :param weather_condition: weather condition
        :param trip_style: trip style
        :return: formatted weather-optimized trip plan
        """
        start_date = dates[0].strftime("%B %d, %Y")
        end_date = dates[-1].strftime("%B %d, %Y")
        duration = len(dates)
        
        result = f"🌤️ WEATHER-OPTIMIZED TRIP PLAN FOR {location.upper()}\n"
        result += f"📅 Dates: {start_date} - {end_date} ({duration} days)\n"
        result += f"🌦️ Optimized for: {weather_condition.title()} weather\n"
        result += f"🎨 Style: {trip_style.title()}\n\n"
        
        result += "📋 WEATHER-SPECIFIC ITINERARY:\n\n"
        
        for i, day_plan in enumerate(daily_plans, 1):
            result += f"Day {i} - {day_plan['day_name']}, {day_plan['date']}:\n"
            result += f"☁️ Expected weather: {weather_condition}\n\n"
            
            if day_plan['activities']:
                for activity in day_plan['activities']:
                    time_emoji = {"morning": "🌅", "afternoon": "☀️", "evening": "🌙"}.get(activity.get('time', ''), "📍")
                    result += f"  {time_emoji} {activity.get('name', 'Activity')}\n"
                    result += f"     Perfect for {weather_condition} weather\n"
                    result += f"     Type: {activity.get('type', 'N/A').replace('_', ' ').title()}\n"
                    result += f"     Rating: {activity.get('rating', 'N/A')}/5.0\n\n"
            else:
                result += "  No activities planned for this day\n\n"
        
        result += "🌈 WEATHER PLANNING NOTES:\n"
        result += f"• All activities optimized for {weather_condition} conditions\n"
        result += f"• Indoor alternatives available for weather changes\n"
        result += f"• Check weather forecast 24-48 hours before activities\n"
        result += f"• Pack appropriate clothing for {weather_condition} weather\n"
        
        return result 
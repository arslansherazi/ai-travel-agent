"""
Weather service module containing the WeatherService utils
"""

from typing import List, Dict
from mcp.servers.base_service import BaseService
from mcp.servers.weather.constants import (
    WEATHER_API_BASE_URL,
    CURRENT_WEATHER_PARAMS,
    DAILY_FORECAST_PARAMS,
    DETAILED_DAILY_PARAMS,
    HOURLY_PARAMS,
    TEMPERATURE_THRESHOLDS,
    WIND_THRESHOLDS,
    PRECIPITATION_THRESHOLDS,
    WEATHER_CODE_PENALTIES,
    SEVERE_WEATHER_CODES,
    DEFAULT_FORECAST_DAYS,
    MAX_DISPLAY_DAYS
)


class WeatherService(BaseService):
    """
    Service class for weather-related operations
    """
    def get_current_weather(self, location: str) -> str:
        """
        Get current weather and forecast for a location
        
        :param location: location to check
        :return: weather report string
        """
        lat, lon = self.get_coordinates(location)
        if not lat or not lon:
            return f"Could not find coordinates for {location}"
        
        # Get current weather data
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": CURRENT_WEATHER_PARAMS,
            "daily": DAILY_FORECAST_PARAMS,
            "timezone": "auto"
        }
        
        data = self.make_api_request(WEATHER_API_BASE_URL, params=params)
        
        if data.get("error"):
            return self.format_error_response(data["error"], "weather data fetch")
        
        return WeatherService._format_weather_report(location, data)

    def get_trip_recommendations(self, location: str) -> str:
        """
        Find the best days for a trip based on weather conditions
        
        :param location: location to check
        :return: recommended days for a trip
        """
        lat, lon = self.get_coordinates(location)
        if not lat or not lon:
            return f"Could not find coordinates for {location}"
        
        # Get 7-days forecast
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": DETAILED_DAILY_PARAMS,
            "timezone": "auto"
        }
        
        data = self.make_api_request(WEATHER_API_BASE_URL, params=params)
        
        if data.get("error"):
            return self.format_error_response(data["error"], "weather forecast data fetch")
        
        daily = data.get("daily", {})
        
        # Score and rank days
        days = WeatherService._score_weather_days(daily)
        return WeatherService._format_trip_recommendations(location, days)

    def get_severe_weather_events(self, location: str) -> str:
        """
        Get severe weather events for a location
        
        :param location: location to check
        :return: list of weather events
        """
        lat, lon = self.get_coordinates(location)
        if not lat or not lon:
            return f"Could not find coordinates for {location}"
        
        # Get weather data with hourly and daily forecast
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": HOURLY_PARAMS,
            "daily": ["weather_code", "precipitation_probability_max"],
            "forecast_days": DEFAULT_FORECAST_DAYS,
            "timezone": "auto"
        }
        
        data = self.make_api_request(WEATHER_API_BASE_URL, params=params)
        
        if data.get("error"):
            return self.format_error_response(data["error"], "weather events data fetch")
        
        hourly = data.get("hourly", {})
        
        # Detect severe weather events
        events = WeatherService._detect_severe_weather_events(hourly)
        return WeatherService._format_weather_events(location, events)

    @staticmethod
    def _format_weather_report(location: str, data: Dict) -> str:
        """
        Format weather data into a readable report
        
        :param location: location name
        :param data: weather data from API
        :return: formatted weather report
        """
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        report = f"Weather for {location}:\n"
        report += f"Current Temperature: {current.get("temperature_2m", "N/A")} {data.get("current_units", {}).get("temperature_2m", "°C")}\n"
        report += f"Feels Like: {current.get("apparent_temperature", "N/A")} {data.get("current_units", {}).get("apparent_temperature", "°C")}\n"
        report += f"Humidity: {current.get("relative_humidity_2m", "N/A")} {data.get("current_units", {}).get("relative_humidity_2m", "%")}\n"
        report += f"Precipitation: {current.get("precipitation", "N/A")} {data.get("current_units", {}).get("precipitation", "mm")}\n"
        report += f"Wind Speed: {current.get("wind_speed_10m", "N/A")} {data.get("current_units", {}).get("wind_speed_10m", "km/h")}\n"
        report += f"Wind Direction: {current.get("wind_direction_10m", "N/A")} {data.get("current_units", {}).get("wind_direction_10m", "°")}\n\n"
        
        # Add forecast for next few days
        report += "Forecast for the next days:\n"
        for i in range(min(MAX_DISPLAY_DAYS, len(daily.get("time", [])))):
            date = daily.get("time", [])[i]
            max_temp = daily.get("temperature_2m_max", [])[i]
            min_temp = daily.get("temperature_2m_min", [])[i]
            precip = daily.get("precipitation_sum", [])[i]
            wind = daily.get("wind_speed_10m_max", [])[i]
            
            report += f"{date}: {min_temp}-{max_temp} {data.get("daily_units", {}).get("temperature_2m_max", "°C")}, "
            report += f"Precipitation: {precip} {data.get("daily_units", {}).get("precipitation_sum", "mm")}, "
            report += f"Wind: {wind} {data.get("daily_units", {}).get("wind_speed_10m_max", "km/h")}\n"
        
        return report
    
    @staticmethod
    def _score_weather_days(daily: Dict) -> List[Dict]:
        """
        Score weather days based on conditions
        
        :param daily: daily weather data
        :return: list of scored days
        """
        days = []
        for i in range(len(daily.get("time", []))):
            date = daily.get("time", [])[i]
            max_temp = daily.get("temperature_2m_max", [])[i]
            min_temp = daily.get("temperature_2m_min", [])[i]
            precip_sum = daily.get("precipitation_sum", [])[i]
            precip_prob = daily.get("precipitation_probability_max", [])[i]
            wind = daily.get("wind_speed_10m_max", [])[i]
            weather_code = daily.get("weather_code", [])[i]
            
            # Calculate score
            score = WeatherService._calculate_day_score(max_temp, min_temp, precip_sum, precip_prob, wind, weather_code)
            days.append({"date": date, "score": score, "max_temp": max_temp, "precip": precip_sum})
        
        # Sort by score (highest first)
        days.sort(key=lambda x: x["score"], reverse=True)
        return days

    @staticmethod
    def _calculate_day_score(
            max_temp: float, min_temp: float, precip_sum: float, precip_prob: float, wind: float, weather_code: int
    ) -> int:
        """
        Calculate a score for a day based on weather conditions
        
        :param max_temp: maximum temperature
        :param min_temp: minimum temperature
        :param precip_sum: precipitation sum
        :param precip_prob: precipitation probability
        :param wind: wind speed
        :param weather_code: weather code
        :return: weather score (0-100)
        """
        score = 100.0  # Use float for calculations
        
        # Temperature penalty
        if max_temp > TEMPERATURE_THRESHOLDS["extreme"]["max"] or min_temp < TEMPERATURE_THRESHOLDS["extreme"]["min"]:
            score -= TEMPERATURE_THRESHOLDS["extreme"]["penalty"]
        elif max_temp > TEMPERATURE_THRESHOLDS["moderate"]["max"] or min_temp < TEMPERATURE_THRESHOLDS["moderate"]["min"]:
            score -= TEMPERATURE_THRESHOLDS["moderate"]["penalty"]
        
        # Precipitation penalty
        score -= min(50.0, precip_sum * 10.0)  # Up to 50 points off for heavy rain
        score -= min(30.0, precip_prob / 2.0)  # Up to 30 points off for high probability
        
        # Wind penalty
        if wind > WIND_THRESHOLDS["severe"]["speed"]:
            score -= WIND_THRESHOLDS["severe"]["penalty"]
        elif wind > WIND_THRESHOLDS["moderate"]["speed"]:
            score -= WIND_THRESHOLDS["moderate"]["penalty"]
        
        # Weather code penalty
        if weather_code >= WEATHER_CODE_PENALTIES["snow"]["min"]:
            score -= WEATHER_CODE_PENALTIES["snow"]["penalty"]
        elif weather_code >= WEATHER_CODE_PENALTIES["rain"]["min"]:
            score -= WEATHER_CODE_PENALTIES["rain"]["penalty"]
        elif weather_code >= WEATHER_CODE_PENALTIES["drizzle"]["min"]:
            score -= WEATHER_CODE_PENALTIES["drizzle"]["penalty"]
        
        return int(max(0.0, score))  # Convert back to int for return

    @staticmethod
    def _format_trip_recommendations(location: str, days: List[Dict]) -> str:
        """
        Format trip recommendations based on scored days
        
        :param location: location name
        :param days: list of scored days
        :return: formatted recommendations
        """
        result = f"Best days for a trip to {location} in the next week:\n"
        for i, day in enumerate(days[:MAX_DISPLAY_DAYS]):
            result += f"{i+1}. {day["date"]}: Score {day["score"]}/100, Max temp: {day["max_temp"]}°C, Precipitation: {day["precip"]}mm\n"
        
        result += "\nDays to avoid:\n"
        for day in days[-2:]:
            result += f"{day["date"]}: Score {day["score"]}/100, Max temp: {day["max_temp"]}°C, Precipitation: {day["precip"]}mm\n"
        
        return result

    @staticmethod
    def _detect_severe_weather_events(hourly: Dict) -> List[Dict]:
        """
        Detect severe weather events from hourly data
        
        :param hourly: hourly weather data
        :return: list of weather events
        """
        events = []
        
        # Check hourly data for events
        for i in range(len(hourly.get("time", []))):
            time = hourly.get("time", [])[i]
            precip = hourly.get("precipitation", [])[i]
            weather_code = hourly.get("weather_code", [])[i]
            wind_speed = hourly.get("wind_speed_10m", [])[i]
            
            # Check for heavy rain
            if precip >= PRECIPITATION_THRESHOLDS["heavy_rain"]:
                events.append({"time": time, "event": "Heavy Rain", "value": f"{precip}mm/h"})
            
            # Check for strong winds
            if wind_speed >= PRECIPITATION_THRESHOLDS["strong_winds"]:
                events.append({"time": time, "event": "Strong Winds", "value": f"{wind_speed}km/h"})
            
            # Check for severe weather codes
            if weather_code >= SEVERE_WEATHER_CODES["thunderstorm"]:
                events.append({"time": time, "event": "Thunderstorm", "value": f"Weather code {weather_code}"})
            elif weather_code >= SEVERE_WEATHER_CODES["snow"]:
                events.append({"time": time, "event": "Snow", "value": f"Weather code {weather_code}"})
        
        return events

    @staticmethod
    def _format_weather_events(location: str, events: List[Dict]) -> str:
        """
        Format weather events into a readable report
        
        :param location: location name
        :param events: list of weather events
        :return: formatted events report
        """
        if not events:
            return f"No severe weather events predicted for {location} in the next {DEFAULT_FORECAST_DAYS} days."
        
        result = f"Severe weather events for {location} in the next {DEFAULT_FORECAST_DAYS} days:\n"
        
        # Group events by day for better readability
        events_by_day = {}
        for event in events:
            day = event["time"].split("T")[0]
            if day not in events_by_day:
                events_by_day[day] = []
            events_by_day[day].append(event)
        
        for day, day_events in events_by_day.items():
            result += f"\n{day}:\n"
            for event in day_events:
                time = event["time"].split("T")[1]
                result += f"  {time}: {event["event"]} - {event["value"]}\n"
        
        return result

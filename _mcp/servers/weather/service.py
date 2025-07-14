"""
Weather service module containing the WeatherService utils
"""

from typing import List, Dict, Optional
from _mcp.servers.base_service import BaseService
from _mcp.servers.weather.constants import (
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
            return f"Could not find coordinates for {location}. Check your location name."
        
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

    def get_forecast(self, location: str, days: int = DEFAULT_FORECAST_DAYS) -> str:
        """
        Get weather forecast for a location
        
        :param location: location to check
        :param days: number of days to forecast
        :return: weather forecast string
        """
        forecast_data = self.get_forecast_data(location, days)
        if isinstance(forecast_data, str):  # Error case
            return forecast_data
        
        return self._format_forecast_report(location, forecast_data, days)
    
    def get_forecast_data(self, location: str | tuple, days: int = DEFAULT_FORECAST_DAYS) -> Dict | str:
        """
        Get structured weather forecast data for use by other services
        
        :param location: location to check  
        :param days: number of days to forecast
        :return: structured weather data or error string
        """
        if isinstance(location, tuple):
            lat, lon = location
        else:
            lat, lon = self.get_coordinates(location)
            if not lat or not lon:
                return f"Could not find coordinates for {location}"
        
        # Get forecast data
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": DETAILED_DAILY_PARAMS,
            "forecast_days": min(days, 16),  # API limit
            "timezone": "auto"
        }
        
        data = self.make_api_request(WEATHER_API_BASE_URL, params=params)
        
        if data.get("error"):
            return self.format_error_response(data["error"], "weather forecast data fetch")
        
        return data

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
    def _format_forecast_report(location: str, data: Dict, days: int) -> str:
        """
        Format forecast data into a readable report
        
        :param location: location name
        :param data: weather data from API
        :param days: number of days
        :return: formatted forecast report
        """
        daily = data.get("daily", {})
        
        report = f"{days}-day weather forecast for {location}:\n\n"
        
        for i in range(min(days, len(daily.get("time", [])))):
            date = daily.get("time", [])[i]
            max_temp = daily.get("temperature_2m_max", [])[i]
            min_temp = daily.get("temperature_2m_min", [])[i]
            precip_sum = daily.get("precipitation_sum", [])[i]
            precip_prob = daily.get("precipitation_probability_max", [])[i]
            wind = daily.get("wind_speed_10m_max", [])[i]
            weather_code = daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0
            
            # Weather description based on code
            weather_desc = WeatherService._get_weather_description(weather_code)
            
            report += f"{date}:\n"
            report += f"  Temperature: {min_temp}°C - {max_temp}°C\n"
            report += f"  Weather: {weather_desc}\n"
            report += f"  Precipitation: {precip_sum}mm (Probability: {precip_prob}%)\n"
            report += f"  Wind: {wind} km/h\n\n"
        
        return report
    
    @staticmethod
    def _get_weather_description(weather_code: int) -> str:
        """
        Get weather description from weather code
        
        :param weather_code: WMO weather code
        :return: weather description
        """
        if weather_code == 0:
            return "Clear sky"
        elif weather_code in [1, 2, 3]:
            return "Partly cloudy"
        elif weather_code in [45, 48]:
            return "Foggy"
        elif weather_code in [51, 53, 55]:
            return "Drizzle"
        elif weather_code in [61, 63, 65]:
            return "Rain"
        elif weather_code in [71, 73, 75]:
            return "Snow"
        elif weather_code in [80, 81, 82]:
            return "Rain showers"
        elif weather_code in [95, 96, 99]:
            return "Thunderstorm"
        else:
            return "Unknown"
    
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
        score -= precip_sum * 10.0  # Heavy penalty for rain
        score -= precip_prob / 2.0  # Lighter penalty for rain probability
        
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
        
        return int(max(0.0, score))

    @staticmethod
    def _format_trip_recommendations(location: str, days: List[Dict]) -> str:
        """
        Format trip recommendations based on weather scores
        
        :param location: location name
        :param days: list of scored days
        :return: formatted trip recommendations
        """
        report = f"Best trip days for {location} (next 7 days):\n\n"
        
        for i, day in enumerate(days[:5], 1):  # Show top 5 days
            date = day["date"]
            score = day["score"]
            max_temp = day["max_temp"]
            precip = day["precip"]
            
            quality = "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
            
            report += f"{i}. {date} - {quality} (Score: {score}/100)\n"
            report += f"   Max Temperature: {max_temp}°C, Precipitation: {precip}mm\n\n"
        
        return report

    @staticmethod
    def _detect_severe_weather_events(hourly: Dict) -> List[Dict]:
        """
        Detect severe weather events from hourly data
        
        :param hourly: hourly weather data
        :return: list of weather events
        """
        events = []
        times = hourly.get("time", [])
        temperatures = hourly.get("temperature_2m", [])
        precipitation = hourly.get("precipitation", [])
        wind_speeds = hourly.get("wind_speed_10m", [])
        weather_codes = hourly.get("weather_code", [])
        
        for i in range(len(times)):
            time = times[i]
            temp = temperatures[i] if i < len(temperatures) else 0
            precip = precipitation[i] if i < len(precipitation) else 0
            wind_speed = wind_speeds[i] if i < len(wind_speeds) else 0
            weather_code = weather_codes[i] if i < len(weather_codes) else 0
            
            # Check for severe weather conditions
            if precip >= PRECIPITATION_THRESHOLDS["heavy_rain"]:
                events.append({"time": time, "type": "Heavy Rain", "value": f"{precip}mm"})
            
            if wind_speed >= PRECIPITATION_THRESHOLDS["strong_winds"]:
                events.append({"time": time, "type": "Strong Winds", "value": f"{wind_speed}km/h"})
            
            if weather_code >= SEVERE_WEATHER_CODES["thunderstorm"]:
                events.append({"time": time, "type": "Thunderstorm", "value": "Severe"})
            elif weather_code >= SEVERE_WEATHER_CODES["snow"]:
                events.append({"time": time, "type": "Snow", "value": "Heavy"})
        
        return events

    @staticmethod
    def _format_weather_events(location: str, events: List[Dict]) -> str:
        """
        Format weather events into a readable report
        
        :param location: location name
        :param events: list of weather events
        :return: formatted weather events report
        """
        if not events:
            return f"No severe weather events expected for {location} in the next {DEFAULT_FORECAST_DAYS} days."
        
        report = f"Severe weather events for {location}:\n\n"
        
        for event in events:
            time = event["time"]
            event_type = event["type"]
            value = event["value"]
            
            report += f"⚠️  {time}: {event_type} ({value})\n"
        
        return report

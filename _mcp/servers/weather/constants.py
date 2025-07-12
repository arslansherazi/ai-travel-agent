"""Weather service constants"""

# API URLs
WEATHER_API_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Weather Parameters
CURRENT_WEATHER_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m"
]

DAILY_FORECAST_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max"
]

DETAILED_DAILY_PARAMS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
    "weather_code"
]

HOURLY_PARAMS = [
    "temperature_2m",
    "precipitation",
    "weather_code",
    "wind_speed_10m"
]

# Weather Thresholds
TEMPERATURE_THRESHOLDS = {
    "extreme": {"min": 5, "max": 30, "penalty": 30},
    "moderate": {"min": 10, "max": 25, "penalty": 15},
    "ideal": {"min": 15, "max": 25}
}

WIND_THRESHOLDS = {
    "severe": {"speed": 40, "penalty": 25},
    "moderate": {"speed": 30, "penalty": 15}
}

PRECIPITATION_THRESHOLDS = {
    "heavy_rain": 5.0,  # mm/h
    "strong_winds": 40.0,  # km/h
}

# Weather Code Classifications
WEATHER_CODE_PENALTIES = {
    "snow": {"min": 70, "penalty": 40},
    "rain": {"min": 50, "penalty": 30},
    "drizzle": {"min": 30, "penalty": 20}
}

SEVERE_WEATHER_CODES = {
    "thunderstorm": 90,
    "snow": 70
}

# Forecast Settings
DEFAULT_FORECAST_DAYS = 3
MAX_DISPLAY_DAYS = 3 
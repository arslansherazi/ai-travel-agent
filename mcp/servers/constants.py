"""Shared constants across all servers"""

# Geocoding API URL (used by base service)
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Common HTTP timeouts
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 60

# Common pagination limits
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 10

# Distance calculations
EARTH_RADIUS_KM = 6371.0

# Common coordinate validation
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0

import enum

GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"

class RequestMethod(enum.Enum):
    GET = "GET"
    POST = "POST"

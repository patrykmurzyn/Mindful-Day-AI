from dataclasses import dataclass

@dataclass
class WeatherData:
    datetime: str          # Date and time
    temperature: float     # Temperature (important for drone flights)
    wind_speed: float      # Wind speed (crucial for drone flights)
    wind_gust: float       # Wind gusts (important for flying)
    visibility: float      # Visibility (important for recording and flying drones)
    cloud_cover: int       # Cloud cover (affects lighting during recording)
    humidity: int          # Humidity (affects air quality)
    pressure: float        # Pressure (important for drones)
    uv_index: float        # UV index (important for outdoor activities)
    us_epa_index: int      # Air quality index (US EPA)
    chance_of_rain: int    # Chance of rain (in percentage)
    chance_of_snow: int    # Chance of snow (in percentage)
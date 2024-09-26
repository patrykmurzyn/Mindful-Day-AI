import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from models.weather_model import WeatherData
from typing import List

WEATHER_API_URL = "http://api.weatherapi.com/v1"

class WeatherAPI:
    def __init__(self):
        """
        Initializes the WeatherAPI class and loads the API key.
        Raises an exception if the required environment variables are not set.
        """
        load_dotenv()
        self.api_key = os.getenv("WEATHERAPI_API_KEY")
        
        if not self.api_key:
            raise EnvironmentError("Missing WEATHERAPI_API_KEY in environment variables")

    def get_weather(self, city: str, date: str) -> List[WeatherData]:
        """
        Fetches weather data for a given city and date.

        Args:
            city (str): The city for which to fetch the weather.
            date (str): The date in "YYYY-MM-DD" format for which to fetch the weather.

        Returns:
            List[WeatherData]: A list of WeatherData objects representing the weather forecast for the day.
        """
        if not isinstance(date, str):
            raise ValueError(f"Expected date to be a string, got {type(date).__name__} instead.")
        if not WeatherAPI.is_date_valid(date):
            raise ValueError(f"Invalid date format: {date}. Expected format is YYYY-MM-DD.")

        params = {
            "key": self.api_key,
            "q": city,
            "dt": date,
            "days": 1,
            "aqi": "yes",
            "alerts": "yes"
        }

        response = self._make_api_request(params)
        return self._process_weather_data(response, city, date)


    @staticmethod
    def _make_api_request(params: dict) -> dict:
        """
        Makes a request to the weather API.

        Args:
            params (dict): Parameters for the API request.

        Returns:
            dict: The JSON response from the API.
        
        Raises:
            requests.HTTPError: If the request to the API fails.
        """
        response = requests.get(f"{WEATHER_API_URL}/forecast.json", params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _process_weather_data(data: dict, city: str, date: str) -> List[WeatherData]:
        """
        Processes raw weather data from the API response.

        Args:
            data (dict): The raw data returned by the API.
            city (str): The city for which the weather is being fetched.
            date (str): The date for which the weather is being fetched.

        Returns:
            List[WeatherData]: A list of WeatherData objects for the valid forecast hours.
        """
        if 'forecast' not in data or not data['forecast']['forecastday']:
            print(f"No forecast data available for {city} on {date}")
            return []

        weather_data = []
        for hour_data in data['forecast']['forecastday'][0]['hour']:
            hour = int(hour_data['time'].split(' ')[1].split(':')[0])
            if 8 <= hour <= 22:  # Only select hours between 8:00 and 22:00
                weather_data.append(WeatherAPI._create_weather_data(hour_data))

        return weather_data

    @staticmethod
    def _create_weather_data(hour_data: dict) -> WeatherData:
        """
        Creates a WeatherData object from raw API data for a specific hour.

        Args:
            hour_data (dict): The raw data for a specific hour.

        Returns:
            WeatherData: The created WeatherData object.
        """
        return WeatherData(
            datetime=hour_data['time'],
            temperature=hour_data['temp_c'],
            wind_speed=round(hour_data['wind_kph'] / 3.6, 1),
            wind_gust=round(hour_data['gust_kph'] / 3.6, 1),
            visibility=hour_data['vis_km'],
            cloud_cover=hour_data['cloud'],
            humidity=hour_data['humidity'],
            pressure=hour_data['pressure_mb'],
            uv_index=hour_data['uv'],
            us_epa_index=hour_data['air_quality']['us-epa-index'],
            chance_of_rain=hour_data.get('chance_of_rain', 0),
            chance_of_snow=hour_data.get('chance_of_snow', 0)
        )

    @staticmethod
    def is_date_valid(date_string: str) -> bool:
        """
        Validates if the date string is in the correct "YYYY-MM-DD" format.

        Args:
            date_string (str): The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

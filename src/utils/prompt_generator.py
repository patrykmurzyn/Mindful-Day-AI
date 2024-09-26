from typing import List

class PromptGenerator:
    def __init__(self, today: str, city: str, tasks: List, events: List, weather_data_list: List):
        self.today = today
        self.city = city
        self.tasks = tasks
        self.events = events
        self.weather_data_list = weather_data_list

    def _validate_data(self):
        if not self.weather_data_list:
            raise ValueError("Weather data list is empty.")

    def generate_prompt(self) -> str:
        self._validate_data()

        events_text = "\n".join([
                f"- {event.summary} from {event.start_time} to {event.end_time} (Description: {event.description})"
                for event in self.events
            ])

        tasks_text = "\n".join([
            f"- {task.title} (Notes: {task.notes}, Due: {task.due}, Status: {task.status})"
            for task in self.tasks
        ])

        weather_text = "\n".join([
            f"- {weather_data.datetime}: {weather_data.temperature}°C, Wind: {weather_data.wind_speed} km/h, "
            f"Gust: {weather_data.wind_gust} km/h, Visibility: {weather_data.visibility} km, "
            f"Cloud Cover: {weather_data.cloud_cover}%, Humidity: {weather_data.humidity}%, "
            f"Pressure: {weather_data.pressure} hPa, UV Index: {weather_data.uv_index}, "
            f"US EPA Index: {weather_data.us_epa_index}, Chance of Rain: {weather_data.chance_of_rain}%, "
            f"Chance of Snow: {weather_data.chance_of_snow}%"
            for weather_data in self.weather_data_list
        ])

        return f"""
            You are an advanced planning assistant. You will be provided with calendar events, tasks, and weather data for {self.today}. Based on this information, you need to generate a detailed day plan in JSON format, covering the time from 8:00 to 22:00.

            Here is what you will receive:
            1. `events`: 
            {events_text}

            2. `tasks`: 
            {tasks_text}

            3. `weather_data_list`: 
            {weather_text}

            4. `today`: {self.today}

            5. `city`: {self.city}

            Your task is to:
            - Generate a summary of the day's weather and highlight if it's a good day for outdoor activities.
            - Create a detailed plan of activities for the day, considering the events, tasks, and weather. Outdoor activities should be included if the weather is suitable.
            - Low-priority tasks should only be scheduled if the weather is not good for outdoor activities.
            - Recommend at least 5 short breaks throughout the day, focused on hydration by drinking a glass of water.
            - Include a daily 1 hour chess session and 1 hour of reading a book.
            - Provide one interesting fact about today, such as a historical event or an international celebration.

            Return the information in the following JSON format:

            {{
            "summary": "A brief overview of the weather and day.",
            "today_fact": "An interesting fact about today, such as a historical event or international celebration",
            "plan": {{
                "hours": {{
                    "8": "Description of the activity",
                    "9": "Description of the activity",
                    ...
                    "22": "Description of the activity"
                }}
            }},
            "break_recommendations": [
                {{
                "time": "Time of the break",
                "duration": "Duration of the break",
                "activity": "Recommended break activity, including drinking water"
                }},
                ...
            ]
            }}
        """
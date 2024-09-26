import os
from api.weather_api import WeatherAPI
from api.google_calendar_api import GoogleCalendarAPI
from api.google_tasks_api import GoogleTasksAPI
from api.genai_api import GenAIAPI
from api.gmail_api import GmailAPI
from datetime import datetime

def main():
    today = datetime.now().date()
    city = "Muszyna"

    calendar_api = GoogleCalendarAPI()
    events = calendar_api.get_events_for_day(today)
    print("Calendar data fetched successfully")

    tasks_api = GoogleTasksAPI()
    tasks = tasks_api.get_tasks()
    print("Tasks data fetched successfully")

    weather_api = WeatherAPI()
    weather_data_list = weather_api.get_weather(city, today.isoformat())
    print("Weather data fetched successfully")

    genai_api = GenAIAPI()
    response = genai_api.ai_quest(today, city, tasks, events, weather_data_list)
    print(response)

    formatted_date = today.strftime("%d-%m-%Y")
    gmail_api = GmailAPI()
    gmail_api.send_email(f"me@patrykmurzyn.com", f"Mindful Day AI - {formatted_date}", response)
    print("Email sent successfully")

if __name__ == "__main__":
    main()
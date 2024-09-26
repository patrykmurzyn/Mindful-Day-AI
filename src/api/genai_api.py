import os
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from utils.prompt_generator import PromptGenerator
from typing import List

class GenAIAPI:
    def __init__(self, api_key: str = None):
        """
        GenAIAPI constructor to initialize the Generative AI model.

        Args:
            api_key (str): API key for Google Generative AI. If not provided, it will be loaded from environment variables.
        
        Raises:
            ValueError: If the API key is not found.
        """
        self.api_key = api_key or os.getenv("GENAI_API_KEY")
        if not self.api_key:
            raise ValueError("GENAI_API_KEY not found in environment variables")

        self._configure_api()

    def _configure_api(self):
        """
        Configures the Generative AI model with the provided API key.
        """
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def ai_quest(self, today: str, city: str, tasks: List, events: List, weather_data_list: List) -> str:
        """
        Generates content using the Generative AI model based on the provided parameters.

        Args:
            today (str): The current date.
            city (str): The city for which the content is generated.
            tasks (List): A list of tasks.
            events (List): A list of events.
            weather_data_list (List): A list of weather data.

        Returns:
            str: The generated AI content.

        Raises:
            RuntimeError: If an error occurs while generating AI content.
        """
        prompt_generator = PromptGenerator(today, city, tasks, events, weather_data_list)
        prompt = prompt_generator.generate_prompt()
        print(prompt)
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            return response.text

        except GoogleAPIError as e:
            print(f"Błąd Google API: {e}")
            print(f"Kod błędu: {e.code}")
            print(f"Szczegóły błędu: {e.details}")
            raise RuntimeError("Failed to generate AI content") from e
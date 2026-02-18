import google.generativeai as genai
from app.core.settings import settings

class GoogleAIClient:
    def __init__(self):
        # Configure API key once
        genai.configure(api_key=settings.google_api_key)
        # Initialize the model once
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def ask(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()

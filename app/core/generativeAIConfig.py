from app.core.settings import settings
import google.genai as genai

class GoogleAIClient:
    def __init__(self):
        # Configure API key once
        genai.configure(api_key=settings.google_api_key)
        # Initialize a supported free model
        self.model = genai.GenerativeModel("gemini-1.0-pro")

    def ask(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()

from app.core.settings import settings
import google.genai as genai

class GoogleAIClient:
    def __init__(self):
        # Pass the API key directly when creating the model
        self.model = genai.GenerativeModel(
            "gemini-1.0-pro", 
            api_key=settings.google_api_key
        )

    def ask(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Optional: log or handle errors gracefully
            return f"Error generating content: {str(e)}"

from app.core.settings import settings
import google.genai as genai



class GoogleAIClient:
    def __init__(self):
        # Create a client with your API key from settings
        self.client = genai.Client(api_key=settings.google_api_key)
        for model in self.client.models.list(): 
            print(model.name, model.supported_generation_methods)

    def ask(self, prompt: str) -> str:
        # Use the client to generate content
        response = self.client.models.generate_content(
            model="gemini-1.0-pro",  # free-tier model
            contents=prompt
        )
        return response.text.strip()

import os
import google.generativeai as genai

class GoogleAIClient:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def ask(self, prompt: str) -> str:
        model = genai.GenerativeModel("gemini-1.5-flash")  # fast + cost-effective
        response = model.generate_content(prompt)
        return response.text.strip()

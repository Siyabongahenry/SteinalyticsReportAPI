import boto3
import json
from app.core.settings import settings

class BedrockAIClient:
    def __init__(self):
        # IAM role credentials are automatically picked up by boto3
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.region  # e.g. "us-east-1"
        )

        # Use a currently active model from list-foundation-models
        self.model_id = "anthropic.claude-sonnet-4-20250514-v1:0"

    def ask(self, prompt: str) -> str:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 512
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )

        output = json.loads(response["body"].read())
        return output.get("completion", "").strip()

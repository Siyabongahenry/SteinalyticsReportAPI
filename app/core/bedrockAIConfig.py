import boto3
import json
from app.core.settings import settings

class BedrockAIClient:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.region  # e.g. "us-east-1"
        )

        # Inference profile ARN for Claude 3 Sonnet
        self.model_id = (
            "arn:aws:bedrock:us-east-1:092963739214:"
            "inference-profile/us.anthropic.claude-3-sonnet-20240229-v1:0"
        )

    def ask(self, prompt: str) -> str:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "system": "You are a helpful assistant.",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )

        output = json.loads(response["body"].read())

        # 🔹 Correct extraction: look inside "content"
        if "content" in output and output["content"]:
            first_content = output["content"][0]
            if first_content.get("type") == "text":
                return first_content.get("text", "").strip()

        return ""

import boto3
import json
from app.core.settings import settings

class BedrockAIClient:
    def __init__(self):
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.region  # e.g. "us-east-1"
        )

        # Use the inference profile ARN for Claude 3 Sonnet
        self.model_id = (
            "arn:aws:bedrock:us-east-1:092963739214:"
            "inference-profile/us.anthropic.claude-3-sonnet-20240229-v1:0"
        )

    def ask(self, prompt: str) -> str:
        body = json.dumps({
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

        # Claude 3.x returns output under "output" → list of dicts with "content"
        if "output" in output and output["output"]:
            return output["output"][0].get("content", "").strip()
        return ""

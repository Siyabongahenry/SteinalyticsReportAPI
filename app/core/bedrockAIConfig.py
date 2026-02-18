import boto3
import json
from app.core.settings import settings

class BedrockAIClient:
    def __init__(self):
        # No need for access keys — boto3 will use the IAM role attached to your EC2 instance
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.aws_region  # e.g. "us-east-1"
        )

        # Choose a Bedrock model available in your region/account
        # Examples: "anthropic.claude-v2", "ai21.j2-mid", "amazon.titan-text-express-v1"
        self.model_id = "anthropic.claude-v2"

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

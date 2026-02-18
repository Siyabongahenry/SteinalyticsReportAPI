import boto3
import json
from app.core.settings import settings

class BedrockAIClient:
    def __init__(self):
        # boto3 will use the IAM role attached to your EC2 instance
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
        # Claude requires Human/Assistant format
        formatted_prompt = f'Human: {prompt}\n\nAssistant:'

        body = json.dumps({
            "prompt": formatted_prompt,
            "max_tokens_to_sample": 512
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )

        output = json.loads(response["body"].read())
        return output.get("completion", "").strip()

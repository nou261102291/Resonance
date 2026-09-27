"""AWS Bedrock integration for Project Resonance - Phase 2."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from models import ContextToken

logger = logging.getLogger(__name__)

# Model IDs for Amazon Nova
NOVA_LITE_MODEL_ID = "amazon.nova-lite-v1:0"
NOVA_PRO_MODEL_ID = "amazon.nova-pro-v1:0"

# Default to Nova Lite for cost efficiency
DEFAULT_MODEL_ID = NOVA_LITE_MODEL_ID


def _call_bedrock_converse(
    bedrock_client: Any,
    model_id: str,
    messages: list[dict],
    system_prompt: str,
    inference_config: dict,
) -> dict:
    """
    Synchronous helper to call Bedrock converse API.
    Runs in a thread pool to avoid blocking the event loop.
    """
    return bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=[{"text": system_prompt}],
        inferenceConfig=inference_config,
    )


async def analyze_image_context(
    image_base64: str,
    model_id: str = DEFAULT_MODEL_ID,
) -> ContextToken:
    """
    Analyze an image using Amazon Nova multimodal model to classify environmental context.

    Args:
        image_base64: Base64-encoded image data
        model_id: Bedrock model ID to use (default: amazon.nova-lite-v1:0)

    Returns:
        ContextToken with scene classification and confidence

    Raises:
        ValueError: If the model response cannot be parsed
        BotoCoreError: If there's an issue with the Bedrock API call
    """
    # Initialize Bedrock client
    bedrock_client = boto3.client("bedrock-runtime")

    # Construct the prompt for scene classification
    system_prompt = """You are an environmental context classifier for a wellness monitoring system.
Analyze the image and classify the scene into exactly one of these categories:
- "sedentary": Person sitting/lying down, indoor, low activity (reading, watching TV, working at desk)
- "active": Person exercising, moving vigorously, or in exercise equipment/clothing
- "outdoor": Person clearly outside (nature, streets, parks, buildings visible)
- "unknown": Cannot determine, image unclear, no person visible, or ambiguous

Return ONLY a valid JSON object with this exact schema:
{
  "scene": "sedentary|active|outdoor|unknown",
  "confidence": 0.0-1.0
}"""

    # Prepare the message with image
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": "Classify the environmental context in this image."
                },
                {
                    "image": {
                        "format": "jpeg",
                        "source": {"bytes": image_base64}
                    }
                }
            ]
        }
    ]

    # Inference configuration
    inference_config = {
        "maxTokens": 100,
        "temperature": 0.1,
        "topP": 0.9,
    }

    try:
        # Call Bedrock converse API in a thread pool to avoid blocking
        response = await asyncio.to_thread(
            _call_bedrock_converse,
            bedrock_client,
            model_id,
            messages,
            system_prompt,
            inference_config,
        )

        # Extract the response text
        response_text = response["output"]["message"]["content"][0]["text"]

        # Parse JSON from response
        try:
            result_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock response as JSON: {response_text}")
            raise ValueError(f"Invalid JSON response from Bedrock: {e}") from e

        # Validate and create ContextToken
        scene = result_data.get("scene")
        confidence = result_data.get("confidence")

        if scene not in ("sedentary", "active", "outdoor", "unknown"):
            logger.warning(f"Invalid scene from Bedrock: {scene}, defaulting to unknown")
            scene = "unknown"

        if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
            logger.warning(f"Invalid confidence from Bedrock: {confidence}, defaulting to 0.5")
            confidence = 0.5

        return ContextToken(scene=scene, confidence=float(confidence))

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Bedrock API error: {e}")
        raise
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Unexpected response structure from Bedrock: {e}")
        raise ValueError(f"Unexpected response structure: {e}") from e


async def get_bedrock_client() -> Any:
    """
    Get a configured Bedrock runtime client.
    Useful for testing or custom configurations.
    """
    return boto3.client("bedrock-runtime")
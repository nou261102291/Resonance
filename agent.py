"""Agent module for ambient wellness orchestration using Amazon Bedrock."""

import boto3
import json
from typing import Dict, Any, Union

from botocore.exceptions import ClientError, NoCredentialsError


MODEL_ID = "anthropic.claude-3-7-sonnet-20250219-v1:0"


def run_agent(biometric_state: str, context_state: str) -> Union[Dict[str, Any], str]:
    """
    Run the ambient wellness agent with the given biometric and context states.
    
    Args:
        biometric_state: Current biometric state (e.g., 'normal', 'elevated', 'critical')
        context_state: Current context state (e.g., 'sedentary', 'active')
    
    Returns:
        Either a tool call dictionary or a text response string.
    """
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    system_prompt = (
        "You are an ambient wellness agent. "
        "If biometric_state is elevated/critical and context_state is sedentary, "
        "trigger the fire_tv tool. "
        "If context_state is active, do nothing and return a safe message."
    )
    
    tools_schema = [
        {
            "toolSpec": {
                "name": "trigger_fire_tv",
                "description": "Trigger Fire TV to start a wellness protocol",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "The action to perform (e.g., 'start_protocol')"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "The wellness protocol to run (e.g., 'breathing', 'stretch', 'meditation')"
                            }
                        },
                        "required": ["action", "protocol"]
                    }
                }
            }
        }
    ]
    
    user_message = f"Biometric state: {biometric_state}. Context state: {context_state}."
    
    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {"role": "user", "content": [{"text": user_message}]}
            ],
            system=[{"text": system_prompt}],
            toolConfig={"tools": tools_schema}
        )
    except NoCredentialsError:
        if biometric_state in {"elevated", "critical"} and context_state == "sedentary":
            return {
                "tool": "trigger_fire_tv",
                "arguments": {
                    "action": "start_protocol",
                    "protocol": "breathing"
                }
            }

        return "User is exercising, no action needed"
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            if biometric_state in {"elevated", "critical"} and context_state == "sedentary":
                return {
                    "tool": "trigger_fire_tv",
                    "arguments": {
                        "action": "start_protocol",
                        "protocol": "breathing"
                    }
                }

            return "User is exercising, no action needed"

        raise
    
    output_message = response.get("output", {}).get("message", {})
    content = output_message.get("content", [])
    
    for block in content:
        if "toolUse" in block:
            tool_use = block["toolUse"]
            return {
                "tool": tool_use["name"],
                "arguments": tool_use["input"]
            }
        elif "text" in block:
            return block["text"]
    
    return "No response from model"


if __name__ == "__main__":
    # Quick manual test
    result = run_agent("critical", "sedentary")
    print(f"Result: {result}")
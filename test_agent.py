"""Tests for the ambient wellness agent."""

import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError, NoCredentialsError
from agent import run_agent


EXPECTED_MODEL_ID = "anthropic.claude-3-7-sonnet-20250219-v1:0"


@patch("agent.boto3.client")
def test_agent_intervention(mock_boto_client):
    """Test that agent triggers fire_tv tool when biometric is critical and context is sedentary."""
    # Setup mock response with toolUse
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "toolUse": {
                            "toolUseId": "test-id-123",
                            "name": "trigger_fire_tv",
                            "input": {
                                "action": "start_protocol",
                                "protocol": "breathing"
                            }
                        }
                    }
                ]
            }
        }
    }
    
    result = run_agent("critical", "sedentary")
    
    assert isinstance(result, dict)
    assert result["tool"] == "trigger_fire_tv"
    assert result["arguments"]["action"] == "start_protocol"
    assert result["arguments"]["protocol"] == "breathing"
    
    # Verify the converse API was called correctly
    mock_client.converse.assert_called_once()
    call_args = mock_client.converse.call_args
    assert call_args.kwargs["modelId"] == EXPECTED_MODEL_ID
    assert "system" in call_args.kwargs
    assert "toolConfig" in call_args.kwargs


@patch("agent.boto3.client")
def test_agent_no_intervention(mock_boto_client):
    """Test that agent returns text when context is active (no intervention needed)."""
    # Setup mock response with plain text
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client
    
    mock_client.converse.return_value = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "text": "User is exercising, no action needed"
                    }
                ]
            }
        }
    }
    
    result = run_agent("elevated", "active")
    
    assert isinstance(result, str)
    assert result == "User is exercising, no action needed"
    
    # Verify the converse API was called correctly
    mock_client.converse.assert_called_once()
    call_args = mock_client.converse.call_args
    assert call_args.kwargs["modelId"] == EXPECTED_MODEL_ID


@patch("agent.boto3.client")
def test_agent_falls_back_when_model_is_unavailable(mock_boto_client):
    """Test that a retired or unavailable model triggers the built-in fallback."""
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": "ResourceNotFoundException", "Message": "model retired"}},
        operation_name="Converse",
    )

    result = run_agent("critical", "sedentary")

    assert isinstance(result, dict)
    assert result["tool"] == "trigger_fire_tv"
    assert result["arguments"]["action"] == "start_protocol"
    assert result["arguments"]["protocol"] == "breathing"


@patch("agent.boto3.client")
def test_agent_raises_for_non_recoverable_client_error(mock_boto_client):
    """Test that unexpected Bedrock errors still surface instead of being masked."""
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    mock_client.converse.side_effect = ClientError(
        error_response={"Error": {"Code": "AccessDeniedException", "Message": "denied"}},
        operation_name="Converse",
    )

    with pytest.raises(ClientError):
        run_agent("critical", "sedentary")


@patch("agent.boto3.client")
def test_agent_handles_empty_model_response(mock_boto_client):
    """Test that a valid but empty model response returns the safe default message."""
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    mock_client.converse.return_value = {"output": {"message": {"role": "assistant", "content": []}}}

    result = run_agent("normal", "active")

    assert result == "No response from model"


@patch("agent.boto3.client")
def test_agent_falls_back_without_credentials(mock_boto_client):
    """Test the offline fallback path when credentials are unavailable."""
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    mock_client.converse.side_effect = NoCredentialsError()

    result = run_agent("elevated", "sedentary")

    assert result["tool"] == "trigger_fire_tv"
    assert result["arguments"]["protocol"] == "breathing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""Pytest tests for AWS Bedrock integration - Strict TDD Phase 2."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from models import ContextToken


class TestAnalyzeImageContext:
    """Tests for analyze_image_context function."""

    @pytest.mark.asyncio
    async def test_analyze_image_context_returns_context_token(self):
        """Test analyze_image_context returns valid ContextToken from mocked Bedrock response."""
        # Import here to avoid import errors before implementation
        from aws_services import analyze_image_context

        # Mock Bedrock response
        mock_response = {
            "output": {
                "message": {
                    "content": [
                        {
                            "text": json.dumps({"scene": "sedentary", "confidence": 0.95})
                        }
                    ]
                }
            }
        }

        with patch("boto3.client") as mock_boto_client:
            mock_bedrock = MagicMock()
            # converse is synchronous, called via asyncio.to_thread
            mock_bedrock.converse.return_value = mock_response
            mock_boto_client.return_value = mock_bedrock

            result = await analyze_image_context("fake_base64_string")

            # Verify result
            assert isinstance(result, ContextToken)
            assert result.scene == "sedentary"
            assert result.confidence == 0.95

            # Verify boto3 was called correctly
            mock_boto_client.assert_called_once_with("bedrock-runtime")
            mock_bedrock.converse.assert_called_once()

            # Verify the call arguments
            call_args = mock_bedrock.converse.call_args
            assert call_args.kwargs["modelId"] in [
                "amazon.nova-lite-v1:0",
                "amazon.nova-pro-v1:0",
            ]
            assert "messages" in call_args.kwargs
            assert "inferenceConfig" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_analyze_image_context_handles_all_scenes(self):
        """Test analyze_image_context handles all valid scene types."""
        from aws_services import analyze_image_context

        for scene in ["sedentary", "active", "outdoor", "unknown"]:
            mock_response = {
                "output": {
                    "message": {
                        "content": [{"text": json.dumps({"scene": scene, "confidence": 0.9})}]
                    }
                }
            }

            with patch("boto3.client") as mock_boto_client:
                mock_bedrock = MagicMock()
                mock_bedrock.converse.return_value = mock_response
                mock_boto_client.return_value = mock_bedrock

                result = await analyze_image_context("fake_base64_string")

                assert isinstance(result, ContextToken)
                assert result.scene == scene
                assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_analyze_image_context_raises_on_invalid_response(self):
        """Test analyze_image_context raises on malformed Bedrock response."""
        from aws_services import analyze_image_context

        mock_response = {
            "output": {
                "message": {
                    "content": [{"text": "not valid json"}]
                }
            }
        }

        with patch("boto3.client") as mock_boto_client:
            mock_bedrock = MagicMock()
            mock_bedrock.converse.return_value = mock_response
            mock_boto_client.return_value = mock_bedrock

            with pytest.raises((json.JSONDecodeError, ValueError)):
                await analyze_image_context("fake_base64_string")

    @pytest.mark.asyncio
    async def test_analyze_image_context_raises_on_bedrock_error(self):
        """Test analyze_image_context propagates Bedrock API errors."""
        from aws_services import analyze_image_context

        with patch("boto3.client") as mock_boto_client:
            mock_bedrock = MagicMock()
            mock_bedrock.converse.side_effect = Exception("Bedrock API Error")
            mock_boto_client.return_value = mock_bedrock

            with pytest.raises(Exception, match="Bedrock API Error"):
                await analyze_image_context("fake_base64_string")


class TestBedrockClientInitialization:
    """Tests for Bedrock client initialization."""

    def test_boto3_client_called_with_correct_service(self):
        """Test that boto3.client is called with 'bedrock-runtime'."""
        from aws_services import analyze_image_context

        mock_response = {
            "output": {
                "message": {
                    "content": [{"text": json.dumps({"scene": "sedentary", "confidence": 0.95})}]
                }
            }
        }

        with patch("boto3.client") as mock_boto_client:
            mock_bedrock = MagicMock()
            mock_bedrock.converse.return_value = mock_response
            mock_boto_client.return_value = mock_bedrock

            import asyncio

            asyncio.run(analyze_image_context("fake_base64_string"))

            mock_boto_client.assert_called_once_with("bedrock-runtime")
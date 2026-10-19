# Amazon Bedrock Integration

## Current status

Resonance is a local prototype first. Its standard demonstration uses synthetic tokens, local mock sensor handlers, simulated Fire TV actuation, and a simulated reasoning fallback. AWS account access has been blocked, so no Bedrock request or AWS deployment has been verified against a live account. The test suite mocks Bedrock responses; passing tests validate request construction and response handling, not AWS access.

There are two Bedrock code paths:

| Code | Model and operation | Status |
|------|---------------------|--------|
| `agent.py` | `bedrock-runtime` Converse with `anthropic.claude-3-7-sonnet-20250219-v1:0`; returns text or a Fire TV tool-use request; `maxTokens` is 512. | The model invocation is implemented and is used by the reasoning path when credentials/model access are available. It is not a complete agent loop: it neither invokes the requested MCP tool nor returns a `toolResult` to Bedrock. The UI's fallback is simulated. |
| `aws_services.py` | `bedrock-runtime` Converse with `amazon.nova-lite-v1:0` by default (or Nova Pro when selected); accepts base64-encoded JPEG bytes, decodes them, and requests a scene label; `maxTokens` is 100. | The classifier and mocked tests exist, but the function is not called by `mcp_server.py` or `streamlit_app.py`. Ring/camera data is not captured or processed by this path in the demo. |

No real Bee wearable, Ring camera, or Fire TV integration is implemented. Do not describe the prototype as autonomously sensing, diagnosing, or intervening.

## Running the local demo

No AWS credentials are required for the normal mock-based demo. Start the server and Streamlit UI as described in the [README](README.md). Keep sensor/context values synthetic. The demo may attempt the Claude path when AWS credentials are configured; when unavailable, it can display simulated reasoning. This is a demonstration fallback, not proof of a successful Bedrock integration.

## Enabling the Bedrock reasoning call

1. Use Python dependencies from `requirements.txt` and configure standard AWS credentials (prefer an IAM role in deployed environments).
2. Confirm that the account can invoke the configured Claude model in `us-east-1`, currently pinned in `agent.py`. Verify that the model remains available and enabled in that region before relying on it.
3. Run the app's reasoning path and inspect the returned model result and logs. This repository has not verified a live request, and AWS SCPs/account policy may deny it.

The Nova classifier defaults to the boto3-configured region and model ID in `aws_services.py`. It has no camera connector; a caller must provide a valid base64-encoded JPEG string. The image is decoded to bytes for the Converse request.

## IAM and deployment

The CloudFormation task role currently allows `bedrock:Converse` and `bedrock:InvokeModel` against `"*"`. This is intentionally disclosed as a demo limitation, not a production-ready policy. Before deployment, restrict actions and resources to the specific supported model ARNs in the selected region, and confirm that the necessary Converse permissions are sufficient for the actual SDK/model behavior. Use task roles rather than long-lived IAM user keys. Enable CloudTrail and define appropriate log retention/access controls.

## Privacy, safety, and cost

- Synthetic demo tokens do not establish an edge-privacy guarantee.
- The Nova function would transmit its supplied image to Amazon Bedrock. Do not pass real images or biometric data until user consent, purpose limitation, data retention, security controls, and applicable legal requirements are addressed.
- Guard against placing prompts, images, tool arguments, or model responses containing sensitive data in application logs.
- Treat model-generated tool arguments as untrusted input. Validate them and require an explicit policy/consent decision before any real-world actuation.
- Both Converse calls set `maxTokens` explicitly to bound output generation. Review model pricing and quotas before live use.

## Work needed for a complete integration

1. Restore AWS access and verify Claude and Nova invocations in the chosen region.
2. Connect an explicitly consented image/context source to `analyze_image_context()` or remove the unused classifier from the claimed architecture.
3. Implement and test a bounded agent loop: validate each tool request, call the appropriate tool, pass a `toolResult` to Converse, and enforce no-intervention/false-positive rules.
4. Replace simulated actuation only after a real integration and authorization model are designed.
5. Narrow the ECS task role and validate the deployment template and live endpoint.

# Resonance AWS Deployment

## Exact AWS service choice

**Amazon ECS on AWS Fargate** behind an **Application Load Balancer**, with container images stored in **Amazon ECR** and CI/CD handled by **AWS CodePipeline + AWS CodeBuild + AWS CodeConnections**.

Why this stack:
- ECS Fargate gives a fully managed runtime without EC2 fleet management.
- A single public ALB gives a stable live demo URL for both Streamlit and MCP endpoints.
- ECR stores the Docker image produced from GitHub pushes.
- CodeConnections keeps the source link tied to the GitHub repository.
- CodePipeline coordinates source, build, and deployment stages.

## Runtime shape

This repo is built as a single demo container that starts both processes:
- `mcp_server.py` on port `8000`
- `streamlit_app.py` on port `8501`

For the public demo, the ALB targets both ports:
- Port `8501` for the Streamlit app (user-facing entry point)
- Port `8000` for the MCP server (judge evaluation endpoint)

## CI/CD flow

1. GitHub push triggers CodePipeline through CodeConnections.
2. CodeBuild runs `deploy/buildspec.yml`.
3. CodeBuild builds the Docker image and pushes it to ECR.
4. CodeBuild emits `imagedefinitions.json`.
5. CodePipeline deploys the new image to the ECS Fargate service.
6. The ALB continues serving both live demo URLs during each deployment.

## Required AWS resources

- ECR repository: `resonance-demo`
- ECS cluster: `resonance-demo`
- ECS service: `resonance-demo`
- ECS task definition: `deploy/taskdef.json`
- Application Load Balancer with target groups on ports `8501` (Streamlit) and `8000` (MCP)
- CloudWatch Logs group: `/ecs/resonance-demo`
- CodeConnections connection to the GitHub repo
- CodeBuild project with privileged mode enabled for Docker builds
- CodePipeline with Source -> Build -> Deploy stages

## Deployment notes

- CodeBuild must run in privileged mode so Docker can build the image.
- The ECS task execution role needs ECR pull and CloudWatch Logs permissions.
- If you later split the app into two services, keep the Streamlit app public and the MCP server private.

## Deploying the stack

Use the CloudFormation template at [deploy/resonance-stack.yaml](resonance-stack.yaml) with these required parameters:

- `VpcId`
- `PublicSubnetIds`
- `CodeConnectionArn`
- `GitHubFullRepositoryId`
- `GitHubBranchName`

After the stack reaches `CREATE_COMPLETE`, check the `AlbUrl` output in CloudFormation to open the live Streamlit demo, and the `McpUrl` output for the MCP server endpoint.

from aws_cdk import (
    Stack,
    aws_iam as iam,
    Duration,
)
from constructs import Construct

class GitHubOidcDeploymentRoleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        role_name = "github-actions-ourchants-deploy"
        github_repo = "ford-at-home/ourchants-api"
        branch = "main"

        oidc_provider = iam.OpenIdConnectProvider(
            self, "GitHubOIDCProvider",
            url="https://token.actions.githubusercontent.com",
            client_ids=["sts.amazonaws.com"]
        )

        deploy_role = iam.Role(
            self, "GitHubOIDCDeployRole",
            role_name=role_name,
            assumed_by=iam.FederatedPrincipal(
                oidc_provider.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": f"repo:{github_repo}:ref:refs/heads/{branch}"
                    }
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity"
            ),
            description="GitHub Actions deployment role for ourchants-api repo",
            max_session_duration=Duration.hours(1)
        )

        # CDK permissions
        deploy_role.add_to_policy(iam.PolicyStatement(
            actions=[
                "cloudformation:*",
                "iam:*",
                "s3:*",
                "apigateway:*",
                "lambda:*",
                "logs:*",
                "dynamodb:*"
            ],
            resources=["*"],
            conditions={
                "StringEquals": {
                    "aws:RequestTag/aws:cloudformation:stack-name": ["ApiStack", "DatabaseStack"]
                }
            }
        ))

        # Allow the role to pass itself to other services
        deploy_role.add_to_policy(iam.PolicyStatement(
            actions=["iam:PassRole"],
            resources=[deploy_role.role_arn],
            conditions={
                "StringEquals": {
                    "iam:PassedToService": [
                        "cloudformation.amazonaws.com",
                        "lambda.amazonaws.com",
                        "apigateway.amazonaws.com"
                    ]
                }
            }
        )) 
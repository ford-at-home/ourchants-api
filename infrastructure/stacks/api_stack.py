from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    CfnOutput,
    Duration
)
from constructs import Construct
from .db_stack import DatabaseStack
import os

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, db_stack: DatabaseStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the path to the Lambda code
        lambda_code_path = os.path.join(os.path.dirname(__file__), "../../api")

        # Create Lambda function
        function = lambda_.Function(
            self, "SongsLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset(lambda_code_path),
            environment={
                "DYNAMODB_TABLE_NAME": db_stack.table.table_name
            }
        )

        # Grant Lambda function access to DynamoDB table
        db_stack.table.grant_read_write_data(function)

        # Create HTTP API with CORS enabled
        api = apigw.HttpApi(
            self, "SongsHttpApi",
            description="HTTP API for managing songs",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["http://ourchants-website.s3-website-us-east-1.amazonaws.com"],
                allow_methods=[apigw.CorsHttpMethod.GET, apigw.CorsHttpMethod.POST, 
                             apigw.CorsHttpMethod.PUT, apigw.CorsHttpMethod.DELETE],
                allow_headers=["Content-Type", "Accept"],
                max_age=Duration.seconds(3000)
            )
        )

        # Create Lambda integration
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            function
        )

        # Add routes with proper integration
        api.add_routes(
            path="/songs",
            methods=[apigw.HttpMethod.GET],
            integration=lambda_integration
        )

        api.add_routes(
            path="/songs",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration
        )

        api.add_routes(
            path="/songs/{song_id}",
            methods=[apigw.HttpMethod.GET],
            integration=lambda_integration
        )

        api.add_routes(
            path="/songs/{song_id}",
            methods=[apigw.HttpMethod.PUT],
            integration=lambda_integration
        )

        api.add_routes(
            path="/songs/{song_id}",
            methods=[apigw.HttpMethod.DELETE],
            integration=lambda_integration
        )

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url
        ) 
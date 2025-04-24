from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_iam as iam,
    CfnOutput,
    Duration,
    aws_s3 as s3
)
from constructs import Construct
from .db_stack import DatabaseStack
import os
import aws_cdk as cdk

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, db_stack: DatabaseStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the path to the Lambda code
        lambda_code_path = os.path.join(os.path.dirname(__file__), "../../api")
        
        # Get the absolute path to the api directory
        api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api"))

        # Create a Lambda layer for dependencies
        layer = lambda_.LayerVersion(
            self, "DependenciesLayer",
            code=lambda_.Code.from_asset(os.path.abspath(os.path.join(os.path.dirname(__file__), "../layers/python/layer.zip"))),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            description="Layer containing Python dependencies"
        )

        # Create Lambda function
        function = lambda_.Function(
            self, "SongsLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset(lambda_code_path),
            layers=[layer],
            timeout=Duration.seconds(30),  # Increase timeout to 30 seconds
            environment={
                "DYNAMODB_TABLE_NAME": db_stack.table.table_name,
                "S3_BUCKET": db_stack.bucket.bucket_name  # Use the bucket name from DatabaseStack
            }
        )

        # Grant Lambda function access to DynamoDB table
        db_stack.table.grant_read_write_data(function)

        # Use the bucket from DatabaseStack
        self.audio_bucket = db_stack.bucket

        # Grant Lambda function access to S3 bucket
        self.audio_bucket.grant_read_write(function)  # Grant read/write access to the bucket

        # Create HTTP API with CORS enabled
        api = apigw.HttpApi(
            self, "SongsHttpApi",
            description="HTTP API for managing songs",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["https://ourchants.com", "http://ourchants-website.s3-website-us-east-1.amazonaws.com"],
                allow_methods=[apigw.CorsHttpMethod.GET, apigw.CorsHttpMethod.POST, 
                             apigw.CorsHttpMethod.PUT, apigw.CorsHttpMethod.DELETE,
                             apigw.CorsHttpMethod.OPTIONS],
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

        # Add pre-signed URL endpoint
        api.add_routes(
            path="/presigned-url",
            methods=[apigw.HttpMethod.POST],
            integration=lambda_integration
        )

        # Output the API URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url
        ) 
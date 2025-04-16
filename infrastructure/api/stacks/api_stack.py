from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    CfnOutput
)
from constructs import Construct
from infrastructure.database.stacks.db_stack import DatabaseStack
import os

class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, db_stack: DatabaseStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the path to the Lambda code
        lambda_code_path = os.path.join(os.path.dirname(__file__), "../../../api")

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

        # Create API Gateway
        api = apigw.RestApi(
            self, "SongsApi",
            description="API for managing songs"
        )

        # Create API resources and methods
        songs = api.root.add_resource("songs")
        
        # GET /songs
        songs.add_method(
            "GET",
            apigw.LambdaIntegration(function)
        )
        
        # POST /songs
        songs.add_method(
            "POST",
            apigw.LambdaIntegration(function)
        )

        # Individual song resource
        song = songs.add_resource("{song_id}")
        
        # GET /songs/{song_id}
        song.add_method(
            "GET",
            apigw.LambdaIntegration(function)
        )
        
        # PUT /songs/{song_id}
        song.add_method(
            "PUT",
            apigw.LambdaIntegration(function)
        )
        
        # DELETE /songs/{song_id}
        song.add_method(
            "DELETE",
            apigw.LambdaIntegration(function)
        )

        # Export API endpoint
        CfnOutput(
            self, "ApiEndpoint",
            value=api.url,
            description="URL of the API Gateway"
        ) 
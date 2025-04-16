from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    RemovalPolicy
)
from constructs import Construct

class SongsApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            self, "SongsTable",
            partition_key=dynamodb.Attribute(
                name="song_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Lambda function
        function = lambda_.Function(
            self, "SongsLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="app.lambda_handler",
            code=lambda_.Code.from_asset("../lambda"),
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name
            }
        )

        # Grant Lambda function access to DynamoDB table
        table.grant_read_write_data(function)

        # Create API Gateway
        api = apigw.RestApi(
            self, "SongsApi",
            description="API for managing songs"
        )

        # Add Cognito User Pool authorizer
        # TODO: Add actual user pool reference
        # authorizer = apigw.CognitoUserPoolsAuthorizer(...)

        # Create API resources and methods
        songs = api.root.add_resource("songs")
        
        # GET /songs
        songs.add_method(
            "GET",
            apigw.LambdaIntegration(function),
            # authorization_type=apigw.AuthorizationType.COGNITO,
            # authorizer=authorizer
        )
        
        # POST /songs
        songs.add_method(
            "POST",
            apigw.LambdaIntegration(function),
            # authorization_type=apigw.AuthorizationType.COGNITO,
            # authorizer=authorizer
        )

        # Individual song resource
        song = songs.add_resource("{song_id}")
        
        # GET /songs/{song_id}
        song.add_method(
            "GET",
            apigw.LambdaIntegration(function),
            # authorization_type=apigw.AuthorizationType.COGNITO,
            # authorizer=authorizer
        )
        
        # PUT /songs/{song_id}
        song.add_method(
            "PUT",
            apigw.LambdaIntegration(function),
            # authorization_type=apigw.AuthorizationType.COGNITO,
            # authorizer=authorizer
        )
        
        # DELETE /songs/{song_id}
        song.add_method(
            "DELETE",
            apigw.LambdaIntegration(function),
            # authorization_type=apigw.AuthorizationType.COGNITO,
            # authorizer=authorizer
        ) 
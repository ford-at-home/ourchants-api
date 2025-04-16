from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

class SongsTableStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            self,
            "SongsTable",
            table_name="ourchants-items",
            partition_key=dynamodb.Attribute(
                name="song_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # ⚠️ for dev only
        )

        # Create Lambda function
        lambda_function = lambda_.Function(
            self,
            "SongsLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="songs_lambda.lambda_handler",
            code=lambda_.Code.from_asset("api/cdk/lambda"),
            environment={
                "DYNAMODB_TABLE_NAME": table.table_name
            }
        )

        # Grant Lambda permissions to access DynamoDB
        table.grant_read_write_data(lambda_function)

        # Create API Gateway
        api = apigw.RestApi(
            self,
            "SongsApi",
            rest_api_name="Songs API",
            description="API for managing songs"
        )

        # Create API Gateway authorizer
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "SongsAuthorizer",
            cognito_user_pools=[],  # Add your Cognito User Pool here
            identity_source="method.request.header.Authorization"
        )

        # Create API Gateway resources and methods
        songs = api.root.add_resource("songs")
        song = songs.add_resource("{song_id}")

        # Add methods with authorizer
        songs.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_function),
            authorizer=authorizer
        )
        songs.add_method(
            "POST",
            apigw.LambdaIntegration(lambda_function),
            authorizer=authorizer
        )
        song.add_method(
            "GET",
            apigw.LambdaIntegration(lambda_function),
            authorizer=authorizer
        )
        song.add_method(
            "PUT",
            apigw.LambdaIntegration(lambda_function),
            authorizer=authorizer
        )
        song.add_method(
            "DELETE",
            apigw.LambdaIntegration(lambda_function),
            authorizer=authorizer
        )


from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB table
        self.table = dynamodb.Table(
            self, "SongsTable",
            partition_key=dynamodb.Attribute(
                name="song_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Export table name for other stacks to use
        CfnOutput(
            self, "TableName",
            value=self.table.table_name,
            description="Name of the DynamoDB table"
        ) 
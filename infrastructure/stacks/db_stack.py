from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
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

        # Import existing S3 bucket
        self.bucket = s3.Bucket.from_bucket_attributes(
            self, "SongsBucket",
            bucket_name="ourchants-songs",
            bucket_arn=f"arn:aws:s3:::ourchants-songs"
        )

        # Export table name for other stacks to use
        CfnOutput(
            self, "TableName",
            value=self.table.table_name,
            description="Name of the DynamoDB table"
        )

        # Export bucket name for other stacks to use
        CfnOutput(
            self, "BucketName",
            value=self.bucket.bucket_name,
            description="Name of the S3 bucket for song files"
        )

        # Export bucket URI for other stacks to use
        CfnOutput(
            self, "BucketURI",
            value=f"s3://{self.bucket.bucket_name}",
            description="S3 URI for the song files bucket"
        ) 
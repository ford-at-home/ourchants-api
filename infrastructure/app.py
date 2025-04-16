#!/usr/bin/env python3
from aws_cdk import App, Environment
from infrastructure.database.stacks.db_stack import DatabaseStack
from infrastructure.api.stacks.api_stack import ApiStack

app = App()

# Create database stack
db_stack = DatabaseStack(
    app, "DatabaseStack",
    env=Environment(region="us-east-1")
)

# Create API stack that depends on database stack
api_stack = ApiStack(
    app, "ApiStack",
    db_stack=db_stack,
    env=Environment(region="us-east-1")
)

app.synth() 
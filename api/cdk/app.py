#!/usr/bin/env python3
from aws_cdk import App, Environment
from songs_api.songs_api_stack import SongsApiStack

app = App()
SongsApiStack(app, "SongsApiStack", env=Environment(region="us-east-1"))
app.synth() 
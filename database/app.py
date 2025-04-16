#!/usr/bin/env python3

import aws_cdk as cdk
from songs_table.songs_table_stack import SongsTableStack

app = cdk.App()
SongsTableStack(app, "SongsTableStack", env=cdk.Environment(region="us-east-1"))
app.synth()


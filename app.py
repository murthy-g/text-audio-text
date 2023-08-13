#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_api.cdk_api_stack import CdkApiStack


app = cdk.App()
CdkApiStack(app, "CdkApiStack")

app.synth()
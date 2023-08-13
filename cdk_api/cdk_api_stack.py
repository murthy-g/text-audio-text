import os
from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_s3 as s3,
    # core,
    # aws_s3_deployment as s3deploy,
)
from constructs import Construct

class CdkApiStack(Stack):

    def create_layers(self, layers_dir, runtime):
        layers = []

        # Get a list of all zip files in the directory
        zip_files = [file for file in os.listdir(layers_dir) if file.endswith('.zip')]

        # Iterate through the zip files and create layers
        for zip_file in zip_files:
            layer_name = os.path.splitext(zip_file)[0]  # Get layer name from the zip file name

            # Create the layer using the zip file
            layer = _lambda.LayerVersion(
                self,
                f"{layer_name}Layer",
                code=_lambda.Code.from_asset(os.path.join(layers_dir, zip_file)),
                compatible_runtimes=[runtime],
                description=f"A layer for {layer_name}",
            )
            layers.append(layer)  # Append the layer to the list

        return layers

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # Usage
        layers1_dir = './layers/layers/layer1'
        layers2_dir = './layers/layers/layer2'
        runtime = _lambda.Runtime.PYTHON_3_11

        layers1 = CdkApiStack.create_layers(self, layers1_dir, runtime)
        layers2 = CdkApiStack.create_layers(self, layers2_dir, runtime)
        
        #create s3 bucket
        bucket = s3.Bucket(self, "AudioBucket")


        #create iam role to write files into s3 bucket from lambda function
        generate_audio_lambda_role = _iam.Role(
            self,
            "GenerateAudioLambdaRole",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        #attach created iam role to lambda function
        generate_audio_lambda_role.add_to_policy(
            _iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject"],
                resources=[bucket.bucket_arn + "/*"],
            )
        )

        #create lambda function
        generate_audio_lambda = _lambda.Function(
            self,
            "GenerateAudioLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("handlers"),
            layers=layers1,
            handler="generateAudio.handler",
            role=generate_audio_lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        #ccreate lambda function for whisper.py
        whisper_lambda = _lambda.Function(
            self,
            "WhisperLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            code=_lambda.Code.from_asset("handlers"),
            handler="whisper.handler",
            role=generate_audio_lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
            layers=layers2
        )

        

        # Add the 'flask' library to the Lambda deployment package
        # _lambda.Function.add_to_role_policy(
        #     statement=_iam.PolicyStatement(
        #         actions=["s3:GetObject"],  # Adjust the permissions as needed
        #         resources=["*"],
        #     )
        # )

        #create api gateway
        api = apigateway.RestApi(
            self,
            "GenerateAudioApi",
            rest_api_name="GenerateAudioApi",
            description="This service generates audio from text",
            )
        
        #create api gateway lambda integration
        generate_audio_integration = apigateway.LambdaIntegration(generate_audio_lambda)
        whisper_integration = apigateway.LambdaIntegration(whisper_lambda)

        #create api gateway resource
        api.root.add_resource("generate").add_method("POST", generate_audio_integration)
        api.root.add_resource("whisper").add_method("POST", whisper_integration)

        

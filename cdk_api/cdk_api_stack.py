import os
import boto3
from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_s3 as s3,
    aws_logs as logs,
    # core,
    # aws_s3_deployment as s3deploy,
)

from constructs import Construct

class CdkApiStack(Stack):

    def get_all_keys_from_s3_bucket(bucket_name):
        s3_client = boto3.client('s3')
        
        keys = []
        continuation_token = None

        while True:
            list_objects_kwargs = {'Bucket': bucket_name}
            if continuation_token:
                list_objects_kwargs['ContinuationToken'] = continuation_token

            response = s3_client.list_objects_v2(**list_objects_kwargs)

            if 'Contents' in response:
                for obj in response['Contents']:
                    keys.append(obj['Key'])

            if not response.get('IsTruncated'):  # Once all keys are fetched
                break

            continuation_token = response.get('NextContinuationToken')

        return keys

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        #create s3 bucket
        bucket = s3.Bucket(self, "AudioBucket")
        layer_bucket = s3.Bucket.from_bucket_name(self, 'ImportedBucket', 'zoom-api-layers')

        layer_zip_files = [
            'charset_normalizer_urllib3.zip',
            'gtts_soundfile_boto3.zip',
            'torch.zip',
            'torchaudio_pillow_jsonify.zip',
            'transformers.zip'
        ]

        # Create LayerVersion objects for each zipped layer
        layer_objects = []
        for zip_file in layer_zip_files:
            layer_code = _lambda.Code.from_bucket(layer_bucket, zip_file)
            layer = _lambda.LayerVersion(self, zip_file, code=layer_code)
            layer_objects.append(layer)


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
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("handlers"),
            layers=layer_objects,
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
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("handlers"),
            handler="whisper.handler",
            role=generate_audio_lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
            layers=layer_objects,
        )

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

        
        log_group = logs.LogGroup(self, "ApiGatewayAccessLogs")

        api_gateway_logging_role = _iam.Role(
            self,
            "ApiGatewayLoggingRole",
            assumed_by=_iam.ServicePrincipal("apigateway.amazonaws.com"),
        )

        api_gateway_logging_role.add_to_policy(
            _iam.PolicyStatement(
                actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
                resources=[log_group.log_group_arn]
            )
        )

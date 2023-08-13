import json
import boto3
from gtts import gTTS
import os

# Initialize the Boto3 S3 client
s3 = boto3.client('s3')

def handler(event, context):
    try:
        data = event['body']
        if 'text' not in data:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No text provided"})
            }
        
        text = data['text']
        
        # Generate the audio
        tts = gTTS(text=text, lang='en')
        tts.volume = 2.0  # Increase the volume to create high-amplitude audio
        audio_path = "output.wav"
        tts.save(audio_path)
        
        # Upload 'output.wav' to S3 bucket
        s3_bucket_name = os.environ['S3_BUCKET_NAME']
        s3_audio_key = 'audio/output.wav'
        s3.upload_file(audio_path, s3_bucket_name, s3_audio_key)
        
        # Return the S3 URL of the uploaded audio file as a response
        s3_audio_url = f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_audio_key}"
        return {
            "statusCode": 200,
            "body": json.dumps({"audio_url": s3_audio_url}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

import boto3
from PIL import Image
import io
import os
import uuid
import json

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "processed-bucket-demo")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "ImageMetadata")
table = dynamodb.Table(DYNAMODB_TABLE)

def process_image(image_data, size=(128, 128)):
    """Resize the image to the given size."""
    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(size)
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    return output_buffer

def lambda_handler(event, context):
    """Main Lambda handler supporting S3 or API Gateway triggers."""
    records = event.get('Records', [])
    
    # Determine if S3 event or API Gateway
    if records:  # S3 trigger
        responses = []
        for record in records:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # Get the image
            obj = s3.get_object(Bucket=bucket, Key=key)
            processed_data = process_image(obj['Body'].read())

            # Upload processed image
            new_key = f"processed-{uuid.uuid4()}.png"
            s3.put_object(Bucket=PROCESSED_BUCKET, Key=new_key, Body=processed_data)

            # Store metadata
            table.put_item(Item={
                'id': str(uuid.uuid4()),
                'original_file': key,
                'processed_file': new_key
            })
            responses.append({'original': key, 'processed': new_key})

        return {
            'statusCode': 200,
            'body': json.dumps(responses)
        }

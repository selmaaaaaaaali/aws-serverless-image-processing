import boto3
from PIL import Image
import io
import os
import uuid

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Optional DynamoDB table
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "ImageMetadata")
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Download image
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        image_data = response['Body'].read()
        image = Image.open(io.BytesIO(image_data))

        # Resize image
        image.thumbnail((128, 128))

        # Save processed image
        processed_bucket = os.environ.get("PROCESSED_BUCKET", "processed-bucket")
        new_key = f"processed-{uuid.uuid4()}.png"
        out_buffer = io.BytesIO()
        image.save(out_buffer, format='PNG')
        out_buffer.seek(0)
        s3.put_object(Bucket=processed_bucket, Key=new_key, Body=out_buffer)

        # Store metadata
        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'original_file': object_key,
            'processed_file': new_key
        })

    return {
        'statusCode': 200,
        'body': f"Processed {len(event['Records'])} images."
    }

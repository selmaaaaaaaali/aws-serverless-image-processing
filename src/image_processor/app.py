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
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "grad-project-processed-bucket")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "grad-project-image-metadata")
table = dynamodb.Table(DYNAMODB_TABLE)

def process_image(image_data, size=(128, 128)):
    image = Image.open(io.BytesIO(image_data))
    image.thumbnail(size)
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='PNG')
    output_buffer.seek(0)
    return output_buffer

def lambda_handler(event, context):
    records = event.get('Records', [])
    if records:  # S3 trigger
        responses = []
        for record in records:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            obj = s3.get_object(Bucket=bucket, Key=key)
            processed_data = process_image(obj['Body'].read())

            new_key = f"processed-{uuid.uuid4()}.png"
            s3.put_object(Bucket=PROCESSED_BUCKET, Key=new_key, Body=processed_data)

            table.put_item(Item={
                'id': str(uuid.uuid4()),
                'original_file': key,
                'processed_file': new_key
            })
            responses.append({'original': key, 'processed': new_key})

        return {'statusCode': 200, 'body': json.dumps(responses)}

    else:  # API Gateway trigger
        body = json.loads(event.get('body', '{}'))
        bucket = body.get('bucket')
        key = body.get('key')

        if not bucket or not key:
            return {'statusCode': 400, 'body': 'bucket and key required'}

        obj = s3.get_object(Bucket=bucket, Key=key)
        processed_data = process_image(obj['Body'].read())
        new_key = f"processed-{uuid.uuid4()}.png"
        s3.put_object(Bucket=PROCESSED_BUCKET, Key=new_key, Body=processed_data)

        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'original_file': key,
            'processed_file': new_key
        })

        return {'statusCode': 200, 'body': json.dumps({'original': key, 'processed': new_key})}

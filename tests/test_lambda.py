import boto3
import pytest
import json
from moto import mock_s3, mock_dynamodb2
from io import BytesIO
from PIL import Image
import os
import sys

# Add src folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/image_processor')))
import app

# Constants (match your random bucket names)
UPLOAD_BUCKET = "grad-project-upload-bucket-5678"
PROCESSED_BUCKET = "grad-project-processed-bucket"
DYNAMODB_TABLE = "grad-project-image-metadata"

def create_test_image():
    img = Image.new('RGB', (100, 100), color = 'red')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()

@pytest.fixture
def aws_setup():
    with mock_s3():
        with mock_dynamodb2():
            # Create S3 buckets
            s3 = boto3.client('s3', region_name='us-east-1')
            s3.create_bucket(Bucket=UPLOAD_BUCKET)
            s3.create_bucket(Bucket=PROCESSED_BUCKET)

            # Create DynamoDB table
            dynamodb = boto3.client('dynamodb', region_name='us-east-1')
            dynamodb.create_table(
                TableName=DYNAMODB_TABLE,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )

            # Patch environment variables
            os.environ["PROCESSED_BUCKET"] = PROCESSED_BUCKET
            os.environ["DYNAMODB_TABLE"] = DYNAMODB_TABLE

            yield

def test_lambda_s3_trigger(aws_setup):
    s3 = boto3.client('s3', region_name='us-east-1')
    # Upload a test image
    s3.put_object(Bucket=UPLOAD_BUCKET, Key="test.png", Body=create_test_image())

    # Create fake S3 event
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": UPLOAD_BUCKET},
                    "object": {"key": "test.png"}
                }
            }
        ]
    }

    response = app.lambda_handler(event, None)
    body = json.loads(response["body"])

    # Assertions
    assert response['statusCode'] == 200
    assert len(body) == 1
    assert "original" in body[0]
    assert "processed" in body[0]

    # Check processed image exists in S3
    result = s3.list_objects_v2(Bucket=PROCESSED_BUCKET)
    assert result['KeyCount'] == 1

def test_lambda_api_gateway_trigger(aws_setup):
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.put_object(Bucket=UPLOAD_BUCKET, Key="test2.png", Body=create_test_image())

    event = {
        "body": json.dumps({"bucket": UPLOAD_BUCKET, "key": "test2.png"})
    }

    response = app.lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response['statusCode'] == 200
    assert "original" in body
    assert "processed" in body

    result = s3.list_objects_v2(Bucket=PROCESSED_BUCKET)
    assert result['KeyCount'] == 1

#!/bin/bash
set -e

# Variables
STACK_NAME="ServerlessImageProcessing"
REGION="us-east-1"                   # Change if needed
LAMBDA_BUCKET="your-lambda-bucket"   # Replace with your S3 bucket
LAMBDA_KEY="image_processor.zip"
TEMPLATE_FILE="../templates/main.yaml"

# Step 1: Package Lambda function
echo "Packaging Lambda function..."
cd ../src/image_processor
zip -r ../../image_processor.zip .
cd ../../deployment

# Step 2: Upload Lambda package to S3
echo "Uploading Lambda package to S3..."
aws s3 cp ../image_processor.zip s3://$LAMBDA_BUCKET/$LAMBDA_KEY --region $REGION

# Step 3: Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --stack-name $STACK_NAME \
    --template-file $TEMPLATE_FILE \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides LambdaS3CodeBucket=$LAMBDA_BUCKET LambdaS3CodeKey=$LAMBDA_KEY \
    --region $REGION

echo "Deployment complete!"

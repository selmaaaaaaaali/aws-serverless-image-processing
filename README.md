
# Serverless Image Processing on AWS

## Project Overview

This project implements a **serverless image processing solution** using AWS services. Users can upload images to an S3 bucket, which triggers a Lambda function that processes and resizes the images. The processed images are stored in a separate S3 bucket and optionally logged in a DynamoDB table.  

The system uses **CloudFront** to cache processed images globally for low-latency access. This architecture is fully **event-driven, scalable, and serverless**, demonstrating AWS best practices for modern cloud applications.

**Key benefits of this solution:**
- Automatic image resizing and processing
- Serverless architecture (no servers to manage)
- Automatic scaling with AWS Lambda
- Global content delivery with CloudFront
- Optional metadata tracking with DynamoDB

---

## Architecture Diagram

![Architecture Diagram](architecture-diagram.png)

**Components:**
1. **Upload Bucket (S3)** – Users upload original images.  
2. **Processed Bucket (S3)** – Stores processed images.  
3. **AWS Lambda** – Processes images and optionally stores metadata in DynamoDB.  
4. **DynamoDB Table (Optional)** – Stores metadata such as image IDs and processed file names.  
5. **API Gateway (Optional)** – Provides endpoints for processing images via HTTP requests.  
6. **CloudFront Distribution** – Caches processed images for faster global access.  

---

## AWS Services Used

| Service | Role in Project |
|---------|----------------|
| **Amazon S3** | Upload bucket and processed bucket for storing images. |
| **AWS Lambda** | Image processing function triggered by S3 or API Gateway. |
| **Amazon DynamoDB** | Optional table to store image metadata (id, original_file, processed_file). |
| **Amazon API Gateway** | Optional REST API to trigger image processing. |
| **Amazon CloudFront** | Global caching for processed images. |
| **IAM Roles** | Securely grants Lambda permissions to access S3 and DynamoDB. |

---

## Deployment Instructions

### Step 1: Package Lambda Function

Navigate to the Lambda source directory:

```bash
cd src/image_processor
````

Zip the Lambda code:

```bash
zip -r ../../image_processor.zip .
```

---

### Step 2: Deploy Using Deployment Script

Navigate to the deployment directory:

```bash
cd deployment
```

Run the deployment script:

```bash
bash deploy.sh
```

This script will:

* Upload the Lambda zip to a preconfigured S3 bucket
* Deploy the CloudFormation stack
* Create all required resources (buckets, Lambda, DynamoDB, CloudFront)

---

### Step 3: Test S3 Trigger

1. Upload an image to the upload bucket (`grad-project-upload-bucket-5678`).
2. Lambda will automatically process the image and save it to the processed bucket (`grad-project-processed-bucket`).
3. Metadata is recorded in DynamoDB if enabled.

---

### Step 4: Test API Gateway Trigger (Optional)

You can trigger the Lambda function via API Gateway using a POST request:

**Request JSON Example:**

```json
{
  "bucket": "grad-project-upload-bucket-5678",
  "key": "example.png"
}
```

**Expected Response:**

```json
{
  "original": "example.png",
  "processed": "processed-<uuid>.png"
}
```

---

### Step 5: Access Processed Images via CloudFront

* Use the CloudFront distribution domain created by CloudFormation to access processed images globally.
* CloudFront caches images to reduce latency and AWS costs for repeated requests.

---

## Running Tests

Unit tests are included to verify that the Lambda function processes images correctly. The tests use **`moto`** to mock S3 and DynamoDB, so no actual AWS resources are required.

1. Install dependencies:

```bash
pip install pytest moto Pillow boto3
```

2. Run the tests:

```bash
pytest tests/test_lambda.py
```

**Tests Included:**

* S3-triggered Lambda processing
* API Gateway-triggered Lambda processing
* Verifies processed images exist in S3
* Verifies metadata is written to DynamoDB


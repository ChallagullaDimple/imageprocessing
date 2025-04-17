import boto3
import botocore.exceptions

# AWS clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# List of sample images
sample_images = [
    'apple_blight.jpg',            # Diseased
    'banana_leaf_healthy.jpg',     # Healthy
    'corn_rust.jpg',               # Diseased
    'potato_healthy.jpg',          # Healthy
    'tomato_bacterial_spot.jpg'    # Diseased
]

def analyze_image(bucket_name, image_key):
    try:
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}},
            MaxLabels=10
        )

        labels = [label['Name'] for label in response['Labels']]
        print(f"Analyzed {image_key}: Labels found: {labels}")

        # Simple rule for disease detection
        if any(term in labels for term in ["Disease", "Fungus", "Bacterial", "Rust", "Blight"]):
            diagnosis = f"⚠ {image_key} might be diseased."
        else:
            diagnosis = f"✅ {image_key} seems healthy."

        # Store result in DynamoDB
        table = dynamodb.Table('CropDiseaseAnalysis')
        table.put_item(Item={
            'ImageKey': image_key,
            'Labels': labels,
            'Diagnosis': diagnosis
        })

        # Send alert via SNS
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:024848457397:disease',  # ✅ Confirm region/account/topic correctness
            Message=diagnosis,
            Subject='Crop Health Alert'
        )

        return diagnosis

    except botocore.exceptions.ClientError as error:
        error_message = f"Error processing {image_key}: {error.response['Error']['Message']}"
        print(error_message)
        return error_message

def lambda_handler(event, context):
    bucket_name = 'mybuket800151'  # ✅ Your actual S3 bucket name

    results = {}
    for image in sample_images:
        result = analyze_image(bucket_name, image)
        results[image] = result

    return {'statusCode': 200, 'body': results}

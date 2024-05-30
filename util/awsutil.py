import os
import boto3
from dotenv import load_dotenv


def create_secrets():

    # Load .env file
    load_dotenv('.env')

    # Initialize Boto3 client for AWS Secrets Manager
    client = boto3.client('secretsmanager')

    # AWS region where the secrets will be stored
    aws_region = os.getenv('AWS_REGION')

    # Iterate over environment variables and create secrets
    for key, value in os.environ.items():
        if key.startswith('AWS_'):  # Skip AWS specific environment variables
            continue

        secret_name = f"{key}"
        secret_value = value

        try:
            response = client.create_secret(
                Name=secret_name,
                SecretString=secret_value,
                Description=f"Secret for {key}",
                Tags=[
                    {
                        'Key': 'Environment',
                        'Value': 'Production'
                    },
                ]
            )
            print(f"Secret {secret_name} created successfully.")
        except client.exceptions.ResourceExistsException:
            # If the secret already exists, update it
            response = client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
            print(f"Secret {secret_name} updated successfully.")
        except Exception as e:
            print(f"Error creating/updating secret {secret_name}: {str(e)}")

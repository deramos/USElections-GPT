import boto3


def create_secrets():

    # Read .env file and extract desired variables
    env_vars = {}
    with open('../.env.prod', 'r') as file:
        for line in file:
            if not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                env_vars[key.strip()] = value.strip()

    # Remove any system-specific variables
    for key in list(env_vars.keys()):
        if key.startswith('SYSTEM_'):
            del env_vars[key]

    # Create or update AWS Secrets Manager secrets
    secret_name = "us-election-gpt-secrets"
    region_name = "us-east-1"
    client = boto3.client('secretsmanager', region_name=region_name)

    response = client.create_secret(
        Name=secret_name,
        SecretString=str(env_vars)
    )

    print(f"Secret created successfully! with response {response}")


if __name__ == "__main__":
    create_secrets()

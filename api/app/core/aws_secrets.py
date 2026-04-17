"""Fetch secrets from AWS Secrets Manager and set as environment variables."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def load_aws_secrets() -> None:
    """Load secrets from AWS Secrets Manager into environment variables.

    Only runs when APP_ENV=production and SPLITTHETEE_SECRET_ARN is set.
    Must be called before Pydantic Settings reads the environment.
    """
    if os.environ.get("APP_ENV") != "production":
        return

    secret_arn = os.environ.get("SPLITTHETEE_SECRET_ARN")
    if not secret_arn:
        return

    try:
        import boto3

        client = boto3.client(
            "secretsmanager",
            region_name=os.environ.get("AWS_SECRET_REGION", "ca-central-1"),
        )
        response = client.get_secret_value(SecretId=secret_arn)
        secrets = json.loads(response["SecretString"])

        for key, value in secrets.items():
            if key not in os.environ:
                os.environ[key] = str(value)

        logger.info("Loaded %d secrets from Secrets Manager", len(secrets))
    except Exception:
        logger.exception("Failed to load secrets from Secrets Manager")
        raise

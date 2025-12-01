import boto3
from botocore.exceptions import ClientError

from api.core.config import settings
from api.core.logging import get_logger

logger = get_logger(__name__)

# S3 prefixes
DATASETS_PREFIX = "datasets"
API_KEYS_PREFIX = "api_keys"
TRACES_PREFIX = "traces"


def get_s3_client():
    """Get an S3 client configured with credentials from settings."""
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


class S3Storage:
    """S3 storage utility for file operations."""

    def __init__(self):
        self.client = get_s3_client()
        self.bucket = settings.S3_BUCKET_NAME

    # ==================== Dataset Methods ====================

    def upload_dataset(self, name: str, content: str) -> None:
        """Upload a dataset JSONL file to S3 from string content.

        Args:
            name: Dataset name (will be stored as {name}.jsonl)
            content: JSONL content as string
        """
        filename = name if name.endswith(".jsonl") else f"{name}.jsonl"
        key = f"{DATASETS_PREFIX}/{filename}"

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType="application/jsonl",
            )
            logger.info(f"Uploaded dataset to S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to upload dataset to S3: {e}")
            raise

    def upload_dataset_file(self, name: str, file_obj) -> None:
        """Upload a dataset JSONL file to S3 from a file object.

        Uses multipart upload for large files (handled automatically by boto3).

        Args:
            name: Dataset name (will be stored as {name}.jsonl)
            file_obj: File-like object (BytesIO, etc.)
        """
        filename = name if name.endswith(".jsonl") else f"{name}.jsonl"
        key = f"{DATASETS_PREFIX}/{filename}"

        try:
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={"ContentType": "application/jsonl"},
            )
            logger.info(f"Uploaded dataset file to S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to upload dataset file to S3: {e}")
            raise

    def download_dataset(self, name: str) -> str:
        """Download a dataset JSONL file from S3.

        Args:
            name: Dataset name

        Returns:
            str: JSONL content

        Raises:
            FileNotFoundError: If the dataset doesn't exist
        """
        filename = name if name.endswith(".jsonl") else f"{name}.jsonl"
        key = f"{DATASETS_PREFIX}/{filename}"

        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            logger.debug(f"Downloaded dataset from S3: {key}")
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Dataset not found in S3: {name}")
            logger.error(f"Failed to download dataset from S3: {e}")
            raise

    def delete_dataset(self, name: str) -> None:
        """Delete a dataset from S3.

        Args:
            name: Dataset name
        """
        filename = name if name.endswith(".jsonl") else f"{name}.jsonl"
        key = f"{DATASETS_PREFIX}/{filename}"

        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted dataset from S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to delete dataset from S3: {e}")
            raise

    # ==================== API Key Methods ====================

    def upload_api_key(self, user_id: int, provider: str, api_key: str) -> None:
        """Upload an API key to S3.

        Args:
            user_id: User ID who owns the key
            provider: Provider name (e.g., 'openai', 'anthropic')
            api_key: The API key value
        """
        key = f"{API_KEYS_PREFIX}/{user_id}/{provider}.txt"

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=api_key.encode("utf-8"),
                ContentType="text/plain",
            )
            logger.info(f"Uploaded API key to S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to upload API key to S3: {e}")
            raise

    def download_api_key(self, user_id: int, provider: str) -> str:
        """Download an API key from S3.

        Args:
            user_id: User ID who owns the key
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            str: The API key value

        Raises:
            FileNotFoundError: If the API key doesn't exist
        """
        key = f"{API_KEYS_PREFIX}/{user_id}/{provider}.txt"

        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            logger.debug(f"Downloaded API key from S3: {key}")
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"API key not found for user {user_id}, provider {provider}")
            logger.error(f"Failed to download API key from S3: {e}")
            raise

    def delete_api_key(self, user_id: int, provider: str) -> None:
        """Delete an API key from S3.

        Args:
            user_id: User ID who owns the key
            provider: Provider name (e.g., 'openai', 'anthropic')
        """
        key = f"{API_KEYS_PREFIX}/{user_id}/{provider}.txt"

        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted API key from S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to delete API key from S3: {e}")
            raise

    def api_key_exists(self, user_id: int, provider: str) -> bool:
        """Check if an API key exists in S3.

        Args:
            user_id: User ID who owns the key
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            bool: True if the API key exists
        """
        key = f"{API_KEYS_PREFIX}/{user_id}/{provider}.txt"

        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False

    def list_user_api_keys(self, user_id: int) -> list[str]:
        """List all API key providers for a user.

        Args:
            user_id: User ID

        Returns:
            list[str]: List of provider names
        """
        prefix = f"{API_KEYS_PREFIX}/{user_id}/"

        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            providers = []
            for obj in response.get("Contents", []):
                # Extract provider name from key: api_keys/{user_id}/{provider}.txt
                filename = obj["Key"].split("/")[-1]
                provider = filename.replace(".txt", "")
                providers.append(provider)
            return providers
        except ClientError as e:
            logger.error(f"Failed to list API keys from S3: {e}")
            raise

    # ==================== Trace Methods ====================

    def upload_trace(self, trace_id: int, content: str) -> None:
        """Upload a trace JSONL file to S3.

        Args:
            trace_id: Trace ID
            content: JSONL content as string
        """
        key = f"{TRACES_PREFIX}/{trace_id}.jsonl"

        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType="application/jsonl",
            )
            logger.info(f"Uploaded trace to S3: {key}")
        except ClientError as e:
            logger.error(f"Failed to upload trace to S3: {e}")
            raise

    def download_trace(self, trace_id: int) -> str:
        """Download a trace JSONL file from S3.

        Args:
            trace_id: Trace ID

        Returns:
            str: JSONL content

        Raises:
            FileNotFoundError: If the trace doesn't exist
        """
        key = f"{TRACES_PREFIX}/{trace_id}.jsonl"

        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            logger.debug(f"Downloaded trace from S3: {key}")
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Trace not found in S3: {trace_id}")
            logger.error(f"Failed to download trace from S3: {e}")
            raise

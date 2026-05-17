import boto3
from botocore.exceptions import NoCredentialsError
from backend.config import settings
import structlog

logger = structlog.get_logger()

class StorageService:
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name='us-east-1'
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=settings.MINIO_BUCKET)
        except:
            self.client.create_bucket(Bucket=settings.MINIO_BUCKET)
            logger.info(f"Bucket {settings.MINIO_BUCKET} created")

    def upload_file(self, file_object, filename: str) -> str:
        try:
            self.client.upload_fileobj(file_object, settings.MINIO_BUCKET, filename)
            return f"{settings.MINIO_BUCKET}/{filename}"
        except NoCredentialsError:
            logger.error("Credentials not available")
            raise Exception("S3 Credentials Error")

    def get_file_url(self, filename: str) -> str:
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{filename}"

storage_service = StorageService()
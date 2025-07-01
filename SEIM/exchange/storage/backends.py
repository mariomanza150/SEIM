"""
Storage backends for secure file storage with cloud support.
"""

import os
from typing import Optional

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class SecureFileStorage(FileSystemStorage):
    """
    Secure file storage backend with additional security features.
    """

    def __init__(
        self,
        location=None,
        base_url=None,
        file_permissions_mode=None,
        directory_permissions_mode=None,
    ):
        super().__init__(
            location=location or settings.MEDIA_ROOT,
            base_url=base_url or settings.MEDIA_URL,
            file_permissions_mode=file_permissions_mode or 0o640,
            directory_permissions_mode=directory_permissions_mode or 0o750,
        )

    def get_valid_name(self, name):
        """
        Return a filename that's safe for use in the target storage system.
        """
        # Remove any path traversal attempts
        name = name.replace("..", "").replace("/", os.sep)
        return super().get_valid_name(name)

    def _save(self, name, content):
        """
        Save file with additional security checks.
        """
        # Ensure the file has been validated before saving
        if not hasattr(content, "_validated"):
            raise ValueError("File must be validated before saving")

        return super()._save(name, content)


@deconstructible
class S3Storage(SecureFileStorage):
    """
    AWS S3 storage backend for production use.
    """

    def __init__(
        self,
        bucket_name=None,
        region=None,
        access_key=None,
        secret_key=None,
        endpoint_url=None,
    ):
        self.bucket_name = bucket_name or settings.AWS_STORAGE_BUCKET_NAME
        self.region = region or settings.AWS_S3_REGION_NAME
        self.access_key = access_key or settings.AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or settings.AWS_SECRET_ACCESS_KEY
        self.endpoint_url = endpoint_url or settings.AWS_S3_ENDPOINT_URL

        # Initialize boto3 client
        import boto3

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            endpoint_url=self.endpoint_url,
        )

        super().__init__()

    def _save(self, name, content):
        """
        Save file to S3 with server-side encryption.
        """
        # Ensure the file has been validated
        if not hasattr(content, "_validated"):
            raise ValueError("File must be validated before saving")

        # Upload to S3 with encryption
        content.seek(0)
        self.s3_client.upload_fileobj(
            content,
            self.bucket_name,
            name,
            ExtraArgs={
                "ServerSideEncryption": "AES256",
                "ContentType": getattr(content, "content_type", "application/octet-stream"),
                "Metadata": {
                    "checksum": getattr(content, "checksum", ""),
                    "original_filename": getattr(content, "name", ""),
                },
            },
        )

        return name

    def url(self, name):
        """
        Generate a presigned URL for secure file access.
        """
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": name},
            ExpiresIn=3600,  # URL expires in 1 hour
        )

    def delete(self, name):
        """
        Delete file from S3.
        """
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=name)

    def exists(self, name):
        """
        Check if file exists in S3.
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=name)
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False


@deconstructible
class AzureStorage(SecureFileStorage):
    """
    Azure Blob Storage backend for production use.
    """

    def __init__(self, account_name=None, account_key=None, container_name=None):
        self.account_name = account_name or settings.AZURE_ACCOUNT_NAME
        self.account_key = account_key or settings.AZURE_ACCOUNT_KEY
        self.container_name = container_name or settings.AZURE_CONTAINER

        # Initialize Azure client
        from azure.storage.blob import BlobServiceClient

        self.blob_service = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential=self.account_key,
        )
        self.container_client = self.blob_service.get_container_client(self.container_name)

        super().__init__()

    def _save(self, name, content):
        """
        Save file to Azure Blob Storage.
        """
        if not hasattr(content, "_validated"):
            raise ValueError("File must be validated before saving")

        blob_client = self.container_client.get_blob_client(name)
        content.seek(0)

        # Upload with metadata
        blob_client.upload_blob(
            content,
            overwrite=True,
            metadata={
                "checksum": getattr(content, "checksum", ""),
                "original_filename": getattr(content, "name", ""),
            },
        )

        return name

    def url(self, name):
        """
        Generate SAS URL for secure file access.
        """
        from datetime import datetime, timedelta

        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{name}?{sas_token}"

    def delete(self, name):
        """
        Delete file from Azure.
        """
        blob_client = self.container_client.get_blob_client(name)
        blob_client.delete_blob()

    def exists(self, name):
        """
        Check if file exists in Azure.
        """
        blob_client = self.container_client.get_blob_client(name)
        return blob_client.exists()


def get_storage_backend(storage_type: Optional[str] = None) -> SecureFileStorage:
    """
    Factory function to get the appropriate storage backend.
    """
    storage_type = storage_type or getattr(settings, "DEFAULT_FILE_STORAGE_TYPE", "local")

    if storage_type == "s3":
        return S3Storage()
    elif storage_type == "azure":
        return AzureStorage()
    else:
        return SecureFileStorage()

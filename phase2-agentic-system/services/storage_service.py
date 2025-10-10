"""
Storage Service for S3/CDN management
"""
import asyncio
import logging
import os
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timedelta
import hashlib
import mimetypes

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

from config import settings

logger = logging.getLogger(__name__)


class StorageServiceError(Exception):
    """Base exception for storage service errors"""
    pass


class UploadError(StorageServiceError):
    """Upload failed"""
    pass


class DownloadError(StorageServiceError):
    """Download failed"""
    pass


class StorageService:
    """Service for managing video storage in S3 and CDN delivery"""

    def __init__(self):
        """Initialize storage service"""
        self.provider = settings.storage_provider
        self.bucket_name = settings.aws_s3_bucket
        self.region = settings.aws_region
        self.cdn_base_url = settings.cdn_base_url

        if self.provider == "aws":
            self._initialize_s3()
        elif self.provider == "gcp":
            self._initialize_gcs()
        else:
            self._initialize_local()

        logger.info(f"Initialized StorageService with provider: {self.provider}")

    def _initialize_s3(self):
        """Initialize AWS S3 client"""
        try:
            config = Config(
                region_name=self.region,
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            )

            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=self.region,
                config=config
            )

            # Verify bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Connected to S3 bucket: {self.bucket_name}")
            except ClientError:
                logger.warning(f"Bucket {self.bucket_name} does not exist or is not accessible")

        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise StorageServiceError("AWS credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise StorageServiceError(f"Failed to initialize S3: {str(e)}")

    def _initialize_gcs(self):
        """Initialize Google Cloud Storage client"""
        # Placeholder for GCS initialization
        logger.info("GCS storage not implemented yet")
        raise NotImplementedError("GCS storage not implemented")

    def _initialize_local(self):
        """Initialize local file storage"""
        self.local_storage_path = "/tmp/nerdx-videos"
        os.makedirs(self.local_storage_path, exist_ok=True)
        logger.info(f"Initialized local storage at: {self.local_storage_path}")

    async def upload_video(
        self,
        video_data: bytes,
        job_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload video to storage

        Args:
            video_data: Video file data as bytes
            job_id: Unique job identifier
            user_id: User identifier
            metadata: Optional metadata to attach

        Returns:
            CDN URL of uploaded video

        Raises:
            UploadError: If upload fails
        """
        try:
            logger.info(f"[{job_id}] Uploading video ({len(video_data)} bytes) for user {user_id}")

            # Generate object key
            object_key = self._generate_object_key(job_id, user_id, "mp4")

            if self.provider == "aws":
                return await self._upload_to_s3(video_data, object_key, metadata, job_id)
            elif self.provider == "local":
                return await self._upload_to_local(video_data, object_key, job_id)
            else:
                raise UploadError(f"Unsupported storage provider: {self.provider}")

        except Exception as e:
            logger.error(f"[{job_id}] Error uploading video: {e}")
            raise UploadError(f"Failed to upload video: {str(e)}")

    async def _upload_to_s3(
        self,
        data: bytes,
        object_key: str,
        metadata: Optional[Dict[str, Any]],
        job_id: str
    ) -> str:
        """Upload to AWS S3"""
        try:
            # Prepare metadata
            s3_metadata = {
                "job_id": job_id,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

            if metadata:
                # S3 metadata keys must be lowercase
                for key, value in metadata.items():
                    s3_metadata[key.lower()] = str(value)

            # Upload to S3
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=object_key,
                Body=data,
                ContentType="video/mp4",
                Metadata=s3_metadata,
                ServerSideEncryption='AES256',
                StorageClass='STANDARD'
            )

            logger.info(f"[{job_id}] Video uploaded to S3: {object_key}")

            # Generate CDN URL
            cdn_url = self._generate_cdn_url(object_key)
            return cdn_url

        except ClientError as e:
            logger.error(f"[{job_id}] S3 upload error: {e}")
            raise UploadError(f"S3 upload failed: {str(e)}")

    async def _upload_to_local(
        self,
        data: bytes,
        object_key: str,
        job_id: str
    ) -> str:
        """Upload to local storage"""
        try:
            file_path = os.path.join(self.local_storage_path, object_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            await asyncio.to_thread(
                self._write_local_file,
                file_path,
                data
            )

            logger.info(f"[{job_id}] Video saved locally: {file_path}")
            return f"file://{file_path}"

        except Exception as e:
            logger.error(f"[{job_id}] Local upload error: {e}")
            raise UploadError(f"Local upload failed: {str(e)}")

    def _write_local_file(self, file_path: str, data: bytes):
        """Write data to local file"""
        with open(file_path, 'wb') as f:
            f.write(data)

    async def upload_thumbnail(
        self,
        thumbnail_data: bytes,
        job_id: str,
        user_id: str
    ) -> str:
        """
        Upload video thumbnail

        Args:
            thumbnail_data: Thumbnail image data
            job_id: Job identifier
            user_id: User identifier

        Returns:
            CDN URL of thumbnail
        """
        try:
            logger.info(f"[{job_id}] Uploading thumbnail ({len(thumbnail_data)} bytes)")

            object_key = self._generate_object_key(job_id, user_id, "jpg")

            if self.provider == "aws":
                await asyncio.to_thread(
                    self.s3_client.put_object,
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=thumbnail_data,
                    ContentType="image/jpeg",
                    Metadata={"job_id": job_id},
                    ServerSideEncryption='AES256'
                )

                logger.info(f"[{job_id}] Thumbnail uploaded to S3: {object_key}")
                return self._generate_cdn_url(object_key)

            elif self.provider == "local":
                file_path = os.path.join(self.local_storage_path, object_key)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                await asyncio.to_thread(
                    self._write_local_file,
                    file_path,
                    thumbnail_data
                )

                logger.info(f"[{job_id}] Thumbnail saved locally: {file_path}")
                return f"file://{file_path}"

        except Exception as e:
            logger.error(f"[{job_id}] Error uploading thumbnail: {e}")
            # Don't raise - thumbnail is optional
            return ""

    async def download_video(
        self,
        object_key: str,
        job_id: str
    ) -> bytes:
        """
        Download video from storage

        Args:
            object_key: Object key in storage
            job_id: Job identifier for logging

        Returns:
            Video data as bytes
        """
        try:
            logger.info(f"[{job_id}] Downloading video: {object_key}")

            if self.provider == "aws":
                response = await asyncio.to_thread(
                    self.s3_client.get_object,
                    Bucket=self.bucket_name,
                    Key=object_key
                )
                video_data = response['Body'].read()

            elif self.provider == "local":
                file_path = os.path.join(self.local_storage_path, object_key)
                with open(file_path, 'rb') as f:
                    video_data = f.read()
            else:
                raise DownloadError(f"Unsupported storage provider: {self.provider}")

            logger.info(f"[{job_id}] Downloaded {len(video_data)} bytes")
            return video_data

        except Exception as e:
            logger.error(f"[{job_id}] Error downloading video: {e}")
            raise DownloadError(f"Failed to download video: {str(e)}")

    async def delete_video(
        self,
        object_key: str,
        job_id: str
    ) -> bool:
        """
        Delete video from storage

        Args:
            object_key: Object key to delete
            job_id: Job identifier for logging

        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"[{job_id}] Deleting video: {object_key}")

            if self.provider == "aws":
                await asyncio.to_thread(
                    self.s3_client.delete_object,
                    Bucket=self.bucket_name,
                    Key=object_key
                )
            elif self.provider == "local":
                file_path = os.path.join(self.local_storage_path, object_key)
                if os.path.exists(file_path):
                    os.remove(file_path)

            logger.info(f"[{job_id}] Video deleted successfully")
            return True

        except Exception as e:
            logger.error(f"[{job_id}] Error deleting video: {e}")
            return False

    async def generate_presigned_url(
        self,
        object_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for temporary access

        Args:
            object_key: Object key
            expiration: URL expiration in seconds

        Returns:
            Presigned URL
        """
        try:
            if self.provider == "aws":
                url = await asyncio.to_thread(
                    self.s3_client.generate_presigned_url,
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_key},
                    ExpiresIn=expiration
                )
                return url
            else:
                # For local storage, return the CDN URL
                return self._generate_cdn_url(object_key)

        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return self._generate_cdn_url(object_key)

    def _generate_object_key(
        self,
        job_id: str,
        user_id: str,
        extension: str
    ) -> str:
        """
        Generate a unique object key for storage

        Args:
            job_id: Job identifier
            user_id: User identifier
            extension: File extension

        Returns:
            Object key path
        """
        # Create a folder structure: videos/{user_id}/{date}/{job_id}.{ext}
        date_path = datetime.utcnow().strftime("%Y/%m/%d")

        if extension == "mp4":
            folder = "videos"
        elif extension in ["jpg", "jpeg", "png"]:
            folder = "thumbnails"
        else:
            folder = "misc"

        object_key = f"{folder}/{user_id}/{date_path}/{job_id}.{extension}"
        return object_key

    def _generate_cdn_url(self, object_key: str) -> str:
        """
        Generate CDN URL for an object

        Args:
            object_key: Object key in storage

        Returns:
            Full CDN URL
        """
        if self.provider == "aws":
            # Use CloudFront or direct S3 URL
            if self.cdn_base_url and self.cdn_base_url != "https://cdn.nerdx.com":
                return f"{self.cdn_base_url}/{object_key}"
            else:
                # Default S3 URL
                return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_key}"
        else:
            return f"{self.cdn_base_url}/{object_key}"

    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage stats
        """
        try:
            if self.provider == "aws":
                # Get bucket metrics
                response = await asyncio.to_thread(
                    self.s3_client.list_objects_v2,
                    Bucket=self.bucket_name,
                    Prefix="videos/"
                )

                total_size = sum(obj.get('Size', 0) for obj in response.get('Contents', []))
                total_objects = response.get('KeyCount', 0)

                return {
                    "provider": "aws",
                    "bucket": self.bucket_name,
                    "total_objects": total_objects,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                }

            elif self.provider == "local":
                total_size = 0
                total_files = 0

                for root, dirs, files in os.walk(self.local_storage_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        total_files += 1

                return {
                    "provider": "local",
                    "path": self.local_storage_path,
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                }

            return {}

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """
        Check if storage service is healthy

        Returns:
            True if healthy
        """
        try:
            if self.provider == "aws":
                await asyncio.to_thread(
                    self.s3_client.head_bucket,
                    Bucket=self.bucket_name
                )
                return True
            elif self.provider == "local":
                return os.path.exists(self.local_storage_path)
            return False

        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False


# Singleton instance
storage_service = StorageService()

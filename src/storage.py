"""Cloud storage uploaders for making videos publicly accessible."""
import os
from typing import Optional
from pathlib import Path
from loguru import logger

from src.config import (
    CDN_BASE_URL,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_REGION
)


class StorageUploader:
    """Base class for storage uploaders."""

    def upload(self, local_path: Path, remote_filename: Optional[str] = None) -> str:
        """Upload file and return public URL."""
        raise NotImplementedError


class S3Uploader(StorageUploader):
    """Upload files to AWS S3 and return public URLs."""

    def __init__(
        self,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        cdn_base: Optional[str] = None
    ):
        self.bucket = bucket or AWS_BUCKET_NAME
        self.region = region or AWS_REGION
        self.access_key = access_key or AWS_ACCESS_KEY_ID
        self.secret_key = secret_key or AWS_SECRET_ACCESS_KEY
        self.cdn_base = cdn_base or CDN_BASE_URL

        # Try to import boto3
        try:
            import boto3
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            self.available = True
        except ImportError:
            logger.warning("boto3 not installed. S3 uploads unavailable.")
            self.available = False
        except Exception as e:
            logger.warning(f"S3 client initialization failed: {e}")
            self.available = False

    def upload(self, local_path: Path, remote_filename: Optional[str] = None) -> str:
        """Upload to S3 and return public URL."""
        if not self.available:
            raise RuntimeError("S3 uploader not available")

        if not remote_filename:
            remote_filename = local_path.name

        # Ensure bucket has public-read or use pre-signed URL
        # For Instagram Graph API, the URL must be publicly accessible
        try:
            self.s3.upload_file(
                str(local_path),
                self.bucket,
                f"reels/{remote_filename}",
                ExtraArgs={"ContentType": "video/mp4", "ACL": "public-read"}
            )

            # Construct URL
            if self.cdn_base:
                url = f"{self.cdn_base.rstrip('/')}/reels/{remote_filename}"
            else:
                url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/reels/{remote_filename}"

            logger.success(f"Uploaded to S3: {url}")
            return url

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise


class LocalUploader(StorageUploader):
    """
    Development-only uploader that copies to a public web directory.

    In production, use S3, Cloudflare R2, or similar.
    """

    def __init__(self, public_dir: Optional[str] = None, base_url: Optional[str] = None):
        self.public_dir = Path(public_dir) if public_dir else Path("/var/www/reels")
        self.base_url = base_url or CDN_BASE_URL or "http://localhost:8000/reels"
        self.public_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, local_path: Path, remote_filename: Optional[str] = None) -> str:
        """Copy to public directory and return URL."""
        if not remote_filename:
            remote_filename = local_path.name

        dest = self.public_dir / remote_filename
        import shutil
        shutil.copy2(str(local_path), str(dest))

        url = f"{self.base_url.rstrip('/')}/{remote_filename}"
        logger.info(f"Local upload (dev): {url}")
        return url


def get_uploader() -> StorageUploader:
    """Factory function to get appropriate uploader based on config."""
    if AWS_ACCESS_KEY_ID and AWS_BUCKET_NAME:
        return S3Uploader()
    else:
        logger.warning("No S3 config found, using local uploader (dev only)")
        return LocalUploader()


if __name__ == "__main__":
    uploader = get_uploader()
    print(f"Using uploader: {type(uploader).__name__}")

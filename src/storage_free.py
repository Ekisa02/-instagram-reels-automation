"""Free cloud storage using Cloudflare R2 (S3-compatible, 10GB free tier)."""
import os
from typing import Optional
from pathlib import Path
from loguru import logger

from src.config_free import (
    R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME, R2_PUBLIC_URL
)


class R2Uploader:
    """
    Upload files to Cloudflare R2 (free tier: 10GB storage + 10M ops/month).
    Setup:
    1. Go to https://dash.cloudflare.com
    2. Sign up (free, no credit card needed)
    3. Go to R2 in sidebar -> Create bucket
    4. Settings -> Allow public access
    5. Manage R2 API Tokens -> Create API Token (Object Read and Write)
    6. Copy Account ID, Access Key ID, Secret Access Key
    """

    def __init__(self):
        self.account_id = R2_ACCOUNT_ID
        self.access_key = R2_ACCESS_KEY_ID
        self.secret_key = R2_SECRET_ACCESS_KEY
        self.bucket = R2_BUCKET_NAME
        self.public_url = R2_PUBLIC_URL

        if not all([self.account_id, self.access_key, self.secret_key, self.bucket]):
            raise ValueError(
                "Cloudflare R2 credentials missing. Get free credentials at: "
                "https://dash.cloudflare.com -> R2 -> Manage API Tokens"
            )

        # R2 uses S3-compatible API
        try:
            import boto3
            from botocore.config import Config

            self.s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version="s3v4")
            )
            logger.info("R2 uploader initialized (free tier)")
        except ImportError:
            raise ImportError("Install boto3: pip install boto3")

    def upload(self, local_path: Path, remote_filename: Optional[str] = None) -> str:
        """Upload file to R2 and return public URL."""
        if not remote_filename:
            remote_filename = local_path.name

        key = f"reels/{remote_filename}"

        try:
            logger.info(f"Uploading to R2: {key}")
            self.s3.upload_file(
                str(local_path),
                self.bucket,
                key,
                ExtraArgs={"ContentType": "video/mp4"}
            )

            # Public URL format
            if self.public_url:
                url = f"{self.public_url.rstrip('/')}/reels/{remote_filename}"
            else:
                # Fallback: construct from bucket endpoint
                url = f"https://{self.account_id}.r2.cloudflarestorage.com/{self.bucket}/reels/{remote_filename}"

            logger.success(f"R2 upload complete: {url}")
            return url

        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            raise


class LocalDevUploader:
    """Development fallback - copies to a local public directory."""

    def __init__(self, public_dir: str = "/tmp/reels-public"):
        self.public_dir = Path(public_dir)
        self.public_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, local_path: Path, remote_filename: Optional[str] = None) -> str:
        if not remote_filename:
            remote_filename = local_path.name
        dest = self.public_dir / remote_filename
        import shutil
        shutil.copy2(str(local_path), str(dest))
        url = f"file://{dest}"
        logger.info(f"Local dev upload: {url}")
        return url


def get_free_uploader():
    """Factory: try R2 first, fallback to local."""
    try:
        return R2Uploader()
    except Exception as e:
        logger.warning(f"R2 not configured: {e}")
        logger.warning("Falling back to local uploader (wont work with Instagram API)")
        return LocalDevUploader()


if __name__ == "__main__":
    uploader = get_free_uploader()
    print(f"Using: {type(uploader).__name__}")

"""Instagram Graph API publisher for Reels."""
import time
import requests
from typing import Optional, Dict
from pathlib import Path
from loguru import logger

from src.config import (
    INSTAGRAM_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    CDN_BASE_URL
)


class InstagramPublisher:
    """
    Publish Reels to Instagram using the official Graph API.

    Requirements:
    - Business or Creator Instagram account
    - Connected Facebook Page
    - Long-lived access token with instagram_content_publish permission
    """

    GRAPH_API_VERSION = "v18.0"
    BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(
        self,
        access_token: Optional[str] = None,
        account_id: Optional[str] = None
    ):
        self.access_token = access_token or INSTAGRAM_ACCESS_TOKEN
        self.account_id = account_id or INSTAGRAM_ACCOUNT_ID

        if not self.access_token or not self.account_id:
            raise ValueError("Instagram access token and account ID are required")

    def upload_reel(
        self,
        video_url: str,
        caption: str,
        cover_url: Optional[str] = None,
        share_to_feed: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict:
        """
        Upload and publish a Reel to Instagram.

        Args:
            video_url: Publicly accessible URL to MP4 video (Instagram fetches this)
            caption: Post caption with hashtags
            cover_url: Optional thumbnail image URL
            share_to_feed: Whether to also share to feed
            max_wait_seconds: Max time to wait for processing

        Returns:
            API response dictionary with published media ID
        """
        logger.info(f"Publishing reel to account {self.account_id}")

        # Step 1: Create media container
        container_id = self._create_container(
            video_url=video_url,
            caption=caption,
            cover_url=cover_url,
            share_to_feed=share_to_feed
        )

        if not container_id:
            raise Exception("Failed to create media container")

        logger.info(f"Container created: {container_id}")

        # Step 2: Wait for processing and publish
        media_id = self._wait_and_publish(
            container_id=container_id,
            max_wait_seconds=max_wait_seconds
        )

        if not media_id:
            raise Exception("Failed to publish reel (processing timeout or error)")

        logger.success(f"Reel published successfully! Media ID: {media_id}")

        return {
            "success": True,
            "media_id": media_id,
            "container_id": container_id,
            "permalink": f"https://instagram.com/p/{media_id}"  # Approximate
        }

    def _create_container(
        self,
        video_url: str,
        caption: str,
        cover_url: Optional[str] = None,
        share_to_feed: bool = True
    ) -> Optional[str]:
        """Create an Instagram media container for a Reel."""
        url = f"{self.BASE_URL}/{self.account_id}/media"

        params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token,
            "share_to_feed": str(share_to_feed).lower()
        }

        if cover_url:
            params["cover_url"] = cover_url

        try:
            response = requests.post(url, params=params, timeout=30)
            data = response.json()

            if response.status_code == 200:
                return data.get("id")
            else:
                logger.error(f"Container creation error: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"Container creation request failed: {e}")
            return None

    def _wait_and_publish(
        self,
        container_id: str,
        max_wait_seconds: int = 300,
        check_interval: int = 5
    ) -> Optional[str]:
        """
        Wait for container processing to complete, then publish.

        Instagram needs time to download and process the video.
        """
        start_time = time.time()

        while (time.time() - start_time) < max_wait_seconds:
            # Check status
            status = self._check_container_status(container_id)

            if status == "FINISHED":
                # Publish now
                return self._publish_container(container_id)
            elif status == "ERROR":
                logger.error(f"Container {container_id} entered error state")
                return None
            elif status == "IN_PROGRESS":
                logger.info(f"Processing... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(check_interval)
            else:
                logger.warning(f"Unknown status: {status}")
                time.sleep(check_interval)

        logger.error(f"Processing timeout after {max_wait_seconds}s")
        return None

    def _check_container_status(self, container_id: str) -> str:
        """Check the processing status of a media container."""
        url = f"{self.BASE_URL}/{container_id}"
        params = {
            "fields": "status_code",
            "access_token": self.access_token
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data.get("status_code", "UNKNOWN")
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return "ERROR"

    def _publish_container(self, container_id: str) -> Optional[str]:
        """Publish a finished container to Instagram."""
        url = f"{self.BASE_URL}/{self.account_id}/media_publish"
        params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }

        try:
            response = requests.post(url, params=params, timeout=30)
            data = response.json()

            if response.status_code == 200:
                return data.get("id")
            else:
                logger.error(f"Publish error: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"Publish request failed: {e}")
            return None

    def get_account_info(self) -> Dict:
        """Get basic info about the Instagram account."""
        url = f"{self.BASE_URL}/{self.account_id}"
        params = {
            "fields": "username,followers_count,follows_count,media_count",
            "access_token": self.access_token
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return {}


if __name__ == "__main__":
    pub = InstagramPublisher()
    info = pub.get_account_info()
    print(f"Account info: {info}")

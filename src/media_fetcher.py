"""Fetch royalty-free stock media from Pexels."""
import os
import requests
import random
from typing import Optional, List
from pathlib import Path
from loguru import logger

from src.config import PEXELS_API_KEY, TEMP_DIR


class MediaFetcher:
    """Fetch stock videos and images from Pexels API."""

    BASE_URL = "https://api.pexels.com/v1"
    VIDEOS_URL = "https://api.pexels.com/videos"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PEXELS_API_KEY
        if not self.api_key:
            logger.warning("No Pexels API key provided. Media fetching will fail.")
        self.headers = {"Authorization": self.api_key}

    def search_videos(
        self, 
        query: str, 
        per_page: int = 5,
        orientation: str = "portrait",
        min_duration: int = 5
    ) -> List[dict]:
        """
        Search for stock videos on Pexels.

        Returns:
            List of video metadata dicts with download links
        """
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }

        try:
            response = requests.get(
                f"{self.VIDEOS_URL}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            videos = []
            for video in data.get("videos", []):
                # Filter by minimum duration
                if video.get("duration", 0) >= min_duration:
                    # Get best quality video file
                    files = sorted(
                        video.get("video_files", []),
                        key=lambda x: x.get("width", 0) * x.get("height", 0),
                        reverse=True
                    )
                    if files:
                        videos.append({
                            "id": video["id"],
                            "url": files[0]["link"],
                            "width": files[0].get("width", 0),
                            "height": files[0].get("height", 0),
                            "duration": video["duration"],
                            "query": query
                        })

            logger.info(f"Found {len(videos)} videos for query: {query}")
            return videos

        except requests.RequestException as e:
            logger.error(f"Failed to fetch videos for '{query}': {e}")
            return []

    def download_video(self, video_url: str, filename: Optional[str] = None) -> Optional[Path]:
        """Download a video to temp directory."""
        if not filename:
            filename = f"stock_{random.randint(10000, 99999)}.mp4"

        filepath = TEMP_DIR / filename

        try:
            logger.info(f"Downloading video: {video_url[:60]}...")
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.success(f"Downloaded: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def get_stock_footage_for_prompts(
        self, 
        prompts: List[str], 
        clips_needed: int = 5
    ) -> List[Path]:
        """
        Fetch stock videos for a list of visual prompts.

        Args:
            prompts: List of search queries
            clips_needed: Number of clips to download

        Returns:
            List of downloaded file paths
        """
        downloaded = []

        for i, prompt in enumerate(prompts[:clips_needed]):
            videos = self.search_videos(prompt, per_page=3)

            if videos:
                # Try each result until one downloads successfully
                for video in videos:
                    filepath = self.download_video(
                        video["url"],
                        f"clip_{i:02d}_{video['id']}.mp4"
                    )
                    if filepath:
                        downloaded.append(filepath)
                        break
            else:
                # Fallback: try a generic niche-related query
                fallback_prompt = random.choice([
                    "business workspace", "city skyline", "person typing",
                    "coffee morning", "sunrise motivation"
                ])
                videos = self.search_videos(fallback_prompt, per_page=2)
                if videos:
                    filepath = self.download_video(
                        videos[0]["url"],
                        f"clip_{i:02d}_fallback.mp4"
                    )
                    if filepath:
                        downloaded.append(filepath)

        logger.info(f"Downloaded {len(downloaded)} stock clips")
        return downloaded


if __name__ == "__main__":
    fetcher = MediaFetcher()
    clips = fetcher.get_stock_footage_for_prompts([
        "person working on laptop",
        "morning coffee sunrise",
        "city skyline night"
    ])
    print(f"Downloaded: {clips}")

"""Main orchestrator for the Instagram Reels automation pipeline."""
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from src.config import validate_config, OUTPUT_DIR, TEMP_DIR, NICHE
from src.script_generator import ScriptGenerator
from src.media_fetcher import MediaFetcher
from src.voice_generator import VoiceGenerator
from src.video_assembler import VideoAssembler
from src.storage import get_uploader
from src.instagram_publisher import InstagramPublisher


class ReelsAutomation:
    """
    End-to-end Instagram Reels automation pipeline.

    Workflow:
    1. Generate script with AI
    2. Fetch stock footage
    3. Generate voiceover
    4. Assemble video
    5. Upload to CDN
    6. Publish to Instagram
    """

    def __init__(self):
        validate_config()

        self.script_gen = ScriptGenerator()
        self.media_fetcher = MediaFetcher()
        self.voice_gen = VoiceGenerator()
        self.assembler = VideoAssembler()
        self.uploader = get_uploader()
        self.publisher = InstagramPublisher()

        logger.info("ReelsAutomation initialized")

    def create_and_publish_reel(
        self,
        topic: Optional[str] = None,
        style: str = "educational",
        dry_run: bool = False
    ) -> dict:
        """
        Execute full pipeline: create one Reel and optionally publish it.

        Args:
            topic: Specific topic (auto-generated if None)
            style: Content style
            dry_run: If True, skip actual publishing (for testing)

        Returns:
            Result dictionary with paths and status
        """
        result = {
            "success": False,
            "topic": None,
            "video_path": None,
            "public_url": None,
            "instagram_media_id": None,
            "error": None
        }

        try:
            # Step 1: Generate script
            logger.info("=== Step 1: Generating Script ===")
            script = self.script_gen.generate_script(topic=topic, style=style)
            result["topic"] = script["topic"]
            logger.info(f"Topic: {script['topic']}")
            logger.info(f"Hook: {script['hook']}")

            # Step 2: Fetch stock footage
            logger.info("=== Step 2: Fetching Stock Footage ===")
            visual_prompts = script.get("visual_prompts", [])
            if not visual_prompts:
                visual_prompts = [script["topic"], NICHE, "motivation"]

            stock_clips = self.media_fetcher.get_stock_footage_for_prompts(
                visual_prompts,
                clips_needed=5
            )

            if len(stock_clips) < 3:
                logger.warning("Few stock clips found, video may have repeated footage")

            # Step 3: Generate voiceover
            logger.info("=== Step 3: Generating Voiceover ===")
            voiceover_text = f"{script['hook']}. {script['script']}"
            voiceover_path = self.voice_gen.generate_voiceover(voiceover_text)

            if not voiceover_path:
                raise Exception("Voiceover generation failed")

            # Step 4: Assemble video
            logger.info("=== Step 4: Assembling Video ===")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"reel_{timestamp}.mp4"

            video_path = self.assembler.assemble_reel(
                script_data=script,
                stock_clips=stock_clips,
                voiceover_path=voiceover_path,
                output_filename=output_filename
            )

            result["video_path"] = str(video_path)

            if dry_run:
                logger.info("=== DRY RUN: Skipping upload and publish ===")
                result["success"] = True
                return result

            # Step 5: Upload to CDN
            logger.info("=== Step 5: Uploading to CDN ===")
            public_url = self.uploader.upload(video_path, remote_filename=output_filename)
            result["public_url"] = public_url

            # Step 6: Publish to Instagram
            logger.info("=== Step 6: Publishing to Instagram ===")
            caption = self._build_caption(script)

            publish_result = self.publisher.upload_reel(
                video_url=public_url,
                caption=caption
            )

            result["instagram_media_id"] = publish_result.get("media_id")
            result["success"] = True

            logger.success("=== Reel Published Successfully ===")
            logger.info(f"Media ID: {result['instagram_media_id']}")

            # Cleanup temp files
            self._cleanup_temp_files()

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result["error"] = str(e)

        return result

    def _build_caption(self, script: dict) -> str:
        """Build Instagram caption from script data."""
        lines = [
            script.get("hook", ""),
            "",
            script.get("script", "")[:150] + "..." if len(script.get("script", "")) > 150 else script.get("script", ""),
            "",
            script.get("cta", "Follow for daily tips! 👇"),
            "",
            " ".join(script.get("hashtags", ["#Reels", "#Viral", "#Tips"]))
        ]
        return "\n".join(lines)

    def _cleanup_temp_files(self):
        """Remove temporary files to save disk space."""
        try:
            for f in TEMP_DIR.glob("*"):
                if f.is_file():
                    f.unlink()
            logger.info("Temp files cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    def run_daily(self, posting_time: str = "09:00"):
        """
        Run the automation daily at specified time.

        Note: In production, use cron or a task scheduler instead of
        keeping a Python process running.
        """
        import schedule

        def job():
            logger.info("Running scheduled reel creation...")
            self.create_and_publish_reel()

        schedule.every().day.at(posting_time).do(job)
        logger.info(f"Scheduler set for {posting_time} daily")

        while True:
            schedule.run_pending()
            time.sleep(60)


def run_once(topic: Optional[str] = None, dry_run: bool = False):
    """CLI entry point for single execution."""
    automation = ReelsAutomation()
    result = automation.create_and_publish_reel(topic=topic, dry_run=dry_run)

    if result["success"]:
        print(f"\n✅ SUCCESS")
        print(f"Topic: {result['topic']}")
        print(f"Video: {result['video_path']}")
        if result['public_url']:
            print(f"URL: {result['public_url']}")
        if result['instagram_media_id']:
            print(f"Instagram Media ID: {result['instagram_media_id']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")

    return result


if __name__ == "__main__":
    run_once()

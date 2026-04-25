"""Zero-budget Instagram Reels automation pipeline."""
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger

from src.config_free import validate_config, OUTPUT_DIR, TEMP_DIR, NICHE
from src.script_generator_free import FreeScriptGenerator
from src.media_fetcher import MediaFetcher
from src.voice_generator_free import FreeVoiceGenerator
from src.video_assembler import VideoAssembler
from src.storage_free import get_free_uploader
from src.instagram_publisher import InstagramPublisher


class ZeroBudgetReelsAutomation:
    """
    Complete free pipeline. No paid APIs required.

    Uses:
    - Groq or Gemini (free) for scripts
    - Edge-TTS (free, unlimited) for voice
    - Pexels (free) for footage
    - Cloudflare R2 (free) for hosting
    - Instagram Graph API (free) for publishing
    """

    def __init__(self):
        validate_config()

        self.script_gen = FreeScriptGenerator()
        self.media_fetcher = MediaFetcher()
        self.voice_gen = FreeVoiceGenerator()
        self.assembler = VideoAssembler()
        self.uploader = get_free_uploader()
        self.publisher = InstagramPublisher()

        logger.info("ZeroBudgetReelsAutomation initialized - $0/month mode")

    def create_and_publish_reel(
        self,
        topic: Optional[str] = None,
        style: str = "educational",
        dry_run: bool = False
    ) -> dict:
        """Execute full free pipeline."""
        result = {
            "success": False,
            "topic": None,
            "video_path": None,
            "public_url": None,
            "instagram_media_id": None,
            "error": None
        }

        try:
            # Step 1: Generate script (free AI)
            logger.info("=== Step 1: Generating Script (Free AI) ===")
            script = self.script_gen.generate_script(topic=topic, style=style)
            result["topic"] = script["topic"]
            logger.info(f"Topic: {script['topic']}")

            # Step 2: Fetch stock footage (free)
            logger.info("=== Step 2: Fetching Stock Footage (Free) ===")
            visual_prompts = script.get("visual_prompts", [])
            if not visual_prompts:
                visual_prompts = [script["topic"], NICHE, "motivation"]

            stock_clips = self.media_fetcher.get_stock_footage_for_prompts(
                visual_prompts, clips_needed=5
            )

            # Step 3: Generate voiceover (free Edge-TTS)
            logger.info("=== Step 3: Generating Voiceover (Free TTS) ===")
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

            # Step 5: Upload to free CDN
            logger.info("=== Step 5: Uploading to Free CDN ===")
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

            logger.success("=== Reel Published (Zero Budget) ===")

            # Cleanup
            self._cleanup_temp_files()

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result["error"] = str(e)

        return result

    def _build_caption(self, script: dict) -> str:
        """Build Instagram caption."""
        lines = [
            script.get("hook", ""),
            "",
            script.get("script", "")[:150] + "..." if len(script.get("script", "")) > 150 else script.get("script", ""),
            "",
            script.get("cta", "Follow for daily tips!"),
            "",
            " ".join(script.get("hashtags", ["#Reels", "#Viral", "#Tips"]))
        ]
        return "\n".join(lines)

    def _cleanup_temp_files(self):
        """Remove temp files."""
        try:
            for f in TEMP_DIR.glob("*"):
                if f.is_file():
                    f.unlink()
            logger.info("Temp files cleaned")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")

    def run_daily(self, posting_time: str = "09:00"):
        """Daily scheduler."""
        import schedule

        def job():
            logger.info("Running scheduled reel...")
            self.create_and_publish_reel()

        schedule.every().day.at(posting_time).do(job)
        logger.info(f"Scheduler set for {posting_time} daily")

        while True:
            schedule.run_pending()
            time.sleep(60)


def run_once_free(topic: Optional[str] = None, dry_run: bool = False):
    """CLI entry point for zero-budget mode."""
    automation = ZeroBudgetReelsAutomation()
    result = automation.create_and_publish_reel(topic=topic, dry_run=dry_run)

    if result["success"]:
        print(f"\nSUCCESS (Zero Budget)")
        print(f"Topic: {result['topic']}")
        print(f"Video: {result['video_path']}")
        if result['public_url']:
            print(f"URL: {result['public_url']}")
        if result['instagram_media_id']:
            print(f"Instagram Media ID: {result['instagram_media_id']}")
    else:
        print(f"\nFAILED: {result['error']}")

    return result


if __name__ == "__main__":
    run_once_free()

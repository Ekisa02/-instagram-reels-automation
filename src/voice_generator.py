"""AI voiceover generation using ElevenLabs."""
import os
import requests
import time
from typing import Optional
from pathlib import Path
from loguru import logger

from src.config import (
    ELEVENLABS_API_KEY, 
    ELEVENLABS_VOICE_ID, 
    TEMP_DIR
)


class VoiceGenerator:
    """Generate natural-sounding voiceovers with ElevenLabs."""

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(
        self, 
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        self.api_key = api_key or ELEVENLABS_API_KEY
        self.voice_id = voice_id or ELEVENLABS_VOICE_ID

        if not self.api_key:
            logger.warning("No ElevenLabs API key provided. Voice generation will fail.")

    def generate_voiceover(
        self, 
        text: str, 
        output_filename: str = "voiceover.mp3",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.3,
        model: str = "eleven_multilingual_v2"
    ) -> Optional[Path]:
        """
        Generate voiceover from text.

        Args:
            text: Script text to convert to speech
            output_filename: Output filename
            stability: Voice stability (0-1)
            similarity_boost: Similarity boost (0-1)
            style: Style exaggeration (0-1)
            model: ElevenLabs model ID

        Returns:
            Path to generated audio file or None
        """
        if not self.api_key:
            logger.error("Cannot generate voiceover: No API key")
            return None

        url = f"{self.BASE_URL}/text-to-speech/{self.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }
        }

        try:
            logger.info(f"Generating voiceover ({len(text)} chars)...")

            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()

            output_path = TEMP_DIR / output_filename
            with open(output_path, "wb") as f:
                f.write(response.content)

            # Verify file was created and has content
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.success(f"Voiceover saved: {output_path}")
                return output_path
            else:
                logger.error("Voiceover file is empty")
                return None

        except requests.RequestException as e:
            logger.error(f"Voiceover generation failed: {e}")
            return None

    def get_voice_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds using ffprobe via moviepy."""
        try:
            # MoviePy 2.x compatible
            try:
                from moviepy import AudioFileClip
            except ImportError:
                from moviepy.editor import AudioFileClip

            with AudioFileClip(str(audio_path)) as audio:
                return audio.duration
        except Exception as e:
            logger.error(f"Could not get audio duration: {e}")
            return 60.0  # Default fallback


if __name__ == "__main__":
    gen = VoiceGenerator()
    path = gen.generate_voiceover(
        "Here are 5 productivity hacks that completely changed how I work. Number one: the two-minute rule."
    )
    print(f"Generated: {path}")

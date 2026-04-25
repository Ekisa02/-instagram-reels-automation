"""Free voiceover generation using Microsoft Edge TTS (no API key needed)."""
import asyncio
import edge_tts
from pathlib import Path
from typing import Optional
from loguru import logger

from src.config_free import TEMP_DIR, ELEVENLABS_API_KEY, USE_EDGE_TTS

# Optional: ElevenLabs free tier (10k chars/month)
try:
    from src.voice_generator import VoiceGenerator as ElevenLabsVoice
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False


class FreeVoiceGenerator:
    """
    Free voiceover generation.
    Priority: ElevenLabs free tier -> Edge-TTS (unlimited, free)
    """

    # Edge-TTS voices (high quality, free, no key needed)
    VOICES = {
        "us_male": "en-US-GuyNeural",
        "us_female": "en-US-JennyNeural",
        "uk_male": "en-GB-RyanNeural",
        "uk_female": "en-GB-SoniaNeural",
        "australian_male": "en-AU-WilliamNeural",
        "australian_female": "en-AU-NatashaNeural",
        "indian_male": "en-IN-PrabhatNeural",
        "indian_female": "en-IN-NeerjaNeural",
    }

    def __init__(self, voice: str = "us_male"):
        self.voice = self.VOICES.get(voice, "en-US-GuyNeural")
        self.elevenlabs = None

        # Try ElevenLabs first if key exists (free tier)
        if ELEVENLABS_API_KEY and ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs = ElevenLabsVoice()
                logger.info("Using ElevenLabs free tier for voiceover")
            except Exception:
                pass

        if not self.elevenlabs:
            logger.info(f"Using Edge-TTS (free, unlimited): {self.voice}")

    def generate_voiceover(
        self, 
        text: str, 
        output_filename: str = "voiceover.mp3"
    ) -> Optional[Path]:
        """Generate voiceover file."""

        # Try ElevenLabs first (better quality, but limited free chars)
        if self.elevenlabs:
            try:
                result = self.elevenlabs.generate_voiceover(text, output_filename)
                if result:
                    return result
                logger.warning("ElevenLabs free tier exhausted, falling back to Edge-TTS")
            except Exception as e:
                logger.warning(f"ElevenLabs failed: {e}, using Edge-TTS")

        # Edge-TTS: completely free, unlimited
        return self._generate_with_edge_tts(text, output_filename)

    def _generate_with_edge_tts(self, text: str, output_filename: str) -> Optional[Path]:
        """Generate voice using Microsoft Edge TTS (no API key, no limits)."""
        output_path = TEMP_DIR / output_filename

        try:
            logger.info(f"Generating Edge-TTS voiceover ({len(text)} chars)...")

            # Edge-TTS requires async
            asyncio.run(self._edge_tts_speak(text, str(output_path)))

            if output_path.exists() and output_path.stat().st_size > 0:
                logger.success(f"Edge-TTS voiceover saved: {output_path}")
                return output_path
            else:
                logger.error("Edge-TTS produced empty file")
                return None

        except Exception as e:
            logger.error(f"Edge-TTS failed: {e}")
            return None

    async def _edge_tts_speak(self, text: str, output_path: str):
        """Async helper for Edge-TTS."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def get_voice_duration(self, audio_path: Path) -> float:
        """Get audio duration using ffprobe via moviepy."""
        try:
            from moviepy.editor import AudioFileClip
            with AudioFileClip(str(audio_path)) as audio:
                return audio.duration
        except Exception as e:
            logger.error(f"Could not get duration: {e}")
            # Rough estimate: ~150 words per minute
            return 60.0


if __name__ == "__main__":
    gen = FreeVoiceGenerator()
    path = gen.generate_voiceover(
        "Here are 5 productivity hacks that completely changed how I work. Number one: the two-minute rule."
    )
    print(f"Generated: {path}")

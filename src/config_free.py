"""Zero-budget configuration using free API alternatives."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = ASSETS_DIR / "temp"
OUTPUT_DIR = ASSETS_DIR / "output"
FONTS_DIR = ASSETS_DIR / "fonts"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# ZERO BUDGET MODE: Free API Alternatives
# ============================================================

# Option 1: Groq (Free tier: 20 requests/min, 1,000,000 tokens/day)
# Sign up: https://console.groq.com - Free, no credit card required
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Option 2: Google Gemini (Free tier: 60 requests/min)
# Sign up: https://aistudio.google.com/app/apikey - Free, no credit card required
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Fallback priority: Groq -> Gemini -> None
# You only need ONE of these two.

# ElevenLabs (Free tier: 10,000 characters/month ~ 3 reels)
# If you run out, system falls back to Edge-TTS (completely free)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# Pexels (Free, 200 requests/hour)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Instagram Graph API (Free)
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# Cloudflare R2 (Free tier: 10GB storage, 10M Class A ops, 1M Class B ops/month)
# Sign up: https://dash.cloudflare.com - Free, add R2 from sidebar
# Or use AWS S3 if you have credits. Otherwise R2 is the best free option.
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")  # e.g., https://pub-yourhash.r2.dev

# Content
NICHE = os.getenv("NICHE", "productivity")
POSTING_TIME = os.getenv("POSTING_TIME", "09:00")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# Video
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")
AUDIO_CODEC = os.getenv("AUDIO_CODEC", "aac")

# Zero-budget flags
USE_GROQ = bool(GROQ_API_KEY)
USE_GEMINI = bool(GEMINI_API_KEY and not GROQ_API_KEY)  # Prefer Groq
USE_EDGE_TTS = not bool(ELEVENLABS_API_KEY)  # Fallback to free TTS


def validate_config():
    """Validate that minimum configuration is present."""
    required = {
        "INSTAGRAM_ACCESS_TOKEN": INSTAGRAM_ACCESS_TOKEN,
        "INSTAGRAM_ACCOUNT_ID": INSTAGRAM_ACCOUNT_ID,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required config: {', '.join(missing)}")

    if not GROQ_API_KEY and not GEMINI_API_KEY:
        raise ValueError(
            "Missing AI provider. Get a free key from: "
            "Groq (https://console.groq.com) or "
            "Gemini (https://aistudio.google.com/app/apikey)"
        )

    if not R2_PUBLIC_URL and not os.getenv("CDN_BASE_URL"):
        raise ValueError(
            "Missing public URL for video hosting. Use Cloudflare R2 (free): "
            "https://dash.cloudflare.com -> R2 -> Create bucket -> Allow public access"
        )

    return True

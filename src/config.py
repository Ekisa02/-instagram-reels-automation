"""Configuration management for Instagram Reels Automation."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = ASSETS_DIR / "temp"
OUTPUT_DIR = ASSETS_DIR / "output"
FONTS_DIR = ASSETS_DIR / "fonts"

# Ensure directories exist
TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# CDN / Storage
CDN_BASE_URL = os.getenv("CDN_BASE_URL", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Content Settings
NICHE = os.getenv("NICHE", "productivity")
POSTING_TIME = os.getenv("POSTING_TIME", "09:00")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# Video Settings
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "30"))
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")
AUDIO_CODEC = os.getenv("AUDIO_CODEC", "aac")
VIDEO_DURATION = 60  # Target duration in seconds

# Validation
def validate_config():
    """Validate that required configuration is present."""
    required = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "INSTAGRAM_ACCESS_TOKEN": INSTAGRAM_ACCESS_TOKEN,
        "INSTAGRAM_ACCOUNT_ID": INSTAGRAM_ACCOUNT_ID,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    return True

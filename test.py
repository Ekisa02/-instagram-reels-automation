#!/usr/bin/env python3
"""Test script to validate all components without full execution."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")

def test_config():
    """Test configuration loading."""
    try:
        from src.config import validate_config, OPENAI_API_KEY
        validate_config()
        logger.success("Configuration: OK")
        return True
    except Exception as e:
        logger.error(f"Configuration: FAIL - {e}")
        return False

def test_script_generator():
    """Test OpenAI script generation."""
    try:
        from src.script_generator import ScriptGenerator
        gen = ScriptGenerator()
        # We won't actually call the API in tests, just verify initialization
        logger.success("Script Generator: OK")
        return True
    except Exception as e:
        logger.error(f"Script Generator: FAIL - {e}")
        return False

def test_media_fetcher():
    """Test Pexels media fetcher."""
    try:
        from src.media_fetcher import MediaFetcher
        fetcher = MediaFetcher()
        logger.success("Media Fetcher: OK")
        return True
    except Exception as e:
        logger.error(f"Media Fetcher: FAIL - {e}")
        return False

def test_voice_generator():
    """Test ElevenLabs voice generator."""
    try:
        from src.voice_generator import VoiceGenerator
        gen = VoiceGenerator()
        logger.success("Voice Generator: OK")
        return True
    except Exception as e:
        logger.error(f"Voice Generator: FAIL - {e}")
        return False

def test_video_assembler():
    """Test MoviePy video assembler."""
    try:
        from src.video_assembler import VideoAssembler
        from src.config import VIDEO_WIDTH, VIDEO_HEIGHT
        assembler = VideoAssembler()
        assert assembler.width == VIDEO_WIDTH
        assert assembler.height == VIDEO_HEIGHT
        logger.success("Video Assembler: OK")
        return True
    except Exception as e:
        logger.error(f"Video Assembler: FAIL - {e}")
        return False

def test_instagram_publisher():
    """Test Instagram publisher initialization."""
    try:
        from src.instagram_publisher import InstagramPublisher
        pub = InstagramPublisher()
        logger.success("Instagram Publisher: OK")
        return True
    except Exception as e:
        logger.error(f"Instagram Publisher: FAIL - {e}")
        return False

def test_storage():
    """Test storage uploader."""
    try:
        from src.storage import get_uploader
        uploader = get_uploader()
        logger.success(f"Storage: OK ({type(uploader).__name__})")
        return True
    except Exception as e:
        logger.error(f"Storage: FAIL - {e}")
        return False

def main():
    print("=" * 50)
    print("Instagram Reels Automation - Component Tests")
    print("=" * 50)

    tests = [
        ("Configuration", test_config),
        ("Script Generator", test_script_generator),
        ("Media Fetcher", test_media_fetcher),
        ("Voice Generator", test_voice_generator),
        ("Video Assembler", test_video_assembler),
        ("Instagram Publisher", test_instagram_publisher),
        ("Storage", test_storage),
    ]

    results = []
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        results.append(test_func())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} passed")

    if all(results):
        print("All systems operational!")
        return 0
    else:
        print("Some components failed. Check configuration and dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

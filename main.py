#!/usr/bin/env python3
"""
Instagram Reels Automation System

Usage:
    python main.py --free --topic "productivity tips" --dry-run
    python main.py --free --daily --time 09:00
    python main.py --setup
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger

def setup_logging():
    logger.add(
        "logs/reels_automation.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║           Instagram Reels AI Automation System                ║
║                                                               ║
║  Mode: --free (Zero Budget)  |  Paid APIs (default)          ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description="Instagram Reels Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  FREE MODE (no credit card needed):
    %(prog)s --free                          Run with free APIs
    %(prog)s --free --topic "AI tools"       Specific topic, free mode
    %(prog)s --free --dry-run                Test without publishing
    %(prog)s --free --daily --time 09:00     Daily automation, free

  PAID MODE (better quality):
    %(prog)s --topic "AI tools"              Use OpenAI + ElevenLabs
    %(prog)s --daily --time 14:00            Daily with paid APIs

  SETUP:
    %(prog)s --setup                         Show setup instructions
    %(prog)s --validate                      Check configuration
        """
    )

    parser.add_argument("--free", action="store_true", help="Use zero-budget free APIs (Groq, Edge-TTS, R2)")
    parser.add_argument("--topic", "-t", type=str, help="Specific topic for the reel")
    parser.add_argument("--style", "-s", type=str, default="educational", choices=["educational", "motivational", "storytelling", "trending"])
    parser.add_argument("--dry-run", "-d", action="store_true", help="Create video but skip publishing")
    parser.add_argument("--daily", action="store_true", help="Run continuously and post daily")
    parser.add_argument("--time", type=str, default="09:00", help="Posting time for daily mode (HH:MM)")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions and exit")
    parser.add_argument("--validate", action="store_true", help="Validate configuration and exit")

    args = parser.parse_args()

    if args.setup:
        if args.free:
            print_zero_budget_setup()
        else:
            print_paid_setup()
        return

    print_banner()
    setup_logging()

    # Choose mode
    if args.free:
        run_free_mode(args)
    else:
        run_paid_mode(args)


def run_free_mode(args):
    """Run zero-budget pipeline."""
    print("\n[ZERO BUDGET MODE] Using free APIs:")
    print("  - Scripts: Groq or Gemini (free)")
    print("  - Voice: Edge-TTS (free, unlimited)")
    print("  - Storage: Cloudflare R2 (free, 10GB/mo)")
    print("  - Cost: $0/month\n")

    from src.config_free import validate_config
    from src.scheduler_free import run_once_free, ZeroBudgetReelsAutomation

    if args.validate:
        try:
            validate_config()
            print("Zero-budget configuration is valid!")
        except ValueError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
        return

    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Run: python main.py --free --setup")
        sys.exit(1)

    if args.daily:
        print(f"Starting free daily scheduler (posts at {args.time})")
        print("Press Ctrl+C to stop")
        automation = ZeroBudgetReelsAutomation()
        automation.run_daily(posting_time=args.time)
    else:
        print(f"Creating reel (free mode)...")
        if args.topic:
            print(f"Topic: {args.topic}")
        if args.dry_run:
            print("Mode: DRY RUN (no publishing)")

        result = run_once_free(topic=args.topic, dry_run=args.dry_run)
        if not result["success"]:
            sys.exit(1)


def run_paid_mode(args):
    """Run paid pipeline (original system)."""
    print("\n[PAID MODE] Using premium APIs:")
    print("  - Scripts: OpenAI GPT-4o")
    print("  - Voice: ElevenLabs")
    print("  - Storage: AWS S3 or custom")
    print("  - Cost: ~$6-10/month\n")

    from src.config import validate_config
    from src.scheduler import run_once, ReelsAutomation

    if args.validate:
        try:
            validate_config()
            print("Paid configuration is valid!")
        except ValueError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
        return

    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Run: python main.py --setup")
        sys.exit(1)

    if args.daily:
        print(f"Starting daily scheduler (posts at {args.time})")
        print("Press Ctrl+C to stop")
        automation = ReelsAutomation()
        automation.run_daily(posting_time=args.time)
    else:
        print(f"Creating reel...")
        result = run_once(topic=args.topic, dry_run=args.dry_run)
        if not result["success"]:
            sys.exit(1)


def print_zero_budget_setup():
    print("""
ZERO BUDGET SETUP ($0/month)
═════════════════════════════

1. GET FREE API KEYS (no credit card)
   ├─ Groq:        https://console.groq.com  (1M tokens/day free)
   ├─ Pexels:      https://www.pexels.com/api  (200 req/hour free)
   ├─ Cloudflare:  https://dash.cloudflare.com/sign-up  (10GB R2 free)
   └─ Instagram:   Convert to Business + Meta Developer  (25 posts/day free)

2. INSTALL
   pip install -r requirements.txt

3. CONFIGURE
   cp .env.example .env
   # Edit .env with your free keys

4. RUN
   python main.py --free --validate
   python main.py --free --dry-run
   python main.py --free --topic "your topic"

For detailed steps: see ZERO_BUDGET_SETUP.md
""")

def print_paid_setup():
    print("""
PAID SETUP (~$6-10/month)
══════════════════════════

1. GET API KEYS
   ├─ OpenAI:      https://platform.openai.com
   ├─ ElevenLabs:  https://elevenlabs.io
   ├─ Pexels:      https://www.pexels.com/api
   └─ Instagram:   Meta Developer + Business Account

2. INSTALL
   pip install -r requirements.txt

3. CONFIGURE
   cp .env.example .env
   # Edit .env with your keys

4. RUN
   python main.py --validate
   python main.py --dry-run
   python main.py --topic "your topic"

For detailed steps: see README.md
""")


if __name__ == "__main__":
    main()

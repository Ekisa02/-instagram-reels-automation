# Instagram Reels AI Automation System

A production-ready Python system that generates original Instagram Reels using AI (GPT-4 for scripts, ElevenLabs for voiceovers, Pexels for royalty-free stock footage) and publishes them via the official Instagram Graph API.

> **This creates ORIGINAL content.** It does NOT scrape, repost, or steal viral videos. That approach violates Instagram's Terms of Service and copyright law.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  AI Script Gen  │────▶│  Video Assembly  │────▶│  Graph API Post │
│  (GPT-4/Claude) │     │ (MoviePy/FFmpeg) │     │ (Official API)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Trend Analysis  │     │  AI Voice +      │     │  Schedule/Queue │
│ (Google Trends, │     │  Stock Footage   │     │  (Cron/Docker)  │
│  TikTok Creative│     │  (Pexels/Pixabay)│     │                 │
│  Center)        │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Features

- **AI Script Generation**: GPT-4o creates viral-style hooks, scripts, captions, and visual prompts
- **Royalty-Free Footage**: Fetches HD stock videos from Pexels API
- **AI Voiceovers**: Natural-sounding narration via ElevenLabs
- **Professional Editing**: Auto-assembles 1080x1920 Reels with animated captions
- **Official API Publishing**: Posts via Instagram Graph API (no browser automation)
- **Scheduling**: Cron-based or continuous daily posting
- **Docker Support**: Containerized deployment ready

---

## Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd instagram-reels-automation
pip install -r requirements.txt

# System dependencies (Ubuntu/Debian)
sudo apt-get install ffmpeg imagemagick fonts-liberation
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Validate & Test

```bash
# Check configuration
python main.py --validate

# Create a reel without publishing (dry run)
python main.py --dry-run

# Create and publish a reel
python main.py --topic "productivity hacks"
```

---

## Required API Keys

| Service | Purpose | Cost |
|---------|---------|------|
| **OpenAI** | Script generation | ~$0.03/reel |
| **ElevenLabs** | AI voiceover | ~$0.15/reel |
| **Pexels** | Stock footage | Free |
| **Meta Graph API** | Publishing | Free |
| **AWS S3/R2** | Video hosting | ~$0.10/reel |

**Total per reel: ~$0.30 | Monthly (daily): ~$9-15**

---

## Instagram API Setup

### Step 1: Convert Account
- Go to Instagram → Settings → Account → Switch to Professional Account
- Choose **Business** or **Creator**

### Step 2: Connect Facebook Page
- Settings → Account → Linked Accounts → Facebook
- Link an existing Page or create new

### Step 3: Create Meta App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create App → Select **Business** type
3. Add products:
   - Instagram Basic Display
   - Instagram Graph API

### Step 4: Generate Access Token
```bash
# Use Graph API Explorer
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_SHORT_TOKEN"

# Exchange for Long-Lived Token (60 days)
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN"
```

### Step 5: Get Account ID
```bash
curl -X GET "https://graph.facebook.com/v18.0/me?fields=instagram_business_account&access_token=TOKEN"
```

---

## Configuration (.env)

```ini
# AI Services
OPENAI_API_KEY=sk-your-openai-key
ELEVENLABS_API_KEY=your-elevenlabs-key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Media
PEXELS_API_KEY=your-pexels-key

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=your-long-lived-token
INSTAGRAM_ACCOUNT_ID=17841400000000000

# Cloud Storage (publicly accessible for Instagram)
CDN_BASE_URL=https://your-cdn.com/reels
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_BUCKET_NAME=...
AWS_REGION=us-east-1

# Content
NICHE=productivity
POSTING_TIME=09:00
```

---

## Usage

### Single Post
```bash
# Auto-generate topic
python main.py

# Specific topic
python main.py --topic "AI tools for entrepreneurs"

# Specific style
python main.py --style motivational --topic "morning routines"
```

### Daily Automation
```bash
# Run continuously (keeps process alive)
python main.py --daily --time 09:00

# Or use cron (recommended)
crontab -e
# Add: 0 9 * * * cd /path/to/project && ./cron/daily-post.sh
```

### Docker
```bash
# Build
docker-compose build

# Dry run
docker-compose up reels-automation

# Daily scheduled (keeps running)
docker-compose up reels-automation --command "python main.py --daily --time 09:00"

# With cron profile
docker-compose --profile cron up reels-cron
```

---

## Project Structure

```
instagram-reels-automation/
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container image
├── docker-compose.yml      # Docker orchestration
├── .env.example            # Configuration template
├── .gitignore
├── cron/
│   ├── daily-post.sh       # Cron execution script
│   └── crontab.example     # Example crontab entries
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── script_generator.py # GPT-4 script generation
│   ├── media_fetcher.py    # Pexels stock footage
│   ├── voice_generator.py  # ElevenLabs voiceover
│   ├── video_assembler.py  # MoviePy video editing
│   ├── storage.py          # S3/R2/CDN uploaders
│   ├── instagram_publisher.py # Graph API publishing
│   └── scheduler.py        # Pipeline orchestrator
├── assets/
│   ├── temp/               # Temporary files (cleaned)
│   ├── output/             # Final video files
│   └── fonts/              # Custom fonts (optional)
└── logs/                   # Execution logs
```

---

## How It Works

### 1. Script Generation (`src/script_generator.py`)
- Sends niche/topic to GPT-4o
- Returns structured JSON: hook, script, captions, visual prompts, hashtags
- Optimized for 60-90 second Reels with pattern-interrupt hooks

### 2. Media Fetching (`src/media_fetcher.py`)
- Searches Pexels API using visual prompts from script
- Downloads 5 HD portrait videos
- Falls back to generic queries if specific search returns no results

### 3. Voice Generation (`src/voice_generator.py`)
- Sends full script to ElevenLabs API
- Uses `eleven_multilingual_v2` model for natural speech
- Returns MP3 file synced to video duration

### 4. Video Assembly (`src/video_assembler.py`)
- Concatenates stock clips to match voiceover duration
- Resizes all footage to 1080x1920 (9:16)
- Adds animated captions with stroke effects
- Displays hook overlay (first 3s, gold text)
- Displays CTA overlay (last 5s)

### 5. Publishing (`src/instagram_publisher.py`)
- Uploads video to public CDN (S3/R2)
- Creates Instagram media container via Graph API
- Polls for processing completion
- Publishes to account feed

---

## Instagram Limits & Policies (2026)

| Limit | Value |
|-------|-------|
| Posts per 24h | 25 |
| Video duration | 3s - 60min |
| Aspect ratio | 9:16 (1080x1920 recommended) |
| File size | Max 4GB |
| Caption length | Max 2,200 characters |
| Hashtags | Max 30 |

**Policy Compliance:**
- This system creates **original** content
- No scraping, reposting, or copyright violation
- No fake engagement or bot behavior
- Complies with Instagram Graph API Terms

Violating these (e.g., scraping viral videos) results in:
- Strike 1: 14-30 day shadowban
- Strike 2: 90-day feature suspension
- Strike 3: Permanent account disablement

---

## Customization

### Change Niche
Edit `.env`:
```ini
NICHE=fitness
```

### Custom Voice
1. Clone/create voice in ElevenLabs dashboard
2. Copy Voice ID
3. Update `.env`: `ELEVENLABS_VOICE_ID=your-voice-id`

### Add Background Music
1. Add royalty-free MP3 to `assets/music/`
2. Modify `video_assembler.py` to mix audio tracks
3. Adjust `music_volume` parameter

### Custom Fonts
1. Add `.ttf` files to `assets/fonts/`
2. Update font references in `video_assembler.py`

### Content Calendar
Modify `script_generator.py` `_generate_topic()` to pull from a content calendar CSV or Notion database.

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `Container creation failed` | Check access token; ensure `instagram_content_publish` permission |
| `Processing timeout` | Video URL must be publicly accessible; check CDN |
| `No module named 'moviepy'` | Run `pip install -r requirements.txt` |
| `Voiceover empty` | Check ElevenLabs credits and API key |
| `ImageMagick policy error` | Run `sed` commands from Dockerfile or use Docker |
| `Rate limited by Pexels` | Free tier: 200 requests/hour. Add delays or upgrade |

---

## Cost Breakdown

**Per Reel:**
- OpenAI GPT-4: ~$0.03 (1,500 tokens)
- ElevenLabs: ~$0.15 (90 seconds)
- Pexels: $0 (free)
- AWS S3: ~$0.02 (storage + bandwidth)
- **Total: ~$0.20/reel**

**Monthly (30 reels):**
- **~$6-9/month** (depending on API usage)

Compare to:
- Hiring editor: $500-2,000/month
- Buying engagement bait courses: $50-500 (scam)

---

## Roadmap

- [ ] Add TikTok/YouTube Shorts cross-posting
- [ ] Integrate trending topic detection (Google Trends API)
- [ ] Add AI-generated B-roll with Runway/Stable Video
- [ ] Analytics dashboard (engagement tracking)
- [ ] A/B testing for hooks and thumbnails
- [ ] Notion/Airtable content calendar integration

---

## License

MIT License - Use at your own risk. Comply with all platform Terms of Service.

## Disclaimer

This tool is for **original content creation only**. The creator is not responsible for:
- Account bans due to policy violations
- Copyright infringement from user-uploaded assets
- Misleading claims about income potential

The "₹750,000/month" claim from viral posts is unrealistic for 99% of accounts. Building a real audience takes 6-12 months of consistent, valuable content.
# -instagram-reels-automation

# Zero-Budget Setup Guide
## Run Instagram Reels Automation for $0/Month

This guide assumes you have **no money, no credit card, and no existing API accounts**.

---

## What You Need (All Free)

| Requirement | Cost | Time to Set Up |
|-------------|------|----------------|
| Groq Account | $0 | 2 minutes |
| Pexels Account | $0 | 2 minutes |
| Cloudflare Account | $0 | 3 minutes |
| Instagram Business Account | $0 | 5 minutes |
| Meta Developer Account | $0 | 5 minutes |
| Python + FFmpeg | $0 | 10 minutes |
| **Total** | **$0** | **~30 minutes** |

---

## Step 1: Install Software

### Python (Windows/Mac/Linux)
1. Go to https://python.org/downloads
2. Download Python 3.11 or 3.12
3. Install with "Add Python to PATH" checked

### FFmpeg (Required for video processing)

**Windows:**
1. Download from https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

**Mac:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg -y
```

---

## Step 2: Get Free API Keys

### 2A. Groq (Free AI for Scripts)
1. Go to https://console.groq.com
2. Sign up with email or Google (no credit card)
3. Click "API Keys" in the sidebar
4. Create new key → copy it
5. **Free limit:** 1,000,000 tokens/day (enough for ~600 reels/day)

> **Alternative:** If Groq doesn't work in your country, use Google Gemini (step 2B).

### 2B. Google Gemini (Backup AI)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key
5. **Free limit:** 60 requests/minute

### 2C. Pexels (Free Stock Videos)
1. Go to https://www.pexels.com/api
2. Sign up / log in
3. Click "Your API Key"
4. Copy the key
5. **Free limit:** 200 requests/hour (unlimited downloads)

### 2D. Cloudflare R2 (Free Video Hosting)
Instagram needs a public URL to download your video. We use R2 because it's free forever.

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up with email (no credit card required)
3. In the sidebar, click **R2**
4. Click **Create bucket**
   - Name: `instagram-reels-bucket`
   - Location: Automatic
5. Click the bucket → **Settings** tab
   - Scroll to **Public Access**
   - Click **Allow Public Access**
   - Note the **Public URL** (looks like `https://pub-xxx.r2.dev`)
6. Go back to R2 overview → **Manage R2 API Tokens**
   - Click **Create API Token**
   - Name: `reels-upload`
   - Permissions: **Object Read & Write**
   - Copy:
     - Account ID
     - Access Key ID
     - Secret Access Key

**Free limit:** 10GB storage + 10 million operations/month (you'll use ~2GB/month posting daily).

---

## Step 3: Instagram API Setup (Free)

### Convert to Business Account
1. Open Instagram app
2. Profile → Menu (☰) → **Settings and privacy**
3. **Account type and tools** → **Switch to professional account**
4. Choose **Creator** (recommended) or **Business**
5. Select a category (e.g., "Digital Creator")
6. Connect to a **Facebook Page** (create one if needed — free)

### Get Instagram Account ID
1. Go to https://business.facebook.com/settings/instagram-account
2. Click your connected Instagram account
3. The ID is in the URL or displayed on the page (starts with `178414...`)

### Create Meta App & Access Token
1. Go to https://developers.facebook.com
2. Log in with Facebook
3. **My Apps** → **Create App**
   - Select **Business** type
   - App name: `Reels Automation`
   - Contact email: your email
4. On the app dashboard, click **Add Product**
   - Add **Instagram Graph API**
5. Go to **Instagram Graph API** → **Basic Display** or **API Setup**
6. Under **User Token Generator**, select your Instagram account
7. Generate token → copy the **Long-Lived Token**
   - If it gives a short token, exchange it:
   ```
   https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_TOKEN
   ```

**Free limit:** 25 publishes per 24 hours.

---

## Step 4: Configure the System

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in any text editor (Notepad, VS Code, etc.)

3. Fill in your keys:
   ```ini
   GROQ_API_KEY=gsk_your_actual_key_here
   PEXELS_API_KEY=your_pexels_key_here
   INSTAGRAM_ACCESS_TOKEN=your_long_token_here
   INSTAGRAM_ACCOUNT_ID=178414your_actual_id
   FACEBOOK_PAGE_ID=your_page_id
   R2_ACCOUNT_ID=your_cloudflare_account_id
   R2_ACCESS_KEY_ID=your_r2_access_key
   R2_SECRET_ACCESS_KEY=your_r2_secret_key
   R2_BUCKET_NAME=instagram-reels-bucket
   R2_PUBLIC_URL=https://pub-yourhash.r2.dev
   ```

4. Save the file.

---

## Step 5: Install & Run

```bash
# Install Python dependencies
pip install -r requirements.txt

# Validate everything is configured
python main.py --validate

# Test: create a reel without publishing (dry run)
python main.py --free --dry-run

# Publish your first reel!
python main.py --free --topic "productivity hacks for students"
```

---

## Daily Automation (Free Forever)

### Option A: Cron (Linux/Mac)
```bash
crontab -e
```
Add this line to post every day at 9 AM:
```
0 9 * * * cd /path/to/instagram-reels-automation && python main.py --free >> logs/cron.log 2>&1
```

### Option B: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task → Daily
3. Action: Start a program
4. Program: `python`
5. Arguments: `main.py --free`
6. Start in: `C:\path\to\instagram-reels-automation`

---

## What If Something Breaks?

| Problem | Fix |
|---------|-----|
| "No module named groq" | Run `pip install groq` |
| "Groq rate limit" | Wait 1 minute (20 req/min limit) or switch to Gemini |
| "Edge-TTS not found" | Run `pip install edge-tts` |
| "R2 upload failed" | Check your bucket has "Allow Public Access" enabled |
| "Instagram container failed" | Your token expired (lasts 60 days). Generate a new one. |
| "No stock footage found" | Pexels API key is wrong, or your visual prompts are too niche |

---

## The Realistic Truth

This system costs **$0/month** to run. But building an audience still requires:

- **3-6 months** of consistent posting before meaningful growth
- **Engaging with comments** (automation can't do this well)
- **Niche focus** — don't jump topics randomly
- **Realistic expectations** — most accounts earn $0-100 in their first year

The "₹750,000/month" post from your screenshot is **engagement bait** designed to sell courses to broke people. Don't fall for it. This free system gives you the actual tools — but you still need patience and strategy.

---

## Free Tier Limits Summary

| Service | Free Limit | How Many Reels? |
|---------|-----------|-----------------|
| Groq | 1M tokens/day | ~600 reels/day |
| Gemini | 60 req/min | ~3,600 reels/day |
| Edge-TTS | Unlimited | Unlimited |
| Pexels | 200 req/hour | ~40 reels/hour |
| R2 | 10GB/month | ~100 reels/month |
| Instagram API | 25 posts/24h | 25 reels/day |

**Your bottleneck:** Instagram's 25 posts/day limit, not the free APIs.

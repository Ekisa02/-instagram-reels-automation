#!/bin/bash
# Daily Instagram Reels Post Script
# Add to crontab: 0 9 * * * /path/to/cron/daily-post.sh

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Log file
LOG_FILE="logs/cron-$(date +%Y%m%d).log"
mkdir -p logs

echo "========================================" >> "$LOG_FILE"
echo "Starting reel creation at $(date)" >> "$LOG_FILE"

# Run the automation
python main.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "SUCCESS: Reel posted at $(date)" >> "$LOG_FILE"
else
    echo "FAILED: Exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"

# Optional: Send notification on failure
 if [ $EXIT_CODE -ne 0 ]; then
     curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"       -H 'Content-type: application/json'          --data '{"text":"Instagram Reels automation failed!"}'
 fi

exit $EXIT_CODE

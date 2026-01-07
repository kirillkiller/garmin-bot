#!/bin/bash
# Daily sync script - stáhne data pro včerejšek každý den
# Použití: Přidej do crontab: 0 1 * * * /path/to/daily_sync.sh

cd "/Users/kirilljuran/Downloads/test cursor"

# Načtení environment variables
export GARMIN_EMAIL='juran.kirill@gmail.com'
export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'

# Log file
LOG_FILE="logs/daily_sync_$(date +%Y%m%d).log"
mkdir -p logs

# Stáhnout data pro včerejšek
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

echo "$(date): 🔄 Začínám denní synchronizaci pro $YESTERDAY" >> "$LOG_FILE"

python3 garmin_bot.py --once --date "$YESTERDAY" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Synchronizace úspěšná pro $YESTERDAY" >> "$LOG_FILE"
else
    echo "$(date): ❌ Chyba při synchronizaci pro $YESTERDAY" >> "$LOG_FILE"
    # Můžeš přidat notifikaci (email, push, atd.)
fi


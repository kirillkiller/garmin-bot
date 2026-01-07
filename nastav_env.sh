#!/bin/bash
# Skript pro nastavení environment variables pro Garmin Bot

echo "🔧 Nastavení Garmin Bot environment variables"
echo ""
echo "Zadej své údaje:"
echo ""

# Garmin Email
read -p "📧 Garmin Email: " GARMIN_EMAIL
export GARMIN_EMAIL="$GARMIN_EMAIL"

# Garmin Password
read -sp "🔒 Garmin Heslo: " GARMIN_PASSWORD
echo ""
export GARMIN_PASSWORD="$GARMIN_PASSWORD"

# Google Sheet ID
read -p "📊 Google Sheet ID (nebo URL): " SHEET_INPUT

# Pokud je to URL, vytáhni ID
if [[ $SHEET_INPUT == *"docs.google.com"* ]]; then
    GOOGLE_SHEET_ID=$(echo "$SHEET_INPUT" | grep -o '/d/[^/]*' | cut -d'/' -f3)
    echo "✅ Sheet ID extrahován: $GOOGLE_SHEET_ID"
else
    GOOGLE_SHEET_ID="$SHEET_INPUT"
fi

export GOOGLE_SHEET_ID="$GOOGLE_SHEET_ID"

echo ""
echo "✅ Environment variables nastaveny!"
echo ""
echo "📋 Zkontroluj nastavení:"
echo "   python3 setup_garmin_bot.py"
echo ""
echo "🚀 Spusť test:"
echo "   python3 garmin_bot.py --once"


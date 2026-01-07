#!/bin/bash
# Rychlý start script pro YouTube bota

echo "📺 YouTube Bot - Rychlý start"
echo ""

# Zkontroluj, zda je yt-dlp nainstalován
if ! python3 -c "import yt_dlp" 2>/dev/null; then
    echo "❌ yt-dlp není nainstalován"
    echo "   Instaluji..."
    pip3 install yt-dlp
fi

# Zkontroluj, zda existuje databáze
if [ ! -d "data" ]; then
    mkdir -p data
fi

# Zkontroluj, zda existují logy
if [ ! -d "logs" ]; then
    mkdir -p logs
fi

echo "✅ Všechno připraveno!"
echo ""
echo "📋 Dostupné příkazy:"
echo "  python3 youtube_bot.py add <channel_url>  - Přidá kanál"
echo "  python3 youtube_bot.py check              - Zkontroluje všechny kanály"
echo "  python3 youtube_bot.py list                - Zobrazí kanály"
echo "  python3 youtube_bot.py videos              - Zobrazí videa"
echo "  python3 youtube_scheduler.py               - Spustí automatický scheduler"
echo ""
echo "📖 Více informací: cat YOUTUBE_BOT_README.md"
echo ""


#!/bin/bash
# Skript pro sledování průběhu stahování historických dat

echo "📊 Průběh stahování historických dat"
echo "======================================"
echo ""

# Zkontrolovat, zda proces běží
if pgrep -f "fetch_historical_data.py" > /dev/null; then
    echo "✅ Proces běží"
    echo ""
    echo "📝 Poslední záznamy z logu:"
    echo "----------------------------------------"
    tail -15 logs/historical_fetch_output.log 2>/dev/null || tail -15 logs/historical_fetch.log 2>/dev/null
    echo ""
    echo "📈 Počet řádků v Google Sheets:"
    echo "----------------------------------------"
    # Zkusit zjistit počet řádků (pokud máme přístup k API)
    echo "💡 Zkontroluj Google Sheet pro aktuální počet řádků"
else
    echo "❌ Proces neběží"
    echo ""
    echo "📝 Poslední záznamy z logu:"
    echo "----------------------------------------"
    tail -20 logs/historical_fetch_output.log 2>/dev/null || tail -20 logs/historical_fetch.log 2>/dev/null
fi

echo ""
echo "💡 Pro sledování v reálném čase použij:"
echo "   tail -f logs/historical_fetch_output.log"


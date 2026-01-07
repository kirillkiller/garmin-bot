#!/bin/bash
# Start webového rozhraní

cd "$(dirname "$0")"

echo "🚀 Spouštím webové rozhraní..."
echo ""

# Zkontroluj, zda port 8080 je volný
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8080 je obsazený. Zkusím port 8081..."
    PORT=8081
else
    PORT=8080
fi

echo "🌐 Server běží na: http://127.0.0.1:$PORT"
echo "📝 Otevři Safari a jdi na: http://127.0.0.1:$PORT"
echo "   Nebo: http://localhost:$PORT"
echo ""
echo "🛑 Pro zastavení stiskni Ctrl+C"
echo ""

python3 web_app.py

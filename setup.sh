#!/bin/bash

echo "🚀 Nastavení AI agenta..."
echo ""

# Kontrola Pythonu
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 není nainstalován"
    exit 1
fi

echo "✅ Python3 nalezen: $(python3 --version)"

# Kontrola pip
if ! python3 -m pip --version &> /dev/null; then
    echo "⚠️  pip není dostupný, zkusím nainstalovat..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip je dostupný"

# Instalace závislostí
echo ""
echo "📦 Instaluji závislosti..."
python3 -m pip install --user openai

if [ $? -eq 0 ]; then
    echo "✅ Závislosti nainstalovány"
else
    echo "⚠️  Instalace selhala. Možná potřebuješ nainstalovat Xcode Command Line Tools:"
    echo "   xcode-select --install"
    echo ""
    echo "Nebo zkus:"
    echo "   python3 -m pip install openai --user"
fi

echo ""
echo "🔑 Nastav OPENAI_API_KEY:"
echo "   export OPENAI_API_KEY='tvůj-api-klíč'"
echo ""
echo "✅ Hotovo! Spusť agenta:"
echo "   python3 agent_simple.py"


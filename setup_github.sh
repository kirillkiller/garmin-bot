#!/bin/bash
# Skript pro automatické nastavení GitHub

echo "🚀 GitHub Setup - Automatický skript"
echo "======================================"
echo ""

# Zkontrolovat, jestli je Git nainstalován
if ! command -v git &> /dev/null; then
    echo "❌ Git není nainstalován!"
    echo "   Nainstaluj Git z: https://git-scm.com/download/mac"
    exit 1
fi

echo "✅ Git je nainstalován: $(git --version)"
echo ""

# Zeptat se na GitHub username
read -p "📝 Zadej své GitHub username: " GITHUB_USERNAME

# Zeptat se na název repo
read -p "📝 Zadej název repo (např. garmin-bot): " REPO_NAME

if [ -z "$GITHUB_USERNAME" ] || [ -z "$REPO_NAME" ]; then
    echo "❌ Username a název repo jsou povinné!"
    exit 1
fi

echo ""
echo "📋 Shrnutí:"
echo "   GitHub username: $GITHUB_USERNAME"
echo "   Název repo: $REPO_NAME"
echo "   URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "✅ Je to správně? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Zrušeno"
    exit 1
fi

echo ""
echo "🔄 Inicializuji Git..."
git init

echo "📦 Přidávám soubory..."
git add .

echo "💾 Vytvářím commit..."
git commit -m "Initial commit - Garmin Bot"

echo "🌿 Nastavuji hlavní větev..."
git branch -M main

echo "🔗 Přidávám GitHub jako vzdálený repozitář..."
git remote remove origin 2>/dev/null  # Odstranit pokud už existuje
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo ""
echo "✅ Git je připraven!"
echo ""
echo "📝 DALŠÍ KROKY:"
echo "   1. Jdi na: https://github.com/new"
echo "   2. Vytvoř nový repo s názvem: $REPO_NAME"
echo "   3. NEOZAČÍNEJ žádné checkboxy (README, .gitignore, license)"
echo "   4. Klikni 'Create repository'"
echo ""
echo "   5. Pak spusť tento příkaz pro nahrání:"
echo "      git push -u origin main"
echo ""
echo "   ⚠️  Při push se tě GitHub zeptá na:"
echo "      - Username: $GITHUB_USERNAME"
echo "      - Password: Použij Personal Access Token (ne heslo!)"
echo ""
echo "   💡 Jak vytvořit token:"
echo "      1. GitHub.com → Settings → Developer settings"
echo "      2. Personal access tokens → Tokens (classic)"
echo "      3. Generate new token (classic)"
echo "      4. Zaškrtni 'repo'"
echo "      5. Zkopíruj token a použij ho jako heslo"
echo ""


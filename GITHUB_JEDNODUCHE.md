# 🚀 GitHub - Nejjednodušší způsob

## ✅ Co potřebuješ:

1. ✅ **Git je nainstalován** (máš ho!)
2. ⏳ **GitHub účet** (vytvoř na https://github.com)
3. ⏳ **5 minut času**

---

## 📋 Dva způsoby:

### ZPŮSOB 1: Automatický skript (NEJLEPŠÍ) ⭐

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
./setup_github.sh
```

Skript tě provede vším krok za krokem!

---

### ZPŮSOB 2: Ručně (pokud chceš vědět, co se děje)

#### 1. Vytvoř repo na GitHub (2 minuty)

1. Jdi na: https://github.com/new
2. **Repository name:** `garmin-bot` (nebo jak chceš)
3. **NEOZAČÍNEJ** žádné checkboxy! (README, .gitignore, license)
4. Klikni **"Create repository"**

#### 2. Spusť tyto příkazy (3 minuty)

**NAHRAĎ:**
- `TVOJE-USERNAME` = tvůj GitHub username
- `garmin-bot` = název tvého repo

```bash
cd "/Users/kirilljuran/Downloads/test cursor"

# Inicializuj Git
git init

# Přidej všechny soubory
git add .

# Vytvoř commit
git commit -m "Initial commit - Garmin Bot"

# Nastav hlavní větev
git branch -M main

# Přidej GitHub (NAHRAĎ username a repo název!)
git remote add origin https://github.com/TVOJE-USERNAME/garmin-bot.git

# Nahraj na GitHub
git push -u origin main
```

#### 3. Personal Access Token (5 minut)

Při `git push` se tě GitHub zeptá na heslo. **NEPOUŽÍVEJ heslo!** Použij token:

1. **GitHub.com** → klikni na profil (vpravo nahoře) → **Settings**
2. **Vlevo dole:** "Developer settings"
3. **"Personal access tokens"** → **"Tokens (classic)"**
4. **"Generate new token"** → **"Generate new token (classic)"**
5. **Zaškrtni:** `repo` (všechno pod tím)
6. **Klikni:** "Generate token"
7. **Zkopíruj token** (vypadá jako: `ghp_xxxxxxxxxxxx`)
8. **Použij ho jako heslo** při `git push`

---

## ✅ Hotovo!

Teď by měl být projekt na GitHub!

**Ověř:** Jdi na https://github.com/tvuj-username/garmin-bot

---

## 🎯 Další krok:

Když máš projekt na GitHub, pokračuj s **Render.com** podle `RENDER_QUICK_START.md`!

---

## 🆘 Pomoc:

Pokud máš problém, zkontroluj `GITHUB_SETUP.md` - je tam detailní návod.


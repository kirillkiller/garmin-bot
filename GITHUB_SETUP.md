# 📚 GitHub Setup - Krok za krokem pro začátečníky

## 🎯 Co je GitHub?

GitHub je místo, kde můžeš uložit svůj kód na internetu. Render.com pak z něj může automaticky stahovat a spouštět tvůj bot.

---

## 📋 Krok za krokem:

### KROK 1: Vytvoř účet na GitHub (5 minut)

1. **Jdi na:** https://github.com
2. **Klikni:** "Sign up" (vpravo nahoře)
3. **Vyplň:**
   - Email: `juran.kirill@gmail.com` (nebo jiný)
   - Heslo: (vymysli silné heslo)
   - Uživatelské jméno: (např. `kirilljuran`)
4. **Ověř email** - GitHub ti pošle email, klikni na odkaz

---

### KROK 2: Vytvoř nový repozitář (2 minuty)

1. **Přihlas se** na GitHub.com
2. **Klikni na zelené tlačítko** "New" (nebo ikonka "+" vpravo nahoře → "New repository")
3. **Vyplň:**
   - **Repository name:** `garmin-bot` (nebo jak chceš)
   - **Description:** `Garmin Connect to Google Sheets Bot` (volitelné)
   - **Public** nebo **Private** - vyber si (Private = jen ty to vidíš)
   - **NEOZAČÍNEJ** "Add a README file" - nech to prázdné!
   - **NEOZAČÍNEJ** "Add .gitignore" - nech to prázdné!
   - **NEOZAČÍNEJ** "Choose a license" - nech to prázdné!
4. **Klikni:** "Create repository"

---

### KROK 3: Nainstaluj Git na počítač (5 minut)

#### Na Mac (co máš):

1. **Otevři Terminal** (najdeš v Aplikacích → Utility)
2. **Zkontroluj, jestli máš Git:**
   ```bash
   git --version
   ```
   
   Pokud vidíš něco jako `git version 2.x.x`, máš Git! ✅
   
   Pokud vidíš `command not found`, nainstaluj Git:
   ```bash
   # Git je už pravděpodobně nainstalovaný, ale pokud ne:
   # Stáhni z: https://git-scm.com/download/mac
   # Nebo použij Homebrew:
   brew install git
   ```

---

### KROK 4: Připrav projekt pro Git (2 minuty)

1. **Otevři Terminal**
2. **Přejdi do složky s projektem:**
   ```bash
   cd "/Users/kirilljuran/Downloads/test cursor"
   ```
3. **Zkontroluj, že jsi ve správné složce:**
   ```bash
   ls
   ```
   Měl bys vidět soubory jako `garmin_bot.py`, `render.yaml`, atd.

---

### KROK 5: Inicializuj Git a nahraj projekt (5 minut)

**Pozor:** Nahraď `kirilljuran` svým GitHub username a `garmin-bot` názvem svého repo!

```bash
# 1. Inicializuj Git v této složce
git init

# 2. Přidej všechny soubory
git add .

# 3. Vytvoř první commit (uložení)
git commit -m "Initial commit - Garmin Bot"

# 4. Přejmenuj hlavní větev na "main" (moderní standard)
git branch -M main

# 5. Přidej GitHub jako vzdálený repozitář
# NAHRAĎ "kirilljuran" svým GitHub username!
# NAHRAĎ "garmin-bot" názvem svého repo!
git remote add origin https://github.com/kirilljuran/garmin-bot.git

# 6. Nahraj projekt na GitHub
git push -u origin main
```

**Pozor:** Při `git push` se tě GitHub zeptá na:
- **Username:** Tvoje GitHub username
- **Password:** NE heslo! Musíš použít **Personal Access Token**

---

### KROK 6: Vytvoř Personal Access Token (5 minut)

GitHub už nepoužívá hesla, potřebuješ token:

1. **Jdi na GitHub.com** → klikni na svůj profil (vpravo nahoře) → **Settings**
2. **Vlevo dole:** "Developer settings"
3. **"Personal access tokens"** → **"Tokens (classic)"**
4. **"Generate new token"** → **"Generate new token (classic)"**
5. **Vyplň:**
   - **Note:** `Garmin Bot` (nebo jak chceš)
   - **Expiration:** `90 days` (nebo jak chceš)
   - **Zaškrtni:** `repo` (všechno pod tím)
6. **Klikni:** "Generate token" (dole)
7. **DŮLEŽITÉ:** Zkopíruj token hned! (vypadá jako: `ghp_xxxxxxxxxxxxxxxxxxxx`)
8. **Ulož si ho** - už ho neuvidíš!

---

### KROK 7: Nahraj projekt s tokenem (2 minuty)

```bash
# Zkus znovu:
git push -u origin main
```

Když se tě zeptá:
- **Username:** Tvoje GitHub username
- **Password:** Vlož **Personal Access Token** (ne heslo!)

---

## ✅ Hotovo!

Teď by měl být tvůj projekt na GitHub!

**Ověř:**
1. Jdi na https://github.com/tvuj-username/garmin-bot
2. Měl bys vidět všechny soubory

---

## 🆘 Časté problémy:

### "fatal: remote origin already exists"
```bash
# Odstraň starý origin a přidej znovu:
git remote remove origin
git remote add origin https://github.com/tvuj-username/garmin-bot.git
```

### "Permission denied"
- Zkontroluj, že používáš **Personal Access Token**, ne heslo
- Zkontroluj, že máš správné GitHub username

### "repository not found"
- Zkontroluj, že repo existuje na GitHub
- Zkontroluj, že máš správné jméno repo v URL

---

## 📝 Shrnutí příkazů:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
git init
git add .
git commit -m "Initial commit - Garmin Bot"
git branch -M main
git remote add origin https://github.com/TVOJE-USERNAME/TVOJE-REPO.git
git push -u origin main
```

**Nahraď:**
- `TVOJE-USERNAME` = tvůj GitHub username
- `TVOJE-REPO` = název tvého repo

---

## 🎉 Další krok:

Když máš projekt na GitHub, můžeš pokračovat s **Render.com setup** podle `RENDER_QUICK_START.md`!


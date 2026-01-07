# 🚀 Render.com Setup - Jednodušší než VPS!

## ✅ Proč Render.com?

- ✅ **Zdarma** - free tier pro cron jobs
- ✅ **Jednoduché** - nasazení z Git repozitáře
- ✅ **Automatické** - deploy při push
- ✅ **Cron Jobs** - perfektní pro denní synchronizaci
- ✅ **Bez serveru** - nemusíš spravovat VPS
- ✅ **Monitoring** - automatické logy a notifikace

---

## 📋 Krok za krokem:

### 1. **Vytvoř účet na Render.com** (2 minuty)

1. Jdi na https://render.com
2. Klikni "Get Started for Free"
3. Přihlas se přes GitHub (nejjednodušší)

---

### 2. **Připrav projekt pro Render** (5 minut)

#### 2.1 Vytvoř `render.yaml` (Blueprint):

```yaml
services:
  - type: cron
    name: garmin-daily-sync
    env: python
    schedule: "0 1 * * *"  # Každý den v 1:00 UTC (2:00 CET)
    buildCommand: pip install -r requirements.txt
    startCommand: python3 daily_sync_improved.py --once
    envVars:
      - key: GARMIN_EMAIL
        sync: false
      - key: GARMIN_PASSWORD
        sync: false
      - key: GOOGLE_SHEET_ID
        sync: false
      - key: GOOGLE_CREDENTIALS_PATH
        value: credentials.json
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
```

#### 2.2 Vytvoř `requirements.txt`:

```txt
garminconnect>=0.2.0
gspread>=5.0.0
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
garth>=0.4.0
requests>=2.28.0
```

#### 2.3 Vytvoř `.renderignore`:

```
logs/
*.log
.env
__pycache__/
*.pyc
```

---

### 3. **Nahraj projekt na GitHub** (5 minut)

```bash
# Pokud ještě nemáš Git repo:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tvuj-username/garmin-bot.git
git push -u origin main
```

---

### 4. **Nastav Render Cron Job** (10 minut)

#### 4.1 Vytvoř nový Cron Job:

1. V Render dashboard klikni "New +"
2. Vyber "Cron Job"
3. Propoj s GitHub repozitářem
4. Vyplň:
   - **Name:** `garmin-daily-sync`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 daily_sync_improved.py --once`
   - **Schedule:** `0 1 * * *` (každý den v 1:00 UTC)

#### 4.2 Nastav Environment Variables:

V Render dashboard → Environment:
- `GARMIN_EMAIL` = `juran.kirill@gmail.com`
- `GARMIN_PASSWORD` = `**h2^SdcZkY!2Hq22F`
- `GOOGLE_SHEET_ID` = `1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM`
- `GOOGLE_CREDENTIALS_PATH` = `credentials.json`
- `TELEGRAM_BOT_TOKEN` = `8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4`
- `TELEGRAM_CHAT_ID` = `670619301`

#### 4.3 Nahraj `credentials.json`:

V Render dashboard → Environment → Secret Files:
- Klikni "Add Secret File"
- Name: `credentials.json`
- Nahraj obsah tvého `credentials.json`

---

### 5. **První spuštění** (5 minut)

1. V Render dashboard klikni "Manual Deploy" → "Deploy latest commit"
2. Sleduj logy v real-time
3. Pokud je potřeba MFA kód:
   - Bot pošle Telegram notifikaci
   - Zadej MFA kód (bude potřeba upravit kód pro interaktivní vstup)

---

## 🔧 Úprava kódu pro Render:

Render cron jobs nepodporují interaktivní vstup (MFA kód). Musíme upravit:

### Možnost 1: MFA kód přes environment variable (doporučeno)

```python
# V garmin_bot.py - pokud je MFA potřeba, použij z env
mfa_code = os.getenv('GARMIN_MFA_CODE')
if mfa_code:
    # Použít MFA kód z env
```

**Postup:**
1. Když je potřeba MFA, bot pošle Telegram notifikaci
2. Přidej `GARMIN_MFA_CODE` do Render environment variables
3. Bot použije kód a uloží session
4. Příště už nebude potřeba

### Možnost 2: Background Worker (pokud potřebuješ interaktivní vstup)

Místo Cron Job použij Background Worker, který běží neustále.

---

## 📊 Srovnání: Render vs. VPS

| Vlastnost | Render.com | VPS (Hetzner) |
|-----------|------------|---------------|
| **Cena** | Zdarma (free tier) | 4-10€/měsíc |
| **Setup** | 15 minut | 30-60 minut |
| **Správa** | Automatická | Manuální |
| **Monitoring** | Automatické logy | Musíš nastavit |
| **Scaling** | Automatické | Manuální |
| **Backup** | Automatické | Musíš nastavit |
| **MFA handling** | Potřebuje úpravu | Plně podporováno |

---

## ✅ Výhody Render.com:

1. **Zdarma** - free tier stačí pro cron job
2. **Jednoduché** - nasazení z Git, automatické deploy
3. **Bez starostí** - nemusíš spravovat server
4. **Monitoring** - automatické logy a notifikace
5. **Backup** - automatické zálohy

---

## ⚠️ Limity Render.com:

1. **MFA kód** - potřebuje úpravu (viz výše)
2. **Free tier** - může být pomalejší
3. **Cron jobs** - max 1x za minutu (pro nás OK)

---

## 🎯 Doporučení:

**Pro tebe je Render.com lepší volba:**
- ✅ Jednodušší setup
- ✅ Zdarma
- ✅ Méně práce s údržbou
- ✅ Automatické deploy

**Postupuj podle tohoto návodu a máš to za 15 minut hotové!**

---

## 📚 Další zdroje:

- Render Docs: https://render.com/docs
- Cron Jobs: https://render.com/docs/cron-jobs
- Environment Variables: https://render.com/docs/environment-variables


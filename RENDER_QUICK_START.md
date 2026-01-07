# 🚀 Render.com - Rychlý Start (15 minut)

## ✅ Proč Render.com?

- ✅ **Zdarma** - free tier pro cron jobs
- ✅ **Jednoduché** - nasazení z Git
- ✅ **Bez serveru** - nemusíš spravovat VPS
- ✅ **Automatické** - deploy při push

---

## 📋 Krok za krokem:

### 1. **Připrav projekt** (2 minuty)

Soubory jsou už připravené:
- ✅ `render.yaml` - Render konfigurace
- ✅ `requirements.txt` - Python závislosti
- ✅ `.renderignore` - co ignorovat

### 2. **Nahraj na GitHub** (5 minut)

```bash
# Pokud ještě nemáš Git repo:
git init
git add .
git commit -m "Initial commit - Garmin Bot"
git branch -M main

# Vytvoř repo na GitHub.com a pak:
git remote add origin https://github.com/tvuj-username/garmin-bot.git
git push -u origin main
```

### 3. **Vytvoř účet na Render.com** (2 minuty)

1. Jdi na https://render.com
2. Klikni "Get Started for Free"
3. Přihlas se přes GitHub

### 4. **Vytvoř Cron Job** (5 minut)

1. V Render dashboard klikni **"New +"**
2. Vyber **"Cron Job"**
3. **Connect GitHub** - vyber svůj repo
4. Vyplň:
   - **Name:** `garmin-daily-sync`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python3 daily_sync_improved.py --once`
   - **Schedule:** `0 1 * * *` (každý den v 1:00 UTC = 2:00/3:00 CET)

### 5. **Nastav Environment Variables** (3 minuty)

V Render dashboard → **Environment** → **Add Environment Variable**:

```
GARMIN_EMAIL = juran.kirill@gmail.com
GARMIN_PASSWORD = **h2^SdcZkY!2Hq22F
GOOGLE_SHEET_ID = 1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM
GOOGLE_CREDENTIALS_PATH = credentials.json
TELEGRAM_BOT_TOKEN = 8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4
TELEGRAM_CHAT_ID = 670619301
TELEGRAM_NOTIFY_SUCCESS = false
```

### 6. **Nahraj credentials.json** (2 minuty)

1. V Render dashboard → **Environment** → **Secret Files**
2. Klikni **"Add Secret File"**
3. **Name:** `credentials.json`
4. **Content:** Vlož obsah tvého `credentials.json` (celý JSON)

### 7. **První spuštění** (1 minuta)

1. Klikni **"Manual Deploy"** → **"Deploy latest commit"**
2. Sleduj logy v real-time
3. Pokud je potřeba MFA kód:
   - Bot pošle Telegram notifikaci
   - Přidej `GARMIN_MFA_CODE` do environment variables
   - Bot se znovu spustí automaticky

---

## 🔐 MFA kód - Jak to funguje:

### První spuštění:
1. Bot se pokusí připojit
2. Pokud je potřeba MFA, pošle Telegram notifikaci
3. Zkontroluj SMS/e-mail pro MFA kód
4. Přidej do Render: `GARMIN_MFA_CODE = tvuj-kod`
5. Bot se znovu spustí a použije kód
6. Session se uloží

### Další spuštění:
- ✅ Session funguje - MFA už není potřeba
- ✅ Bot stahuje data automaticky

---

## ✅ Hotovo!

Bot teď:
- ✅ Běží každý den v 1:00 UTC (2:00/3:00 CET)
- ✅ Stahuje data pro včerejšek
- ✅ Posílá notifikace při chybách
- ✅ Posílá notifikace při potřebě MFA

---

## 📊 Sledování:

### Logy:
- V Render dashboard → **Logs** - vidíš všechny logy v real-time

### Telegram:
- Notifikace při chybách
- Notifikace při potřebě MFA

### Google Sheets:
- Nové záznamy každý den

---

## 🆘 Troubleshooting:

### Cron job se nespustí:
- Zkontroluj Schedule: `0 1 * * *`
- Zkontroluj logy v Render dashboard

### MFA kód vyžadován:
- Bot pošle Telegram notifikaci
- Přidej `GARMIN_MFA_CODE` do environment variables
- Bot se znovu spustí

### Chyby v logu:
- Zkontroluj environment variables
- Zkontroluj, že `credentials.json` je nahraný
- Zkontroluj Telegram notifikace

---

## 🎉 To je vše!

**Máš to za 15 minut hotové a zdarma!** 🚀


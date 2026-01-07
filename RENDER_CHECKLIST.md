# ✅ Render.com Setup - Checklist

## 🎯 Rychlý checklist s konkrétními hodnotami

---

## KROK 1: Účet (2 min)

- [ ] Jdi na https://render.com
- [ ] Klikni "Get Started for Free"
- [ ] Přihlas se přes GitHub
- [ ] Autorizuj přístup k repo `kirillkiller/garmin-bot`

---

## KROK 2: Vytvoř Cron Job (5 min)

- [ ] Klikni "New +" → "Cron Job"
- [ ] Connect GitHub → vyber `kirillkiller/garmin-bot`
- [ ] Vyplň:
  - **Name:** `garmin-daily-sync`
  - **Environment:** `Python 3`
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `python3 daily_sync_improved.py --once`
  - **Schedule:** `0 1 * * *`

---

## KROK 3: Environment Variables (3 min)

V Render → Environment → Add Environment Variable:

- [ ] **GARMIN_EMAIL** = `juran.kirill@gmail.com`
- [ ] **GARMIN_PASSWORD** = `**h2^SdcZkY!2Hq22F`
- [ ] **GOOGLE_SHEET_ID** = `1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM`
- [ ] **GOOGLE_CREDENTIALS_PATH** = `credentials.json`
- [ ] **TELEGRAM_BOT_TOKEN** = `8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4`
- [ ] **TELEGRAM_CHAT_ID** = `670619301`
- [ ] **TELEGRAM_NOTIFY_SUCCESS** = `false`

---

## KROK 4: Secret File - credentials.json (2 min)

- [ ] Render → Environment → Secret Files
- [ ] Klikni "Add Secret File"
- [ ] **Name:** `credentials.json`
- [ ] **Content:** Zkopíruj celý obsah z lokálního `credentials.json`

---

## KROK 5: První spuštění (1 min)

- [ ] Klikni "Manual Deploy" → "Deploy latest commit"
- [ ] Sleduj Logs
- [ ] Pokud je potřeba MFA:
  - [ ] Zkontroluj Telegram notifikaci
  - [ ] Přidej `GARMIN_MFA_CODE` = `tvuj-kod` do environment variables
  - [ ] Bot se znovu spustí automaticky

---

## ✅ Hotovo!

Bot běží automaticky každý den v 1:00 UTC (2:00/3:00 CET)!

---

## 📊 Sledování:

- **Logy:** Render dashboard → Logs
- **Telegram:** Notifikace při chybách/MFA
- **Google Sheets:** Nové záznamy každý den

---

## 🆘 Problémy?

Viz `RENDER_STEP_BY_STEP.md` pro detailní návod.


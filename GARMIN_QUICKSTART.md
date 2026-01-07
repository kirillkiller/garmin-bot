# ⚡ Garmin Bot - Rychlý start (5 minut)

## 1️⃣ Instalace

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
pip3 install -r requirements.txt
```

## 2️⃣ Google Sheets Setup (2 minuty)

1. **Jdi na:** https://console.cloud.google.com/
2. **Vytvoř projekt** → Povol "Google Sheets API" a "Google Drive API"
3. **Vytvoř Service Account:**
   - "APIs & Services" → "Credentials" → "Create Credentials" → "Service Account"
   - Stáhni JSON → Přejmenuj na `credentials.json` → Ulož do složky projektu
4. **Sdílej Google Sheet:**
   - Otevři Sheet → "Share" → Vlož email z JSON (`client_email`) → "Editor"

## 3️⃣ Nastavení

```bash
export GARMIN_EMAIL='vas@email.cz'
export GARMIN_PASSWORD='heslo'
export GOOGLE_SHEET_ID='1ABC123...'  # Z URL Google Sheet
```

## 4️⃣ Test

```bash
python3 garmin_bot.py --once
```

## 5️⃣ Spuštění (polling)

```bash
python3 garmin_bot.py
```

**Hotovo! 🎉**

Více detailů: `GARMIN_BOT_README.md`


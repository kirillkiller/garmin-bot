# 🚀 Render.com Setup - Krok za krokem

## 📋 Přehled:

Tento návod tě provede nastavením Render.com pro automatické spouštění Garmin bota každý den.

**Čas:** ~10 minut
**Cena:** Zdarma (free tier)

---

## KROK 1: Vytvoř účet na Render.com (2 minuty)

1. **Jdi na:** https://render.com
2. **Klikni:** "Get Started for Free" (vpravo nahoře)
3. **Přihlas se přes GitHub:**
   - Klikni "Sign up with GitHub"
   - Autorizuj Render.com přístup k tvému GitHub účtu
   - Vyber repo: `kirillkiller/garmin-bot` (pokud se zeptá)

---

## KROK 2: Vytvoř Cron Job (5 minut)

### 2.1 Otevři Render Dashboard

1. Po přihlášení uvidíš **Dashboard**
2. Klikni **"New +"** (vpravo nahoře)
3. Vyber **"Cron Job"**

### 2.2 Propoj s GitHub

1. **Connect GitHub** (pokud ještě není propojeno)
2. Vyber repo: **`kirillkiller/garmin-bot`**
3. Klikni **"Connect"**

### 2.3 Vyplň detaily

**Základní informace:**
- **Name:** `garmin-daily-sync`
- **Environment:** `Python 3`
- **Region:** `Frankfurt` (nebo nejbližší k tobě)
- **Branch:** `main`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python3 daily_sync_improved.py --once`
- **Schedule:** `0 1 * * *` (každý den v 1:00 UTC = 2:00/3:00 CET)

**Poznámka k času:**
- `0 1 * * *` = 1:00 UTC
- V létě (CEST) = 3:00 ráno
- V zimě (CET) = 2:00 ráno

---

## KROK 3: Nastav Environment Variables (3 minuty)

V Render dashboard → **Environment** → **Add Environment Variable**

Přidej tyto proměnné (jednu po druhé):

### 3.1 Garmin credentials:
```
Key: GARMIN_EMAIL
Value: juran.kirill@gmail.com
```

```
Key: GARMIN_PASSWORD
Value: **h2^SdcZkY!2Hq22F
```

### 3.2 Google Sheets:
```
Key: GOOGLE_SHEET_ID
Value: 1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM
```

```
Key: GOOGLE_CREDENTIALS_PATH
Value: credentials.json
```

### 3.3 Telegram:
```
Key: TELEGRAM_BOT_TOKEN
Value: 8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4
```

```
Key: TELEGRAM_CHAT_ID
Value: 670619301
```

### 3.4 Volitelné:
```
Key: TELEGRAM_NOTIFY_SUCCESS
Value: false
```

---

## KROK 4: Nahraj credentials.json (2 minuty)

### 4.1 Vytvoř Secret File

1. V Render dashboard → **Environment** → **Secret Files**
2. Klikni **"Add Secret File"**
3. **Name:** `credentials.json`
4. **Content:** 
   - Otevři `credentials.json` z lokálního počítače
   - Zkopíruj **CELÝ obsah** (celý JSON)
   - Vlož do pole "Content"

### 4.2 Ověř

- Měl bys vidět `credentials.json` v seznamu Secret Files

---

## KROK 5: První spuštění (1 minuta)

1. V Render dashboard klikni **"Manual Deploy"** → **"Deploy latest commit"**
2. Sleduj **Logs** v real-time
3. Mělo by se zobrazit:
   - ✅ Build proběhl úspěšně
   - ✅ Bot se připojil k Garmin
   - ✅ Data se stáhla

---

## KROK 6: MFA kód (pokud je potřeba)

### Pokud bot pošle Telegram notifikaci o potřebě MFA:

1. **Zkontroluj SMS/e-mail** pro MFA kód
2. **Přidej do Render Environment Variables:**
   ```
   Key: GARMIN_MFA_CODE
   Value: tvuj-mfa-kod-zde
   ```
3. **Bot se automaticky znovu spustí** a použije kód
4. **Session se uloží** - příště už nebude potřeba

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
- Můžeš filtrovat podle času

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
- Bot se znovu spustí automaticky

### Chyby v logu:
- Zkontroluj environment variables
- Zkontroluj, že `credentials.json` je nahraný
- Zkontroluj Telegram notifikace

### Build selhává:
- Zkontroluj `requirements.txt`
- Zkontroluj logy build procesu

---

## 🎉 Gratulace!

Máš to hotové! Bot běží automaticky na Render.com zdarma! 🚀


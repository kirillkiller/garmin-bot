# ✅ Render.com Form - Kontrolní seznam

## 📋 Co je správně:

- ✅ **Name:** `garmin-bot` (OK, nebo můžeš použít `garmin-daily-sync`)
- ✅ **Language:** `Python 3` ✅
- ✅ **Branch:** `main` ✅
- ✅ **Region:** `Frankfurt (EU Central)` ✅
- ✅ **Root Directory:** Prázdné ✅ (není potřeba)
- ✅ **Build Command:** `pip install -r requirements.txt` ✅
- ✅ **Instance type:** `Starter` ✅ (zdarma)

---

## ❌ CO MUSÍŠ OPRAVIT:

### 1. **Schedule** - ZMĚŇ!

**Špatně:** `*/5 * * * *` (každých 5 minut - to je moc často!)

**Správně:** `0 1 * * *` (každý den v 1:00 UTC = 2:00/3:00 CET)

**Jak změnit:**
- Klikni na "every 5 minutes"
- Vyber "Custom cron expression"
- Zadej: `0 1 * * *`

---

### 2. **Command** - PŘIDEJ!

**Chybí:** Command je prázdný!

**Přidej:** `python3 daily_sync_improved.py --once`

**Jak přidat:**
- Do pole "Command" zadej: `python3 daily_sync_improved.py --once`

---

### 3. **Environment Variables** - PŘIDEJ VŠECHNY!

**Chybí:** Environment Variables jsou prázdné!

**Přidej tyto (jednu po druhé):**

1. **GARMIN_EMAIL**
   - Name: `GARMIN_EMAIL`
   - Value: `juran.kirill@gmail.com`

2. **GARMIN_PASSWORD**
   - Name: `GARMIN_PASSWORD`
   - Value: `**h2^SdcZkY!2Hq22F`

3. **GOOGLE_SHEET_ID**
   - Name: `GOOGLE_SHEET_ID`
   - Value: `1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM`

4. **GOOGLE_CREDENTIALS_PATH**
   - Name: `GOOGLE_CREDENTIALS_PATH`
   - Value: `credentials.json`

5. **TELEGRAM_BOT_TOKEN**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: `8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4`

6. **TELEGRAM_CHAT_ID**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: `670619301`

7. **TELEGRAM_NOTIFY_SUCCESS** (volitelné)
   - Name: `TELEGRAM_NOTIFY_SUCCESS`
   - Value: `false`

**Jak přidat:**
- Klikni "Add Environment Variable"
- Vyplň Name a Value
- Klikni "Add"
- Opakuj pro všechny

---

## ✅ FINÁLNÍ KONTROLA:

Před kliknutím "Create Cron Job" zkontroluj:

- [ ] **Schedule:** `0 1 * * *` (ne `*/5 * * * *`!)
- [ ] **Command:** `python3 daily_sync_improved.py --once` (ne prázdné!)
- [ ] **Environment Variables:** Všech 6-7 proměnných přidáno
- [ ] **Secret File:** `credentials.json` (přidáš po vytvoření cron jobu)

---

## 📝 PO VYTVOŘENÍ CRON JOBU:

1. **Přidej Secret File:**
   - Jdi do Environment → Secret Files
   - Klikni "Add Secret File"
   - Name: `credentials.json`
   - Content: Zkopíruj celý obsah z lokálního `credentials.json`

2. **Spusť první deploy:**
   - Klikni "Manual Deploy" → "Deploy latest commit"
   - Sleduj logy

---

## 🎯 Shrnutí změn:

1. ❌ Schedule: `*/5 * * * *` → ✅ `0 1 * * *`
2. ❌ Command: (prázdné) → ✅ `python3 daily_sync_improved.py --once`
3. ❌ Environment Variables: (prázdné) → ✅ Přidej všech 6-7 proměnných

---

## ✅ Pak to bude správně!


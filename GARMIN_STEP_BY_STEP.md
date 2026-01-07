# 📋 Garmin Bot - Step by Step Průvodce

Postupuj krok za krokem podle tohoto návodu.

---

## ✅ KROK 1: Instalace závislostí (1 minuta)

**Zkopíruj a vlož do terminálu:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && pip3 install garminconnect gspread google-auth google-auth-oauthlib google-auth-httplib2
```

**Stiskni Enter a počkej** (1-2 minuty).

---

## ✅ KROK 2: Vytvoření Google Service Account (3 minuty)

### 2.1 Otevři Google Cloud Console

1. **Otevři prohlížeč** (Safari/Chrome)
2. **Jdi na:** https://console.cloud.google.com/
3. **Přihlas se** svým Google účtem

### 2.2 Vytvoř projekt

1. **Klikni na dropdown** v horní části (vedle "Google Cloud")
2. **Klikni "New Project"**
3. **Zadej název:** `Garmin Bot` (nebo cokoliv)
4. **Klikni "Create"**
5. **Počkej** až se projekt vytvoří (5-10 sekund)

### 2.3 Povol API

1. **V menu vlevo** → "APIs & Services" → "Library"
2. **Vyhledej:** `Google Sheets API`
3. **Klikni na "Google Sheets API"**
4. **Klikni "Enable"** (Povolit)
5. **Zpět na "Library"**
6. **Vyhledej:** `Google Drive API`
7. **Klikni na "Google Drive API"**
8. **Klikni "Enable"**

### 2.4 Vytvoř Service Account

1. **V menu vlevo** → "APIs & Services" → "Credentials"
2. **Klikni "Create Credentials"** (nahoře)
3. **Vyber "Service Account"**
4. **Zadej:**
   - Service account name: `garmin-bot`
   - Service account ID: (nech automaticky)
5. **Klikni "Create and Continue"**
6. **Přeskoč "Grant this service account access to project"** → klikni "Continue"
7. **Přeskoč "Grant users access"** → klikni "Done"

### 2.5 Stáhni JSON klíč

1. **Klikni na vytvořený Service Account** (v seznamu)
2. **Klikni na tab "Keys"**
3. **Klikni "Add Key"** → "Create new key"
4. **Vyber "JSON"**
5. **Klikni "Create"**
6. **Soubor se stáhne** (např. `garmin-bot-xxxxx-xxxxx.json`)

### 2.6 Přesuň a přejmenuj soubor

1. **Najdi stažený soubor** (obvykle ve složce Downloads)
2. **Přejmenuj ho na:** `credentials.json`
3. **Přesuň ho** do složky projektu: `/Users/kirilljuran/Downloads/test cursor`

**💡 Tip:** Můžeš to udělat v Finderu nebo terminálem:
```bash
mv ~/Downloads/garmin-bot-*.json "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

---

## ✅ KROK 3: Vytvoření Google Sheet (1 minuta)

1. **Otevři:** https://sheets.google.com/
2. **Klikni "Blank"** (prázdný sheet)
3. **Pojmenuj ho** (např. "Garmin Data")
4. **Zkopíruj ID z URL:**
   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL012MNO345PQR/edit
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      TOHLE JE ID - ZKOPÍRUJ TO!
   ```

**💡 Ulož si to ID - budeš ho potřebovat v dalším kroku!**

---

## ✅ KROK 4: Sdílení Google Sheet s Service Account (1 minuta)

### 4.1 Najdi email Service Account

1. **Otevři soubor** `credentials.json` (který jsi stáhl v kroku 2.6)
2. **Najdi řádek:** `"client_email": "garmin-bot-xxxxx@xxxxx.iam.gserviceaccount.com"`
3. **Zkopíruj celý email** (včetně uvozovek, ale bez uvozovek)

### 4.2 Sdílej Sheet

1. **V Google Sheet** klikni tlačítko **"Share"** (Sdílet) vpravo nahoře
2. **Vlož email Service Account** (ten co jsi zkopíroval)
3. **Nastav oprávnění na "Editor"**
4. **Klikni "Send"** (nebo "Done")

---

## ✅ KROK 5: Nastavení environment variables (1 minuta)

**Otevři terminál a zkopíruj/vlož** (nahraď svými údaji):

```bash
export GARMIN_EMAIL='tvuj-email@gmail.com'
export GARMIN_PASSWORD='tvoje-heslo'
export GOOGLE_SHEET_ID='1ABC123DEF456GHI789JKL012MNO345PQR'
```

**Příklad:**
```bash
export GARMIN_EMAIL='jan.novak@gmail.com'
export GARMIN_PASSWORD='moje-super-heslo-123'
export GOOGLE_SHEET_ID='1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890'
```

**Stiskni Enter.**

**⚠️ DŮLEŽITÉ:** Tyto proměnné platí jen pro aktuální terminál. Pokud zavřeš terminál, musíš je nastavit znovu.

**💡 Pro trvalé nastavení** (volitelné):
```bash
echo 'export GARMIN_EMAIL="tvuj-email@gmail.com"' >> ~/.zshrc
echo 'export GARMIN_PASSWORD="tvoje-heslo"' >> ~/.zshrc
echo 'export GOOGLE_SHEET_ID="1ABC123..."' >> ~/.zshrc
source ~/.zshrc
```

---

## ✅ KROK 6: Kontrola nastavení (30 sekund)

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 setup_garmin_bot.py
```

**Stiskni Enter.**

Mělo by se zobrazit:
- ✅ Všechny knihovny jsou nainstalované
- ✅ Všechny environment variables jsou nastavené
- ✅ credentials.json nalezen
- ✅ Vše je připraveno!

Pokud vidíš chyby, vrať se k příslušnému kroku.

---

## ✅ KROK 7: První test (1 minuta)

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 garmin_bot.py --once
```

**Stiskni Enter.**

**Co se stane:**
- Bot se připojí k Garmin Connect
- Pokud máš MFA, může tě vyzvat k zadání kódu z SMS/e-mailu
- Stáhne dnešní data
- Odešle je do Google Sheets

**Zkontroluj Google Sheet** - měl by se objevit nový řádek s daty!

---

## ✅ KROK 8: Spuštění automatického režimu (polling)

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 garmin_bot.py
```

**Stiskni Enter.**

Bot bude každých 10 minut automaticky stahovat data a posílat je do Google Sheets.

**Pro zastavení:** Stiskni `Ctrl + C`

---

## 🎉 HOTOVO!

Pokud vše proběhlo úspěšně:
- ✅ Data se ukládají do Google Sheets
- ✅ Bot běží automaticky
- ✅ Logy jsou v `logs/garmin_bot.log`

---

## ❓ Problémy?

### "GARMIN_EMAIL musí být nastaven"
→ Vrať se na **KROK 5** a nastav environment variables znovu

### "Google credentials nenalezeny"
→ Zkontroluj, že máš `credentials.json` ve složce projektu (**KROK 2.6**)

### "Permission denied" při zápisu do Google Sheets
→ Zkontroluj, že jsi sdílel Sheet s emailem Service Account (**KROK 4**)

### "Chyba při připojení k Garmin Connect"
→ Zkontroluj email a heslo
→ Pokud máš MFA, zadej kód při prvním spuštění

### "Garmin IP blocked"
→ Počkej 10-30 minut
→ Zvyš interval: `python3 garmin_bot.py --interval 1800` (30 minut)

---

**Hodně štěstí! 🚀**


# 🤖 Garmin Connect Bot - Návod k použití

Bot automaticky stahuje data z Garmin Connect a posílá je do Google Sheets.

---

## 🚀 Rychlý start

### 1️⃣ Instalace závislostí

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
pip3 install -r requirements.txt
```

---

### 2️⃣ Nastavení Google Sheets

#### Varianta A: Service Account (Doporučeno - jednodušší)

1. **Jdi na:** https://console.cloud.google.com/
2. **Vytvoř nový projekt** (nebo použij existující)
3. **Povol Google Sheets API:**
   - V menu → "APIs & Services" → "Library"
   - Vyhledej "Google Sheets API" → "Enable"
   - Vyhledej "Google Drive API" → "Enable"
4. **Vytvoř Service Account:**
   - "APIs & Services" → "Credentials"
   - "Create Credentials" → "Service Account"
   - Zadej název (např. "garmin-bot")
   - Klikni "Create and Continue"
   - Přeskoč další kroky → "Done"
5. **Stáhni JSON klíč:**
   - Klikni na vytvořený Service Account
   - "Keys" tab → "Add Key" → "Create new key"
   - Vyber "JSON" → "Create"
   - Soubor se stáhne (např. `garmin-bot-xxxxx.json`)
6. **Přejmenuj soubor na `credentials.json`** a ulož do složky projektu
7. **Sdílej Google Sheet s emailem Service Account:**
   - Otevři Google Sheet
   - Klikni "Share" (Sdílet)
   - Vlož email Service Account (najdeš v JSON souboru, pole `client_email`)
   - Nastav oprávnění na "Editor"
   - Klikni "Send"

#### Varianta B: OAuth2 (Pokročilejší)

1. **Vytvoř OAuth2 credentials:**
   - https://console.cloud.google.com/ → "APIs & Services" → "Credentials"
   - "Create Credentials" → "OAuth client ID"
   - Vyber "Desktop app"
   - Stáhni `credentials.json`
2. **První spuštění vytvoří `token.json`:**
   ```bash
   python3 garmin_bot.py --once
   ```
   - Otevře se prohlížeč → přihlas se → povol přístup
   - `token.json` se vytvoří automaticky

---

### 3️⃣ Získání Google Sheet ID

1. **Otevři Google Sheet**
2. **Zkopíruj ID z URL:**
   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL012MNO345PQR/edit
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      TOHLE JE SHEET ID
   ```

---

### 4️⃣ Nastavení environment variables

**Zkopíruj a vlož do terminálu** (nahraď svými údaji):

```bash
export GARMIN_EMAIL='vas@email.cz'
export GARMIN_PASSWORD='tvoje-heslo'
export GOOGLE_SHEET_ID='1ABC123DEF456GHI789JKL012MNO345PQR'
export GOOGLE_CREDENTIALS_PATH='credentials.json'  # (volitelné, default: credentials.json)
```

**Příklad:**
```bash
export GARMIN_EMAIL='jan.novak@gmail.com'
export GARMIN_PASSWORD='moje-super-heslo'
export GOOGLE_SHEET_ID='1aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890'
```

---

### 5️⃣ První spuštění (test)

**Spusť jednou pro test:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
python3 garmin_bot.py --once
```

**Co se stane:**
- ✅ Připojí se k Garmin Connect (při prvním spuštění může vyžadovat MFA kód)
- ✅ Stáhne dnešní data
- ✅ Odešle je do Google Sheets
- ✅ Ukončí se

**Zkontroluj Google Sheet** - měl by se objevit nový řádek s daty!

---

### 6️⃣ Spuštění polling módu (automatické)

**Spusť bot v pozadí, který bude každých 10 minut stahovat data:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
python3 garmin_bot.py
```

**Nebo s vlastním intervalem (např. každých 5 minut = 300 sekund):**

```bash
python3 garmin_bot.py --interval 300
```

**Pro zastavení:** Stiskni `Ctrl + C`

---

## 📊 Co se ukládá do Google Sheets?

Bot ukládá následující metriky:

| Sloupec | Popis |
|---------|-------|
| Datum | Datum měření (YYYY-MM-DD) |
| Čas záznamu | Kdy byla data stažena |
| Kroky | Počet kroků |
| Vzdálenost (km) | Ujetá vzdálenost v kilometrech |
| Kalorie | Celkové spálené kalorie |
| Průměrný tep | Průměrná tepová frekvence |
| Max tep | Maximální tepová frekvence |
| Min tep | Minimální tepová frekvence |
| Stres | Průměrná úroveň stresu |
| Body Battery (nabito) | Body Battery - nabito |
| Body Battery (vybito) | Body Battery - vybito |
| Schody nahoru | Počet schodů nahoru |
| Schody dolů | Počet schodů dolů |
| Aktivní kalorie | Kalorie z aktivity |
| BMR kalorie | Bazální metabolismus kalorie |

---

## 🔧 Pokročilé použití

### Stáhnout data pro konkrétní datum

```bash
python3 garmin_bot.py --once --date 2026-01-05
```

### Změnit interval polling

```bash
# Každých 5 minut
python3 garmin_bot.py --interval 300

# Každou hodinu
python3 garmin_bot.py --interval 3600
```

### Trvalé nastavení environment variables

**Pro macOS/Linux** - přidej do `~/.zshrc` nebo `~/.bashrc`:

```bash
echo 'export GARMIN_EMAIL="vas@email.cz"' >> ~/.zshrc
echo 'export GARMIN_PASSWORD="heslo"' >> ~/.zshrc
echo 'export GOOGLE_SHEET_ID="1ABC123..."' >> ~/.zshrc
source ~/.zshrc
```

---

## ⚠️ Důležité poznámky

### MFA (Dvoufázové ověření)

Pokud máte na Garmin účtu zapnuté MFA:
- Při prvním spuštění vás bot vyzve k zadání kódu z SMS/e-mailu
- Po zadání kódu se session uloží a další spuštění budou automatická

### Interval mezi dotazy

- **Nedoporučuji méně než 5-10 minut**
- Při příliš častém volání (např. každou vteřinu) Garmin může dočasně zablokovat vaši IP adresu
- Defaultní interval je 10 minut (600 sekund)

### Aktuálnost dat

- Bot získává data, která hodinky již odeslaly do cloudu (přes telefon)
- Pokud hodinky nejsou v dosahu telefonu, data v cloudu nebudou aktuální
- Doporučuji spouštět bot po synchronizaci hodinek s telefonem

### Duplicitní záznamy

- Bot automaticky kontroluje, zda už pro dané datum existuje záznam
- Pokud existuje, **aktualizuje** ho (ne vytvoří duplicit)
- Pokud neexistuje, **přidá** nový řádek

---

## 🐛 Řešení problémů

### "GARMIN_EMAIL musí být nastaven"

→ Nastav environment variables (krok 4)

### "Google credentials nenalezeny"

→ Zkontroluj, že máte `credentials.json` v složce projektu (Service Account) nebo `token.json` (OAuth2)

### "Permission denied" při zápisu do Google Sheets

→ Sdílej Google Sheet s emailem Service Account (Varianta A, krok 7)

### "Chyba při připojení k Garmin Connect"

→ Zkontroluj email a heslo
→ Pokud máte MFA, zadej kód při prvním spuštění
→ Zkontroluj, že máte internetové připojení

### "Garmin IP blocked"

→ Počkej 10-30 minut
→ Zvyš interval mezi dotazy (--interval 1800 = 30 minut)

---

## 📝 Logy

Logy se ukládají do: `logs/garmin_bot.log`

**Zobrazení posledních logů:**
```bash
tail -n 50 logs/garmin_bot.log
```

---

## ✅ Hotovo!

Pokud vidíš v logu:
- `✅ Připojeno k Garmin Connect`
- `✅ Google Sheets připojeno`
- `✅ Data přidána pro YYYY-MM-DD`

**Vše funguje! 🎉**

---

**Hodně štěstí! 🚀**


# 🚀 Nastavení Garmin Bot - Tvé kroky

## ✅ Sheet ID zjištěn:
```
1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM
```

---

## 📋 KROK 1: Nastav environment variables

**Otevři terminál a zkopíruj/vlož** (nahraď svými Garmin údaji):

```bash
export GARMIN_EMAIL='tvuj-garmin-email@gmail.com'
export GARMIN_PASSWORD='tvoje-garmin-heslo'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'
```

**Příklad:**
```bash
export GARMIN_EMAIL='jan.novak@gmail.com'
export GARMIN_PASSWORD='moje-heslo-123'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'
```

**Stiskni Enter.**

---

## 📋 KROK 2: Zkontroluj nastavení

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 setup_garmin_bot.py
```

**Mělo by se zobrazit:**
- ✅ Všechny knihovny jsou nainstalované
- ✅ Všechny environment variables jsou nastavené
- ✅ credentials.json nalezen
- ✅ Vše je připraveno!

**Pokud vidíš chyby, vrať se na KROK 1 a zkontroluj údaje.**

---

## 📋 KROK 3: První test

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 garmin_bot.py --once
```

**Co se stane:**
- Bot se připojí k Garmin Connect
- Pokud máš MFA (dvoufázové ověření), může tě vyzvat k zadání kódu z SMS/e-mailu
- Stáhne dnešní data z Garmin
- Odešle je do Google Sheets

**Zkontroluj Google Sheet** - měl by se objevit nový řádek s daty!

---

## 📋 KROK 4: Spuštění automatického režimu (volitelné)

Pokud chceš, aby bot automaticky každých 10 minut stahoval data:

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 garmin_bot.py
```

**Bot bude běžet dokud ho nezastavíš:**
- Stiskni `Ctrl + C` pro zastavení

---

## ⚠️ Důležité poznámky:

### MFA (Dvoufázové ověření)
- Pokud máš na Garmin účtu zapnuté MFA, při prvním spuštění tě bot vyzve k zadání kódu
- Zadej kód z SMS/e-mailu
- Bot si session uloží a další spuštění budou automatická

### Environment variables
- Tyto proměnné platí jen pro aktuální terminál
- Pokud zavřeš terminál, musíš je nastavit znovu
- Pro trvalé nastavení viz níže

### Trvalé nastavení (volitelné)
Pokud chceš, aby se proměnné nastavily automaticky při každém otevření terminálu:

```bash
echo 'export GARMIN_EMAIL="tvuj-email@gmail.com"' >> ~/.zshrc
echo 'export GARMIN_PASSWORD="tvoje-heslo"' >> ~/.zshrc
echo 'export GOOGLE_SHEET_ID="1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🎉 Hotovo!

Pokud vše proběhlo úspěšně:
- ✅ Data se ukládají do Google Sheets
- ✅ Bot funguje
- ✅ Můžeš spustit automatický režim

---

## ❓ Problémy?

### "GARMIN_EMAIL musí být nastaven"
→ Vrať se na KROK 1 a nastav environment variables znovu

### "Chyba při připojení k Garmin Connect"
→ Zkontroluj email a heslo
→ Pokud máš MFA, zadej kód při prvním spuštění

### "Permission denied" při zápisu do Google Sheets
→ Zkontroluj, že jsi nasdílel Sheet s emailem: `garmin-bot@cursor-garmin-data.iam.gserviceaccount.com`
→ Oprávnění musí být "Editor"

### "Garmin IP blocked"
→ Počkej 10-30 minut
→ Zvyš interval: `python3 garmin_bot.py --interval 1800` (30 minut)

---

**Hodně štěstí! 🚀**


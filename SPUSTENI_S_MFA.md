# 🔐 Spuštění Garmin Bot s MFA

## ✅ Vše je nastavené!

Environment variables jsou nastavené a vše je připraveno. Teď potřebuješ spustit bot **přímo v terminálu**, aby ses mohl přihlásit s MFA kódem.

---

## 🚀 Spuštění (2 kroky):

### KROK 1: Otevři terminál

Otevři terminál na Macu:
- **Stiskni:** `Cmd + Mezerník`
- **Napiš:** `Terminal`
- **Stiskni:** `Enter`

### KROK 2: Spusť bot

**Zkopíruj a vlož do terminálu:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 garmin_bot.py --once
```

**Stiskni Enter.**

---

## 🔐 Co se stane:

1. **Bot se připojí k Garmin Connect**
2. **Zobrazí se:** `MFA code:`
3. **Zkontroluj SMS nebo e-mail** - měl bys dostat kód
4. **Zadej kód** a stiskni Enter
5. **Bot stáhne data** a odešle je do Google Sheets

**💡 Po prvním přihlášení si bot uloží session a další spuštění budou automatická (bez MFA)!**

---

## ✅ Zkontroluj výsledek:

**Otevři Google Sheet:**
https://docs.google.com/spreadsheets/d/1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM/edit

**Měl by se objevit:**
- Nový list "Garmin Data" (pokud neexistoval)
- Řádek s dnešními daty (kroky, tep, stres, atd.)

---

## 🚀 Automatický režim (po prvním přihlášení):

Až se poprvé úspěšně přihlásíš, můžeš spustit automatický režim:

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 garmin_bot.py
```

Bot bude každých 10 minut automaticky stahovat data.

**Pro zastavení:** Stiskni `Ctrl + C`

---

## 💡 Pro trvalé nastavení (volitelné):

Pokud nechceš pokaždé zadávat environment variables, přidej je do `~/.zshrc`:

```bash
echo 'export GARMIN_EMAIL="juran.kirill@gmail.com"' >> ~/.zshrc
echo 'export GARMIN_PASSWORD="**h2^SdcZkY!2Hq22F"' >> ~/.zshrc
echo 'export GOOGLE_SHEET_ID="1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM"' >> ~/.zshrc
source ~/.zshrc
```

Pak můžeš spustit bot jednoduše:
```bash
python3 garmin_bot.py --once
```

---

**Hodně štěstí! 🚀**


# ⚙️ KROK 5: Nastavení environment variables

## Co potřebuješ:

1. **Garmin email** - email, který používáš pro Garmin Connect
2. **Garmin heslo** - heslo pro Garmin Connect
3. **Google Sheet ID** - ID z URL tvého Google Sheet

---

## 📋 KROK 5.1: Získání Google Sheet ID

### Jak najít Sheet ID:

1. **Otevři Google Sheet** v prohlížeči
2. **Podívej se do adresního řádku** (kde je URL)
3. **URL vypadá takto:**
   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL012MNO345PQR/edit#gid=0
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      TOHLE JE SHEET ID!
   ```

4. **Zkopíruj část mezi `/d/` a `/edit`**
   - To je tvůj Sheet ID
   - Příklad: `1ABC123DEF456GHI789JKL012MNO345PQR`

**💡 Nebo mi dej URL a já ti ho vytáhnu!**

---

## 📋 KROK 5.2: Nastavení environment variables

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

---

## ✅ KROK 5.3: Kontrola nastavení

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 setup_garmin_bot.py
```

**Mělo by se zobrazit:**
- ✅ Všechny knihovny jsou nainstalované
- ✅ Všechny environment variables jsou nastavené
- ✅ credentials.json nalezen
- ✅ Vše je připraveno!

---

## 🚀 KROK 5.4: První test

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 garmin_bot.py --once
```

**Co se stane:**
- Bot se připojí k Garmin Connect
- Pokud máš MFA, může tě vyzvat k zadání kódu
- Stáhne dnešní data
- Odešle je do Google Sheets

**Zkontroluj Google Sheet** - měl by se objevit nový řádek s daty!

---

## ⚠️ Důležité:

**Environment variables platí jen pro aktuální terminál!**

Pokud zavřeš terminál, musíš je nastavit znovu.

**Pro trvalé nastavení** (volitelné):
```bash
echo 'export GARMIN_EMAIL="tvuj-email@gmail.com"' >> ~/.zshrc
echo 'export GARMIN_PASSWORD="tvoje-heslo"' >> ~/.zshrc
echo 'export GOOGLE_SHEET_ID="1ABC123..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 🎉 Hotovo!

Pokud vše proběhlo úspěšně, můžeš spustit automatický režim:
```bash
python3 garmin_bot.py
```


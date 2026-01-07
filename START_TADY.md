# 🚀 ZAČNI TADY - Rychlý start

Toto je nejjednodušší způsob, jak spustit aplikaci. Postupuj krok za krokem.

---

## ⚡ RYCHLÝ START (5 minut)

### 1️⃣ Otevři Terminál

**Stiskni:** `Cmd + Mezerník` → napiš `Terminal` → stiskni `Enter`

---

### 2️⃣ Zkopíruj a vlož tento příkaz (celý řádek):

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 check_ready.py
```

**Stiskni Enter.**

Tento příkaz zkontroluje, co je potřeba nastavit.

---

### 3️⃣ Pokud vidíš chybu s Xcode tools:

**Zkopíruj a vlož:**

```bash
xcode-select --install
```

**Stiskni Enter.**

Otevře se okno - klikni **"Install"** a počkej (5-10 minut).

---

### 4️⃣ Nainstaluj závislosti

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && pip3 install -r requirements.txt
```

**Stiskni Enter** a počkej (1-2 minuty).

---

### 5️⃣ Získej Gemini API klíč

1. **Otevři prohlížeč** (Safari/Chrome)
2. **Jdi na:** https://makersuite.google.com/app/apikey
3. **Přihlas se** Google účtem
4. **Klikni:** "Create API Key" nebo "Get API Key"
5. **Zkopíruj klíč** (dlouhý text)

---

### 6️⃣ Nastav API klíč

**Zkopíruj a vlož** (nahraď `TVUJ-KLIC` svým klíčem):

```bash
export GEMINI_API_KEY='TVUJ-KLIC'
```

**Stiskni Enter.**

**Příklad:**
```bash
export GEMINI_API_KEY='AIzaSyAbc123def456ghi789jkl012mno345pqr'
```

---

### 7️⃣ Uprav konfiguraci

**Zkopíruj a vlož:**

```bash
open -a TextEdit config/config.yaml
```

**Stiskni Enter.**

V TextEdit:
1. Najdi `https://example.com`
2. Změň na skutečný web (např. `https://techcrunch.com`)
3. Ulož: `Cmd + S`
4. Zavři TextEdit

---

### 8️⃣ Spusť aplikaci

**Zkopíruj a vlož:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && python3 main.py --once
```

**Stiskni Enter.**

Počkej 1-5 minut. Aplikace:
- ✅ Scrapuje weby
- ✅ Analyzuje pomocí Gemini AI
- ✅ Zobrazuje výsledky

---

### 9️⃣ Zkontroluj výsledky

**Zkopíruj a vlož:**

```bash
tail -n 50 logs/monitoring.log
```

**Stiskni Enter.**

Uvidíš výsledky!

---

## ✅ HOTOVO!

Pokud vidíš v logu:
- `✅ Gemini Analyzer inicializován`
- `✅ Relevantní obsah nalezen`
- `📊 Statistiky:`

**Vše funguje! 🎉**

---

## ❓ Problémy?

### "command not found"
→ Zkontroluj, že jsi v správné složce:
```bash
cd "/Users/kirilljuran/Downloads/test cursor"
```

### "GEMINI_API_KEY musí být nastaven"
→ Nastav klíč znovu (KROK 6)

### "google-generativeai není nainstalován"
→ Nainstaluj znovu (KROK 4)

### Chceš detailnější návod?
→ Otevři soubor: `NAVOD_PRO_ZACATECNIKY.md`

---

## 📧 (Volitelné) Nastavení emailu

Pokud chceš email reporty:

1. **Jdi na:** https://myaccount.google.com/apppasswords
2. Vytvoř App Password pro "Mail"
3. **Zkopíruj a vlož** (nahraď svými údaji):

```bash
export EMAIL_USERNAME='tvuj-email@gmail.com'
export EMAIL_PASSWORD='app-password-zde'
export EMAIL_FROM='tvuj-email@gmail.com'
export EMAIL_TO='recipient@example.com'
```

---

**Hodně štěstí! 🚀**


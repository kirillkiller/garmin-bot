# 🔧 Oprava chyby 403

## Problém
Vidíš chybu "HTTP ERROR 403 - Přístup odepřen" v prohlížeči.

## Řešení

### Možnost 1: Spusť pomocí skriptu (nejjednodušší)

V terminálu zkopíruj a vlož:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
./start_web.sh
```

**Stiskni Enter.**

---

### Možnost 2: Ruční spuštění

**Krok 1:** Otevři terminál

**Krok 2:** Zkopíruj a vlož (celý blok najednou):

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GEMINI_API_KEY='AIzaSyChgMKbJkVphcOsajYLdfKNWLTgK0kJt3Y'
python3 web_app.py
```

**Stiskni Enter** po každém řádku.

**Krok 3:** Měl bys vidět:
```
🌐 Webové rozhraní spuštěno na http://localhost:5000
 * Running on http://127.0.0.1:5000
```

**Krok 4:** Otevři prohlížeč a jdi na: **http://127.0.0.1:5000**

(NE `localhost:5000`, ale `127.0.0.1:5000`)

---

### Možnost 3: Pokud stále nefunguje

Zkus jiný port:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GEMINI_API_KEY='AIzaSyChgMKbJkVphcOsajYLdfKNWLTgK0kJt3Y'
python3 -c "
from web_app import app
app.run(host='127.0.0.1', port=5001, debug=True)
"
```

Pak jdi na: **http://127.0.0.1:5001**

---

## ✅ Co bys měl vidět

Po úspěšném spuštění:
- V terminálu: "Running on http://127.0.0.1:5000"
- V prohlížeči: Webové rozhraní s 4 záložkami (Weby, AI Prompt, Reporty, Statistiky)

---

## ❓ Stále nefunguje?

1. **Zkontroluj, že terminál je otevřený** a server běží
2. **Zkontroluj chybové hlášky** v terminálu
3. **Zkus jiný port** (5001, 8000, atd.)
4. **Zkontroluj firewall** - možná blokuje localhost

---

**Pošli, co vidíš v terminálu, a pomůžu ti to opravit!**


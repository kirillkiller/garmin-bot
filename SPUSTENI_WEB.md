# 🚀 Spuštění Webového Rozhraní

## Krok 1: Nainstaluj Flask

V terminálu zkopíruj a vlož:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
pip3 install flask flask-cors
```

**Stiskni Enter** a počkej na instalaci.

---

## Krok 2: Nastav API klíč

Zkopíruj a vlož (pokud ještě nemáš nastavený):

```bash
export GEMINI_API_KEY='AIzaSyChgMKbJkVphcOsajYLdfKNWLTgK0kJt3Y'
```

**Stiskni Enter.**

---

## Krok 3: Spusť webové rozhraní

Zkopíruj a vlož:

```bash
python3 web_app.py
```

**Stiskni Enter.**

Měl bys vidět:
```
🌐 Webové rozhraní spuštěno na http://localhost:5000
 * Running on http://0.0.0.0:5000
```

---

## Krok 4: Otevři v prohlížeči

1. Otevři **Safari** nebo **Chrome**
2. Jdi na adresu: **http://localhost:5000**
3. **Stiskni Enter**

Měl by se otevřít webový interface!

---

## ✅ Hotovo!

Teď můžeš:
- ✅ Přidávat weby k monitorování
- ✅ Upravovat AI prompt
- ✅ Generovat reporty
- ✅ Zobrazovat statistiky
- ✅ Spouštět monitoring

---

## ❓ Problémy?

### "flask: command not found" nebo "ModuleNotFoundError: No module named 'flask'"
→ Nainstaluj Flask znovu:
```bash
pip3 install flask flask-cors
```

### "Port 5000 already in use"
→ Zavři jinou aplikaci, která používá port 5000, nebo změň port v `web_app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)  # Změň 5000 na 5001
```

### "GEMINI_API_KEY musí být nastaven"
→ Nastav klíč:
```bash
export GEMINI_API_KEY='AIzaSyChgMKbJkVphcOsajYLdfKNWLTgK0kJt3Y'
```

---

## 🛑 Zastavení

Pro zastavení webového rozhraní:
- Stiskni `Ctrl + C` v terminálu

---

**Hodně štěstí! 🚀**


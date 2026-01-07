# 🔑 Nastavení Gemini API klíče - Jednoduchý návod

## 🚀 Automatický způsob (doporučeno)

Po dokončení instalace Xcode Tools spusť:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
python3 setup_gemini.py
```

Tento skript:
- ✅ Otevře prohlížeč s Google AI Studio
- ✅ Provede tě celým procesem
- ✅ Nastaví klíč automaticky
- ✅ Uloží ho trvale (pokud chceš)

---

## 📝 Ruční způsob

### 1. Získání klíče

1. **Otevři prohlížeč** a jdi na: https://makersuite.google.com/app/apikey
2. **Přihlas se** Google účtem
3. **Klikni** na "Create API Key" nebo "Get API Key"
4. **Zkopíruj** vygenerovaný klíč (vypadá jako: `AIzaSyAbc123...`)

### 2. Nastavení v terminálu

**Zkopíruj a vlož** (nahraď `TVUJ-KLIC` svým klíčem):

```bash
export GEMINI_API_KEY='TVUJ-KLIC'
```

**Stiskni Enter.**

### 3. Ověření

```bash
echo $GEMINI_API_KEY
```

Měl bys vidět svůj klíč.

### 4. (Volitelné) Trvalé uložení

Aby se klíč nastavil automaticky při každém otevření terminálu:

```bash
echo 'export GEMINI_API_KEY="TVUJ-KLIC"' >> ~/.zshrc
source ~/.zshrc
```

---

## ✅ Hotovo!

Po nastavení můžeš pokračovat s instalací závislostí:

```bash
pip3 install -r requirements.txt
```

---

## ❓ Problémy?

### "command not found"
→ Zkontroluj, že jsi v správné složce:
```bash
cd "/Users/kirilljuran/Downloads/test cursor"
```

### "GEMINI_API_KEY musí být nastaven"
→ Spusť znovu: `python3 setup_gemini.py`

### Nemám Google účet
→ Vytvoř si ho na: https://accounts.google.com/signup


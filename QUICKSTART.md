# 🚀 Rychlý start

## 1. Instalace

```bash
# Instalace závislostí
pip install -r requirements.txt
```

## 2. Nastavení API klíčů

**Všechna AI práce se dělá pomocí Google Gemini API.**

```bash
# Gemini API klíč (z https://makersuite.google.com/app/apikey)
export GEMINI_API_KEY='tvůj-klíč'

# Email (pro Gmail použij App Password)
export EMAIL_USERNAME='tvůj-email@gmail.com'
export EMAIL_PASSWORD='app-password'
export EMAIL_FROM='tvůj-email@gmail.com'
export EMAIL_TO='recipient@example.com'
```

## 3. Konfigurace

```bash
# Zkopíruj příklad konfigurace
cp config/config.example.yaml config/config.yaml

# Uprav config/config.yaml - přidej weby, které chceš monitorovat
```

## 4. Spuštění

```bash
# Jednorázové spuštění
python main.py --once

# Nebo kontinuální monitoring
python main.py
```

## 5. Gmail App Password

Pro Gmail musíš vytvořit App Password:

1. Jdi na https://myaccount.google.com/apppasswords
2. Vyber "Mail" a "Other (Custom name)"
3. Zadej "Web Monitoring"
4. Zkopíruj vygenerované heslo
5. Použij ho jako `EMAIL_PASSWORD`

## ✅ Hotovo!

Aplikace nyní:
- ✅ Scrolluje konfigurované weby
- ✅ Extrahuje obsah
- ✅ Analyzuje pomocí Gemini AI
- ✅ Detekuje relevantní informace
- ✅ Posílá emailové reporty

## 🔍 Kontrola logů

```bash
tail -f logs/monitoring.log
```

## 📊 Statistiky

Statistiky se zobrazují v logu po každém běhu. Můžeš také použít:

```python
from storage import Database

db = Database()
stats = db.get_statistics()
print(stats)
```


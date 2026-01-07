# 🚀 Návod k spuštění aplikace

## Krok 1: Instalace závislostí

```bash
# Přejdi do složky projektu
cd "/Users/kirilljuran/Downloads/test cursor"

# Nainstaluj závislosti
pip3 install -r requirements.txt
```

**Pokud máš problém s instalací** (chybějící Xcode tools):
```bash
# Nainstaluj Xcode Command Line Tools
xcode-select --install
```

Nebo použij `--user` flag:
```bash
pip3 install --user -r requirements.txt
```

## Krok 2: Získání Gemini API klíče

1. Jdi na: https://makersuite.google.com/app/apikey
2. Přihlas se pomocí Google účtu
3. Klikni na "Create API Key"
4. Zkopíruj vygenerovaný klíč

## Krok 3: Nastavení environment variables

Otevři terminál a nastav:

```bash
# Gemini API klíč (POVINNÉ)
export GEMINI_API_KEY='tvůj-gemini-api-klíč-zde'

# Email nastavení (POVINNÉ pokud chceš email reporty)
export EMAIL_USERNAME='tvůj-email@gmail.com'
export EMAIL_PASSWORD='app-password'  # Viz krok 4
export EMAIL_FROM='tvůj-email@gmail.com'
export EMAIL_TO='recipient@example.com'
```

**Pro trvalé nastavení** (aby se neobnovovalo při každém restartu):
```bash
# Přidej do ~/.zshrc
echo 'export GEMINI_API_KEY="tvůj-klíč"' >> ~/.zshrc
echo 'export EMAIL_USERNAME="tvůj-email@gmail.com"' >> ~/.zshrc
echo 'export EMAIL_PASSWORD="app-password"' >> ~/.zshrc
echo 'export EMAIL_FROM="tvůj-email@gmail.com"' >> ~/.zshrc
echo 'export EMAIL_TO="recipient@example.com"' >> ~/.zshrc

# Načti změny
source ~/.zshrc
```

## Krok 4: Gmail App Password (pokud používáš Gmail)

Pokud chceš posílat emaily přes Gmail:

1. Jdi na: https://myaccount.google.com/apppasswords
2. Vyber "Mail" a "Other (Custom name)"
3. Zadej "Web Monitoring"
4. Zkopíruj vygenerované 16-místné heslo
5. Použij ho jako `EMAIL_PASSWORD` (ne běžné heslo!)

## Krok 5: Konfigurace webů

Uprav `config/config.yaml`:

```yaml
websites:
  - url: "https://techcrunch.com"  # Změň na weby, které chceš monitorovat
    name: "TechCrunch"
    scroll_depth: 3
    wait_time: 2
    selectors:
      title: "h1, h2"
      content: "article, .content, p"
      links: "a[href]"
```

**Důležité:** Změň `example.com` na skutečné weby, které chceš monitorovat!

## Krok 6: Test konfigurace

Zkontroluj, že vše funguje:

```bash
# Zkontroluj, že máš nastavené proměnné
echo $GEMINI_API_KEY
echo $EMAIL_USERNAME

# Zkontroluj, že máš nainstalované závislosti
python3 -c "import google.generativeai; print('✅ Gemini OK')"
python3 -c "import selenium; print('✅ Selenium OK')"
python3 -c "import yaml; print('✅ YAML OK')"
```

## Krok 7: Spuštění aplikace

### Varianta A: Jednorázové spuštění (test)

```bash
python3 main.py --once
```

Toto spustí monitoring jednou a skončí. Ideální pro testování.

### Varianta B: Kontinuální monitoring

```bash
python3 main.py
```

Toto bude monitorovat weby opakovaně podle nastavení v `config.yaml` (defaultně každou hodinu).

**Pro zastavení:** Stiskni `Ctrl+C`

## Krok 8: Kontrola výsledků

### Logy
```bash
# Sleduj logy v reálném čase
tail -f logs/monitoring.log

# Nebo zobraz posledních 50 řádků
tail -n 50 logs/monitoring.log
```

### Databáze
```bash
# Zobraz statistiky (v Pythonu)
python3 -c "
from storage import Database
db = Database()
stats = db.get_statistics()
print(stats)
"
```

### Email
Pokud je vše nastavené správně, měl bys dostat email s relevantními obsahy.

## 🔧 Troubleshooting

### Chyba: "GEMINI_API_KEY musí být nastaven"
```bash
# Zkontroluj, že je nastaven
echo $GEMINI_API_KEY

# Pokud není, nastav ho
export GEMINI_API_KEY='tvůj-klíč'
```

### Chyba: "google-generativeai není nainstalován"
```bash
pip3 install google-generativeai
```

### Chyba: "ChromeDriver not found"
Selenium 4.6+ automaticky stáhne ChromeDriver. Pokud máš problém:
```bash
# macOS
brew install chromedriver

# Nebo stáhni ručně z:
# https://chromedriver.chromium.org/
```

### Chyba: "Email sending failed"
- Zkontroluj, že používáš **App Password** pro Gmail, ne běžné heslo
- Zkontroluj SMTP nastavení v `config.yaml`
- Zkontroluj logy pro detailní chybovou hlášku

### Aplikace běží, ale nenalézá žádné relevantní obsahy
- Zkontroluj, že weby v `config.yaml` jsou správné
- Sniž `relevance_threshold` v konfiguraci (např. na 0.5)
- Přidej více kategorií do `interesting_categories`
- Zkontroluj logy, zda se vůbec scrapuje

## ✅ Kontrolní seznam před spuštěním

- [ ] Závislosti nainstalovány (`pip3 install -r requirements.txt`)
- [ ] Gemini API klíč nastaven (`export GEMINI_API_KEY='...'`)
- [ ] Email proměnné nastaveny (pokud chceš emaily)
- [ ] Gmail App Password vytvořen (pokud používáš Gmail)
- [ ] `config/config.yaml` upraven (skutečné weby místo example.com)
- [ ] Chrome/Chromium nainstalován (pro Selenium)

## 🎯 Rychlý test

Pro rychlý test bez emailu:

1. V `config/config.yaml` nastav:
   ```yaml
   email:
     enabled: false
   ```

2. Spusť:
   ```bash
   python3 main.py --once
   ```

3. Zkontroluj logy:
   ```bash
   tail -n 100 logs/monitoring.log
   ```

## 📚 Další informace

- `README_MONITORING.md` - Kompletní dokumentace
- `GEMINI_FEATURES.md` - Vše o AI funkcích
- `ARCHITEKTURA.md` - Architektura aplikace


# 🌐 Web Monitoring s AI Agentem (Gemini)

Aplikace pro automatické monitorování webů, analýzu obsahu pomocí **Google Gemini AI** a posílání emailových reportů o relevantních informacích.

**Všechna AI práce se dělá pomocí Google Gemini API** - analýza, kategorizace, filtrování, sumarizace a extrakce entit.

## 🏗️ Architektura

Aplikace se skládá z následujících komponent:

1. **Web Scraper** - Scrolluje weby a extrahuje obsah
2. **Gemini Analyzer** - Analyzuje obsah pomocí Google Gemini AI
3. **Database** - Ukládá zpracované informace (detekce duplicit)
4. **Email Service** - Posílá emailové reporty
5. **Scheduler** - Pravidelné spouštění monitoringu
6. **Main Orchestrator** - Koordinuje všechny komponenty

## 📋 Požadavky

- Python 3.7+
- Chrome/Chromium browser (pro Selenium)
- ChromeDriver (automaticky stáhne Selenium 4.6+)
- Google Gemini API klíč
- Email účet pro odesílání reportů

## 🚀 Instalace

### 1. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 2. Instalace ChromeDriver

Selenium 4.6+ automaticky stáhne ChromeDriver. Pokud máš problémy:

```bash
# macOS
brew install chromedriver

# Nebo stáhni ručně z:
# https://chromedriver.chromium.org/
```

### 3. Nastavení API klíčů

Získej Gemini API klíč z [Google AI Studio](https://makersuite.google.com/app/apikey)

```bash
export GEMINI_API_KEY='tvůj-gemini-api-klíč'
```

### 4. Konfigurace

Uprav `config/config.yaml`:

```yaml
ai:
  api_key: "${GEMINI_API_KEY}"  # nebo přímo zde

websites:
  - url: "https://example.com"
    name: "Example Site"
    scroll_depth: 3
    wait_time: 2

interesting_categories:
  - "technologie"
  - "AI a machine learning"

email:
  username: "${EMAIL_USERNAME}"
  password: "${EMAIL_PASSWORD}"
  from_address: "monitoring@example.com"
  to_addresses:
    - "recipient@example.com"
```

Nebo nastav environment variables:

```bash
export GEMINI_API_KEY='tvůj-klíč'
export EMAIL_USERNAME='tvůj-email@gmail.com'
export EMAIL_PASSWORD='app-password'  # Pro Gmail použij App Password
export EMAIL_FROM='monitoring@example.com'
export EMAIL_TO='recipient@example.com'
```

## 💻 Použití

### Jednorázové spuštění

```bash
python main.py --once
```

### Spuštění se schedulerem (kontinuální monitoring)

```bash
python main.py
```

Aplikace bude automaticky kontrolovat weby každou hodinu (nebo podle konfigurace).

### S vlastní konfigurací

```bash
python main.py --config cesta/k/config.yaml --once
```

## 📁 Struktura projektu

```
.
├── main.py                 # Hlavní orchestrator
├── config/
│   ├── config.yaml        # Konfigurační soubor
│   └── __init__.py        # Konfigurační modul
├── scraper/
│   ├── web_scraper.py     # Web scraper
│   └── __init__.py
├── analyzer/
│   ├── gemini_analyzer.py # Gemini AI analyzer
│   └── __init__.py
├── storage/
│   ├── database.py        # Database modul
│   └── __init__.py
├── email_service/
│   ├── email_sender.py    # Email service
│   └── __init__.py
├── scheduler/
│   ├── task_scheduler.py  # Scheduler
│   └── __init__.py
├── data/                  # Databáze (vytvoří se automaticky)
├── logs/                  # Logy (vytvoří se automaticky)
└── requirements.txt
```

## ⚙️ Konfigurace

### Websites

```yaml
websites:
  - url: "https://example.com"
    name: "Example Site"
    scroll_depth: 3        # Kolikrát scrollovat (0 = nekonečně)
    wait_time: 2          # Sekundy čekání mezi scrollováním
    selectors:            # CSS selektory
      title: "h1, h2"
      content: "article, .content"
      links: "a[href]"
```

### Zajímavé kategorie

```yaml
interesting_categories:
  - "technologie"
  - "AI a machine learning"
  - "startupy"
  - "investice"

relevance_threshold: 0.7  # Práh relevance (0-1)
```

### Email

```yaml
email:
  enabled: true
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_tls: true
  username: "${EMAIL_USERNAME}"
  password: "${EMAIL_PASSWORD}"  # Pro Gmail použij App Password
  from_address: "${EMAIL_FROM}"
  to_addresses:
    - "${EMAIL_TO}"
  subject_template: "🔔 Nový relevantní obsah - {category}"
```

**Poznámka pro Gmail:** Musíš vytvořit [App Password](https://myaccount.google.com/apppasswords) místo běžného hesla.

### Scheduler

```yaml
scheduler:
  enabled: true
  check_interval: 3600  # Sekundy (1 hodina)
```

## 📊 Databáze

Aplikace používá SQLite databázi (`data/monitoring.db`) s následujícími tabulkami:

- `scraped_content` - Extrahovaný obsah
- `analyses` - AI analýzy
- `sent_reports` - Historie odeslaných emailů

## 🔍 Jak to funguje

1. **Scraping**: Aplikace scrolluje konfigurované weby a extrahuje obsah
2. **AI Před-filtrování** (volitelné): Gemini inteligentně vybere nejrelevantnější obsahy před analýzou
3. **Deduplikace**: Kontroluje hash obsahu v databázi (zabránění duplicitám)
4. **AI Analýza**: Gemini analyzuje obsah, kategorizuje a hodnotí relevanci
5. **AI Vylepšení** (volitelné): Gemini vylepšuje shrnutí pro lepší čitelnost
6. **AI Extrakce entit** (volitelné): Gemini extrahuje klíčové entity (lidé, společnosti, témata)
7. **Filtrace**: Pouze obsah s `relevance_score >= threshold` a `is_relevant = true`
8. **AI Agregované shrnutí**: Gemini vytváří agregované shrnutí pro více článků
9. **Email Report**: Odeslání HTML emailu se shrnutím a zdroji
10. **Uložení**: Všechny výsledky se ukládají do databáze

## 🤖 AI Funkce (vše pomocí Gemini)

Aplikace využívá Google Gemini pro:

- ✅ **Analýza obsahu** - Kategorizace, relevance scoring, extrakce klíčových bodů
- ✅ **Inteligentní filtrování** - Před-analýza výběr nejrelevantnějších obsahů
- ✅ **Vylepšování shrnutí** - Zlepšení čitelnosti a informativnosti shrnutí
- ✅ **Agregované shrnutí** - Shrnutí více článků do jednoho přehledu
- ✅ **Extrakce entit** - Identifikace lidí, společností, témat a míst

## 🐛 Troubleshooting

### ChromeDriver chyby

```bash
# Zkontroluj verzi Chrome
google-chrome --version

# Stáhni odpovídající ChromeDriver
# https://chromedriver.chromium.org/
```

### Gemini API chyby

- Zkontroluj, zda je `GEMINI_API_KEY` správně nastaven
- Ověř, zda máš dostatek API kvóty (Gemini má generosní free tier)
- Zkontroluj logy pro detailní chybové hlášky
- Získej nový klíč z: https://makersuite.google.com/app/apikey

### Email chyby

- Pro Gmail: Použij App Password, ne běžné heslo
- Zkontroluj SMTP nastavení
- Některé servery vyžadují TLS

### Selenium chyby

- Zkontroluj, zda máš nainstalovaný Chrome/Chromium
- Zkontroluj ChromeDriver verzi
- Zkus spustit v non-headless módu pro debugging

## 📈 Rozšíření

Aplikaci můžeš rozšířit o:

- PostgreSQL místo SQLite
- Redis queue pro paralelní zpracování
- Webhook notifikace místo emailu
- Dashboard pro vizualizaci
- API endpoint pro externí přístup
- Více Gemini modelů (gemini-1.5-pro, gemini-pro-vision pro obrázky)
- Batch processing s Gemini pro větší objemy dat

## 📝 License

MIT

## 🤝 Contributing

Pull requesty jsou vítány!


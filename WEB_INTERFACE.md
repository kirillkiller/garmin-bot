# 🌐 Webové rozhraní - Návod

## Spuštění webového rozhraní

### 1. Instalace závislostí

```bash
pip3 install flask flask-cors
```

### 2. Spuštění

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GEMINI_API_KEY='tvůj-klíč'
python3 web_app.py
```

### 3. Otevření v prohlížeči

Jdi na: **http://localhost:5000**

## Funkce webového rozhraní

### 📋 Správa webů
- **Přidat web**: Klikni na "+ Přidat web" a vyplň formulář
- **Smazat web**: Klikni na "🗑️ Smazat" u příslušného webu
- **Automatické uložení**: Změny se ukládají do `config/config.yaml`

### 🤖 Fine-tuning AI Promptu
- **Upravit prompt**: Přejdi na záložku "AI Prompt"
- **Uložit**: Klikni na "💾 Uložit Prompt"
- **Proměnné**: Můžeš použít `{title}`, `{content}`, `{categories}`, `{threshold}`
- **Uložení**: Prompt se ukládá do `config/ai_prompt.txt`

### 📊 Reporty
- **Vygenerovat report**: Vyber měsíc a klikni na "📄 Vygenerovat Report"
- **Filtrování duplicit**: Automaticky se vyloučí obsahy z předchozích měsíců
- **Měsíční reporty**: Automaticky se generují na konci každého měsíce

### 📈 Statistiky
- Zobrazení celkových statistik
- Počet obsahů, analýz, relevantních obsahů

### ▶️ Spuštění monitoringu
- Klikni na "▶️ Spustit Monitoring" pro manuální spuštění

## API Endpointy

### GET `/api/status`
Získá status aplikace a statistiky

### GET `/api/websites`
Získá seznam monitorovaných webů

### POST `/api/websites`
Přidá nový web
```json
{
  "url": "https://example.com",
  "name": "Example",
  "scroll_depth": 5,
  "wait_time": 2
}
```

### DELETE `/api/websites/<index>`
Odstraní web podle indexu

### GET `/api/prompt`
Získá aktuální AI prompt

### POST `/api/prompt`
Aktualizuje AI prompt
```json
{
  "prompt": "Tvůj custom prompt..."
}
```

### GET `/api/reports`
Získá seznam reportů

### POST `/api/reports/generate`
Vygeneruje report
```json
{
  "month": "2025-01"  // volitelné
}
```

### POST `/api/monitor/run`
Spustí monitoring na požádání

## Měsíční reporty

### Automatické generování

Měsíční reporty se automaticky generují na konci každého měsíce.

Pro spuštění monthly scheduleru:

```python
from monthly_scheduler import MonthlyScheduler

scheduler = MonthlyScheduler()
scheduler.start()
```

### Manuální generování

```python
from report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate_monthly_report("2025-01")
generator.send_monthly_report("2025-01")  # Pošle emailem
generator.save_report_to_file("2025-01")  # Uloží do souboru
```

## Filtrování duplicit

Aplikace automaticky filtruje duplicity:
- Obsahy z předchozích měsíců se nevkládají do nových reportů
- Každý obsah se zobrazí pouze jednou v měsíčním reportu
- Historie je uložena v databázi

## Custom AI Prompt

Můžeš použít následující proměnné v promptu:
- `{title}` - Nadpis článku
- `{content}` - Textový obsah
- `{categories}` - Seznam zajímavých kategorií
- `{threshold}` - Relevance threshold

Příklad:
```
Analyzuj následující obsah:

Nadpis: {title}
Obsah: {content}

Zajímavé kategorie: {categories}
Relevance threshold: {threshold}

Vrať JSON s analýzou...
```


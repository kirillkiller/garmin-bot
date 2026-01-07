# 🤖 Gemini AI Funkce

Tento dokument popisuje všechny AI funkce, které aplikace využívá pomocí **Google Gemini API**.

## Přehled AI funkcí

Všechna AI práce v aplikaci se dělá pomocí Google Gemini. Žádné jiné AI služby se nepoužívají.

## 1. Analýza obsahu (`analyze_content`)

**Co dělá:**
- Analyzuje extrahovaný obsah z webů
- Kategorizuje obsah do kategorií
- Hodnotí relevanci (0-1 score)
- Extrahuje klíčové body
- Vytváří shrnutí
- Poskytuje reasoning pro rozhodnutí

**Použití:**
```python
analysis = analyzer.analyze_content(
    url="https://example.com/article",
    title="Nadpis článku",
    content="Textový obsah..."
)
```

**Výstup:**
```json
{
    "category": "technologie",
    "relevance_score": 0.85,
    "summary": "Shrnutí obsahu...",
    "key_points": ["bod 1", "bod 2"],
    "is_relevant": true,
    "reasoning": "Vysvětlení relevance"
}
```

## 2. Inteligentní filtrování (`intelligent_filter`)

**Co dělá:**
- Před-analýza filtrování velkého množství obsahů
- Gemini vybere nejrelevantnější obsahy před detailní analýzou
- Šetří API volání a čas

**Kdy použít:**
- Když scrapuješ velké množství obsahů (>10)
- Chceš analyzovat jen nejrelevantnější
- Chceš ušetřit API kvótu

**Konfigurace:**
```yaml
ai:
  use_intelligent_filtering: true
```

## 3. Vylepšování shrnutí (`enhance_summary`)

**Co dělá:**
- Vylepšuje původní shrnutí pomocí Gemini
- Dělá shrnutí jasnější, stručnější a informativnější
- Používá kontext z analýzy

**Kdy použít:**
- Když chceš lepší kvalitu shrnutí v emailech
- Když původní shrnutí není dostatečně jasné

**Konfigurace:**
```yaml
ai:
  enhance_summaries: true
```

## 4. Agregované shrnutí (`summarize_multiple`)

**Co dělá:**
- Vytváří agregované shrnutí z více analýz
- Identifikuje hlavní témata napříč články
- Vytváří přehled klíčových poznatků

**Kdy použít:**
- Když máš více relevantních článků v jedné kategorii
- Chceš vytvořit přehledný report

**Použití:**
Automaticky se používá v email reportech, když je více článků.

## 5. Extrakce entit (`extract_key_entities`)

**Co dělá:**
- Extrahuje klíčové entity z obsahu
- Identifikuje: lidi, společnosti, témata, místa
- Ukládá strukturovaně v JSON

**Kdy použít:**
- Když chceš strukturovaná data o entitách
- Pro další analýzu nebo filtrování
- Pro lepší kategorizaci

**Konfigurace:**
```yaml
ai:
  extract_entities: true
```

**Výstup:**
```json
{
    "people": ["Elon Musk", "Satya Nadella"],
    "companies": ["OpenAI", "Google"],
    "topics": ["AI", "Machine Learning"],
    "locations": ["San Francisco", "Seattle"]
}
```

## 6. Batch analýza (`batch_analyze`)

**Co dělá:**
- Analyzuje více obsahů najednou
- Efektivní zpracování většího množství dat

**Použití:**
```python
contents = [
    {"url": "...", "title": "...", "content": "..."},
    {"url": "...", "title": "...", "content": "..."}
]
analyses = analyzer.batch_analyze(contents)
```

## Konfigurace AI

Všechny AI funkce se konfigurují v `config/config.yaml`:

```yaml
ai:
  provider: "gemini"  # Pouze Gemini
  model: "gemini-pro"  # gemini-pro, gemini-1.5-pro
  api_key: "${GEMINI_API_KEY}"
  temperature: 0.7  # Kreativita (0-1)
  
  # Pokročilé funkce
  use_intelligent_filtering: true
  enhance_summaries: true
  extract_entities: false
```

## Gemini modely

Dostupné modely:
- `gemini-pro` - Standardní model pro text
- `gemini-1.5-pro` - Pokročilejší model (pokud dostupný)
- `gemini-pro-vision` - Pro obrázky (není v této verzi použito)

## API kvóta

Google Gemini má generosní free tier:
- 60 požadavků za minutu
- 1500 požadavků za den
- Více než dostatečné pro monitoring aplikaci

Pro produkci můžeš upgradovat na paid tier.

## Best practices

1. **Teplota**: Pro analýzu použij 0.5-0.7 (konzistentnější)
2. **Filtrování**: Zapni pro velké objemy dat
3. **Shrnutí**: Zapni pro lepší email reporty
4. **Entity**: Zapni jen pokud je potřebuješ
5. **Batch processing**: Použij pro efektivitu

## Monitoring AI použití

AI volání se logují v `logs/monitoring.log`:
- Počet analýz
- Chyby API
- Časy odpovědí

## Troubleshooting

**Chyby API:**
- Zkontroluj API klíč
- Ověř kvótu
- Zkontroluj logy

**Pomalé odpovědi:**
- Sniž teplotu
- Použij filtrování
- Omez délku obsahu

**Špatné výsledky:**
- Uprav zajímavé kategorie
- Změň relevance threshold
- Uprav prompty v kódu


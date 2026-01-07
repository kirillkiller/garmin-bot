# 🏗️ Architektura Web Monitoring Aplikace s AI Agentem

## Přehled systému

Aplikace monitoruje weby, analyzuje obsah pomocí AI a posílá emailové reporty o relevantních informacích.

## Komponenty

### 1. **Web Scraper** (`scraper/`)
- **Účel**: Scrolluje weby a extrahuje obsah
- **Technologie**: Selenium/Playwright (pro JavaScript weby) nebo BeautifulSoup (pro statické)
- **Funkce**:
  - Scrollování stránky
  - Extrakce textu, obrázků, odkazů
  - Čekání na načtení dynamického obsahu
  - Zpracování více stránek

### 2. **AI Analyzer** (`analyzer/`)
- **Účel**: Analyzuje extrahovaný obsah pomocí AI
- **Technologie**: OpenAI API
- **Funkce**:
  - Kategorizace obsahu
  - Detekce relevantních informací
  - Shrnutí a extrakce klíčových bodů
  - Scoring relevance

### 3. **Email Service** (`email_service/`)
- **Účel**: Posílá emailové reporty
- **Technologie**: SMTP (smtplib)
- **Funkce**:
  - Formátování reportů
  - Odesílání emailů
- **Podpora**: HTML i plain text

### 4. **Database/Storage** (`storage/`)
- **Účel**: Ukládá zpracované informace (aby se neposílaly duplicity)
- **Technologie**: SQLite (jednoduché) nebo PostgreSQL (produkce)
- **Funkce**:
  - Ukládání extrahovaného obsahu
  - Hashování pro detekci duplicit
  - Historie zpracování
  - Metadata (datum, zdroj, kategorie)

### 5. **Configuration** (`config/`)
- **Účel**: Konfigurace aplikace
- **Obsah**:
  - Seznam monitorovaných webů
  - Zajímavé kategorie
  - Email nastavení
  - AI nastavení
  - Scraping parametry

### 6. **Scheduler** (`scheduler/`)
- **Účel**: Pravidelné spouštění monitoringu
- **Technologie**: APScheduler nebo cron
- **Funkce**:
  - Naplánování kontrol
  - Retry logika
  - Error handling

### 7. **Main Orchestrator** (`main.py`)
- **Účel**: Koordinuje všechny komponenty
- **Funkce**:
  - Spouští scraper
  - Předává data analyzátoru
  - Ukládá do databáze
  - Posílá emaily při detekci relevance

## Datový tok

```
1. Scheduler → Spustí monitoring
2. Scraper → Scrolluje web → Extrahuje obsah
3. Storage → Kontrola duplicit (hash)
4. Analyzer → AI analýza → Kategorizace + Scoring
5. Orchestrator → Rozhodnutí: relevantní?
   ├─ ANO → Email Service → Odeslání reportu
   └─ NE → Uložení do DB (bez emailu)
6. Storage → Uložení výsledku
```

## Struktura dat

### Extrahovaný obsah
```python
{
    "url": "https://example.com/article",
    "title": "Nadpis článku",
    "content": "Textový obsah...",
    "timestamp": "2024-01-01T12:00:00",
    "hash": "sha256_hash"
}
```

### Analýza
```python
{
    "content_id": "hash",
    "category": "technologie",
    "relevance_score": 0.85,
    "summary": "Shrnutí...",
    "key_points": ["bod1", "bod2"],
    "is_relevant": True
}
```

### Report
```python
{
    "subject": "Nový relevantní obsah nalezen",
    "body": "HTML/Text report",
    "sources": [{"url": "...", "title": "..."}],
    "timestamp": "..."
}
```

## Bezpečnost a best practices

1. **Rate limiting**: Respektování robots.txt a rate limits
2. **User-Agent**: Nastavení vhodného user agentu
3. **Error handling**: Graceful handling chyb
4. **Logging**: Kompletní logování pro debugging
5. **Retry logic**: Opakování při selhání
6. **Data privacy**: Šifrování citlivých dat

## Škálovatelnost

- **Horizontální**: Více workerů pro paralelní scraping
- **Vertikální**: Větší databáze, více paměti
- **Queue system**: Redis/RabbitMQ pro task queue
- **Caching**: Cache pro často přistupovaná data


# 📺 YouTube Bot - Monitorování kanálů a stahování transkriptů

Bot pro automatické monitorování YouTube kanálů a stahování transkriptů nových videí.

## 🚀 Rychlý start

### 1. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 2. Přidání kanálu

```bash
python youtube_bot.py add "https://www.youtube.com/@channelname"
```

Nebo různé formáty URL:
- `https://www.youtube.com/@channelname`
- `https://www.youtube.com/channel/UCxxxxx`
- `https://youtube.com/c/channelname`

### 3. Kontrola kanálů

```bash
# Jednorázová kontrola
python youtube_bot.py check

# Nebo automatický scheduler
python youtube_scheduler.py
```

## 📋 Příkazy

### Přidání kanálu

```bash
python youtube_bot.py add <channel_url>
```

Příklad:
```bash
python youtube_bot.py add "https://www.youtube.com/@mkbhd"
```

### Kontrola všech kanálů

```bash
python youtube_bot.py check
```

Zkontroluje všechny aktivní kanály a stáhne transkripty nových videí.

### Seznam kanálů

```bash
python youtube_bot.py list
```

Zobrazí všechny monitorované kanály.

### Seznam videí

```bash
# Všechna videa
python youtube_bot.py videos

# Videa z konkrétního kanálu
python youtube_bot.py videos "https://www.youtube.com/@channelname"
```

## ⚙️ Automatický scheduler

Pro automatické periodické kontroly:

```bash
# Spustí scheduler (kontroluje každou hodinu)
python youtube_scheduler.py

# Jednorázová kontrola
python youtube_scheduler.py --once
```

Nastavení intervalu v `config/config.yaml`:

```yaml
youtube:
  enabled: true
  check_interval: 3600  # sekundy (1 hodina)
  max_videos_per_channel: 50
```

## 🗄️ Databáze

Všechna data jsou uložena v SQLite databázi `data/monitoring.db`:

- **youtube_channels** - Monitorované kanály
- **youtube_videos** - Videa s transkripty

### Přístup k datům

```python
from storage.database import Database

db = Database()

# Získej kanály
channels = db.get_youtube_channels()

# Získej videa
videos = db.get_youtube_videos(channel_url="https://...")

# Videa s transkripty
videos_with_transcripts = db.get_youtube_videos(with_transcript=True)
```

## 🧪 Testování

```bash
python test_youtube_bot.py
```

Testuje všechny funkce bota:
- Přidání kanálu
- Získání videí
- Stahování transkriptů
- Zpracování kanálu

## 📝 Transkripty

Bot automaticky stahuje transkripty v následujících jazycích (v pořadí priority):
1. Čeština (cs)
2. Angličtina (en)
3. Slovenština (sk)
4. Automatické titulky (pokud nejsou dostupné manuální)

Transkripty jsou uloženy jako čistý text v databázi.

## 🔧 Konfigurace

V `config/config.yaml`:

```yaml
youtube:
  enabled: true
  check_interval: 3600  # sekundy
  max_videos_per_channel: 50
  channels:
    - "https://www.youtube.com/@channel1"
    - "https://www.youtube.com/@channel2"
  transcript_languages:
    - "cs"
    - "en"
    - "sk"
```

## 📊 Logy

Logy jsou ukládány do `logs/youtube_bot.log`:

```bash
# Sleduj logy v reálném čase
tail -f logs/youtube_bot.log

# Posledních 50 řádků
tail -n 50 logs/youtube_bot.log
```

## 🐛 Troubleshooting

### Chyba: "yt-dlp není nainstalován"

```bash
pip install yt-dlp
```

### Transkript není dostupný

Některá videa nemají transkripty. Bot to zaznamená v logu a uloží video i bez transkriptu.

### Kanál se nepodařilo přidat

Zkontroluj formát URL. Podporované formáty:
- `https://www.youtube.com/@channelname`
- `https://www.youtube.com/channel/UCxxxxx`
- `https://youtube.com/c/channelname`

### Pomalé stahování

Sniž `max_videos_per_channel` v konfiguraci nebo zkontroluj rychlost internetu.

## 💡 Tipy

1. **Pravidelné kontroly**: Použij scheduler pro automatické kontroly
2. **Limit videí**: Nastav `max_videos_per_channel` podle potřeby
3. **Backup**: Pravidelně zálohuj `data/monitoring.db`
4. **Výkon**: Pro velké kanály zvaž nižší `max_videos_per_channel`

## 📦 Struktura

```
youtube_bot.py          # Hlavní bot
youtube_scheduler.py     # Automatický scheduler
test_youtube_bot.py     # Test script
storage/database.py     # Databáze (rozšířena o YouTube tabulky)
config/config.yaml      # Konfigurace
```

## 🎯 Použití v kódu

```python
from youtube_bot import YouTubeBot

# Vytvoř bot
bot = YouTubeBot()

# Přidej kanál
bot.add_channel("https://www.youtube.com/@channelname")

# Zpracuj kanál
stats = bot.process_channel("https://www.youtube.com/@channelname")

# Zkontroluj všechny kanály
stats = bot.check_all_channels()
```

## ✅ Funkce

- ✅ Monitorování více kanálů současně
- ✅ Automatické stahování transkriptů
- ✅ Podpora více jazyků
- ✅ SQLite databáze pro ukládání
- ✅ Automatický scheduler
- ✅ Detekce nových videí
- ✅ Logování všech akcí
- ✅ CLI rozhraní

## 📄 Licence

Stejná jako hlavní projekt.


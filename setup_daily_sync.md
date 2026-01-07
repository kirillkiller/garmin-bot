# 📅 Nastavení denní synchronizace

## ✅ Co máme hotovo:

- ✅ **366 záznamů** v Google Sheets (celý rok 2025)
- ✅ **Robustní MFA handling** - session se ukládá, není potřeba opakovaně zadávat kód
- ✅ **Správné parsování** - rozlišení mezi `None` (chybějící data) a `0` (skutečná nula)
- ✅ **Opravené chyby** - `max_vo2` a `max_fitness_age` se správně parsují

## 🚀 Navržené další kroky:

### 1. **Denní automatická synchronizace** (DOPORUČENO)

Stahovat data pro včerejšek každý den automaticky.

**Možnosti:**

#### A) Cron job (macOS/Linux)
```bash
# Otevři crontab editor
crontab -e

# Přidej tento řádek (stahuje data každý den v 1:00 ráno)
0 1 * * * cd "/Users/kirilljuran/Downloads/test cursor" && /path/to/daily_sync.sh
```

#### B) LaunchAgent (macOS - doporučeno)
Vytvoř `~/Library/LaunchAgents/com.garmin.daily_sync.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.garmin.daily_sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/kirilljuran/Downloads/test cursor/daily_sync.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>1</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/kirilljuran/Downloads/test cursor/logs/daily_sync.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/kirilljuran/Downloads/test cursor/logs/daily_sync_error.log</string>
</dict>
</plist>
```

Pak spusť:
```bash
launchctl load ~/Library/LaunchAgents/com.garmin.daily_sync.plist
```

### 2. **Monitoring a notifikace**

- Email notifikace při chybách
- Slack/Discord webhook
- Push notifikace (macOS)

### 3. **Statistiky a analýzy**

- Týdenní/měsíční reporty
- Trendy a grafy v Google Sheets
- Porovnání s předchozími obdobími

### 4. **Backup a recovery**

- Automatický backup Google Sheets
- Recovery script pro chybějící data
- Verzování dat

## 💡 Doporučení:

**Začni s denní synchronizací** - je to nejdůležitější pro udržení dat aktuálních.

Chceš, abych nastavil některou z těchto možností?


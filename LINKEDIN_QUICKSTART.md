# 🚀 LinkedIn Monitoring - Rychlý Start

Nejjednodušší způsob, jak spustit LinkedIn monitoring agenta.

## ⚡ 5 kroků k spuštění

### 1️⃣ Nainstaluj závislosti

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
pip3 install -r requirements.txt
playwright install chromium
```

### 2️⃣ Nastav LinkedIn přihlašovací údaje

```bash
export LINKEDIN_EMAIL='tvuj-email@example.com'
export LINKEDIN_PASSWORD='tvoje-heslo'
```

### 3️⃣ Uprav konfiguraci

Otevři `config/linkedin_config.yaml` a přidej profily k monitorování:

```yaml
monitored_profiles:
  - "https://www.linkedin.com/in/username-1"
  - "https://www.linkedin.com/in/username-2"
```

**Tip:** Můžeš použít jen username místo celé URL:
```yaml
monitored_profiles:
  - "username-1"
```

### 4️⃣ Spusť jednou (test)

```bash
python3 linkedin_monitor.py --once
```

Toto spustí jeden cyklus monitoringu. Měl bys vidět prohlížeč, který se přihlásí na LinkedIn a začne monitorovat profily.

### 5️⃣ Spusť kontinuálně

```bash
python3 linkedin_monitor.py
```

Agent bude automaticky kontrolovat profily každou hodinu (nebo podle nastavení v config).

---

## ✅ Hotovo!

Agent nyní:
- ✅ Sleduje zadané LinkedIn profily
- ✅ Detekuje nové posty
- ✅ Sleduje interakce (lajky, komentáře)
- ✅ Ukládá všechna data do databáze

## 📊 Zobrazení dat

Data jsou v SQLite databázi:

```bash
sqlite3 data/monitoring.db
```

Příklady dotazů:

```sql
-- Všechny nové posty
SELECT * FROM linkedin_posts ORDER BY scraped_at DESC LIMIT 10;

-- Aktivity z posledních 24 hodin
SELECT * FROM linkedin_activity_log 
WHERE datetime(detected_at) >= datetime('now', '-24 hours')
ORDER BY detected_at DESC;
```

## ⚠️ Důležité poznámky

1. **LinkedIn může detekovat automatizaci** - používej opatrně
2. **Doporučený interval** - minimálně 1 hodina mezi kontrolami
3. **2FA** - Pokud máš zapnuté 2FA, můžeš potřebovat dočasně vypnout
4. **Headless mód** - Pro debugging použij `headless: false` v config

## 🐛 Problémy?

### "Playwright není nainstalován"
```bash
playwright install chromium
```

### "Nepodařilo se přihlásit"
- Zkontroluj email a heslo
- Zkus se přihlásit manuálně v prohlížeči
- Pokud máš 2FA, zkus dočasně vypnout

### "LinkedIn detekuje automatizaci"
- Zvyš `slow_mo` na 200-500 v config
- Zvyš `delay_between_profiles` na 10-15 sekund
- Používej `headless: false` pro debugging

---

**Více informací:** Viz `LINKEDIN_MONITORING.md`


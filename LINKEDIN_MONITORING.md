# 🔍 LinkedIn Monitoring Agent

Automatický agent pro sledování aktivity konkrétních LinkedIn účtů a jejich interakcí s jinými účty.

## 🎯 Funkce

- ✅ **Sledování profilů** - Monitoruje konkrétní LinkedIn účty
- ✅ **Detekce nových postů** - Automaticky detekuje nové příspěvky
- ✅ **Sledování interakcí** - Sleduje lajky, komentáře a sdílení
- ✅ **Ukládání do databáze** - Všechna data se ukládají pro pozdější analýzu
- ✅ **Periodické kontroly** - Automatické pravidelné kontroly
- ✅ **Detekce změn** - Detekuje nové aktivity a interakce

## 📋 Požadavky

### 1. Instalace závislostí

```bash
pip3 install -r requirements.txt
```

### 2. Instalace Playwright prohlížeče

Playwright potřebuje nainstalovat prohlížeč:

```bash
playwright install chromium
```

### 3. Nastavení LinkedIn přihlašovacích údajů

Nastav environment variables pro přihlášení na LinkedIn:

```bash
export LINKEDIN_EMAIL='tvuj-email@example.com'
export LINKEDIN_PASSWORD='tvoje-heslo'
```

**⚠️ DŮLEŽITÉ:** 
- Použij běžné přihlašovací údaje (ne API klíč)
- Pokud máš 2FA, můžeš potřebovat dočasně vypnout nebo použít App Password
- LinkedIn může detekovat automatizaci - používej opatrně

## ⚙️ Konfigurace

### 1. Uprav konfigurační soubor

Otevři `config/linkedin_config.yaml` a přidej profily k monitorování:

```yaml
monitored_profiles:
  - "https://www.linkedin.com/in/username-1"
  - "https://www.linkedin.com/in/username-2"
  - "username-3"  # Můžeš použít jen username
```

### 2. Nastavení intervalu

Uprav `check_interval` podle potřeby:

```yaml
monitoring:
  check_interval: 3600  # 1 hodina (v sekundách)
```

## 🚀 Spuštění

### Jednorázové spuštění

Spustí jeden cyklus monitoringu a skončí:

```bash
python3 linkedin_monitor.py --once
```

### Kontinuální monitoring

Spustí kontinuální monitoring s pravidelnými kontrolami:

```bash
python3 linkedin_monitor.py
```

Nebo s vlastním intervalem:

```bash
python3 linkedin_monitor.py --interval 1800  # každých 30 minut
```

## 📊 Databáze

Všechna data se ukládají do SQLite databáze `data/monitoring.db`:

### Tabulky

- **linkedin_profiles** - Informace o sledovaných profilech
- **linkedin_posts** - Všechny nalezené posty
- **linkedin_interactions** - Lajky, komentáře a sdílení
- **linkedin_activity_log** - Log všech detekovaných aktivit

### Dotazy na data

Můžeš použít SQLite pro dotazy:

```bash
sqlite3 data/monitoring.db
```

Příklady dotazů:

```sql
-- Všechny nové posty z posledních 24 hodin
SELECT * FROM linkedin_posts 
WHERE datetime(scraped_at) >= datetime('now', '-24 hours')
ORDER BY scraped_at DESC;

-- Aktivity konkrétního profilu
SELECT * FROM linkedin_activity_log 
WHERE profile_url = 'https://www.linkedin.com/in/username'
ORDER BY detected_at DESC;

-- Interakce na konkrétní post
SELECT * FROM linkedin_interactions 
WHERE post_url = 'https://www.linkedin.com/posts/...'
ORDER BY timestamp DESC;
```

## 🔧 API (Python)

Můžeš použít monitor programově:

```python
from linkedin_monitor import LinkedInMonitor

# Vytvořit monitor
monitor = LinkedInMonitor(config_path='config/linkedin_config.yaml')

# Spustit jednou
monitor.run_once()

# Nebo kontinuálně
monitor.run_continuous(interval_seconds=3600)

# Získat shrnutí aktivity
summary = monitor.get_activity_summary(
    profile_url='https://www.linkedin.com/in/username',
    hours=24
)
print(summary)
```

## ⚠️ Omezení a varování

### LinkedIn Rate Limiting

LinkedIn má ochranu proti scrapingu:
- **Nepoužívej příliš často** - doporučený interval je minimálně 1 hodina
- **Používej slow_mo** - pomalejší akce vypadají přirozeněji
- **Headless mód** - může být snáze detekovatelný, používej opatrně

### Detekce automatizace

LinkedIn může:
- Požádat o ověření (captcha)
- Dočasně zablokovat účet
- Vyžadovat telefonní ověření

**Doporučení:**
- Začni s `headless: false` pro debugging
- Používej rozumné intervaly (minimálně 1 hodina)
- Monitoruj jen několik profilů najednou
- Pokud máš problémy, zkus zvýšit `slow_mo` a `delay_between_profiles`

### Legálnost

- Scraping LinkedIn může porušovat jejich Terms of Service
- Používej pouze pro osobní účely
- Respektuj privacy ostatních uživatelů
- Nepoužívej data pro komerční účely bez souhlasu

## 🐛 Řešení problémů

### "Playwright není nainstalován"

```bash
playwright install chromium
```

### "Nepodařilo se přihlásit"

- Zkontroluj, že máš správně nastavené `LINKEDIN_EMAIL` a `LINKEDIN_PASSWORD`
- Zkus se přihlásit manuálně v prohlížeči
- Pokud máš 2FA, můžeš potřebovat dočasně vypnout

### "LinkedIn detekuje automatizaci"

- Zvyš `slow_mo` na 200-500
- Zvyš `delay_between_profiles` na 10-15 sekund
- Používej `headless: false` pro debugging
- Sniž frekvenci kontrol (zvýš `check_interval`)

### "Prohlížeč se nespustí"

- Zkontroluj, že máš nainstalovaný Playwright: `playwright install chromium`
- Zkontroluj, že máš dostatek paměti
- Zkus restartovat počítač

## 📈 Budoucí vylepšení

Možná budoucí funkce:
- Email notifikace při nových aktivitách
- Webhook notifikace
- Analýza sentimentu komentářů
- Detekce trendů v aktivitě
- Export do CSV/JSON
- Webové rozhraní pro zobrazení dat

## 📝 Poznámky

- Agent používá Playwright pro automatizaci prohlížeče
- Všechna data se ukládají lokálně do SQLite databáze
- Agent respektuje rate limiting a používá zpoždění mezi akcemi
- Struktura LinkedIn se může měnit - scraper může potřebovat aktualizace

---

**Vytvořeno podle principů Dona:**
- Simplicity is the ultimate sophistication
- Execution > Ideas
- Automatizace > manuální práce


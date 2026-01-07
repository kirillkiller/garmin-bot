# 📅 Stažení historických dat z Garmin Connect

Bot umí stahovat data z minulosti! Máš několik možností:

---

## ✅ Možnost 1: Jednoduché - konkrétní datum

**Použij přímo garmin_bot.py s parametrem `--date`:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 garmin_bot.py --once --date 2025-12-25
```

**Příklad:**
- `--date 2025-12-25` - stáhne data pro 25. prosince 2025
- `--date 2025-01-01` - stáhne data pro 1. ledna 2025

---

## ✅ Možnost 2: Rozsah dat (od-do)

**Použij pomocný skript `stahnout_historicka_data.py`:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_historicka_data.py --range 2025-12-01 2025-12-31
```

**Příklad:**
- `--range 2025-12-01 2025-12-31` - stáhne všechna data za prosinec 2025
- `--range 2025-01-01 2025-12-31` - stáhne všechna data za celý rok 2025

**Co se stane:**
- Bot projde každý den v rozsahu
- Stáhne data pro každý den
- Odešle je do Google Sheets
- Zobrazí progress a výsledky

---

## ✅ Možnost 3: Posledních N dní

**Stáhni data za posledních X dní:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_historicka_data.py --days 30
```

**Příklad:**
- `--days 30` - stáhne data za posledních 30 dní
- `--days 90` - stáhne data za posledních 90 dní
- `--days 365` - stáhne data za poslední rok

---

## ✅ Možnost 4: Konkrétní datum (pomocný skript)

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_historicka_data.py --date 2025-12-25
```

---

## ⚠️ Důležité poznámky:

### Formát data
- Vždy používej formát: `YYYY-MM-DD`
- Příklad: `2025-12-25` (ne `25.12.2025`)

### MFA kód
- Při prvním spuštění můžeš být vyzván k zadání MFA kódu
- Po prvním přihlášení se session uloží a další dotazy budou automatické

### Rychlost
- Bot stahuje data postupně (jeden den po druhém)
- Pro velký rozsah (např. celý rok) to může trvat několik minut
- Garmin má rate limiting, takže bot čeká mezi dotazy

### Duplicitní záznamy
- Bot automaticky kontroluje, zda už pro dané datum existuje záznam
- Pokud existuje, **aktualizuje** ho (ne vytvoří duplicit)
- Pokud neexistuje, **přidá** nový řádek

---

## 💡 Příklady použití:

### Stáhnout data za prosinec 2025:
```bash
python3 stahnout_historicka_data.py --range 2025-12-01 2025-12-31
```

### Stáhnout data za poslední měsíc:
```bash
python3 stahnout_historicka_data.py --days 30
```

### Stáhnout data za celý rok 2025:
```bash
python3 stahnout_historicka_data.py --range 2025-01-01 2025-12-31
```

### Stáhnout data pro konkrétní den:
```bash
python3 garmin_bot.py --once --date 2025-12-25
```

---

## 🎯 Tip:

Pokud chceš stáhnout data za dlouhé období (např. celý rok), můžeš to rozdělit na menší části:

```bash
# Leden
python3 stahnout_historicka_data.py --range 2025-01-01 2025-01-31

# Únor
python3 stahnout_historicka_data.py --range 2025-02-01 2025-02-28

# atd...
```

---

**Hodně štěstí! 🚀**


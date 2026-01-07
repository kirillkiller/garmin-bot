# 📊 Shrnutí nul v Google Sheet

## 🔍 Nalezené problémy:

### 1. HRV průměr/max/min (59 řádků s nulami)
- **Sloupce:** HRV průměr, HRV max, HRV min
- **Problém:** Většinou starší data z roku 2025
- **Příčina:** HRV data nejsou dostupná pro starší data (možná nebyl zapnutý HRV tracking)

### 2. Tep průměr HRV (61 řádků s nulami)
- **Sloupec:** Tep průměr HRV
- **Problém:** Včetně novějších dat (2026-01-05, 2026-01-06)
- **Příčina:** `get_heart_rates()` vrací prázdný dict nebo neobsahuje `averageHeartRate`

### 3. Tep max/min HRV (59 řádků s nulami)
- **Sloupce:** Tep max HRV, Tep min HRV
- **Problém:** Většinou starší data z roku 2025
- **Příčina:** `get_heart_rates()` vrací prázdný dict nebo neobsahuje `maxHeartRate`/`minHeartRate`

## 💡 Řešení:

### Možnost 1: Data prostě nejsou dostupná (OK)
- Pokud HRV tracking nebyl zapnutý pro starší data, je to normální
- Nuly jsou v pořádku - znamenají, že data nejsou dostupná

### Možnost 2: Zlepšit parsování (pokud data jsou dostupná)
- Zkontrolovat, jestli `get_heart_rates()` vrací data v jiném formátu
- Zkontrolovat, jestli HRV data jsou v jiném místě (např. v `sleep_data` nebo `hrv_data`)

## 🔧 Doporučení:

1. **Pro novější data (2026):** Zkontrolovat, jestli `get_heart_rates()` skutečně vrací data
2. **Pro starší data (2025):** Pokud HRV tracking nebyl zapnutý, nuly jsou v pořádku
3. **Alternativní zdroj:** Zkusit získat tep HRV z `sleep_data.get('sleepHeartRate')` místo `get_heart_rates()`


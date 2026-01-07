# 📊 Jak správně stahovat data z Garmin Connect

## ✅ Ano, data jsou za celý den!

Když stáhneš data pro konkrétní datum (např. `2025-12-25`), dostaneš **kompletní data za celý den**:
- ✅ Počet kroků za celý den (od půlnoci do půlnoci)
- ✅ Celková vzdálenost za den
- ✅ Průměrný tep za celý den
- ✅ Stres za celý den
- ✅ Body Battery za celý den
- ✅ Všechny ostatní metriky za celý den

---

## ⚠️ DŮLEŽITÉ: Dnešní den vs. minulé dny

### Minulé dny (doporučeno)
**Data jsou kompletní!** ✅

Pokud stáhneš data pro včerejšek nebo starší datum, dostaneš kompletní data za celý den.

**Příklad:**
```bash
# Dnes je 5. ledna 2026, stáhni data za 4. leden (včera)
python3 garmin_bot.py --once --date 2026-01-04
```
→ Dostaneš kompletní data za celý 4. leden (od půlnoci do půlnoci)

---

### Dnešní den (může být neúplné)
**Data mohou být neúplná!** ⚠️

Pokud stáhneš data pro dnešní den během dne, dostaneš data **jen do aktuálního času**, ne za celý den.

**Příklad:**
- Dnes je 5. ledna 2026, 15:00
- Stáhneš data pro `2026-01-05`
- Dostaneš data **jen do 15:00**, ne za celý den!

**Kdy jsou data kompletní?**
- Data za dnešní den jsou kompletní až **po půlnoci** (když den skončí)
- Nebo až když hodinky synchronizují všechna data do cloudu

---

## 💡 Doporučený postup:

### 1. Pro minulé dny (nejlepší)
Stáhni data pro včerejšek nebo starší datum - budou kompletní:

```bash
# Stáhni data za včerejšek
python3 garmin_bot.py --once --date 2026-01-04

# Nebo stáhni data za posledních 30 dní
python3 stahnout_historicka_data.py --days 30
```

### 2. Pro dnešní den
Pokud chceš stáhnout data pro dnešní den:
- **Počkej až po půlnoci** - pak budou data kompletní
- Nebo stáhni je ráno následujícího dne (pak už budou kompletní za včerejšek)

**Příklad:**
- Dnes je 5. ledna 2026, 23:00
- Počkej až bude 6. ledna 2026, 00:01
- Pak stáhni data pro 5. leden - budou kompletní!

---

## 🎯 Nejlepší strategie:

### Automatický režim (polling)
Spusť bot v automatickém režimu - bude každých 10 minut stahovat data:

```bash
python3 garmin_bot.py
```

**Výhody:**
- Bot automaticky stáhne data pro dnešní den
- Data se postupně aktualizují během dne
- Večer/po půlnoci budou data kompletní

### Ranní stažení historických dat
Každé ráno stáhni data za včerejšek (která jsou už kompletní):

```bash
# Stáhni data za včerejšek
python3 garmin_bot.py --once --date $(date -v-1d +%Y-%m-%d)
```

**Nebo na macOS:**
```bash
# Včerejšek
YESTERDAY=$(date -v-1d +%Y-%m-%d)
python3 garmin_bot.py --once --date $YESTERDAY
```

---

## 📅 Příklad workflow:

### Den 1 (5. ledna 2026):
```bash
# Ráno - stáhni data za včerejšek (4. leden) - kompletní!
python3 garmin_bot.py --once --date 2026-01-04

# Nebo spusť automatický režim - bude stahovat data za dnešek
python3 garmin_bot.py
```

### Den 2 (6. ledna 2026):
```bash
# Ráno - stáhni data za včerejšek (5. leden) - kompletní!
python3 garmin_bot.py --once --date 2026-01-05
```

---

## 🔍 Jak zkontrolovat, zda jsou data kompletní?

### V Google Sheets:
1. Otevři Google Sheet
2. Podívej se na sloupec "Čas záznamu"
3. Pokud je čas záznamu **po půlnoci následujícího dne**, data jsou kompletní
4. Pokud je čas záznamu **během dne**, data mohou být neúplná

### V datech:
- **Počet kroků** - měl by být blízko tvému dennímu cíli (pokud ho plníš)
- **Čas aktivity** - měl by být blízko 24 hodinám (nebo tvému času vzhůru)
- **Body Battery** - měl by mít hodnoty za celý den

---

## ⚠️ Poznámky:

### Synchronizace hodinek
- Data se synchronizují z hodinek do telefonu
- Pak z telefonu do Garmin cloudu
- Pokud hodinky nejsou synchronizované, data v cloudu nebudou aktuální

### Doporučení
- **Synchronizuj hodinky** před stahováním dat
- **Stahuj data pro minulé dny** - jsou vždy kompletní
- **Pro dnešní den** - stáhni je až po půlnoci nebo ráno následujícího dne

---

## ✅ Shrnutí:

| Kdy stahovat | Data jsou kompletní? | Doporučení |
|-------------|----------------------|------------|
| Minulé dny | ✅ Ano | **Nejlepší volba** |
| Dnešní den (během dne) | ⚠️ Ne (jen do aktuálního času) | Počkej až po půlnoci |
| Dnešní den (po půlnoci) | ✅ Ano | OK |
| Automatický režim | ✅ Ano (postupně se aktualizují) | **Doporučeno** |

---

**Hodně štěstí! 🚀**


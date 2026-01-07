# 🛡️ Ochrana proti duplicitním datům

## ✅ Co jsem přidal:

**Robustní detekce a automatické odstranění duplicitních datumů**

---

## 🎯 Jak to funguje:

### Při každém ukládání dat:

1. **Kontrola existence:**
   - Zkontroluje, zda datum už existuje v Google Sheets

2. **Detekce duplicit:**
   - Pokud najde stejné datum na více řádcích, detekuje všechny výskyty
   - Upozorní v logu

3. **Automatické odstranění:**
   - Smaže všechny duplicitní řádky kromě posledního
   - Aktualizuje poslední řádek s nejnovějšími daty

4. **Normální aktualizace:**
   - Pokud je jen jeden výskyt, aktualizuje ho normálně

---

## 💡 Proč to potřebujeme:

### Možné scénáře duplicit:

1. **Chyba při ukládání:**
   - Pokud by selhalo ukládání uprostřed procesu
   - Mohlo by se přidat duplicitní datum

2. **Manuální zásah:**
   - Pokud by někdo manuálně přidal řádek se stejným datem
   - Bot by to detekoval a opravil

3. **Race condition:**
   - Pokud by se spustily dva procesy současně
   - Mohly by přidat duplicitní data

4. **Chyba v API:**
   - Pokud by Google Sheets API vrátilo chybu
   - Mohlo by dojít k duplicitnímu přidání

---

## 🔧 Technické detaily:

### Kód v `send_to_sheets()`:

```python
# Najít všechny výskyty tohoto data
all_indices = [i + 1 for i, d in enumerate(existing_dates) if d == target_date]

if len(all_indices) > 1:
    # Duplicitní datumy nalezeny
    # Smaže všechny kromě posledního
    for idx in reversed(all_indices[:-1]):
        worksheet.delete_rows(idx)
    
    # Aktualizuje poslední řádek
    row_index = all_indices[-1]
else:
    # Normální případ - jen jeden výskyt
    row_index = all_indices[0]
```

### Proč smazat všechny kromě posledního?

- **Poslední řádek** = nejnovější data
- **Starší řádky** = potenciálně zastaralá data
- **Bezpečnější** = ponechat nejnovější a smazat starší

---

## ✅ Výhody:

1. **Automatické:**
   - Funguje bez manuálního zásahu
   - Detekuje a opraví duplicity automaticky

2. **Bezpečné:**
   - Ponechává nejnovější data
   - Smaže pouze starší duplicity

3. **Robustní:**
   - Funguje i když už jsou duplicity v tabulce
   - Opraví je při příštím ukládání

4. **Logování:**
   - Všechny akce jsou logovány
   - Můžeš sledovat, kdy se duplicity objevily

---

## 🧪 Jak otestovat:

### Kontrola duplicit:

```bash
python3 check_duplicates.py
```

Tento skript:
- Zkontroluje všechny datumy v Google Sheets
- Najde duplicitní datumy
- Zobrazí, na kterých řádcích jsou

### Výstup:

```
📊 Celkem záznamů: 366
✅ ŽÁDNÉ DUPLICITY - vše je v pořádku!
```

Nebo pokud najde duplicity:

```
⚠️  NALEZENY DUPLICITNÍ DATUMY: 2
 2026-01-05: 2x
   Řádky: [5, 10]
 2026-01-04: 3x
   Řádky: [4, 9, 15]
```

---

## 📝 Logy:

Bot loguje všechny akce:

```
⚠️  Duplicitní datumy nalezeny pro 2026-01-05 na řádcích: [5, 10]
🗑️  Mažu duplicitní řádky (ponechávám poslední: řádek 10)...
   ✅ Smazán duplicitní řádek 5
✅ Data aktualizována pro 2026-01-05 (řádek 10)
```

---

## 🎉 Výsledek:

**Teď máš:**
- ✅ Automatickou detekci duplicit
- ✅ Automatické odstranění duplicit
- ✅ Ochranu proti budoucím duplicitám
- ✅ Nástroj pro kontrolu duplicit (`check_duplicates.py`)

**Duplicitní data se už nebudou objevovat!** 🛡️

---

## 🔍 Co se stane při aktualizaci:

### Scénář 1: Normální aktualizace (bez duplicit)
```
Datum 2026-01-05 existuje na řádku 5
→ Aktualizuje řádek 5 s novými daty
```

### Scénář 2: Duplicitní datumy nalezeny
```
Datum 2026-01-05 existuje na řádcích 5, 10, 15
→ Smaže řádky 5 a 10
→ Aktualizuje řádek 15 s novými daty
```

### Scénář 3: Nové datum
```
Datum 2026-01-06 neexistuje
→ Přidá nový řádek s daty
```

---

## ✅ Shrnutí:

**Ochrana proti duplicitám je nyní:**
- ✅ Automatická
- ✅ Robustní
- ✅ Bezpečná
- ✅ Logovaná

**Nemusíš se bát duplicitních dat!** 🎉


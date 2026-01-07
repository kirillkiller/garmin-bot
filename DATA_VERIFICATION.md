# 🔍 Verifikace a aktualizace dat

## ✅ Co jsem přidal:

**Automatická kontrola a aktualizace dat za předvčerejšek**

---

## 🎯 Jak to funguje:

### Každý den v 1:00 ráno:

1. **Stáhne data za včerejšek** (hlavní úkol)
   - Např. dnes je 7.1., stáhne data za 6.1.

2. **Zkontroluje data za předvčerejšek** (verifikace)
   - Např. dnes je 7.1., zkontroluje data za 5.1.
   - Stáhne aktuální data z Garmin
   - Porovná s existujícími daty v Google Sheets
   - Pokud se data změnila, automaticky je aktualizuje

---

## 💡 Proč to děláme:

### Problém:
- Garmin hodinky synchronizují data s cloudem postupně
- Data stáhnutá v 1:00 ráno mohou být neúplná
- Data stáhnutá v 8:00 ráno mohou být kompletnější
- Např. aktivity z večera se mohou synchronizovat až ráno

### Řešení:
- V 1:00 stáhneme data za včerejšek
- Zároveň zkontrolujeme data za předvčerejšek
- Pokud se změnila (např. přibyly aktivity), aktualizujeme je

---

## 📊 Příklad:

### Scénář:
- **6.1. večer:** Běh 5 km (hodinky ještě nesynchronizovány)
- **7.1. 1:00:** Bot stáhne data za 6.1. → běh není v datech
- **7.1. 8:00:** Hodinky synchronizují běh do cloudu
- **8.1. 1:00:** 
  - Bot stáhne data za 7.1. (nový den)
  - Bot zkontroluje data za 6.1. (předvčerejšek)
  - Najde běh 5 km → aktualizuje data za 6.1.

---

## 🔧 Technické detaily:

### Co se děje:

1. **Stáhnout data za předvčerejšek:**
   ```python
   new_data = bot.get_garmin_data(day_before_yesterday)
   ```

2. **Zkontrolovat existenci:**
   ```python
   if day_before_yesterday in existing_dates:
       # Data existují - aktualizovat
   else:
       # Data neexistují - přidat
   ```

3. **Automatická aktualizace:**
   - `send_to_sheets()` automaticky detekuje, že datum už existuje
   - Aktualizuje celý řádek s novými daty
   - Pokud se data nezměnila, aktualizace je idempotentní (bezpečná)

---

## ✅ Výhody:

1. **Kompletní data:**
   - Zajišťuje, že máme nejnovější data i pro starší dny
   - Kompenzuje pozdní synchronizaci hodinek

2. **Automatické:**
   - Funguje bez manuálního zásahu
   - Kontroluje se každý den

3. **Bezpečné:**
   - Pokud se data nezměnila, aktualizace nic nezkazí
   - Pokud se změnila, aktualizuje se automaticky

4. **Efektivní:**
   - Kontroluje se jen jeden den zpět (předvčerejšek)
   - Nezatěžuje Garmin API zbytečně

---

## ⚙️ Konfigurace:

**Aktuální nastavení:**
- Kontroluje se **předvčerejšek** (den -2)
- Kontrola probíhá **každý den v 1:00 UTC**

**Můžeš změnit:**
- Počet dní zpět pro kontrolu (aktuálně 1 = předvčerejšek)
- Čas kontroly (aktuálně stejný jako hlavní synchronizace)

---

## 📝 Logy:

Bot loguje:
- `🔍 Kontroluji data za YYYY-MM-DD (mohla se změnit pozdější synchronizací)...`
- `📊 Data pro YYYY-MM-DD existují - aktualizuji (pokud se změnila)...`
- `✅ Kontrola a aktualizace dokončena pro YYYY-MM-DD`

---

## 🎉 Výsledek:

**Teď máš:**
- ✅ Data za včerejšek (hlavní synchronizace)
- ✅ Ověřená data za předvčerejšek (kontrola změn)
- ✅ Automatická aktualizace, pokud se data změnila

**Všechno automaticky, bez manuální práce!** 🚀


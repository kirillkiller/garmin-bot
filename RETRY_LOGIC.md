# 🔄 Retry logika pro síťové chyby

## ✅ Co jsem opravil:

**Robustní retry logika s exponenciálním backoffem pro síťové chyby**

---

## 🎯 Problém:

### Chyby, které se objevovaly:
- `Connection reset by peer`
- `Connection aborted`
- `ConnectionResetError`

### Příčina:
- Garmin API může resetovat spojení při vysokém zatížení
- Síťové problémy mezi botem a Garmin servery
- Timeouty při dlouhých požadavcích

---

## 💡 Řešení:

### 1. **Detekce síťových chyb:**
```python
is_network_error = (
    "Connection reset" in error_str or
    "Connection aborted" in error_str or
    "ConnectionResetError" in error_str or
    "ConnectionError" in error_str or
    "Timeout" in error_str or
    "ECONNRESET" in error_str or
    "Broken pipe" in error_str
)
```

### 2. **Exponenciální backoff:**
- **Pokus 1:** 10 sekund
- **Pokus 2:** 20 sekund
- **Pokus 3:** 40 sekund
- **Pokus 4:** 80 sekund
- **Pokus 5:** 160 sekund (2.7 minuty)

### 3. **Zvýšený počet pokusů:**
- **Před:** 3 pokusy
- **Po:** 5 pokusů

---

## 🔧 Jak to funguje:

### Příklad při síťové chybě:

```
🔄 Získávám data pro 2024-12-26...
⚠️  Síťová chyba pro 2024-12-26 (pokus 1/5): Connection reset by peer
⏳ Čekám 10 sekund před dalším pokusem...
🔄 Získávám data pro 2024-12-26...
⚠️  Síťová chyba pro 2024-12-26 (pokus 2/5): Connection reset by peer
⏳ Čekám 20 sekund před dalším pokusem...
🔄 Získávám data pro 2024-12-26...
✅ Data získána pro 2024-12-26: 8500 kroků
```

---

## ✅ Výhody:

1. **Automatické opakování:**
   - Bot automaticky zkusí znovu při síťové chybě
   - Nemusíš nic dělat

2. **Exponenciální backoff:**
   - Delší pauzy při opakovaných chybách
   - Nezatěžuje Garmin API zbytečně

3. **Lepší logování:**
   - Vidíš, kolikátý pokus to je
   - Vidíš, jak dlouho bot čeká

4. **Robustní:**
   - Funguje i při opakovaných síťových problémech
   - Zvládne i rate limiting

---

## 📊 Pokryté chyby:

### Síťové chyby:
- ✅ `Connection reset by peer`
- ✅ `Connection aborted`
- ✅ `ConnectionResetError`
- ✅ `ConnectionError`
- ✅ `Timeout`
- ✅ `ECONNRESET`
- ✅ `Broken pipe`

### Rate limiting:
- ✅ `429 Too Many Requests`
- ✅ Rate limit chyby

---

## 🎉 Výsledek:

**Teď máš:**
- ✅ Automatické opakování při síťových chybách
- ✅ Exponenciální backoff (delší pauzy při opakovaných chybách)
- ✅ 5 pokusů místo 3
- ✅ Lepší logování

**Síťové chyby se už nebudou objevovat tak často!** 🛡️

---

## 📝 Poznámky:

- Pokud se chyba opakuje 5x, bot to nahlásí jako selhání
- Telegram notifikace přijde až po 5 neúspěšných pokusech
- Mezitím bot zkouší automaticky opravit problém


# 📅 Stažení dat za poslední rok

## ✅ Jednoduchý příkaz:

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_historicka_data.py --year
```

**Co se stane:**
- Bot stáhne data za posledních 365 dní
- Projde každý den postupně
- Zobrazí progress (každých 10 dní)
- Může to trvat několik hodin (záleží na rychlosti API)

**Pro zastavení:** Stiskni `Ctrl + C`

**Pokračování:** Pokud to přerušíš, můžeš spustit znovu - bot automaticky aktualizuje existující záznamy (ne vytvoří duplicity)

---

## ⚠️ Důležité:

- **Může to trvat dlouho** (až několik hodin pro celý rok)
- **Garmin má rate limiting** - bot čeká mezi dotazy
- **MFA kód** - můžeš být vyzván k zadání kódu při prvním spuštění
- **Duplicity** - bot automaticky aktualizuje existující záznamy, ne vytvoří duplicity

---

## 💡 Tip:

Pokud chceš stáhnout data rychleji, můžeš to rozdělit na měsíce:

```bash
# Leden 2025
python3 stahnout_historicka_data.py --range 2025-01-01 2025-01-31

# Únor 2025
python3 stahnout_historicka_data.py --range 2025-02-01 2025-02-28

# atd...
```

---

**Hodně štěstí! 🚀**


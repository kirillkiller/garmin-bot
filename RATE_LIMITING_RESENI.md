# 🚨 Řešení problému s Rate Limiting od Garmin

## ❌ Problém:
Garmin má velmi přísný rate limiting a při příliš mnoha pokusech o přihlášení vás zablokuje (429 chyba).

## ✅ Řešení 1: Počkej a zkus znovu

**Počkej 15-20 minut** a zkus znovu:

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_historicka_data.py --year
```

**💡 Tip:** Garmin knihovna ukládá session - pokud už máš uloženou session, možná nebude potřeba MFA kód.

---

## ✅ Řešení 2: Stáhni data po měsících (DOPORUČENO)

**Použij nový skript, který stahuje data po měsících s pauzami:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor" && export GARMIN_EMAIL='juran.kirill@gmail.com' && export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F' && export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM' && python3 stahnout_po_mesicich.py
```

**Co se stane:**
- Bot stáhne data za jeden měsíc
- Počká 5 minut
- Stáhne další měsíc
- atd.

**Výhody:**
- ✅ Bezpečnější - méně dotazů najednou
- ✅ Můžeš zastavit a pokračovat později
- ✅ Menší riziko rate limiting

---

## ✅ Řešení 3: Stáhni data po menších částech

**Stáhni data za konkrétní měsíc:**

```bash
# Leden 2025
python3 stahnout_historicka_data.py --range 2025-01-01 2025-01-31

# Počkej 10 minut, pak únor
python3 stahnout_historicka_data.py --range 2025-02-01 2025-02-28

# atd...
```

---

## ✅ Řešení 4: Zkus zítra

**Garmin může mít denní limit** - zkus to zítra ráno.

---

## 💡 Tipy:

1. **První přihlášení:** Po prvním úspěšném přihlášení si bot uloží session - další spuštění budou bez MFA kódu
2. **Čekání:** Mezi pokusy o přihlášení počkej alespoň 15-20 minut
3. **Menší části:** Lepší stáhnout data po menších částech než najednou za celý rok

---

**Hodně štěstí! 🚀**


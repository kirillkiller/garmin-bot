# 🚀 Jak spustit bot interaktivně (s MFA kódem)

## ✅ Jednoduchý způsob:

**Otevři terminál a spusť:**

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GARMIN_EMAIL='juran.kirill@gmail.com'
export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'
python3 garmin_bot.py --once
```

**Když se zobrazí `MFA code:`, zadej kód z SMS/e-mailu a stiskni Enter.**

**Po prvním úspěšném přihlášení se session uloží a další spuštění budou bez MFA!** 🎉

---

## 🔄 Pro dnešek (s kódem 208759):

Pokud máš kód **208759**, zadej ho když se bot zeptá:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GARMIN_EMAIL='juran.kirill@gmail.com'
export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'
python3 garmin_bot.py --once
```

**Počkej na `MFA code:` a zadej: `208759`**

---

## 💡 Proč pořád potřebuješ MFA kód?

**Možné příčiny:**

1. **Session nebyla uložena** - zkontroluj `~/.garth/` adresář
2. **Session expirovala** - Garmin může mít limity na dobu platnosti
3. **Session byla smazána** - pokud jsi smazal `~/.garth/` adresář

**Řešení:**
- Po prvním úspěšném přihlášení by se měla session uložit automaticky
- Pokud to nefunguje, zkus smazat `~/.garth/` a přihlásit se znovu

---

## 🔍 Zkontroluj, jestli session existuje:

```bash
ls -la ~/.garth/
```

Pokud vidíš soubory s tokeny, session existuje a měla by se použít automaticky.


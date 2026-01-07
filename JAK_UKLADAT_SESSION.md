# 🔐 Jak zajistit, aby nebyl pořád potřeba MFA kód

## ✅ Jak to funguje:

Knihovna `garminconnect` používá pod kapotou `garth`, který **automaticky ukládá session** do adresáře `~/.garth/` po prvním úspěšném přihlášení.

**Po prvním přihlášení s MFA kódem:**
1. ✅ Session se automaticky uloží do `~/.garth/`
2. ✅ Při dalším spuštění se session načte automaticky
3. ✅ **Nebude potřeba MFA kód** (dokud session neexpiruje)

---

## 🚀 Jak to použít:

### KROK 1: První přihlášení (s MFA kódem)

**Spusť bot přímo v terminálu** (ne přes skript), aby ses mohl přihlásit s MFA kódem:

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export GARMIN_EMAIL='juran.kirill@gmail.com'
export GARMIN_PASSWORD='**h2^SdcZkY!2Hq22F'
export GOOGLE_SHEET_ID='1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM'
python3 garmin_bot.py --once
```

**Když se zobrazí `MFA code:`, zadej kód z SMS/e-mailu.**

### KROK 2: Ověření, že session byla uložena

Po úspěšném přihlášení bys měl vidět v logu:
```
✅ Session byla uložena - příště nebude potřeba MFA kód
💡 Session je uložena v ~/.garth/ a bude použita při dalším spuštění
```

**Zkontroluj, že session existuje:**
```bash
ls -la ~/.garth/
```

Měl bys vidět soubory s tokeny (např. `oauth1_token`, `oauth2_token`).

### KROK 3: Další spuštění (bez MFA)

**Při dalším spuštění** by bot měl automaticky použít uloženou session:

```bash
python3 garmin_bot.py --once
```

**Měl bys vidět:**
```
🔍 Našel jsem uloženou session - zkouším ji použít...
💡 Pokud session funguje, nebude potřeba MFA kód
✅ Připojeno k Garmin Connect
```

**Bez výzvy k MFA kódu!** 🎉

---

## ⚠️ Kdy může být potřeba MFA znovu:

1. **Session expiruje** - obvykle po několika dnech/týdnech
2. **Session byla smazána** - pokud smažeš `~/.garth/`
3. **Změna hesla** - pokud změníš heslo na Garmin účtu
4. **Rate limiting** - pokud Garmin zablokuje IP adresu

---

## 🔧 Řešení problémů:

### Problém: Pořád se ptá na MFA kód

**Řešení 1: Zkontroluj, že session existuje**
```bash
ls -la ~/.garth/
```

Pokud adresář neexistuje nebo je prázdný, session nebyla uložena.

**Řešení 2: Smaž starou session a zkus znovu**
```bash
rm -rf ~/.garth/
python3 garmin_bot.py --once
```

**Řešení 3: Zkontroluj oprávnění**
```bash
chmod 700 ~/.garth/
```

### Problém: Session expiruje příliš často

**Řešení:** Garmin může mít limity na dobu platnosti session. To je normální - prostě zadej MFA kód znovu, když je potřeba.

---

## 💡 Tipy:

1. **První přihlášení:** Vždy spusť bot **přímo v terminálu** (ne přes skript), aby ses mohl přihlásit s MFA kódem
2. **Automatizace:** Po prvním přihlášení můžeš spustit bot v automatickém režimu (polling) - nebude potřeba MFA
3. **Zálohování:** Pokud chceš, můžeš zálohovat `~/.garth/` adresář, ale **pozor** - obsahuje citlivé tokeny!

---

## 📝 Shrnutí:

✅ **První spuštění:** Spusť v terminálu, zadej MFA kód → session se uloží  
✅ **Další spuštění:** Automaticky použije uloženou session → bez MFA kódu  
✅ **Session expiruje:** Po několika dnech/týdnech → zadej MFA kód znovu  

**To je vše!** 🎉


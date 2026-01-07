# 📊 Jak vytvořit Google Sheet pro Garmin Bot

## ✅ Možnost 1: Vytvoř NOVÝ prázdný Sheet (Doporučeno)

### Krok 1: Otevři Google Sheets

1. **Otevři prohlížeč**
2. **Jdi na:** https://sheets.google.com/
3. **Přihlas se** svým Google účtem

### Krok 2: Vytvoř nový Sheet

1. **Klikni na velké tlačítko** "Blank" (nebo "Prázdný")
   - Nebo klikni na ikonu "+" vlevo nahoře
2. **Otevře se nový prázdný Sheet**

### Krok 3: Pojmenuj Sheet

1. **Vlevo nahoře** uvidíš "Untitled spreadsheet" (nebo "Nepojmenovaný")
2. **Klikni na to** a zadej název, např.:
   - `Garmin Data`
   - `Moje Garmin Statistiky`
   - `Garmin Connect Data`
   - Cokoliv chceš!

### Krok 4: Zkopíruj Sheet ID z URL

**URL bude vypadat takto:**
```
https://docs.google.com/spreadsheets/d/1ABC123DEF456GHI789JKL012MNO345PQR/edit#gid=0
                                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                      TOHLE JE SHEET ID - ZKOPÍRUJ TO!
```

**Co udělat:**
1. **Zkopíruj celý ID** (dlouhý řetězec písmen a čísel)
2. **Ulož si ho** - budeš ho potřebovat v KROKU 5

**Příklad ID:**
```
1ABC123DEF456GHI789JKL012MNO345PQR
```

---

## ✅ Možnost 2: Použij existující Sheet

Pokud už máš Google Sheet, který chceš použít:

1. **Otevři existující Sheet**
2. **Zkopíruj ID z URL** (stejně jako výše)
3. **Hotovo!**

**⚠️ POZOR:** 
- Bot vytvoří nový worksheet s názvem "Garmin Data" v tomto Sheetu
- Pokud už máš data v Sheetu, nic se nestane - bot přidá nový list

---

## 🎯 Co se stane dál?

Bot automaticky:
- ✅ Vytvoří worksheet "Garmin Data" (pokud neexistuje)
- ✅ Přidá hlavičky (Datum, Kroky, Tep, atd.)
- ✅ Začne přidávat data

**Nemusíš nic ručně vytvářet!** Bot to udělá za tebe při prvním spuštění.

---

## 💡 Tip: Jak rychle získat Sheet ID

**Z terminálu (pokud máš URL):**
```bash
# Pokud máš URL v schránce, můžeš použít:
pbpaste | grep -o '/d/[^/]*' | cut -d'/' -f3
```

**Nebo ručně:**
1. Zkopíruj URL z prohlížeče
2. Najdi část mezi `/d/` a `/edit`
3. To je tvůj Sheet ID

---

## ✅ Hotovo!

Pokud máš:
- ✅ Google Sheet vytvořený (nebo existující)
- ✅ Sheet ID zkopírovaný

**Můžeš pokračovat na KROK 4 (sdílení Sheetu)! 🎉**


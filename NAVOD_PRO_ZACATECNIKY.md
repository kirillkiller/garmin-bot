# 📖 Úplný návod pro začátečníky - Krok za krokem

Tento návod tě provede úplně od začátku až do spuštění aplikace.

---

## KROK 1: Otevření Terminálu

1. **Stiskni klávesy:** `Cmd + Mezerník` (Command + Space)
2. **Napiš:** `Terminal`
3. **Stiskni:** `Enter`
4. Otevře se okno s černým pozadím - to je terminál

---

## KROK 2: Přejdi do složky projektu

V terminálu napiš (zkopíruj celý řádek):

```bash
cd "/Users/kirilljuran/Downloads/test cursor"
```

**Stiskni Enter.**

Měl bys vidět něco jako:
```
kirilljuran@MacBook test cursor %
```

---

## KROK 3: Zkontroluj, že máš Python

V terminálu napiš:

```bash
python3 --version
```

**Stiskni Enter.**

Měl bys vidět něco jako: `Python 3.9.6` nebo podobné číslo.

✅ **Pokud vidíš číslo verze Pythonu, pokračuj na KROK 4.**

❌ **Pokud vidíš chybu**, napiš mi a pomůžu ti Python nainstalovat.

---

## KROK 4: Instalace závislostí

V terminálu napiš (zkopíruj celý řádek):

```bash
pip3 install -r requirements.txt
```

**Stiskni Enter.**

Počkej, dokud se nainstalují všechny balíčky. Může to trvat 1-2 minuty.

✅ **Pokud vidíš na konci "Successfully installed..."**, pokračuj na KROK 5.

❌ **Pokud vidíš chybu**, zkus:

```bash
pip3 install --user -r requirements.txt
```

---

## KROK 5: Získání Gemini API klíče

### 5.1 Otevři prohlížeč

1. Otevři **Safari** nebo **Chrome**
2. Jdi na adresu: **https://makersuite.google.com/app/apikey**
3. **Stiskni Enter**

### 5.2 Přihlášení

1. Pokud nejsi přihlášený, klikni na **"Sign in"** (Přihlásit se)
2. Přihlas se pomocí svého **Google účtu**
3. Pokud nemáš Google účet, vytvoř si ho

### 5.3 Vytvoření API klíče

1. Na stránce uvidíš tlačítko **"Create API Key"** nebo **"Get API Key"**
2. **Klikni na něj**
3. Možná tě požádá, abys vybral projekt - vyber **"Create API key in new project"** nebo použij existující
4. Počkej, až se vytvoří klíč
5. **Zkopíruj klíč** (vypadá jako dlouhý text, např. `AIzaSyAbc123...`)
6. **ULOŽ SI HO NĚKAM** (do poznámek, textového souboru, atd.)

---

## KROK 6: Nastavení API klíče v terminálu

Vrať se do terminálu a napiš (nahraď `TVUJ-KLIC-ZDE` svým skutečným klíčem):

```bash
export GEMINI_API_KEY='TVUJ-KLIC-ZDE'
```

**Příklad:**
```bash
export GEMINI_API_KEY='AIzaSyAbc123def456ghi789jkl012mno345pqr'
```

**Stiskni Enter.**

**Důležité:** Tento klíč se nastaví jen pro tuto relaci terminálu. Pokud terminál zavřeš, budeš ho muset nastavit znovu.

---

## KROK 7: Ověření, že klíč je nastaven

V terminálu napiš:

```bash
echo $GEMINI_API_KEY
```

**Stiskni Enter.**

Měl bys vidět svůj API klíč.

✅ **Pokud vidíš klíč**, pokračuj na KROK 8.

❌ **Pokud nevidíš nic**, vrať se na KROK 6 a zkontroluj, že jsi správně zkopíroval klíč.

---

## KROK 8: Úprava konfigurace

### 8.1 Otevři soubor v editoru

V terminálu napiš:

```bash
open -a TextEdit config/config.yaml
```

**Stiskni Enter.**

Otevře se TextEdit s konfiguračním souborem.

### 8.2 Uprav weby

Najdi v souboru sekci:

```yaml
websites:
  - url: "https://example.com"
    name: "Example Site"
```

**Změň `https://example.com`** na skutečný web, který chceš monitorovat.

**Příklad:**
```yaml
websites:
  - url: "https://techcrunch.com"
    name: "TechCrunch"
```

**Nebo:**
```yaml
websites:
  - url: "https://www.theverge.com"
    name: "The Verge"
```

### 8.3 Ulož soubor

1. V TextEdit klikni na **"File"** (Soubor) v menu nahoře
2. Klikni na **"Save"** (Uložit) nebo stiskni `Cmd + S`
3. Zavři TextEdit

---

## KROK 9: Test spuštění

Vrať se do terminálu a napiš:

```bash
python3 main.py --once
```

**Stiskni Enter.**

Aplikace se spustí a začne:
- Scrapovat weby
- Analyzovat obsah pomocí Gemini AI
- Zobrazovat výsledky

**Počkej, až skončí** (může to trvat 1-5 minut podle počtu webů).

---

## KROK 10: Kontrola výsledků

### 10.1 Zobrazení logů

V terminálu napiš:

```bash
tail -n 50 logs/monitoring.log
```

**Stiskni Enter.**

Uvidíš posledních 50 řádků z logu.

### 10.2 Co hledat v logu

✅ **Dobré zprávy:**
- `✅ Gemini Analyzer inicializován`
- `✅ Relevantní obsah nalezen`
- `📊 Statistiky:`

❌ **Problémy:**
- `❌ Chyba` - něco se pokazilo
- `⚠️` - varování

---

## KROK 11: (Volitelné) Nastavení emailu

Pokud chceš dostávat email reporty:

### 11.1 Gmail App Password

1. Jdi na: **https://myaccount.google.com/apppasswords**
2. Přihlas se
3. Klikni na **"Select app"** → vyber **"Mail"**
4. Klikni na **"Select device"** → vyber **"Other (Custom name)"**
5. Napiš: **"Web Monitoring"**
6. Klikni **"Generate"**
7. **Zkopíruj 16-místné heslo** (vypadá jako: `abcd efgh ijkl mnop`)

### 11.2 Nastavení v terminálu

V terminálu napiš (nahraď svými údaji):

```bash
export EMAIL_USERNAME='tvuj-email@gmail.com'
export EMAIL_PASSWORD='abcd efgh ijkl mnop'
export EMAIL_FROM='tvuj-email@gmail.com'
export EMAIL_TO='recipient@example.com'
```

**Stiskni Enter** po každém řádku.

---

## KROK 12: Kontinuální monitoring

Pokud chceš, aby aplikace běžela neustále a kontrolovala weby automaticky:

V terminálu napiš:

```bash
python3 main.py
```

**Stiskni Enter.**

Aplikace bude běžet a kontrolovat weby každou hodinu (nebo podle nastavení).

**Pro zastavení:** Stiskni `Ctrl + C` v terminálu.

---

## 🔧 Rychlá pomoc

### Problém: "command not found"
- Zkontroluj, že jsi v správné složce (`cd "/Users/kirilljuran/Downloads/test cursor"`)

### Problém: "GEMINI_API_KEY musí být nastaven"
- Zkontroluj KROK 6 a 7

### Problém: "google-generativeai není nainstalován"
- Zkontroluj KROK 4

### Problém: "ChromeDriver not found"
- Selenium by měl automaticky stáhnout ChromeDriver
- Pokud ne, napiš mi

### Problém: Aplikace běží, ale nenalézá obsahy
- Zkontroluj, že jsi upravil weby v KROKU 8
- Zkontroluj logy: `tail -n 50 logs/monitoring.log`

---

## ✅ Kontrolní seznam

Před spuštěním zkontroluj:

- [ ] Terminál je otevřený
- [ ] Jsem ve správné složce (`test cursor`)
- [ ] Python je nainstalován (`python3 --version` funguje)
- [ ] Závislosti jsou nainstalovány (`pip3 install -r requirements.txt` proběhlo úspěšně)
- [ ] Mám Gemini API klíč
- [ ] API klíč je nastaven (`echo $GEMINI_API_KEY` zobrazuje klíč)
- [ ] Konfigurace je upravena (skutečné weby místo example.com)
- [ ] (Volitelné) Email je nastaven

---

## 🎯 Rychlý test (bez emailu)

Pokud chceš jen rychle otestovat, že vše funguje:

1. V `config/config.yaml` najdi sekci `email:` a změň:
   ```yaml
   email:
     enabled: false
   ```

2. Spusť:
   ```bash
   python3 main.py --once
   ```

3. Zkontroluj logy:
   ```bash
   tail -n 50 logs/monitoring.log
   ```

---

## 📞 Potřebuješ pomoc?

Pokud narazíš na problém:
1. Zkontroluj logy: `tail -n 50 logs/monitoring.log`
2. Zkontroluj, že jsi prošel všechny kroky
3. Zkopíruj chybovou hlášku a pošli mi ji

---

**Hodně štěstí! 🚀**


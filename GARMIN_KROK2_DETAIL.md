# 📋 KROK 2: Vytvoření Google Service Account - Detailní návod

Postupuj přesně podle těchto kroků. Každý krok má screenshot a popis.

---

## 🎯 Co je Service Account?

Service Account je "virtuální uživatel" pro Google, který umožňuje aplikaci (botovi) přistupovat k Google Sheets bez toho, aby ses musel přihlašovat ručně.

---

## ✅ KROK 2.1: Otevři Google Cloud Console

1. **Otevři prohlížeč** (Safari, Chrome, Firefox - cokoliv)
2. **Jdi na:** https://console.cloud.google.com/
3. **Přihlas se** svým Google účtem (stejný, který používáš pro Google Sheets)

**Co uvidíš:**
- Pokud jsi tam poprvé, uvidíš úvodní obrazovku
- Pokud už máš projekty, uvidíš seznam projektů

---

## ✅ KROK 2.2: Vytvoř nový projekt

### 2.2.1 Najdi dropdown s projekty

1. **V horní části stránky** (modrý pruh) najdeš dropdown menu
2. **Vlevo nahoře** uvidíš něco jako:
   ```
   Google Cloud Platform  ▼
   ```
   nebo
   ```
   Select a project  ▼
   ```

3. **Klikni na tento dropdown**

### 2.2.2 Vytvoř nový projekt

1. **V otevřeném menu** klikni na **"NEW PROJECT"** (nebo "Nový projekt")
2. **Otevře se okno** s formulářem
3. **Zadej:**
   - **Project name:** `Garmin Bot` (nebo jakýkoliv název, např. "Muj Garmin Bot")
   - **Project ID:** (nech automaticky vygenerované, nebo zadej vlastní)
4. **Klikni "CREATE"** (nebo "Vytvořit")
5. **Počkej 5-10 sekund** - projekt se vytváří
6. **Když se zobrazí "Project created"** - klikni "SELECT PROJECT" (nebo projekt se automaticky vybere)

**💡 Tip:** Pokud nevidíš "NEW PROJECT", můžeš kliknout na ikonu "+" vedle "Select a project"

---

## ✅ KROK 2.3: Povol Google Sheets API

### 2.3.1 Otevři API Library

1. **V levém menu** (sidebar) najdi **"APIs & Services"** (nebo "Rozhraní API a služby")
2. **Klikni na to**
3. **V podmenu** klikni na **"Library"** (nebo "Knihovna")

**Co uvidíš:**
- Seznam všech Google API
- Vyhledávací pole nahoře

### 2.3.2 Povol Google Sheets API

1. **V vyhledávacím poli** (nahoře) napiš: `Google Sheets API`
2. **Stiskni Enter** nebo klikni na lupu
3. **Klikni na výsledek** "Google Sheets API"
4. **Na stránce API** klikni velké modré tlačítko **"ENABLE"** (nebo "Povolit")
5. **Počkej 2-3 sekundy** - API se povolí
6. **Uvidíš zelenou hlášku** "API enabled" (nebo "Rozhraní API povoleno")

### 2.3.3 Povol Google Drive API

1. **Zpět na "Library"** - klikni vlevo na "APIs & Services" → "Library"
2. **V vyhledávacím poli** napiš: `Google Drive API`
3. **Stiskni Enter**
4. **Klikni na výsledek** "Google Drive API"
5. **Klikni "ENABLE"** (nebo "Povolit")
6. **Počkej** až se povolí

**💡 Proč obě API?**
- Google Sheets API - pro čtení a zápis do Sheets
- Google Drive API - pro přístup k souborům (Sheets jsou součástí Drive)

---

## ✅ KROK 2.4: Vytvoř Service Account

### 2.4.1 Otevři Credentials

1. **V levém menu** → "APIs & Services" → **"Credentials"** (nebo "Přihlašovací údaje")
2. **Uvidíš stránku** s přihlašovacími údaji

### 2.4.2 Vytvoř Service Account

1. **Nahoře** klikni na **"CREATE CREDENTIALS"** (nebo "Vytvořit přihlašovací údaje")
2. **V dropdown menu** vyber **"Service account"**
3. **Otevře se formulář**

### 2.4.3 Vyplň formulář

1. **Service account name:**
   - Zadej: `garmin-bot` (nebo jakýkoliv název)
   - Toto je jen název pro tebe, můžeš použít cokoliv

2. **Service account ID:**
   - Nech automaticky vygenerované (bude něco jako `garmin-bot-123456`)
   - Nebo zadej vlastní (musí být unikátní)

3. **Service account description:** (volitelné)
   - Můžeš nechat prázdné nebo napsat např. "Bot pro Garmin data"

4. **Klikni "CREATE AND CONTINUE"** (nebo "Vytvořit a pokračovat")

### 2.4.4 Přeskoč další kroky

1. **Na další obrazovce** (Grant this service account access to project):
   - **NIC NEVYPLŇUJ**
   - **Klikni "CONTINUE"** (nebo "Pokračovat") dole

2. **Na další obrazovce** (Grant users access to this service account):
   - **NIC NEVYPLŇUJ**
   - **Klikni "DONE"** (nebo "Hotovo") dole

**💡 Proč přeskočit?**
- Pro naše účely nepotřebujeme nastavovat oprávnění v tomto kroku
- Oprávnění nastavíme později přímo na Google Sheet

---

## ✅ KROK 2.5: Stáhni JSON klíč

### 2.5.1 Otevři Service Account

1. **Po vytvoření** uvidíš seznam Service Accounts
2. **Klikni na ten, který jsi právě vytvořil** (např. `garmin-bot`)

**Co uvidíš:**
- Detail Service Account
- Tabs: "Details", "Permissions", "Keys"

### 2.5.2 Vytvoř klíč

1. **Klikni na tab "KEYS"** (nebo "Klíče")
2. **Klikni "ADD KEY"** (nebo "Přidat klíč")
3. **Vyber "Create new key"** (nebo "Vytvořit nový klíč")
4. **V okně** vyber **"JSON"** (ne "P12")
5. **Klikni "CREATE"** (nebo "Vytvořit")

### 2.5.3 Soubor se stáhne

1. **Soubor se automaticky stáhne** do složky Downloads
2. **Název souboru** bude něco jako:
   ```
   garmin-bot-123456-abcdef123456.json
   ```
   nebo
   ```
   project-name-123456-abcdef123456.json
   ```

**⚠️ DŮLEŽITÉ:**
- Tento soubor obsahuje citlivé údaje!
- Nikdy ho nesdílej s nikým
- Nikdy ho necommitni do Git repozitáře

---

## ✅ KROK 2.6: Přesuň a přejmenuj soubor

### 2.6.1 Najdi stažený soubor

1. **Otevři Finder**
2. **Jdi do složky Downloads** (nebo kam se ti stahují soubory)
3. **Najdi soubor** s názvem jako `garmin-bot-xxxxx-xxxxx.json`

### 2.6.2 Přejmenuj soubor

1. **Klikni pravým tlačítkem** na soubor (nebo Ctrl+klik)
2. **Vyber "Rename"** (nebo "Přejmenovat")
3. **Přejmenuj na:** `credentials.json`
4. **Stiskni Enter**

### 2.6.3 Přesuň do složky projektu

**Metoda 1: Přes Finder**
1. **Otevři nové okno Finderu**
2. **Jdi do:** `/Users/kirilljuran/Downloads/test cursor`
3. **Přetáhni** soubor `credentials.json` z Downloads do této složky

**Metoda 2: Přes terminál** (rychlejší)
1. **Otevři terminál**
2. **Zkopíruj a vlož:**
   ```bash
   mv ~/Downloads/*garmin*.json "/Users/kirilljuran/Downloads/test cursor/credentials.json"
   ```
   nebo pokud má jiný název:
   ```bash
   mv ~/Downloads/*.json "/Users/kirilljuran/Downloads/test cursor/credentials.json"
   ```
3. **Stiskni Enter**

### 2.6.4 Ověř, že soubor je na správném místě

**V terminálu:**
```bash
ls -la "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

**Mělo by se zobrazit:**
```
-rw-r--r--  1 tvuj-uzivatel  staff  1234 Jan 15 10:30 /Users/kirilljuran/Downloads/test cursor/credentials.json
```

**Pokud vidíš soubor, je to OK! ✅**

---

## ✅ KROK 2.7: Zkopíruj email Service Account (pro pozdější použití)

1. **Otevři soubor** `credentials.json` (který jsi právě přesunul)
2. **Najdi řádek:**
   ```json
   "client_email": "garmin-bot-123456@project-name-123456.iam.gserviceaccount.com"
   ```
3. **Zkopíruj celý email** (bez uvozovek):
   ```
   garmin-bot-123456@project-name-123456.iam.gserviceaccount.com
   ```
4. **Ulož si ho** (do poznámek, nebo si ho nech otevřený)

**💡 K čemu je to?**
- Tento email použiješ v KROKU 4 pro sdílení Google Sheet

---

## ✅ Hotovo!

Pokud jsi prošel všemi kroky:
- ✅ Projekt vytvořen
- ✅ API povoleny
- ✅ Service Account vytvořen
- ✅ JSON klíč stažen a přejmenován na `credentials.json`
- ✅ Soubor je ve složce projektu
- ✅ Email Service Account zkopírovaný

**Můžeš pokračovat na KROK 3! 🎉**

---

## ❓ Problémy?

### "Nemůžu najít dropdown s projekty"
→ Zkus obnovit stránku (F5 nebo Cmd+R)
→ Zkus jiný prohlížeč

### "CREATE CREDENTIALS není vidět"
→ Zkontroluj, že jsi v sekci "APIs & Services" → "Credentials"
→ Zkus obnovit stránku

### "Soubor se nestáhl"
→ Zkontroluj, že máš povolené stahování v prohlížeči
→ Zkus kliknout znovu na "CREATE" v kroku vytváření klíče

### "Nevím, kde je soubor"
→ V Finderu: Cmd+Shift+D (otevře Downloads)
→ Nebo použij terminál: `ls ~/Downloads/*.json`

---

**Pokud máš jakýkoliv problém, napiš mi! 🚀**


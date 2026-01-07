# 🔍 Kompletní analýza a řešení

## 📊 SOUČASNÝ STAV

### ✅ CO FUNGUJE:
1. **Sleep score: 79** ✅ - Parsování z `sleepScores.overall.value` funguje
2. **Sleep stress: 10.9** ✅ - Parsování z listu `sleepStress` funguje  
3. **HRV max/min** ✅ - Funguje
4. **Data se ukládají do Google Sheets** ✅

### ❌ CO NEFUNGUJE:
1. **Session se neukládá správně** - Tokeny jsou prázdné (0 bytů) nebo se nenačítají
2. **MFA se pořád ptá** - Protože session nefunguje
3. **Rate limiting (429)** - Garmin má přísný rate limit

---

## 🔍 ROOT CAUSE ANALÝZA

### Problém 1: Session se neukládá
**Příčina:**
- `garminconnect` vytváří vlastní `garth` instanci při vytvoření `Garmin()` objektu
- Naše ukládání se volá po `login()`, ale `garminconnect` může vytvořit novou instanci
- `garth.client()` singleton může být jiný než ten, který používá `garminconnect`

**Důkaz:**
- Session soubory existují, ale jsou prázdné (0 bytů)
- Nebo se načítají, ale `Garmin()` vytvoří novou instanci, která session nepoužije

### Problém 2: Session se nenačítá
**Příčina:**
- `garth.client.load()` se volá, ale pak se vytvoří `Garmin()`, který může vytvořit novou instanci
- `garminconnect` může ignorovat načtenou session a vytvořit novou

**Důkaz:**
- Bot se stále ptá na MFA kód, i když session soubory existují a mají obsah

---

## 💡 OUT-OF-THE-BOX ŘEŠENÍ

### Řešení 1: Použít garth přímo místo garminconnect
**Výhody:**
- Plná kontrola nad session
- Jednodušší ukládání/načítání
- Méně abstrakcí

**Nevýhody:**
- Více práce s API voláními
- Musíme implementovat všechny endpointy sami

### Řešení 2: Opravit načítání session před vytvořením Garmin klienta
**Jak:**
1. Načíst session do garth singleton PŘED vytvořením `Garmin()`
2. `Garmin()` by měl použít existující garth instanci
3. Po `login()` uložit session znovu

### Řešení 3: Použít garminconnect správně podle dokumentace
**Jak:**
- `garminconnect` by měl automaticky ukládat session do `~/.garth/`
- Stačí načíst session před vytvořením `Garmin()` objektu
- `Garmin()` by měl použít načtenou session

---

## 🚀 DOPORUČENÉ ŘEŠENÍ (IMPLEMENTOVÁNO)

**✅ Použít `tokenstore` parametr v `Garmin.login()`**

**Klíčové zjištění:**
- `Garmin.login()` má parametr `tokenstore` - pokud ho předáme, načte session automaticky
- To je mnohem jednodušší než naše předchozí řešení

**Implementace:**

1. **Kontrola session před přihlášením:**
   - Zkontrolovat, jestli existuje `~/.garth/oauth1_token.json` a není prázdný
   - Pokud ano, použít cestu jako `tokenstore` parametr

2. **Přihlášení s tokenstore:**
   - `self.garmin_client.login(tokenstore=garth_dir)` - načte session automaticky
   - Pokud session funguje, nebude potřeba MFA kód

3. **Po úspěšném login() uložit session:**
   - Získat `garth_client = self.garmin_client.garth`
   - Uložit pomocí `garth_client.dump(garth_dir)`
   - Ověřit, že soubory nejsou prázdné

4. **Retry logika pro rate limiting:**
   - ✅ Již implementováno v `get_garmin_data()` s exponenciálním backoffem

---

## 🔧 IMPLEMENTACE

### Krok 1: Opravit načítání session
- Načíst session do garth singleton PŘED vytvořením `Garmin()`
- Ověřit, že session byla načtena

### Krok 2: Opravit ukládání session
- Po úspěšném `login()` získat garth client z `garmin_client`
- Uložit pomocí `garth_client.dump()`
- Ověřit, že soubory nejsou prázdné

### Krok 3: Přidat retry logiku
- Exponenciální backoff pro rate limiting
- Automatické opakování při 429 chybách

---

## 📝 NEXT STEPS

1. ✅ Sleep score/stress - HOTOVO
2. ✅ Opravit načítání session - HOTOVO (použití `tokenstore` parametru)
3. ✅ Opravit ukládání session - HOTOVO (použití `garth_client.dump()`)
4. ✅ Retry logika - HOTOVO (již implementováno)

## 🧪 TESTOVÁNÍ

**Co otestovat:**
1. Spustit bot s MFA kódem (první přihlášení)
2. Ověřit, že session byla uložena (`~/.garth/oauth1_token.json` není prázdný)
3. Spustit bot znovu bez MFA kódu - měl by použít uloženou session
4. Ověřit, že data se správně ukládají do Google Sheets


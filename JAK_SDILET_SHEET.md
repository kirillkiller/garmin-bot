# 🔗 Jak sdílet Google Sheet s Service Account

## ✅ Ano! Přesně to je KROK 4

Sdílej Google Sheet s emailem Service Account, aby bot mohl zapisovat data.

---

## 📋 Krok za krokem:

### 1. Otevři Google Sheet

Otevři Sheet, který jsi vytvořil (nebo chceš použít).

### 2. Klikni na tlačítko "Share" (Sdílet)

- **Vpravo nahoře** uvidíš modré tlačítko **"Share"** (nebo "Sdílet")
- **Klikni na něj**

### 3. Vlož email Service Account

**V okně, které se otevře:**

1. **V poli "Add people and groups"** (nebo "Přidat osoby a skupiny"):
   - Vlož tento email:
   ```
   garmin-bot@cursor-garmin-data.iam.gserviceaccount.com
   ```

2. **Vpravo od emailu** klikni na dropdown s oprávněními
   - Vyber **"Editor"** (ne "Viewer" nebo "Commenter")
   - Editor = bot může číst i zapisovat

3. **Klikni "Send"** (nebo "Odeslat")

### 4. Hotovo!

**Co se stane:**
- Service Account dostane přístup k Sheetu
- Bot bude moci zapisovat data
- Ty uvidíš v historii sdílení, že je Sheet sdílený s tímto emailem

---

## ⚠️ Důležité poznámky:

### Proč "Editor"?
- Bot potřebuje **zapisovat** data do Sheetu
- "Viewer" = jen čtení (nefunguje)
- "Commenter" = jen komentáře (nefunguje)
- **"Editor"** = čtení i zápis ✅

### Nečekej potvrzení emailu
- Service Account je virtuální uživatel
- **Nedostaneš email** s potvrzením
- **Nepřihlásí se** do Gmailu
- Je to normální - bot prostě dostane přístup

### Můžeš to zkontrolovat
- V Sheetu klikni znovu na "Share"
- Uvidíš v seznamu: `garmin-bot@cursor-garmin-data.iam.gserviceaccount.com` s oprávněním "Editor"

---

## ✅ Hotovo!

Pokud jsi:
- ✅ Otevřel Sheet
- ✅ Klikl "Share"
- ✅ Vložil email: `garmin-bot@cursor-garmin-data.iam.gserviceaccount.com`
- ✅ Nastavil oprávnění na "Editor"
- ✅ Klikl "Send"

**Můžeš pokračovat na KROK 5 (nastavení environment variables)! 🎉**

---

## 💡 Rychlý tip:

Pokud chceš zkontrolovat, že je Sheet správně sdílený:
1. Klikni znovu na "Share"
2. Měl bys vidět v seznamu email Service Account
3. Pokud ho vidíš s oprávněním "Editor" → vše OK! ✅


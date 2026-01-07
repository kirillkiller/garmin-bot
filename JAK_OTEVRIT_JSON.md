# 📄 Jak otevřít credentials.json

## ✅ Metoda 1: TextEdit (nejjednodušší na Mac)

**Z terminálu:**
```bash
open -a TextEdit "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

**Nebo z Finderu:**
1. Otevři Finder
2. Jdi do složky: `/Users/kirilljuran/Downloads/test cursor`
3. Najdi soubor `credentials.json`
4. Klikni pravým tlačítkem (nebo Ctrl+klik)
5. "Open With" → "TextEdit"

---

## ✅ Metoda 2: V terminálu (nejrychlejší)

**Zobrazit obsah:**
```bash
cat "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

**Nebo s formátováním (hezčí výstup):**
```bash
python3 -m json.tool "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

---

## ✅ Metoda 3: VS Code / Cursor (pokud máš nainstalované)

**Z terminálu:**
```bash
code "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

**Nebo:**
```bash
cursor "/Users/kirilljuran/Downloads/test cursor/credentials.json"
```

---

## ✅ Metoda 4: Jakýkoliv textový editor

- **TextEdit** (součást macOS)
- **VS Code**
- **Cursor**
- **Sublime Text**
- **Atom**
- **Nano** (v terminálu)
- **Vim** (v terminálu)

**Důležité:** NEPOUŽÍVEJ Word nebo Pages - ty mohou změnit formátování!

---

## 🔍 Co hledáš v souboru?

Otevři soubor a najdi řádek:
```json
"client_email": "garmin-bot-123456@project-name-123456.iam.gserviceaccount.com"
```

**Zkopíruj celý email** (bez uvozovek):
```
garmin-bot-123456@project-name-123456.iam.gserviceaccount.com
```

Tento email budeš potřebovat v KROKU 4 pro sdílení Google Sheet.

---

## 💡 Rychlý příkaz pro zkopírování emailu

**Z terminálu (automaticky zkopíruje email):**
```bash
grep -o '"client_email": "[^"]*"' "/Users/kirilljuran/Downloads/test cursor/credentials.json" | cut -d'"' -f4 | pbcopy && echo "Email zkopírován do schránky!"
```

Tento příkaz:
1. Najde email v souboru
2. Zkopíruje ho do schránky (pbcopy)
3. Zobrazí potvrzení

**Pak ho můžeš vložit** (Cmd+V) kamkoliv potřebuješ!


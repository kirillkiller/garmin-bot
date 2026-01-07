# 📱 Telegram Bot Setup - Krok za krokem

## ✅ Bot je vytvořen:
- **Jméno:** Garmin bug reporter
- **Username:** @GarminBugReporter_bot
- **Token:** `8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4`
- **Chat ID:** `670619301`

---

## 🔧 Aktivace bota (POVINNÉ):

### Krok 1: Otevři bota v Telegramu
1. Otevři Telegram
2. Vyhledej: `@GarminBugReporter_bot`
3. Nebo klikni na odkaz: https://t.me/GarminBugReporter_bot

### Krok 2: Spusť bota
1. Pošli zprávu: `/start`
2. Bot by měl odpovědět

### Krok 3: Pošli testovací zprávu
1. Pošli libovolnou zprávu (např. "test")
2. Tím aktivuješ chat s botem

### Krok 4: Otestuj notifikace
```bash
cd "/Users/kirilljuran/Downloads/test cursor"
export TELEGRAM_BOT_TOKEN='8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4'
export TELEGRAM_CHAT_ID='670619301'
python3 test_telegram.py
```

---

## ✅ Po aktivaci:

Bot bude automaticky posílat notifikace při:
- 🔐 Potřebě MFA kódu
- ❌ Chybě synchronizace
- 🛑 Zastavení služby
- ✅ Úspěšné synchronizaci (volitelné)

---

## 🆘 Pokud to nefunguje:

### Chyba: "chat not found"
- ✅ Ujisti se, že jsi poslal `/start` bota
- ✅ Ujisti se, že jsi poslal alespoň jednu zprávu bota

### Chyba: "Unauthorized"
- ✅ Zkontroluj, že token je správný
- ✅ Zkontroluj, že bot není smazán

### Chyba: "Bad Request"
- ✅ Zkontroluj, že chat ID je správné
- ✅ Zkus použít chat ID jako integer místo stringu

---

## 📝 Nastavení v kódu:

Po aktivaci bota nastav environment variables:

```bash
export TELEGRAM_BOT_TOKEN='8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4'
export TELEGRAM_CHAT_ID='670619301'
```

Nebo přidej do `.env` souboru:
```
TELEGRAM_BOT_TOKEN=8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4
TELEGRAM_CHAT_ID=670619301
```

---

## 🎯 Test:

```bash
python3 test_telegram.py
```

Měla by přijít zpráva v Telegramu!


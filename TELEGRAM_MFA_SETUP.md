# 📱 Telegram MFA Handler - Setup

## ✅ Co jsem přidal:

1. **`telegram_mfa_handler.py`** - Handler pro interaktivní zadání MFA kódu
2. **Integrace do `garmin_bot.py`** - Bot automaticky použije Telegram MFA handler
3. **Ukládání MFA kódu** - Kód se ukládá do souboru pro případ webhooku

---

## 🎯 Jak to funguje:

### Když je potřeba MFA kód:

1. **Bot pošle Telegram zprávu:**
   ```
   🔐 Garmin Bot - MFA kód vyžadován
   
   Bot potřebuje MFA kód pro přihlášení k Garmin Connect.
   
   💡 Jak zadat MFA kód:
   1. Zkontroluj SMS nebo e-mail pro MFA kód
   2. Odpověz na tuto zprávu s MFA kódem
   3. Nebo pošli zprávu: /mfa TVUJ-KOD
   ```

2. **Ty odpovíš v Telegramu:**
   - Buď odpovíš přímo na zprávu: `123456`
   - Nebo pošleš: `/mfa 123456`

3. **Bot použije kód:**
   - Bot automaticky detekuje kód
   - Použije ho pro přihlášení
   - Uloží session - příště už nebude potřeba

---

## 🔧 Jak to funguje technicky:

### Render Cron Job (aktuální řešení):

1. Bot běží jako cron job (jednou denně)
2. Když potřebuje MFA, pošle Telegram zprávu
3. Bot **polling** - kontroluje Telegram API každé 2 sekundy
4. Když zadáš kód, bot ho použije
5. Timeout: 5 minut (pak se bot ukončí)

**Výhody:**
- ✅ Jednoduché
- ✅ Funguje s Render free tier
- ✅ Žádné další služby

**Nevýhody:**
- ⚠️ Bot musí běžet a čekat (max 5 minut)
- ⚠️ Render cron job se ukončí po dokončení

---

## 🚀 Vylepšení (volitelné):

### Možnost 1: Webhook Server (pokud chceš lepší UX)

Můžeš vytvořit samostatný webhook server, který běží neustále a přijímá zprávy z Telegramu.

**Soubory:**
- `telegram_bot_server.py` - Webhook server

**Jak nastavit:**
1. Vytvoř Render Web Service (místo Cron Job)
2. Spusť `telegram_bot_server.py`
3. Nastav Telegram webhook na Render URL

**Výhody:**
- ✅ Okamžitá odpověď (ne polling)
- ✅ Může běžet neustále

**Nevýhody:**
- ❌ Není zdarma (Render Web Service není free)
- ❌ Více složité

---

## 📋 Aktuální řešení (doporučeno):

**Render Cron Job + Telegram Polling:**
- ✅ Zdarma
- ✅ Jednoduché
- ✅ Funguje

**Jak to použít:**
1. Bot běží jako cron job
2. Když potřebuje MFA, pošle Telegram zprávu
3. Ty odpovíš v Telegramu s MFA kódem
4. Bot ho použije (polling každé 2 sekundy)
5. Session se uloží

---

## ✅ Co je hotovo:

- ✅ Telegram MFA handler vytvořen
- ✅ Integrace do garmin_bot.py
- ✅ Automatické použití při potřebě MFA
- ✅ Polling mechanismus pro čekání na kód
- ✅ Ukládání kódu do souboru (pro případ webhooku)

---

## 🎉 Hotovo!

Teď když MFA vyprší:
1. Bot pošle Telegram notifikaci
2. Ty zadáš kód do Telegramu
3. Bot ho použije automaticky
4. Session se uloží

**Žádné manuální nastavování environment variables!** 🚀


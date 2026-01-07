# 🚀 Quick Start - Garmin Bot Setup

## ✅ Co je hotovo:

1. ✅ **Telegram notifikace** - MFA a chyby
2. ✅ **Denní synchronizace** - automatické stahování dat
3. ✅ **Server setup návod** - kompletní instrukce
4. ✅ **Vylepšený monitoring** - sledování stavu
5. ✅ **Analýza dostupných dat** - co všechno můžeme tahat

---

## 📱 Krok 1: Nastavení Telegram bota (5 minut)

### 1.1 Vytvoř bota:
1. Otevři Telegram
2. Najdi `@BotFather`
3. Pošli `/newbot`
4. Zadej jméno: `Garmin Sync Bot`
5. Zadej username: `tvuj_garmin_sync_bot`
6. **Zkopíruj token** (vypadá jako: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 Získej Chat ID:
1. Najdi `@userinfobot` v Telegramu
2. Pošli `/start`
3. **Zkopíruj ID** (číslo, např. `123456789`)

### 1.3 Nastav environment variables:
```bash
export TELEGRAM_BOT_TOKEN="tvuj-token-zde"
export TELEGRAM_CHAT_ID="tvoje-chat-id-zde"
```

### 1.4 Otestuj:
```bash
python3 -c "from telegram_notifier import TelegramNotifier; n = TelegramNotifier(); n.send_message('Test zpráva ✅')"
```

Měla by přijít zpráva v Telegramu!

---

## 🖥️ Krok 2: Server Setup (30 minut)

### 2.1 Vyber server:
- **Doporučeno:** VPS (Hetzner, DigitalOcean) - 5-10€/měsíc
- **Alternativa:** AWS EC2 free tier (12 měsíců zdarma)

### 2.2 Postupuj podle `SERVER_SETUP.md`:
```bash
# Na serveru:
1. Nainstaluj Python a závislosti
2. Nahraj projekt
3. Nastav .env soubor
4. Vytvoř systemd service
5. Spusť službu
```

**Detailní návod:** Viz `SERVER_SETUP.md`

---

## 🔄 Krok 3: Test denní synchronizace

### 3.1 Lokálně (test):
```bash
export GARMIN_EMAIL='tvuj-email@gmail.com'
export GARMIN_PASSWORD='tvoje-heslo'
export GOOGLE_SHEET_ID='tvoje-sheet-id'
export TELEGRAM_BOT_TOKEN='tvuj-token'
export TELEGRAM_CHAT_ID='tvoje-chat-id'

python3 daily_sync_improved.py --once
```

### 3.2 Na serveru (produkce):
```bash
# Spustit jako daemon (synchronizace každý den v 1:00)
python3 daily_sync_improved.py --daemon --sync-time 01:00

# NEBO použít systemd service (doporučeno):
systemctl start garmin-sync
systemctl enable garmin-sync
```

---

## 📊 Krok 4: Ověření

### 4.1 Zkontroluj Google Sheets:
- Měly by se přidat nové záznamy
- Data by měla být kompletní

### 4.2 Zkontroluj Telegram:
- Měly by přijít notifikace při:
  - ✅ Úspěšné synchronizaci (pokud je povolena)
  - ❌ Chybě synchronizace
  - 🔐 Potřebě MFA kódu

### 4.3 Zkontroluj logy:
```bash
# Na serveru:
tail -f logs/daily_sync.log

# Nebo systemd logy:
journalctl -u garmin-sync -f
```

---

## 🆘 Troubleshooting

### Telegram notifikace nefungují:
```bash
# Zkontroluj token a chat ID:
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Otestuj znovu:
python3 -c "from telegram_notifier import TelegramNotifier; n = TelegramNotifier(); n.send_message('Test')"
```

### Synchronizace selhává:
```bash
# Zkontroluj logy:
tail -50 logs/daily_sync.log

# Zkontroluj MFA:
# Pokud je potřeba MFA, přijde Telegram notifikace
# Zadej MFA kód lokálně a session se uloží
```

### Server se nespouští:
```bash
# Zkontroluj status:
systemctl status garmin-sync

# Zkontroluj logy:
journalctl -u garmin-sync -n 50

# Restart:
systemctl restart garmin-sync
```

---

## 📚 Další dokumentace:

- **SERVER_SETUP.md** - Detailní návod na server setup
- **IMPROVEMENTS.md** - Vylepšení a doporučení
- **setup_daily_sync.md** - Nastavení denní synchronizace

---

## ✅ Checklist:

- [ ] Telegram bot vytvořen a token nastaven
- [ ] Telegram chat ID získán
- [ ] Environment variables nastaveny
- [ ] Telegram notifikace otestovány
- [ ] Server vytvořen a nastaven
- [ ] Projekt nahraný na server
- [ ] Systemd service vytvořen a spuštěn
- [ ] Test synchronizace proběhl úspěšně
- [ ] Monitoring nastaven

---

## 🎉 Hotovo!

Bot by teď měl:
- ✅ Automaticky stahovat data každý den
- ✅ Posílat notifikace při chybách
- ✅ Posílat notifikace při potřebě MFA
- ✅ Běžet 24/7 na serveru

**Gratulace! 🎊**


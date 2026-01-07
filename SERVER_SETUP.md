# 🖥️ Server Setup - Garmin Bot 24/7

## 📋 Přehled řešení

Pro 24/7 běh Garmin bota potřebuješ server, který běží neustále. Zde jsou možnosti:

### 🎯 Doporučené řešení:

1. **VPS (Virtual Private Server)** - nejlepší poměr cena/výkon
2. **Cloud (AWS, Google Cloud, Azure)** - škálovatelné, ale dražší
3. **Raspberry Pi** - levné, ale vyžaduje vlastní hardware a stabilní internet
4. **Dedikovaný server** - nejvýkonnější, ale dražší

---

## 🚀 Možnost 1: VPS (DOPORUČENO)

### Výhody:
- ✅ Levné (5-10€/měsíc)
- ✅ 24/7 dostupnost
- ✅ Snadná správa
- ✅ SSH přístup

### Doporučené poskytovatelé:
- **Hetzner** (Německo) - 4€/měsíc, dobrá kvalita
- **DigitalOcean** (USA) - 5$/měsíc, jednoduché
- **Linode** (USA) - 5$/měsíc
- **Vultr** (celosvětově) - 2.5$/měsíc

### Setup krok za krokem:

#### 1. Vytvoř VPS instanci
- OS: Ubuntu 22.04 LTS
- Velikost: 1GB RAM, 1 CPU (stačí)
- Lokace: Evropa (pro nižší latenci)

#### 2. Připoj se přes SSH
```bash
ssh root@tvoje-ip-adresa
```

#### 3. Aktualizuj systém
```bash
apt update && apt upgrade -y
```

#### 4. Nainstaluj Python a závislosti
```bash
apt install -y python3 python3-pip git
pip3 install garminconnect gspread google-auth google-auth-oauthlib google-auth-httplib2 garth requests
```

#### 5. Naklonuj projekt (nebo nahraj soubory)
```bash
cd /opt
git clone https://github.com/tvuj-repo/garmin-bot.git
# NEBO nahraj soubory přes SCP:
# scp -r /local/path/* root@server:/opt/garmin-bot/
```

#### 6. Nastav environment variables
```bash
cd /opt/garmin-bot
nano .env
```

Přidej:
```bash
GARMIN_EMAIL=tvuj-email@gmail.com
GARMIN_PASSWORD=tvoje-heslo
GOOGLE_SHEET_ID=tvoje-sheet-id
GOOGLE_CREDENTIALS_PATH=/opt/garmin-bot/credentials.json
TELEGRAM_BOT_TOKEN=tvuj-bot-token
TELEGRAM_CHAT_ID=tvoje-chat-id
```

Načti env variables:
```bash
export $(cat .env | xargs)
```

#### 7. Nahraj credentials.json
```bash
# Přes SCP z lokálního počítače:
scp credentials.json root@server:/opt/garmin-bot/
```

#### 8. Vytvoř systemd service
```bash
nano /etc/systemd/system/garmin-sync.service
```

Přidej:
```ini
[Unit]
Description=Garmin Daily Sync Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/garmin-bot
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/opt/garmin-bot/.env
ExecStart=/usr/bin/python3 /opt/garmin-bot/daily_sync_improved.py --daemon --sync-time 01:00
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 9. Spusť službu
```bash
systemctl daemon-reload
systemctl enable garmin-sync
systemctl start garmin-sync
systemctl status garmin-sync
```

#### 10. Sleduj logy
```bash
# Logy služby
journalctl -u garmin-sync -f

# Nebo logy z aplikace
tail -f /opt/garmin-bot/logs/daily_sync.log
```

---

## ☁️ Možnost 2: Cloud (AWS/Google Cloud/Azure)

### AWS EC2:
- **Free tier**: 12 měsíců zdarma (t2.micro)
- **Cena**: ~5-10$/měsíc po free tier
- **Setup**: Stejný jako VPS

### Google Cloud Run:
- **Výhoda**: Platíš jen za běh (může být levnější)
- **Nevýhoda**: Musíš upravit kód pro event-driven architekturu

---

## 🍓 Možnost 3: Raspberry Pi

### Výhody:
- ✅ Jednorázová investice (~50€)
- ✅ Plná kontrola
- ✅ Může běžet doma

### Nevýhody:
- ❌ Vyžaduje stabilní internet
- ❌ Vyžaduje vlastní hardware
- ❌ Může se přehřát/pokazit

### Setup:
Stejný jako VPS, ale na Raspberry Pi OS.

---

## 🔧 Monitoring a údržba

### Health check script:
```bash
#!/bin/bash
# /opt/garmin-bot/health_check.sh

if ! systemctl is-active --quiet garmin-sync; then
    systemctl restart garmin-sync
    # Můžeš přidat notifikaci
fi
```

### Cron job pro health check:
```bash
crontab -e
# Přidej:
*/5 * * * * /opt/garmin-bot/health_check.sh
```

### Backup:
```bash
# Zálohovat credentials a .env
tar -czf backup-$(date +%Y%m%d).tar.gz credentials.json .env
```

---

## 📱 Telegram Bot Setup

### 1. Vytvoř Telegram bota:
1. Otevři Telegram
2. Najdi `@BotFather`
3. Pošli `/newbot`
4. Zadej jméno a username
5. Zkopíruj **token**

### 2. Získej Chat ID:
1. Najdi `@userinfobot` v Telegramu
2. Pošli `/start`
3. Zkopíruj **ID**

### 3. Nastav v .env:
```bash
TELEGRAM_BOT_TOKEN=tvuj-token-zde
TELEGRAM_CHAT_ID=tvoje-chat-id-zde
```

### 4. Otestuj:
```bash
python3 -c "from telegram_notifier import TelegramNotifier; n = TelegramNotifier(); n.send_message('Test zpráva')"
```

---

## ✅ Checklist před spuštěním:

- [ ] VPS/Server vytvořen a běží
- [ ] Python a závislosti nainstalovány
- [ ] Projekt nahraný na server
- [ ] Environment variables nastaveny
- [ ] credentials.json nahraný
- [ ] Telegram bot vytvořen a token nastaven
- [ ] Systemd service vytvořen a spuštěn
- [ ] Test synchronizace proběhl úspěšně
- [ ] Monitoring nastaven

---

## 🆘 Troubleshooting

### Služba se nespustí:
```bash
systemctl status garmin-sync
journalctl -u garmin-sync -n 50
```

### Chyby s permissions:
```bash
chmod +x /opt/garmin-bot/*.py
chown -R root:root /opt/garmin-bot
```

### Session expirovala:
- Bot automaticky pošle Telegram notifikaci
- Zadej MFA kód přes SSH nebo lokálně

---

## 💡 Tipy:

1. **Použij fail2ban** pro zabezpečení SSH
2. **Nastav automatické updaty** (unattended-upgrades)
3. **Monitoruj disk space** (logy mohou narůst)
4. **Pravidelně zálohuj** credentials a .env

---

## 📊 Odhadované náklady:

- **VPS**: 5-10€/měsíc
- **Cloud (AWS free tier)**: 0€ první rok, pak 5-10$/měsíc
- **Raspberry Pi**: ~50€ jednorázově
- **Telegram bot**: Zdarma

**Celkem: ~5-10€/měsíc** (s VPS)


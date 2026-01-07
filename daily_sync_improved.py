#!/usr/bin/env python3
"""
Vylepšená denní synchronizace s monitoringem a notifikacemi
Běží jako služba a monitoruje stav synchronizace
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from garmin_bot import GarminBot
from telegram_notifier import TelegramNotifier

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailySyncService:
    """Služba pro denní synchronizaci s monitoringem"""
    
    def __init__(self):
        """Inicializace služby"""
        self.garmin_email = os.getenv('GARMIN_EMAIL')
        self.garmin_password = os.getenv('GARMIN_PASSWORD')
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        
        if not all([self.garmin_email, self.garmin_password, self.google_sheet_id]):
            logger.error("❌ Chybí povinné environment variables!")
            sys.exit(1)
        
        # Telegram notifikace
        self.telegram = TelegramNotifier()
        
        # Vytvoření bota
        self.bot = GarminBot(
            garmin_email=self.garmin_email,
            garmin_password=self.garmin_password,
            google_sheet_id=self.google_sheet_id,
            google_credentials_path=self.google_credentials if os.path.exists(self.google_credentials) else None,
            polling_interval=600
        )
        
        # Statistiky
        self.stats = {
            'successful': 0,
            'failed': 0,
            'last_success': None,
            'last_failure': None,
            'consecutive_failures': 0
        }
        
        logger.info("✅ Daily Sync Service inicializována")
    
    def sync_yesterday(self):
        """Synchronizuje data pro včerejšek a zkontroluje předvčerejšek"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        day_before_yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        
        logger.info(f"🔄 Začínám synchronizaci pro {yesterday}...")
        
        try:
            # 1. Synchronizovat včerejšek (hlavní úkol)
            self.bot.run_once(yesterday)
            logger.info(f"✅ Synchronizace úspěšná pro {yesterday}")
            
            # 2. Zkontrolovat a aktualizovat předvčerejšek (pokud se data změnila)
            logger.info(f"🔍 Kontroluji data za {day_before_yesterday} (mohla se změnit pozdější synchronizací)...")
            try:
                # Stáhnout aktuální data za předvčerejšek
                new_data = self.bot.get_garmin_data(day_before_yesterday)
                
                # Zkontrolovat, zda existují data v Google Sheets
                try:
                    worksheet = self.bot.sheet.worksheet('Garmin Data')
                    existing_dates = worksheet.col_values(1)
                    
                    if day_before_yesterday in existing_dates:
                        # Data existují - zkontrolovat, zda se změnila
                        # send_to_sheets automaticky aktualizuje existující řádek
                        logger.info(f"📊 Data pro {day_before_yesterday} existují - aktualizuji pokud se změnila...")
                        self.bot.send_to_sheets(new_data)
                        logger.info(f"✅ Kontrola a aktualizace dokončena pro {day_before_yesterday}")
                    else:
                        logger.info(f"ℹ️  Data pro {day_before_yesterday} neexistují - přidávám...")
                        self.bot.send_to_sheets(new_data)
                        logger.info(f"✅ Data přidána pro {day_before_yesterday}")
                except Exception as e:
                    logger.warning(f"⚠️  Nepodařilo se zkontrolovat existující data: {e}")
                    # Přesto zkusit odeslat (send_to_sheets to zvládne)
                    self.bot.send_to_sheets(new_data)
                    
            except Exception as e:
                logger.warning(f"⚠️  Chyba při kontrole předvčerejška {day_before_yesterday}: {e}")
                # Neukončit celou synchronizaci kvůli této chybě
                logger.info("💡 Pokračuji - hlavní synchronizace pro včerejšek byla úspěšná")
            
            self.stats['successful'] += 1
            self.stats['last_success'] = datetime.now()
            self.stats['consecutive_failures'] = 0
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.stats['failed'] += 1
            self.stats['last_failure'] = datetime.now()
            self.stats['consecutive_failures'] += 1
            logger.error(f"❌ Synchronizace selhala pro {yesterday}: {error_msg}")
            
            # Notifikace o chybě
            if self.telegram:
                self.telegram.notify_sync_error(error_msg, yesterday)
            
            # Pokud jsou 3 po sobě jdoucí chyby, upozornit
            if self.stats['consecutive_failures'] >= 3:
                if self.telegram:
                    self.telegram.send_message(
                        f"🚨 <b>Kritické upozornění</b>\n\n"
                        f"Synchronizace selhala {self.stats['consecutive_failures']}x po sobě!\n"
                        f"Poslední chyba: {error_msg}\n\n"
                        f"💡 Zkontroluj logy a oprav problém."
                    )
            
            return False
    
    def check_health(self):
        """Kontrola zdraví služby"""
        # Pokud poslední úspěch byl před více než 2 dny, něco je špatně
        if self.stats['last_success']:
            days_since_success = (datetime.now() - self.stats['last_success']).days
            if days_since_success > 2:
                if self.telegram:
                    self.telegram.send_message(
                        f"⚠️ <b>Upozornění</b>\n\n"
                        f"Poslední úspěšná synchronizace byla před {days_since_success} dny.\n"
                        f"💡 Zkontroluj stav služby."
                    )
                return False
        return True
    
    def run_once(self):
        """Spustí synchronizaci jednou"""
        self.sync_yesterday()
        self.check_health()
    
    def run_daemon(self, sync_time: str = "01:00"):
        """
        Spustí službu jako daemon
        
        Args:
            sync_time: Čas synchronizace ve formátu HH:MM (default: 01:00)
        """
        logger.info(f"🚀 Daily Sync Service spuštěna jako daemon")
        logger.info(f"⏰ Čas synchronizace: {sync_time}")
        
        # Parse sync time
        sync_hour, sync_minute = map(int, sync_time.split(':'))
        
        while True:
            try:
                now = datetime.now()
                
                # Zkontrolovat, jestli je čas pro synchronizaci
                if now.hour == sync_hour and now.minute == sync_minute:
                    logger.info("⏰ Je čas pro synchronizaci!")
                    self.sync_yesterday()
                    self.check_health()
                    
                    # Počkat minutu, aby se neopakovalo
                    time.sleep(60)
                
                # Health check každou hodinu
                elif now.minute == 0:
                    self.check_health()
                
                # Čekat 30 sekund před dalším checkem
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("🛑 Zastaveno uživatelem")
                if self.telegram:
                    self.telegram.notify_sync_stopped("Uživatel zastavil službu")
                break
            except Exception as e:
                logger.error(f"❌ Chyba v daemon smyčce: {e}")
                if self.telegram:
                    self.telegram.notify_sync_error(str(e), "Daemon loop")
                time.sleep(60)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Sync Service pro Garmin data')
    parser.add_argument('--once', action='store_true', help='Spustit synchronizaci jednou a skončit')
    parser.add_argument('--daemon', action='store_true', help='Spustit jako daemon službu')
    parser.add_argument('--sync-time', type=str, default='01:00', help='Čas synchronizace (HH:MM, default: 01:00)')
    
    args = parser.parse_args()
    
    # Vytvoření složky pro logy
    os.makedirs('logs', exist_ok=True)
    
    service = DailySyncService()
    
    if args.once:
        service.run_once()
    elif args.daemon:
        service.run_daemon(args.sync_time)
    else:
        # Default: spustit jednou
        service.run_once()


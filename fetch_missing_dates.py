#!/usr/bin/env python3
"""
Skript pro stažení pouze chybějících dat z Google Sheets
Čte seznam chybějících datumů z missing_dates.txt nebo je zjistí automaticky
"""
import os
import sys
import time
from datetime import datetime, timedelta
from garmin_bot import GarminBot
import logging
import gspread

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/missing_dates_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_missing_dates_from_sheet(bot):
    """Získá seznam chybějících datumů z Google Sheets"""
    try:
        worksheet = bot.sheet.worksheet('Garmin Data')
        existing_dates = worksheet.col_values(1)[1:]  # Přeskočit hlavičku
        
        # Vytvořit seznam všech dat za poslední rok
        today = datetime.now()
        all_dates = []
        for i in range(1, 366):  # 365 dní zpět
            date = today - timedelta(days=i)
            all_dates.append(date.strftime('%Y-%m-%d'))
        
        # Najít chybějící datumy
        missing_dates = [date for date in all_dates if date not in existing_dates]
        return missing_dates
    except Exception as e:
        logger.error(f"❌ Chyba při získávání chybějících datumů: {e}")
        return []

def fetch_missing_dates(delay_between_requests=10, use_file=False):
    """
    Stáhne pouze chybějící datumy
    
    Args:
        delay_between_requests: Zpoždění mezi požadavky v sekundách (default: 10)
        use_file: Pokud True, použije missing_dates.txt místo automatického zjištění
    """
    # Načtení credentials z environment
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')
    google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    
    if not all([garmin_email, garmin_password, google_sheet_id]):
        logger.error("❌ Chybí povinné environment variables!")
        logger.error("   GARMIN_EMAIL, GARMIN_PASSWORD, GOOGLE_SHEET_ID")
        return
    
    # Vytvoření bota
    bot = GarminBot(
        garmin_email=garmin_email,
        garmin_password=garmin_password,
        google_sheet_id=google_sheet_id,
        google_credentials_path=google_credentials if os.path.exists(google_credentials) else None,
        polling_interval=600
    )
    
    # Získat chybějící datumy
    if use_file and os.path.exists('missing_dates.txt'):
        logger.info("📄 Načítám chybějící datumy z missing_dates.txt...")
        with open('missing_dates.txt', 'r') as f:
            missing_dates = [line.strip() for line in f if line.strip()]
    else:
        logger.info("🔍 Automaticky zjišťuji chybějící datumy z Google Sheets...")
        missing_dates = get_missing_dates_from_sheet(bot)
    
    if not missing_dates:
        logger.info("✅ Všechna data jsou k dispozici! Nic ke stažení.")
        return
    
    logger.info(f"📅 Našel jsem {len(missing_dates)} chybějících datumů")
    logger.info(f"📅 První chybějící: {missing_dates[0]}")
    logger.info(f"📅 Poslední chybějící: {missing_dates[-1]}")
    logger.info(f"⏱️  Delay mezi požadavky: {delay_between_requests} sekund")
    logger.info(f"⏱️  Odhadovaná doba: {len(missing_dates) * delay_between_requests / 60:.1f} minut")
    
    successful = 0
    failed = 0
    rate_limit_errors = 0
    
    for idx, date in enumerate(missing_dates, 1):
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 [{idx}/{len(missing_dates)}] Stahuji data pro {date}...")
            
            # Stáhnout data
            bot.run_once(date)
            successful += 1
            logger.info(f"✅ [{idx}/{len(missing_dates)}] Úspěšně dokončeno pro {date}")
            
            # Delay mezi požadavky (kromě posledního)
            if idx < len(missing_dates):
                logger.info(f"⏳ Čekám {delay_between_requests} sekund před dalším požadavkem...")
                time.sleep(delay_between_requests)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ [{idx}/{len(missing_dates)}] Chyba pro {date}: {error_msg}")
            
            # Detekce rate limiting
            if '429' in error_msg or 'rate limit' in error_msg.lower() or 'too many requests' in error_msg.lower():
                rate_limit_errors += 1
                logger.warning(f"⚠️  Rate limit detekován! Počítám chyby: {rate_limit_errors}")
                
                if rate_limit_errors >= 3:
                    logger.error("🛑 Příliš mnoho rate limit chyb! Zastavuji.")
                    logger.info("💡 Počkej 15-30 minut a spusť skript znovu")
                    logger.info(f"💡 Zbývá {len(missing_dates) - idx} datumů")
                    break
                
                # Delší čekání při rate limit
                wait_time = 60 * (rate_limit_errors + 1)  # 2, 3, 4 minuty...
                logger.info(f"⏳ Čekám {wait_time} sekund kvůli rate limit...")
                time.sleep(wait_time)
                rate_limit_errors = 0  # Reset po úspěšném čekání
            else:
                failed += 1
                # Při jiné chybě počkáme kratší dobu
                logger.info(f"⏳ Čekám {delay_between_requests} sekund před dalším pokusem...")
                time.sleep(delay_between_requests)
    
    # Shrnutí
    logger.info(f"\n{'='*60}")
    logger.info("📊 SHRNUTÍ:")
    logger.info(f"   ✅ Úspěšně: {successful}")
    logger.info(f"   ❌ Chyby: {failed}")
    logger.info(f"   ⚠️  Rate limit chyby: {rate_limit_errors}")
    logger.info(f"   📈 Celkem zpracováno: {successful + failed}/{len(missing_dates)}")
    
    if successful + failed < len(missing_dates):
        remaining = len(missing_dates) - (successful + failed)
        logger.info(f"   ⏳ Zbývá: {remaining} datumů")
        logger.info(f"   💡 Spusť skript znovu pro doplnění zbývajících datumů")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stáhne pouze chybějící data z Garmin Connect')
    parser.add_argument('--delay', type=int, default=10, help='Delay mezi požadavky v sekundách (default: 10)')
    parser.add_argument('--file', action='store_true', help='Použít missing_dates.txt místo automatického zjištění')
    
    args = parser.parse_args()
    
    # Vytvoření složky pro logy pokud neexistuje
    os.makedirs('logs', exist_ok=True)
    
    fetch_missing_dates(delay_between_requests=args.delay, use_file=args.file)


#!/usr/bin/env python3
"""
Skript pro postupné doplnění historických dat do Google Sheets
Stahuje data za poslední rok, od nejnovějších po starší
"""
import os
import sys
import time
from datetime import datetime, timedelta
from garmin_bot import GarminBot
import logging

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/historical_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_historical_data(days_back=365, delay_between_requests=8):
    """
    Postupně stahuje historická data
    
    Args:
        days_back: Počet dní zpět (default: 365 = 1 rok)
        delay_between_requests: Zpoždění mezi požadavky v sekundách (default: 8)
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
    
    # Generování seznamu dat (od včerejška zpět)
    today = datetime.now()
    dates = []
    for i in range(1, days_back + 1):  # Začínáme od včerejška (i=1), ne od dneška
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    logger.info(f"📅 Začínám stahovat data za poslední {days_back} dní")
    logger.info(f"📅 První datum: {dates[0]}, poslední datum: {dates[-1]}")
    logger.info(f"⏱️  Delay mezi požadavky: {delay_between_requests} sekund")
    logger.info(f"⏱️  Odhadovaná doba: {len(dates) * delay_between_requests / 60:.1f} minut")
    
    successful = 0
    failed = 0
    skipped = 0
    rate_limit_errors = 0
    
    for idx, date in enumerate(dates, 1):
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 [{idx}/{len(dates)}] Stahuji data pro {date}...")
            
            # Zkontrolovat, zda už tento den není v Google Sheets
            try:
                worksheet = bot.sheet.worksheet('Garmin Data')
                existing_dates = worksheet.col_values(1)
                if date in existing_dates:
                    logger.info(f"⏭️  Data pro {date} už existují, přeskočeno")
                    skipped += 1
                    continue
            except Exception as e:
                logger.warning(f"⚠️  Nepodařilo se zkontrolovat existující data: {e}")
            
            # Stáhnout data
            bot.run_once(date)
            successful += 1
            logger.info(f"✅ [{idx}/{len(dates)}] Úspěšně dokončeno pro {date}")
            
            # Delay mezi požadavky (kromě posledního)
            if idx < len(dates):
                logger.info(f"⏳ Čekám {delay_between_requests} sekund před dalším požadavkem...")
                time.sleep(delay_between_requests)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ [{idx}/{len(dates)}] Chyba pro {date}: {error_msg}")
            
            # Detekce rate limiting
            if '429' in error_msg or 'rate limit' in error_msg.lower() or 'too many requests' in error_msg.lower():
                rate_limit_errors += 1
                logger.warning(f"⚠️  Rate limit detekován! Počítám chyby: {rate_limit_errors}")
                
                if rate_limit_errors >= 3:
                    logger.error("🛑 Příliš mnoho rate limit chyb! Zastavuji.")
                    logger.info("💡 Počkej 15-30 minut a spusť skript znovu")
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
    logger.info(f"   ⏭️  Přeskočeno (už existuje): {skipped}")
    logger.info(f"   ⚠️  Rate limit chyby: {rate_limit_errors}")
    logger.info(f"   📈 Celkem zpracováno: {successful + failed + skipped}/{len(dates)}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stáhne historická data z Garmin Connect')
    parser.add_argument('--days', type=int, default=365, help='Počet dní zpět (default: 365)')
    parser.add_argument('--delay', type=int, default=8, help='Delay mezi požadavky v sekundách (default: 8)')
    
    args = parser.parse_args()
    
    # Vytvoření složky pro logy pokud neexistuje
    os.makedirs('logs', exist_ok=True)
    
    fetch_historical_data(days_back=args.days, delay_between_requests=args.delay)


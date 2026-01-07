"""
Skript pro stažení historických dat z Garmin Connect po měsících
Toto je bezpečnější způsob - stáhne data po měsících s pauzami mezi nimi
"""
import os
import sys
import time
from datetime import datetime, timedelta
from garmin_bot import GarminBot

def stahnout_mesic(bot, year, month):
    """Stáhne data za konkrétní měsíc"""
    # Zjistit počet dní v měsíci
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    start_date = datetime(year, month, 1)
    end_date = datetime(next_year, next_month, 1) - timedelta(days=1)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\n📅 Stahuji data za {month}/{year}...")
    print(f"   Od {start_str} do {end_str}")
    print(f"   Celkem dní: {(end_date - start_date).days + 1}\n")
    
    current = start_date
    success = 0
    failed = 0
    
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        day_num = (current - start_date).days + 1
        total_days = (end_date - start_date).days + 1
        print(f"🔄 [{day_num}/{total_days}] {date_str}...", end=' ', flush=True)
        
        try:
            bot.run_once(date_str)
            print("✅")
            success += 1
            # Po každém úspěšném dotazu počkat (rate limiting)
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n🛑 Zastaveno uživatelem")
            print(f"📊 Progress: {success} úspěšných, {failed} chyb")
            return False
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                print(f"❌ Rate limit - čekám 60 sekund...")
                time.sleep(60)
                # Zkusit znovu
                try:
                    bot.run_once(date_str)
                    print("✅ (po retry)")
                    success += 1
                except:
                    print(f"❌ Stále chyba po retry")
                    failed += 1
            else:
                print(f"❌ Chyba: {str(e)[:100]}")
                failed += 1
        
        current += timedelta(days=1)
    
    print(f"\n✅ Hotovo pro {month}/{year}! Úspěšně: {success}, Chyby: {failed}")
    return True

def main():
    """Stáhne historická data po měsících"""
    
    # Načtení konfigurace z environment variables
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')
    google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    
    if not all([garmin_email, garmin_password, google_sheet_id]):
        print("❌ Chybí povinné environment variables:")
        print("   GARMIN_EMAIL, GARMIN_PASSWORD, GOOGLE_SHEET_ID")
        return
    
    # Vytvoření bota
    bot = GarminBot(
        garmin_email=garmin_email,
        garmin_password=garmin_password,
        google_sheet_id=google_sheet_id,
        google_credentials_path=google_credentials if os.path.exists(google_credentials) else None,
        polling_interval=600
    )
    
    # Nejdřív zkusit připojit k Garmin (pro MFA)
    print("🔐 Připojuji se k Garmin Connect...")
    print("💡 Bot počká 2 minuty před prvním pokusem (kvůli rate limiting)")
    print("💡 Pokud budeš vyzván k zadání MFA kódu, zadej ho a počkej...\n")
    try:
        bot._init_garmin()
        print("✅ Připojeno k Garmin Connect\n")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Too Many Requests" in error_str:
            print(f"❌ Rate limit (429) při připojování k Garmin")
            print("💡 Garmin má rate limiting - počkej 15-20 minut a zkus znovu")
            print("💡 Nebo zkus zítra - Garmin může mít denní limit")
        else:
            print(f"❌ Chyba při připojování k Garmin: {e}")
            print("💡 Zkus spustit znovu - možná potřebuješ zadat MFA kód")
        return
    
    # Stáhnout data za poslední rok po měsících (od nejstaršího)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print("📥 Stahuji data za poslední rok po měsících...")
    print(f"   Od {start_date.strftime('%Y-%m-%d')} do {end_date.strftime('%Y-%m-%d')}")
    print("💡 Po každém měsíci počkám 5 minut (kvůli rate limiting)\n")
    
    current = start_date
    while current <= end_date:
        year = current.year
        month = current.month
        
        # Stáhnout měsíc
        success = stahnout_mesic(bot, year, month)
        if not success:
            print("\n🛑 Zastaveno uživatelem")
            return
        
        # Po každém měsíci počkat 5 minut (rate limiting)
        if current < end_date:
            print("\n⏳ Čekám 5 minut před dalším měsícem (kvůli rate limiting)...")
            time.sleep(300)  # 5 minut
        
        # Přesunout na další měsíc
        if month == 12:
            current = datetime(year + 1, 1, 1)
        else:
            current = datetime(year, month + 1, 1)
    
    print("\n✅ Hotovo! Všechna data stažena!")

if __name__ == '__main__':
    main()


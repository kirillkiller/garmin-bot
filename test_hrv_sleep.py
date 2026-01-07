"""
Testovací skript pro zjištění struktury HRV a Sleep dat z Garmin API
"""
import os
import json
from garminconnect import Garmin
from datetime import datetime, timedelta

# Načtení credentials z environment
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')
# Test pro včerejšek (kompletní data)
date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

if not email or not password:
    print("❌ Nastav GARMIN_EMAIL a GARMIN_PASSWORD")
    exit(1)

print(f"🔍 Testování HRV a Sleep dat z Garmin API pro {date}...\n")

try:
    client = Garmin(email, password)
    client.login()
    print("✅ Připojeno k Garmin Connect\n")
    
    # Test HRV dat
    print("=" * 60)
    print("HRV DATA (get_hrv_data):")
    print("=" * 60)
    try:
        hrv_data = client.get_hrv_data(date)
        print(json.dumps(hrv_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Sleep dat
    print("\n" + "=" * 60)
    print("SLEEP DATA (get_sleep_data):")
    print("=" * 60)
    try:
        sleep_data = client.get_sleep_data(date)
        print(json.dumps(sleep_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
        import traceback
        traceback.print_exc()
    
    # Test stats (možná tam jsou HRV a sleep data)
    print("\n" + "=" * 60)
    print("STATS DATA (get_stats) - zkontrolovat HRV a sleep v stats:")
    print("=" * 60)
    try:
        stats = client.get_stats(date)
        # Hledat HRV a sleep klíče
        hrv_keys = [k for k in stats.keys() if 'hrv' in k.lower() or 'variability' in k.lower()]
        sleep_keys = [k for k in stats.keys() if 'sleep' in k.lower()]
        print(f"HRV klíče v stats: {hrv_keys}")
        print(f"Sleep klíče v stats: {sleep_keys}")
        if hrv_keys:
            print("\nHRV hodnoty:")
            for key in hrv_keys:
                print(f"  {key}: {stats.get(key)}")
        if sleep_keys:
            print("\nSleep hodnoty:")
            for key in sleep_keys:
                print(f"  {key}: {stats.get(key)}")
    except Exception as e:
        print(f"Chyba: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()


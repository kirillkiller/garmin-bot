"""
Testovací skript pro zjištění struktury sleepStress a sleepScore
"""
import os
import json
from garminconnect import Garmin
from datetime import datetime

# Načtení credentials z environment
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')
date = datetime.now().strftime('%Y-%m-%d')

if not email or not password:
    print("❌ Nastav GARMIN_EMAIL a GARMIN_PASSWORD")
    exit(1)

print(f"🔍 Testování Sleep dat z Garmin API pro {date}...\n")

try:
    client = Garmin(email, password)
    client.login()
    print("✅ Připojeno k Garmin Connect\n")
    
    # Test Sleep dat
    print("=" * 60)
    print("SLEEP DATA (get_sleep_data):")
    print("=" * 60)
    sleep_data = client.get_sleep_data(date)
    
    # Zkontrolovat sleepStress
    print("\n" + "=" * 60)
    print("sleepStress struktura:")
    print("=" * 60)
    sleep_stress = sleep_data.get('sleepStress', [])
    print(f"Type: {type(sleep_stress)}")
    if isinstance(sleep_stress, list):
        print(f"Length: {len(sleep_stress)}")
        if len(sleep_stress) > 0:
            print(f"\nFirst item type: {type(sleep_stress[0])}")
            print(f"First item: {json.dumps(sleep_stress[0], indent=2, default=str) if isinstance(sleep_stress[0], dict) else sleep_stress[0]}")
            if isinstance(sleep_stress[0], dict):
                print(f"First item keys: {list(sleep_stress[0].keys())}")
    else:
        print(f"Content: {sleep_stress}")
    
    # Zkontrolovat sleepScore
    print("\n" + "=" * 60)
    print("sleepScore hledání:")
    print("=" * 60)
    sleep_score = sleep_data.get('sleepScore')
    print(f"sleep_data.get('sleepScore'): {sleep_score}")
    
    daily_sleep = sleep_data.get('dailySleepDTO', {})
    print(f"dailySleepDTO.get('sleepScore'): {daily_sleep.get('sleepScore')}")
    print(f"dailySleepDTO.get('overallSleepScore'): {daily_sleep.get('overallSleepScore')}")
    
    # Zkontrolovat všechny klíče s "score"
    score_keys = [k for k in sleep_data.keys() if 'score' in k.lower()]
    print(f"\nKeys with 'score' in sleep_data: {score_keys}")
    score_keys_dto = [k for k in daily_sleep.keys() if 'score' in k.lower()]
    print(f"Keys with 'score' in dailySleepDTO: {score_keys_dto}")
    
    # Zkontrolovat všechny klíče v sleep_data
    print("\n" + "=" * 60)
    print("Všechny klíče v sleep_data:")
    print("=" * 60)
    print(list(sleep_data.keys()))
    
except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()


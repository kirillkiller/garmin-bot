"""
Testovací skript pro zjištění struktury dat z Garmin API
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

print(f"🔍 Testování Garmin API pro {date}...\n")

try:
    client = Garmin(email, password)
    client.login()
    print("✅ Připojeno k Garmin Connect\n")
    
    # Test různých metod
    print("=" * 60)
    print("1. get_stats:")
    print("=" * 60)
    stats = client.get_stats(date)
    print(json.dumps(stats, indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("2. get_user_summary:")
    print("=" * 60)
    user_summary = client.get_user_summary(date)
    print(json.dumps(user_summary, indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("3. get_steps_data:")
    print("=" * 60)
    steps_data = client.get_steps_data(date)
    print(json.dumps(steps_data, indent=2, default=str) if steps_data else "Žádná data")
    
    print("\n" + "=" * 60)
    print("4. get_body_battery:")
    print("=" * 60)
    try:
        body_battery = client.get_body_battery(date)
        print(json.dumps(body_battery, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
    
    print("\n" + "=" * 60)
    print("5. get_stress_data:")
    print("=" * 60)
    try:
        stress_data = client.get_stress_data(date)
        print(json.dumps(stress_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
    
    print("\n" + "=" * 60)
    print("6. get_hrv_data (HRV - Heart Rate Variability):")
    print("=" * 60)
    try:
        hrv_data = client.get_hrv_data(date)
        print(json.dumps(hrv_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
    
    print("\n" + "=" * 60)
    print("7. get_sleep_data:")
    print("=" * 60)
    try:
        sleep_data = client.get_sleep_data(date)
        print(json.dumps(sleep_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
    
    print("\n" + "=" * 60)
    print("8. get_respiration_data:")
    print("=" * 60)
    try:
        respiration_data = client.get_respiration_data(date)
        print(json.dumps(respiration_data, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
    
    print("\n" + "=" * 60)
    print("9. get_heart_rates:")
    print("=" * 60)
    try:
        heart_rates = client.get_heart_rates(date)
        print(json.dumps(heart_rates, indent=2, default=str))
    except Exception as e:
        print(f"Chyba: {e}")
        
except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()


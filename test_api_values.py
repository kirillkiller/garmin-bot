"""
Testovací skript pro zjištění, co API vrací pro různé metriky
"""
import os
import json
from garminconnect import Garmin
from datetime import datetime

# Načtení credentials z environment
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')
date = '2026-01-05'

if not email or not password:
    print("❌ Nastav GARMIN_EMAIL a GARMIN_PASSWORD")
    exit(1)

print(f"🔍 Testování Garmin API pro {date}...\n")

try:
    # Načíst session pokud existuje
    import garth
    garth_dir = os.path.expanduser('~/.garth')
    if os.path.exists(garth_dir):
        oauth1_file = os.path.join(garth_dir, 'oauth1_token.json')
        if os.path.exists(oauth1_file) and os.path.getsize(oauth1_file) > 0:
            print("🔍 Našel jsem uloženou session - používám ji")
            client = Garmin(email, password)
            client.login(tokenstore=garth_dir)
        else:
            client = Garmin(email, password)
            client.login()
    else:
        client = Garmin(email, password)
        client.login()
    
    print("✅ Připojeno k Garmin Connect\n")
    
    # Test různých metod
    print("=" * 80)
    print("1. RESPIRATION DATA (get_respiration_data):")
    print("=" * 80)
    try:
        respiration_data = client.get_respiration_data(date)
        print(f"Type: {type(respiration_data)}")
        if isinstance(respiration_data, dict):
            print(f"Keys: {list(respiration_data.keys())}")
            print(f"Content: {json.dumps(respiration_data, indent=2, default=str)}")
        else:
            print(f"Content: {respiration_data}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("2. HEART RATES (get_heart_rates):")
    print("=" * 80)
    try:
        heart_rates = client.get_heart_rates(date)
        print(f"Type: {type(heart_rates)}")
        if isinstance(heart_rates, dict):
            print(f"Keys: {list(heart_rates.keys())}")
            print(f"Content: {json.dumps(heart_rates, indent=2, default=str)}")
        elif isinstance(heart_rates, list):
            print(f"Length: {len(heart_rates)}")
            if len(heart_rates) > 0:
                print(f"First item: {json.dumps(heart_rates[0], indent=2, default=str) if isinstance(heart_rates[0], dict) else heart_rates[0]}")
        else:
            print(f"Content: {heart_rates}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("3. ACTIVITIES (get_activities_by_date):")
    print("=" * 80)
    try:
        activities = client.get_activities_by_date(date, date)
        print(f"Type: {type(activities)}")
        if isinstance(activities, list):
            print(f"Length: {len(activities)}")
            if len(activities) > 0:
                print(f"First activity keys: {list(activities[0].keys()) if isinstance(activities[0], dict) else 'not dict'}")
                print(f"First activity (first 500 chars): {json.dumps(activities[0], indent=2, default=str)[:500] if isinstance(activities[0], dict) else activities[0]}")
        else:
            print(f"Content: {activities}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("4. TRAINING READINESS (get_training_readiness):")
    print("=" * 80)
    try:
        training_readiness = client.get_training_readiness(date)
        print(f"Type: {type(training_readiness)}")
        if isinstance(training_readiness, dict):
            print(f"Keys: {list(training_readiness.keys())}")
            print(f"Content: {json.dumps(training_readiness, indent=2, default=str)}")
        else:
            print(f"Content: {training_readiness}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("5. TRAINING STATUS (get_training_status):")
    print("=" * 80)
    try:
        training_status = client.get_training_status(date)
        print(f"Type: {type(training_status)}")
        if isinstance(training_status, dict):
            print(f"Keys: {list(training_status.keys())}")
            print(f"Content: {json.dumps(training_status, indent=2, default=str)}")
        else:
            print(f"Content: {training_status}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("6. ENDURANCE SCORE (get_endurance_score):")
    print("=" * 80)
    try:
        endurance_score = client.get_endurance_score(date)
        print(f"Type: {type(endurance_score)}")
        if isinstance(endurance_score, dict):
            print(f"Keys: {list(endurance_score.keys())}")
            print(f"Content: {json.dumps(endurance_score, indent=2, default=str)}")
        else:
            print(f"Content: {endurance_score}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("7. HILL SCORE (get_hill_score):")
    print("=" * 80)
    try:
        hill_score = client.get_hill_score(date)
        print(f"Type: {type(hill_score)}")
        if isinstance(hill_score, dict):
            print(f"Keys: {list(hill_score.keys())}")
            print(f"Content: {json.dumps(hill_score, indent=2, default=str)}")
        else:
            print(f"Content: {hill_score}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("8. BLOOD PRESSURE (get_blood_pressure):")
    print("=" * 80)
    try:
        blood_pressure = client.get_blood_pressure(date)
        print(f"Type: {type(blood_pressure)}")
        if isinstance(blood_pressure, dict):
            print(f"Keys: {list(blood_pressure.keys())}")
            print(f"Content: {json.dumps(blood_pressure, indent=2, default=str)}")
        elif isinstance(blood_pressure, list):
            print(f"Length: {len(blood_pressure)}")
            if len(blood_pressure) > 0:
                print(f"First item: {json.dumps(blood_pressure[0], indent=2, default=str) if isinstance(blood_pressure[0], dict) else blood_pressure[0]}")
        else:
            print(f"Content: {blood_pressure}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("9. HYDRATION DATA (get_hydration_data):")
    print("=" * 80)
    try:
        hydration_data = client.get_hydration_data(date)
        print(f"Type: {type(hydration_data)}")
        if isinstance(hydration_data, dict):
            print(f"Keys: {list(hydration_data.keys())}")
            print(f"Content: {json.dumps(hydration_data, indent=2, default=str)}")
        else:
            print(f"Content: {hydration_data}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("10. BODY COMPOSITION (get_body_composition):")
    print("=" * 80)
    try:
        body_composition = client.get_body_composition(date)
        print(f"Type: {type(body_composition)}")
        if isinstance(body_composition, dict):
            print(f"Keys: {list(body_composition.keys())}")
            print(f"Content: {json.dumps(body_composition, indent=2, default=str)}")
        elif isinstance(body_composition, list):
            print(f"Length: {len(body_composition)}")
            if len(body_composition) > 0:
                print(f"First item: {json.dumps(body_composition[0], indent=2, default=str) if isinstance(body_composition[0], dict) else body_composition[0]}")
        else:
            print(f"Content: {body_composition}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("11. WEIGH INS (get_weigh_ins):")
    print("=" * 80)
    try:
        weigh_ins = client.get_weigh_ins(date)
        print(f"Type: {type(weigh_ins)}")
        if isinstance(weigh_ins, list):
            print(f"Length: {len(weigh_ins)}")
            if len(weigh_ins) > 0:
                print(f"First item keys: {list(weigh_ins[0].keys()) if isinstance(weigh_ins[0], dict) else 'not dict'}")
                print(f"First item: {json.dumps(weigh_ins[0], indent=2, default=str) if isinstance(weigh_ins[0], dict) else weigh_ins[0]}")
        else:
            print(f"Content: {weigh_ins}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("12. DAILY WEIGH INS (get_daily_weigh_ins):")
    print("=" * 80)
    try:
        daily_weigh_ins = client.get_daily_weigh_ins(date)
        print(f"Type: {type(daily_weigh_ins)}")
        if isinstance(daily_weigh_ins, list):
            print(f"Length: {len(daily_weigh_ins)}")
            if len(daily_weigh_ins) > 0:
                print(f"First item keys: {list(daily_weigh_ins[0].keys()) if isinstance(daily_weigh_ins[0], dict) else 'not dict'}")
                print(f"First item: {json.dumps(daily_weigh_ins[0], indent=2, default=str) if isinstance(daily_weigh_ins[0], dict) else daily_weigh_ins[0]}")
        else:
            print(f"Content: {daily_weigh_ins}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("13. SpO2 DATA (get_spo2_data):")
    print("=" * 80)
    try:
        spo2_data = client.get_spo2_data(date)
        print(f"Type: {type(spo2_data)}")
        if isinstance(spo2_data, dict):
            print(f"Keys: {list(spo2_data.keys())}")
            print(f"Content: {json.dumps(spo2_data, indent=2, default=str)}")
        else:
            print(f"Content: {spo2_data}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("14. MAX METRICS (get_max_metrics):")
    print("=" * 80)
    try:
        max_metrics = client.get_max_metrics(date)
        print(f"Type: {type(max_metrics)}")
        if isinstance(max_metrics, dict):
            print(f"Keys: {list(max_metrics.keys())}")
            print(f"Content: {json.dumps(max_metrics, indent=2, default=str)}")
        else:
            print(f"Content: {max_metrics}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
    print("\n" + "=" * 80)
    print("15. SLEEP DATA - sleepHeartRate:")
    print("=" * 80)
    try:
        sleep_data = client.get_sleep_data(date)
        if isinstance(sleep_data, dict):
            sleep_heart_rate = sleep_data.get('sleepHeartRate', {})
            print(f"Type: {type(sleep_heart_rate)}")
            if isinstance(sleep_heart_rate, dict):
                print(f"Keys: {list(sleep_heart_rate.keys())}")
                print(f"Content: {json.dumps(sleep_heart_rate, indent=2, default=str)}")
            else:
                print(f"Content: {sleep_heart_rate}")
    except Exception as e:
        print(f"❌ Chyba: {e}")
    
except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()


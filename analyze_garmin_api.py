#!/usr/bin/env python3
"""
Analýza všech dostupných metod v garminconnect knihovně
Zjistí, co všechno můžeme tahat z Garmin API
"""
import os
import inspect
from garminconnect import Garmin
from datetime import datetime, timedelta

def analyze_garmin_methods():
    """Analyzuje všechny metody v Garmin třídě"""
    print("🔍 Analýza dostupných metod v garminconnect knihovně\n")
    print("=" * 80)
    
    # Získat všechny metody z Garmin třídy
    garmin_methods = [method for method in dir(Garmin) if not method.startswith('_')]
    
    # Filtrovat pouze metody pro získávání dat (ne login, logout, atd.)
    data_methods = []
    for method_name in garmin_methods:
        method = getattr(Garmin, method_name)
        if callable(method) and not method_name in ['login', 'logout', 'connectapi', 'get_full_name', 'get_unit_system']:
            # Zkontrolovat, jestli metoda má nějaké parametry (obvykle date)
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            # Metody pro získávání dat obvykle mají 'date' nebo 'startdate'/'enddate'
            if any(p in params for p in ['date', 'startdate', 'enddate', 'start_date', 'end_date']):
                data_methods.append((method_name, params))
    
    print(f"📊 Našel jsem {len(data_methods)} metod pro získávání dat:\n")
    
    # Skupiny metod podle typu dat
    categories = {
        'Aktivita': ['get_activities', 'get_steps', 'get_distance'],
        'Zdraví': ['get_heart', 'get_stress', 'get_body', 'get_hrv', 'get_sleep', 'get_respiration', 'get_spo2'],
        'Trénink': ['get_training', 'get_endurance', 'get_hill', 'get_max'],
        'Tělo': ['get_weight', 'get_weigh', 'get_body_composition', 'get_hydration', 'get_blood'],
        'Statistiky': ['get_stats', 'get_summary', 'get_user'],
    }
    
    for category, keywords in categories.items():
        matching = [m for m in data_methods if any(kw in m[0].lower() for kw in keywords)]
        if matching:
            print(f"\n📁 {category}:")
            for method_name, params in sorted(matching):
                print(f"   • {method_name}({', '.join(params)})")
    
    # Ostatní metody
    other_methods = [m for m in data_methods if not any(
        any(kw in m[0].lower() for kw in keywords) 
        for keywords in categories.values()
    )]
    
    if other_methods:
        print(f"\n📁 Ostatní:")
        for method_name, params in sorted(other_methods):
            print(f"   • {method_name}({', '.join(params)})")
    
    print("\n" + "=" * 80)
    print("\n💡 Tip: Spusť tento skript s připojením k Garmin pro testování metod:")
    print("   python3 analyze_garmin_api.py --test")

def test_all_methods(date: str = None):
    """Otestuje všechny metody s reálným připojením"""
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')
    
    if not email or not password:
        print("❌ Nastav GARMIN_EMAIL a GARMIN_PASSWORD")
        return
    
    print(f"\n🧪 Testování metod s reálným připojením pro {date}...\n")
    
    try:
        import garth
        garth_dir = os.path.expanduser('~/.garth')
        client = Garmin(email, password)
        if os.path.exists(garth_dir):
            client.login(tokenstore=garth_dir)
        else:
            client.login()
        
        print("✅ Připojeno k Garmin Connect\n")
        
        # Seznam metod k testování
        test_methods = [
            ('get_user_summary', [date]),
            ('get_steps_data', [date]),
            ('get_floors', [date]),
            ('get_daily_summary', [date]),
            ('get_wellness', [date]),
            ('get_rhr_day', [date]),
            ('get_activities_summary', [date]),
            ('get_activities_by_date', [date, date]),
            ('get_activities_fordate', [date]),
        ]
        
        results = {}
        for method_name, args in test_methods:
            if hasattr(client, method_name):
                try:
                    method = getattr(client, method_name)
                    result = method(*args)
                    results[method_name] = {
                        'success': True,
                        'type': type(result).__name__,
                        'has_data': bool(result) if result is not None else False
                    }
                    print(f"✅ {method_name}: {type(result).__name__} - {'Má data' if result else 'Prázdné'}")
                except Exception as e:
                    results[method_name] = {
                        'success': False,
                        'error': str(e)
                    }
                    print(f"❌ {method_name}: {str(e)[:50]}")
            else:
                print(f"⚠️  {method_name}: Metoda neexistuje")
        
        print("\n" + "=" * 80)
        print("\n📊 Shrnutí:")
        successful = sum(1 for r in results.values() if r.get('success'))
        print(f"   ✅ Úspěšné: {successful}/{len(test_methods)}")
        print(f"   ❌ Chyby: {len(test_methods) - successful}")
        
    except Exception as e:
        print(f"❌ Chyba při připojení: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyzuje dostupné metody v garminconnect')
    parser.add_argument('--test', action='store_true', help='Otestuj metody s reálným připojením')
    parser.add_argument('--date', type=str, help='Datum pro testování (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if args.test:
        test_all_methods(args.date)
    else:
        analyze_garmin_methods()


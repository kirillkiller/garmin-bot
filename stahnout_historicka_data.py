"""
Skript pro stažení historických dat z Garmin Connect
"""
import os
import sys
import time
from datetime import datetime, timedelta
from garmin_bot import GarminBot

def main():
    """Stáhne historická data z Garmin Connect"""
    
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
    
    # Možnosti použití
    if len(sys.argv) > 1:
        if sys.argv[1] == '--range':
            # Stažení dat za rozsah dat
            if len(sys.argv) < 4:
                print("❌ Použití: python3 stahnout_historicka_data.py --range YYYY-MM-DD YYYY-MM-DD")
                print("   Příklad: python3 stahnout_historicka_data.py --range 2025-12-01 2025-12-31")
                return
            
            start_date = sys.argv[2]
            end_date = sys.argv[3]
            
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                
                if start > end:
                    print("❌ Počáteční datum musí být před koncovým datem")
                    return
                
                print(f"📥 Stahuji data od {start_date} do {end_date}...")
                print(f"   Celkem dní: {(end - start).days + 1}\n")
                
                current = start
                success = 0
                failed = 0
                
                while current <= end:
                    date_str = current.strftime('%Y-%m-%d')
                    print(f"🔄 {date_str}...", end=' ')
                    
                    try:
                        bot.run_once(date_str)
                        print("✅")
                        success += 1
                    except Exception as e:
                        print(f"❌ Chyba: {e}")
                        failed += 1
                    
                    current += timedelta(days=1)
                
                print(f"\n✅ Hotovo! Úspěšně: {success}, Chyby: {failed}")
                
            except ValueError:
                print("❌ Neplatný formát data. Použij YYYY-MM-DD")
        
        elif sys.argv[1] == '--days':
            # Stažení dat za posledních N dní
            if len(sys.argv) < 3:
                print("❌ Použití: python3 stahnout_historicka_data.py --days N")
                print("   Příklad: python3 stahnout_historicka_data.py --days 30")
                return
            
            try:
                days = int(sys.argv[2])
                if days < 1:
                    print("❌ Počet dní musí být kladné číslo")
                    return
                
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days-1)
                
                print(f"📥 Stahuji data za posledních {days} dní...")
                print(f"   Od {start_date.strftime('%Y-%m-%d')} do {end_date.strftime('%Y-%m-%d')}\n")
                
                current = start_date
                success = 0
                failed = 0
                
                while current <= end_date:
                    date_str = current.strftime('%Y-%m-%d')
                    print(f"🔄 {date_str}...", end=' ')
                    
                    try:
                        bot.run_once(date_str)
                        print("✅")
                        success += 1
                    except Exception as e:
                        print(f"❌ Chyba: {e}")
                        failed += 1
                    
                    current += timedelta(days=1)
                
                print(f"\n✅ Hotovo! Úspěšně: {success}, Chyby: {failed}")
                
            except ValueError:
                print("❌ Neplatný počet dní")
        
        elif sys.argv[1] == '--year':
            # Stažení dat za poslední rok
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            print(f"📥 Stahuji data za poslední rok...")
            print(f"   Od {start_date.strftime('%Y-%m-%d')} do {end_date.strftime('%Y-%m-%d')}")
            print(f"   Celkem dní: {(end_date - start_date).days + 1}\n")
            print("⚠️  Toto může trvat dlouho (až několik hodin)!")
            print("💡 Můžeš zastavit pomocí Ctrl+C a pokračovat později")
            print("💡 Při prvním spuštění budeš možná vyzván k zadání MFA kódu\n")
            
            # Nejdřív zkusit připojit k Garmin (pro MFA)
            print("🔐 Připojuji se k Garmin Connect...")
            print("💡 Bot počká 2 minuty před prvním pokusem (kvůli rate limiting)")
            print("💡 Pokud budeš vyzván k zadání MFA kódu, zadej ho a počkej...")
            print("💡 Po úspěšném přihlášení bot počká 15 sekund (kvůli rate limiting)\n")
            try:
                bot._init_garmin()
                print("✅ Připojeno k Garmin Connect\n")
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Too Many Requests" in error_str:
                    print(f"❌ Rate limit (429) při připojování k Garmin")
                    print("💡 Garmin má rate limiting - počkej 5-10 minut a zkus znovu")
                    print("💡 Nebo zkus spustit znovu - možná už máš uloženou session")
                else:
                    print(f"❌ Chyba při připojování k Garmin: {e}")
                    print("💡 Zkus spustit znovu - možná potřebuješ zadat MFA kód")
                return
            
            current = start_date
            success = 0
            failed = 0
            total_days = (end_date - start_date).days + 1
            
            while current <= end_date:
                date_str = current.strftime('%Y-%m-%d')
                day_num = (current - start_date).days + 1
                print(f"🔄 [{day_num}/{total_days}] {date_str}...", end=' ', flush=True)
                
                try:
                    bot.run_once(date_str)
                    print("✅")
                    success += 1
                    # Po každém úspěšném dotazu počkat (rate limiting)
                    time.sleep(2)
                except KeyboardInterrupt:
                    print("\n\n🛑 Zastaveno uživatelem")
                    print(f"📊 Progress: {success} úspěšných, {failed} chyb")
                    print(f"💡 Můžeš pokračovat později - bot automaticky aktualizuje existující záznamy")
                    return
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "Too Many Requests" in error_str:
                        print(f"❌ Rate limit - čekám 30 sekund...")
                        time.sleep(30)
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
                
                # Každých 10 dní zobrazit progress
                if day_num % 10 == 0:
                    print(f"\n📊 Progress: {success} úspěšných, {failed} chyb ({day_num}/{total_days} dní)\n")
            
            print(f"\n✅ Hotovo! Úspěšně: {success}, Chyby: {failed}")
        
        elif sys.argv[1] == '--date':
            # Stažení dat pro konkrétní datum
            if len(sys.argv) < 3:
                print("❌ Použití: python3 stahnout_historicka_data.py --date YYYY-MM-DD")
                print("   Příklad: python3 stahnout_historicka_data.py --date 2025-12-25")
                return
            
            date_str = sys.argv[2]
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                print(f"📥 Stahuji data pro {date_str}...")
                bot.run_once(date_str)
                print("✅ Hotovo!")
            except ValueError:
                print("❌ Neplatný formát data. Použij YYYY-MM-DD")
            except Exception as e:
                print(f"❌ Chyba: {e}")
    else:
        print("📋 Použití:")
        print("")
        print("1. Stažení dat za rozsah:")
        print("   python3 stahnout_historicka_data.py --range YYYY-MM-DD YYYY-MM-DD")
        print("   Příklad: python3 stahnout_historicka_data.py --range 2025-12-01 2025-12-31")
        print("")
        print("2. Stažení dat za posledních N dní:")
        print("   python3 stahnout_historicka_data.py --days N")
        print("   Příklad: python3 stahnout_historicka_data.py --days 30")
        print("")
        print("3. Stažení dat za poslední rok:")
        print("   python3 stahnout_historicka_data.py --year")
        print("")
        print("4. Stažení dat pro konkrétní datum:")
        print("   python3 stahnout_historicka_data.py --date YYYY-MM-DD")
        print("   Příklad: python3 stahnout_historicka_data.py --date 2025-12-25")
        print("")
        print("💡 Nebo použij přímo garmin_bot.py:")
        print("   python3 garmin_bot.py --once --date 2025-12-25")

if __name__ == '__main__':
    main()


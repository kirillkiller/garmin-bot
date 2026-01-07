#!/usr/bin/env python3
"""
Skript pro zjištění chybějících dat v Google Sheets
"""
import os
import gspread
from datetime import datetime, timedelta

# Načtení credentials
google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

if not google_sheet_id:
    print("❌ Nastav GOOGLE_SHEET_ID")
    exit(1)

# Připojení k Google Sheets (stejný způsob jako v garmin_bot.py)
if os.path.exists(google_credentials):
    gc = gspread.service_account(filename=google_credentials)
    sheet = gc.open_by_key(google_sheet_id)
    worksheet = sheet.worksheet('Garmin Data')
    
    # Získat všechny datumy z prvního sloupce
    existing_dates = worksheet.col_values(1)[1:]  # Přeskočit hlavičku
    
    print(f"📊 Celkem záznamů v Google Sheets: {len(existing_dates)}")
    print(f"📅 První datum: {existing_dates[0] if existing_dates else 'N/A'}")
    print(f"📅 Poslední datum: {existing_dates[-1] if existing_dates else 'N/A'}")
    
    # Vytvořit seznam všech dat za poslední rok
    today = datetime.now()
    all_dates = []
    for i in range(1, 366):  # 365 dní zpět
        date = today - timedelta(days=i)
        all_dates.append(date.strftime('%Y-%m-%d'))
    
    # Najít chybějící datumy
    missing_dates = []
    for date in all_dates:
        if date not in existing_dates:
            missing_dates.append(date)
    
    print(f"\n❌ Chybějících datumů: {len(missing_dates)}")
    if missing_dates:
        print(f"📅 První chybějící: {missing_dates[0]}")
        print(f"📅 Poslední chybějící: {missing_dates[-1]}")
        print(f"\n📋 Seznam chybějících datumů (prvních 20):")
        for date in missing_dates[:20]:
            print(f"   {date}")
        if len(missing_dates) > 20:
            print(f"   ... a dalších {len(missing_dates) - 20} datumů")
        
        # Uložit do souboru
        with open('missing_dates.txt', 'w') as f:
            for date in missing_dates:
                f.write(f"{date}\n")
        print(f"\n💾 Seznam chybějících datumů uložen do: missing_dates.txt")
    else:
        print("✅ Všechna data jsou k dispozici!")
else:
    print("❌ Soubor credentials.json nenalezen")


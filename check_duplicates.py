#!/usr/bin/env python3
"""
Skript pro kontrolu duplicitních datumů v Google Sheets
"""
import os
import gspread
from collections import Counter
from google.oauth2.service_account import Credentials

# Načtení credentials
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')

if not google_sheet_id:
    print("❌ Nastav GOOGLE_SHEET_ID")
    exit(1)

# Připojení k Google Sheets
if os.path.exists(google_credentials):
    creds = Credentials.from_service_account_file(google_credentials, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(google_sheet_id)
    worksheet = sheet.worksheet('Garmin Data')
    
    # Získat všechny datumy z prvního sloupce (přeskočit hlavičku)
    all_dates = worksheet.col_values(1)[1:]  # Přeskočit hlavičku
    
    print(f"📊 Celkem záznamů: {len(all_dates)}")
    
    # Najít duplicitní datumy
    date_counts = Counter(all_dates)
    duplicates = {date: count for date, count in date_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n⚠️  NALEZENY DUPLICITNÍ DATUMY: {len(duplicates)}")
        print("=" * 60)
        for date, count in sorted(duplicates.items()):
            print(f"  {date}: {count}x")
            
            # Najít řádky s tímto datem
            row_indices = [i + 2 for i, d in enumerate(all_dates) if d == date]  # +2 protože hlavička je řádek 1
            print(f"    Řádky: {row_indices}")
    else:
        print("\n✅ ŽÁDNÉ DUPLICITY - vše je v pořádku!")
    
else:
    print("❌ Credentials soubor nenalezen")
    exit(1)


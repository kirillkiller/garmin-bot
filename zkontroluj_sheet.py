"""
Skript pro kontrolu Google Sheet - zjistí, kde jsou nuly nebo prázdné hodnoty
"""
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Načtení credentials - stejná logika jako v garmin_bot.py
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request

client = None

# Zkusit Service Account nejdřív
if os.path.exists('credentials.json'):
    try:
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(creds)
        print("✅ Google Sheets připojeno pomocí Service Account (credentials.json)")
    except Exception:
        # Pokud to není Service Account, zkusit OAuth2
        if os.path.exists('token.json'):
            creds = OAuthCredentials.from_authorized_user_file('token.json')
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            client = gspread.authorize(creds)
            print("✅ Google Sheets připojeno pomocí OAuth2")
        else:
            print("❌ Credentials soubor nenalezen")
            exit(1)
else:
    print("❌ Credentials soubor nenalezen")
    exit(1)

# Otevření sheetu
sheet_id = os.getenv('GOOGLE_SHEET_ID', '1GgWUi-OZyrNRza8VU2ofSRelRrqTTZpA0KB1PCqfrIM')
spreadsheet = client.open_by_key(sheet_id)
worksheet = spreadsheet.worksheet('Garmin Data')

print("🔍 Kontroluji Google Sheet pro nuly a prázdné hodnoty...\n")

# Načíst hlavičku
header = worksheet.row_values(1)
print(f"📋 Hlavička ({len(header)} sloupců):")
for i, col in enumerate(header, 1):
    print(f"  {i}. {col}")

print("\n" + "=" * 80)
print("🔍 Procházím všechny řádky...\n")

# Načíst všechna data
all_values = worksheet.get_all_values()

# Najít indexy sloupců, které by neměly být nuly
numeric_columns = {}
for i, col_name in enumerate(header):
    col_name_lower = col_name.lower()
    # Sloupce, které by měly mít hodnoty (ne nuly)
    if any(keyword in col_name_lower for keyword in ['steps', 'distance', 'calories', 'hrv', 'stress', 'sleep', 'score', 'quality', 'body', 'battery', 'heart', 'rate']):
        numeric_columns[i] = col_name

print(f"📊 Kontroluji {len(numeric_columns)} numerických sloupců:\n")
for idx, name in numeric_columns.items():
    print(f"  - Sloupec {idx+1} ({chr(65+idx)}): {name}")

print("\n" + "=" * 80)
print("🔍 Hledám řádky s nulami nebo prázdnými hodnotami...\n")

issues = []

for row_idx, row in enumerate(all_values[1:], start=2):  # Začít od řádku 2 (první je hlavička)
    if not row or not row[0]:  # Prázdný řádek nebo chybí datum
        continue
    
    date = row[0] if row else ""
    row_issues = []
    
    for col_idx, col_name in numeric_columns.items():
        if col_idx < len(row):
            value = row[col_idx].strip() if row[col_idx] else ""
            
            # Zkontrolovat, jestli je to nula nebo prázdné
            if value == "" or value == "0" or value == "0.0" or value == "0.00":
                row_issues.append({
                    'column': col_name,
                    'column_idx': col_idx + 1,
                    'value': value if value else "(prázdné)"
                })
    
    if row_issues:
        issues.append({
            'row': row_idx,
            'date': date,
            'issues': row_issues
        })

# Zobrazit výsledky
if issues:
    print(f"⚠️  Našel jsem {len(issues)} řádků s nulami nebo prázdnými hodnotami:\n")
    
    for issue in issues:
        print(f"📅 Řádek {issue['row']} - Datum: {issue['date']}")
        for prob in issue['issues']:
            print(f"   ❌ {prob['column']} (sloupec {chr(64 + prob['column_idx'])}): {prob['value']}")
        print()
    
    print("=" * 80)
    print("📊 Shrnutí problémů podle sloupců:\n")
    
    # Spočítat problémy podle sloupců
    column_issues = {}
    for issue in issues:
        for prob in issue['issues']:
            col_name = prob['column']
            if col_name not in column_issues:
                column_issues[col_name] = []
            column_issues[col_name].append({
                'row': issue['row'],
                'date': issue['date']
            })
    
    for col_name, problems in sorted(column_issues.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {col_name}: {len(problems)} řádků s nulami")
        # Zobrazit první 5 příkladů
        for prob in problems[:5]:
            print(f"    - Řádek {prob['row']} ({prob['date']})")
        if len(problems) > 5:
            print(f"    ... a dalších {len(problems) - 5} řádků")
        print()
else:
    print("✅ Žádné nuly nebo prázdné hodnoty v numerických sloupcích!\n")

print("=" * 80)
print("✅ Kontrola dokončena")


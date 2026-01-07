"""
Pomocný skript pro nastavení Garmin Bot
"""
import os
import sys

def check_requirements():
    """Zkontroluje, zda jsou nainstalované všechny potřebné knihovny"""
    missing = []
    
    try:
        import garminconnect
    except ImportError:
        missing.append("garminconnect")
    
    try:
        import gspread
    except ImportError:
        missing.append("gspread")
    
    try:
        import google.auth
    except ImportError:
        missing.append("google-auth")
    
    if missing:
        print(f"❌ Chybí knihovny: {', '.join(missing)}")
        print(f"📦 Instaluji...")
        os.system(f"pip3 install {' '.join(missing)}")
        print("✅ Hotovo!")
    else:
        print("✅ Všechny knihovny jsou nainstalované")

def check_env_vars():
    """Zkontroluje environment variables"""
    required = ['GARMIN_EMAIL', 'GARMIN_PASSWORD', 'GOOGLE_SHEET_ID']
    missing = []
    
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Chybí environment variables: {', '.join(missing)}")
        print("\n📝 Nastav je pomocí:")
        print("   export GARMIN_EMAIL='vas@email.cz'")
        print("   export GARMIN_PASSWORD='heslo'")
        print("   export GOOGLE_SHEET_ID='1ABC123...'")
        return False
    else:
        print("✅ Všechny environment variables jsou nastavené")
        return True

def check_credentials():
    """Zkontroluje Google credentials"""
    if os.path.exists('credentials.json'):
        print("✅ credentials.json nalezen")
        return True
    elif os.path.exists('token.json'):
        print("✅ token.json nalezen (OAuth2)")
        return True
    else:
        print("⚠️  Google credentials nenalezeny")
        print("   Potřebujete credentials.json (Service Account)")
        return False

def main():
    print("🔍 Kontroluji nastavení Garmin Bot...\n")
    
    check_requirements()
    print()
    
    env_ok = check_env_vars()
    print()
    
    creds_ok = check_credentials()
    print()
    
    if env_ok and creds_ok:
        print("✅ Vše je připraveno!")
        print("\n🚀 Můžeš spustit:")
        print("   python3 garmin_bot.py --once")
    else:
        print("❌ Ještě něco chybí - dokonči nastavení výše")

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Kontrolní skript - zkontroluje, zda je vše připraveno ke spuštění
"""
import os
import sys
from pathlib import Path

def check_mark():
    return "✅"
def fail_mark():
    return "❌"
def warn_mark():
    return "⚠️"

def check_python():
    """Kontrola Pythonu"""
    print(f"{check_mark()} Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Kontrola závislostí"""
    print("\n📦 Kontrola závislostí...")
    all_ok = True
    
    deps = {
        "google.generativeai": "google-generativeai",
        "selenium": "selenium",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4"
    }
    
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"   {check_mark()} {package}")
        except ImportError:
            print(f"   {fail_mark()} {package} - Nainstaluj: pip3 install {package}")
            all_ok = False
    
    return all_ok

def check_config():
    """Kontrola konfigurace"""
    print("\n⚙️  Kontrola konfigurace...")
    
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        print(f"   {fail_mark()} config/config.yaml neexistuje")
        print("   💡 Zkopíruj: cp config/config.example.yaml config/config.yaml")
        return False
    
    print(f"   {check_mark()} config/config.yaml existuje")
    
    # Kontrola, zda nejsou example weby
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            if 'example.com' in content:
                print(f"   {warn_mark()} V config.yaml jsou stále example.com weby")
                print("   💡 Uprav config/config.yaml a přidej skutečné weby")
    except:
        pass
    
    return True

def check_api_keys():
    """Kontrola API klíčů"""
    print("\n🔑 Kontrola API klíčů...")
    all_ok = True
    
    # Gemini API key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        masked = gemini_key[:8] + "..." + gemini_key[-4:] if len(gemini_key) > 12 else "***"
        print(f"   {check_mark()} GEMINI_API_KEY nastaven ({masked})")
    else:
        print(f"   {fail_mark()} GEMINI_API_KEY není nastaven")
        print("   💡 Nastav: export GEMINI_API_KEY='tvůj-klíč'")
        print("   💡 Získej z: https://makersuite.google.com/app/apikey")
        all_ok = False
    
    # Email (volitelné)
    email_user = os.getenv("EMAIL_USERNAME")
    if email_user:
        print(f"   {check_mark()} EMAIL_USERNAME nastaven")
    else:
        print(f"   {warn_mark()} EMAIL_USERNAME není nastaven (volitelné)")
        print("   💡 Pokud chceš email reporty, nastav email proměnné")
    
    return all_ok

def check_chrome():
    """Kontrola Chrome/Chromium"""
    print("\n🌐 Kontrola Chrome/Chromium...")
    
    # Zkus najít Chrome
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if Path(path).exists():
            print(f"   {check_mark()} Chrome nalezen: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print(f"   {warn_mark()} Chrome/Chromium nenalezen")
        print("   💡 Selenium může automaticky stáhnout ChromeDriver")
        print("   💡 Nebo nainstaluj Chrome: https://www.google.com/chrome/")
    
    return True

def check_directories():
    """Kontrola potřebných adresářů"""
    print("\n📁 Kontrola adresářů...")
    
    dirs = ["data", "logs"]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   {check_mark()} Vytvořen adresář: {dir_name}")
        else:
            print(f"   {check_mark()} Adresář existuje: {dir_name}")
    
    return True

def main():
    print("🔍 Kontrola připravenosti aplikace\n")
    print("=" * 60)
    
    results = []
    
    # Kontroly
    results.append(("Python", check_python()))
    results.append(("Závislosti", check_dependencies()))
    results.append(("Konfigurace", check_config()))
    results.append(("API klíče", check_api_keys()))
    results.append(("Chrome", check_chrome()))
    results.append(("Adresáře", check_directories()))
    
    print("\n" + "=" * 60)
    print("\n📊 Shrnutí:\n")
    
    all_ok = True
    for name, result in results:
        status = check_mark() if result else fail_mark()
        print(f"{status} {name}")
        if not result:
            all_ok = False
    
    print()
    
    if all_ok:
        print("✅ Vše je připraveno! Můžeš spustit aplikaci:")
        print("   python3 main.py --once")
    else:
        print("⚠️  Některé kontroly selhaly. Postupuj podle výše uvedených instrukcí.")
        print("\n📚 Více informací: SPUSTENI.md")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


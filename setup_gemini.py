#!/usr/bin/env python3
"""
Interaktivní skript pro nastavení Gemini API klíče
"""
import os
import sys
import subprocess
from pathlib import Path

def print_step(step_num, text):
    """Vytiskne krok"""
    print(f"\n{'='*60}")
    print(f"KROK {step_num}: {text}")
    print('='*60)

def check_api_key():
    """Zkontroluje, zda je API klíč nastaven"""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        print(f"✅ GEMINI_API_KEY je nastaven: {masked}")
        return True
    else:
        print("❌ GEMINI_API_KEY není nastaven")
        return False

def open_browser(url):
    """Otevře URL v prohlížeči"""
    try:
        subprocess.run(["open", url], check=True)
        return True
    except:
        return False

def save_to_zshrc(key):
    """Uloží klíč do ~/.zshrc pro trvalé nastavení"""
    zshrc_path = Path.home() / ".zshrc"
    
    # Zkontroluj, zda už tam není
    if zshrc_path.exists():
        with open(zshrc_path, 'r') as f:
            if 'GEMINI_API_KEY' in f.read():
                print("⚠️  GEMINI_API_KEY už je v ~/.zshrc")
                return False
    
    # Přidej do ~/.zshrc
    with open(zshrc_path, 'a') as f:
        f.write(f'\n# Gemini API Key (přidáno automaticky)\n')
        f.write(f'export GEMINI_API_KEY="{key}"\n')
    
    return True

def main():
    print("\n🤖 Nastavení Gemini API klíče\n")
    
    # Krok 1: Kontrola, zda už není nastaven
    if check_api_key():
        print("\n💡 API klíč už je nastaven!")
        response = input("Chceš ho změnit? (ano/ne): ").lower()
        if response not in ['ano', 'a', 'yes', 'y']:
            print("✅ Použijeme existující klíč.")
            return 0
    
    # Krok 2: Instrukce pro získání klíče
    print_step(1, "Získání Gemini API klíče")
    print("\n📝 Postup:")
    print("1. Otevře se ti prohlížeč s Google AI Studio")
    print("2. Přihlas se pomocí svého Google účtu")
    print("3. Klikni na 'Create API Key' nebo 'Get API Key'")
    print("4. Zkopíruj vygenerovaný klíč")
    print("\n💡 Klíč vypadá jako: AIzaSyAbc123def456ghi789...")
    
    input("\nStiskni Enter, až budeš připravený otevřít Google AI Studio...")
    
    # Otevři prohlížeč
    url = "https://makersuite.google.com/app/apikey"
    print(f"\n🌐 Otevírám {url}...")
    if open_browser(url):
        print("✅ Prohlížeč otevřen!")
    else:
        print("⚠️  Nepodařilo se otevřít prohlížeč automaticky")
        print(f"   Otevři ručně: {url}")
    
    # Krok 3: Zadej klíč
    print_step(2, "Zadání API klíče")
    print("\n📋 Zkopíruj svůj Gemini API klíč a vlož ho sem:")
    print("(Klíč nebude viditelný při psaní pro bezpečnost)\n")
    
    api_key = input("Gemini API klíč: ").strip()
    
    if not api_key:
        print("❌ Klíč nebyl zadán. Ukončuji.")
        return 1
    
    if len(api_key) < 20:
        print("⚠️  Klíč vypadá příliš krátký. Ujisti se, že jsi zkopíroval celý klíč.")
        confirm = input("Přesto pokračovat? (ano/ne): ").lower()
        if confirm not in ['ano', 'a', 'yes', 'y']:
            return 1
    
    # Krok 4: Nastavení pro aktuální session
    print_step(3, "Nastavení klíče")
    
    # Nastav pro aktuální session
    os.environ["GEMINI_API_KEY"] = api_key
    print("✅ Klíč nastaven pro aktuální terminál")
    
    # Uložení do ~/.zshrc
    print("\n💾 Chceš uložit klíč trvale? (nebudeš ho muset nastavovat při každém restartu)")
    save_permanent = input("Uložit do ~/.zshrc? (ano/ne): ").lower()
    
    if save_permanent in ['ano', 'a', 'yes', 'y']:
        if save_to_zshrc(api_key):
            print("✅ Klíč uložen do ~/.zshrc")
            print("💡 Pro načtení v aktuálním terminálu spusť: source ~/.zshrc")
        else:
            print("⚠️  Klíč už je v ~/.zshrc")
    
    # Krok 5: Ověření
    print_step(4, "Ověření")
    
    if check_api_key():
        print("\n✅ Všechno je nastaveno správně!")
        print("\n📝 Další kroky:")
        print("1. Můžeš pokračovat s instalací závislostí:")
        print("   pip3 install -r requirements.txt")
        print("\n2. Nebo spustit kontrolu:")
        print("   python3 check_ready.py")
        return 0
    else:
        print("\n❌ Něco se pokazilo. Zkus to znovu.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Přerušeno uživatelem.")
        sys.exit(1)


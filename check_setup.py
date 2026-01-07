#!/usr/bin/env python3
"""
Kontrolní skript pro ověření, zda je vše připraveno k použití
"""
import sys
import os

def check_python():
    """Kontrola Pythonu"""
    print("🐍 Kontrola Pythonu...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ⚠️  Doporučuje se Python 3.7+")
        return False
    print("   ✅ Python je v pořádku")
    return True

def check_openai():
    """Kontrola OpenAI knihovny"""
    print("\n📦 Kontrola OpenAI knihovny...")
    try:
        import openai
        print(f"   ✅ openai je nainstalována (verze: {openai.__version__})")
        return True
    except ImportError:
        print("   ❌ openai není nainstalována")
        print("   💡 Instaluj: pip3 install openai")
        return False

def check_api_key():
    """Kontrola API klíče"""
    print("\n🔑 Kontrola API klíče...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"   ✅ OPENAI_API_KEY je nastaven ({masked_key})")
        return True
    else:
        print("   ❌ OPENAI_API_KEY není nastaven")
        print("   💡 Nastav: export OPENAI_API_KEY='tvůj-api-klíč'")
        return False

def main():
    print("🔍 Kontrola nastavení AI agenta\n")
    print("=" * 50)
    
    python_ok = check_python()
    openai_ok = check_openai()
    api_key_ok = check_api_key()
    
    print("\n" + "=" * 50)
    
    if python_ok and openai_ok and api_key_ok:
        print("\n✅ Vše je připraveno! Můžeš spustit agenta:")
        print("   python3 agent_simple.py")
        return 0
    else:
        print("\n⚠️  Některé kontroly selhaly. Postupuj podle výše uvedených instrukcí.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


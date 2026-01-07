#!/usr/bin/env python3
"""Test script pro rychlé spuštění serveru"""
import sys
import os

# Přidej aktuální adresář do path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app import app, init_app
    
    print("🚀 Inicializuji server...")
    init_app()
    
    port = 8080
    print("="*60)
    print("🌐 Webové rozhraní spuštěno!")
    print("="*60)
    print(f"📝 Otevři Safari a jdi na:")
    print(f"   http://127.0.0.1:{port}")
    print(f"   nebo")
    print(f"   http://localhost:{port}")
    print("="*60)
    print("🛑 Pro zastavení stiskni Ctrl+C")
    print("="*60)
    print()
    
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    
except Exception as e:
    print(f"❌ Chyba: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


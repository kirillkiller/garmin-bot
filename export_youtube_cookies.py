#!/usr/bin/env python3
"""
Helper script pro export YouTube cookies z prohlížeče
Použij to pro obejití věkového omezení a detekce bota
"""
import sys
from pathlib import Path

def export_with_extension():
    """Návod pro export pomocí browser extension"""
    print("""
🍪 EXPORT COOKIES POMOCÍ BROWSER EXTENSION (NEJLEPŠÍ METODA)

1. Nainstaluj extension:
   - Chrome/Edge: "Get cookies.txt LOCALLY" nebo "Cookie-Editor"
   - Firefox: "cookies.txt" extension

2. Jdi na youtube.com a přihlas se

3. Klikni na extension a exportuj cookies

4. Ulož jako "cookies.txt" do složky projektu

5. Hotovo! Bot automaticky použije cookies.txt
""")

def export_with_yt_dlp():
    """Návod pro export pomocí yt-dlp"""
    print("""
🍪 EXPORT COOKIES POMOCÍ YT-DLP

1. Otevři terminál

2. Spusť příkaz (podle prohlížeče):

   Chrome:
   yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com"

   Firefox:
   yt-dlp --cookies-from-browser firefox --cookies cookies.txt "https://www.youtube.com"

   Safari (macOS):
   yt-dlp --cookies-from-browser safari --cookies cookies.txt "https://www.youtube.com"

3. Soubor cookies.txt se vytvoří v aktuálním adresáři

4. Přesuň ho do složky projektu

5. Hotovo!
""")

def export_manual():
    """Návod pro manuální export"""
    print("""
🍪 MANUÁLNÍ EXPORT COOKIES

1. Otevři prohlížeč a jdi na youtube.com
   (musíš být přihlášený)

2. Otevři Developer Tools (F12)

3. Jdi na záložku Application (Chrome) nebo Storage (Firefox)

4. Vlevo najdi Cookies > https://www.youtube.com

5. Exportuj cookies pomocí:
   - Chrome: Použij extension "Get cookies.txt LOCALLY"
   - Firefox: Použij extension "cookies.txt"
   - Nebo použij yt-dlp příkaz výše

6. Ulož jako cookies.txt do složky projektu
""")

def main():
    print("="*60)
    print("🍪 YOUTUBE COOKIES EXPORT - NÁVOD")
    print("="*60)
    print()
    
    if len(sys.argv) > 1:
        method = sys.argv[1].lower()
        if method == "extension":
            export_with_extension()
        elif method == "yt-dlp":
            export_with_yt_dlp()
        elif method == "manual":
            export_manual()
        else:
            print("❌ Neznámá metoda. Použij: extension, yt-dlp, nebo manual")
    else:
        print("Vyber metodu exportu:\n")
        print("1. Extension (nejjednodušší)")
        print("2. yt-dlp příkaz")
        print("3. Manuální")
        print()
        choice = input("Tvoje volba (1-3): ").strip()
        
        if choice == "1":
            export_with_extension()
        elif choice == "2":
            export_with_yt_dlp()
        elif choice == "3":
            export_manual()
        else:
            print("❌ Neplatná volba")
            return
        
        print("\n" + "="*60)
        print("✅ Po exportu cookies.txt bude bot automaticky používat cookies")
        print("="*60)

if __name__ == "__main__":
    main()


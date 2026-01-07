# 🍪 YouTube Cookies - Obejití věkového omezení a detekce bota

## Problém

YouTube někdy blokuje přístup k videím kvůli:
- Věkovému omezení (vyžaduje přihlášení)
- Detekci bota (rate limiting, CAPTCHA)

## Řešení: Použití cookies

Bot automaticky podporuje cookies pro obejití těchto omezení.

## 📋 Metody exportu cookies

### Metoda 1: Browser Extension (NEJLEPŠÍ)

1. **Nainstaluj extension:**
   - Chrome/Edge: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Jdi na youtube.com a přihlas se**

3. **Exportuj cookies:**
   - Klikni na extension ikonu
   - Klikni "Export" nebo "Save"
   - Ulož jako `cookies.txt` do složky projektu

4. **Hotovo!** Bot automaticky použije cookies

### Metoda 2: yt-dlp příkaz

```bash
# Chrome
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com"

# Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt "https://www.youtube.com"

# Safari (macOS)
yt-dlp --cookies-from-browser safari --cookies cookies.txt "https://www.youtube.com"
```

Soubor `cookies.txt` se vytvoří v aktuálním adresáři. Přesuň ho do složky projektu.

### Metoda 3: Manuální export

1. Otevři Developer Tools (F12)
2. Jdi na záložku Application (Chrome) nebo Storage (Firefox)
3. Vlevo: Cookies > https://www.youtube.com
4. Použij extension nebo yt-dlp příkaz (viz výše)

## 📁 Umístění cookies souboru

Bot automaticky hledá cookies v těchto umístěních (v pořadí priority):

1. `cookies.txt` (v kořenovém adresáři projektu)
2. `youtube_cookies.txt`
3. `data/cookies.txt`
4. `~/.youtube_cookies.txt`

## ✅ Ověření

Po vytvoření `cookies.txt`:

```bash
# Zkontroluj, že bot najde cookies
python3 -c "from youtube_bot import YouTubeBot; bot = YouTubeBot(); print('Cookies:', bot.cookies_file)"
```

Mělo by zobrazit cestu k cookies souboru.

## 🔄 Aktualizace cookies

Cookies expirují! Pokud bot začne selhávat:

1. Znovu exportuj cookies (přihlas se na YouTube)
2. Přepiš starý `cookies.txt`
3. Hotovo

## 🛡️ Další ochrana proti detekci

Bot už má implementováno:

- ✅ Realistický user-agent (Chrome na macOS)
- ✅ Delay mezi requesty (simulace lidského chování)
- ✅ Android client (méně restrikcí než web)
- ✅ Ignorování chyb u jednotlivých videí

## ⚠️ Důležité poznámky

1. **Cookies jsou citlivé** - necommituj je do gitu!
   - Přidej `cookies.txt` do `.gitignore`

2. **Cookies expirují** - obnovuj je pravidelně (každých 1-2 týdny)

3. **Přihlášení** - Musíš být přihlášený na YouTube při exportu cookies

4. **Oprávnění** - Na macOS může být potřeba povolit přístup k cookies v System Preferences

## 🐛 Troubleshooting

### "Operation not permitted" při čtení cookies z prohlížeče

**Řešení:** Použij export cookies do souboru (Metoda 1 nebo 2)

### Cookies nefungují

1. Zkontroluj, že jsi přihlášený na YouTube
2. Znovu exportuj cookies
3. Zkontroluj, že soubor existuje: `ls -la cookies.txt`

### Stále detekuje bot

1. Zvyš delay mezi requesty (v kódu)
2. Použij VPN/proxy
3. Zkontroluj, že cookies jsou aktuální

## 📝 Příklad použití

```python
from youtube_bot import YouTubeBot

# Bot automaticky použije cookies.txt pokud existuje
bot = YouTubeBot()

# Nebo specifikuj cestu k cookies
bot = YouTubeBot(cookies_file="cookies.txt")

# Zpracuj kanál
stats = bot.process_channel("https://www.youtube.com/@channel", max_videos=10)
```

## 🔗 Užitečné odkazy

- [yt-dlp cookies dokumentace](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Get cookies.txt LOCALLY extension](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)


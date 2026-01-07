#!/usr/bin/env python3
"""
Testovací skript pro Telegram notifikace
"""
import os
import requests

# Token a Chat ID
TOKEN = '8510205773:AAFUr4OlPshYb30KgRZuP0W0nf2WY8K-cg4'
CHAT_ID = '670619301'

def test_bot():
    """Test Telegram bota"""
    print("🔍 Testování Telegram bota...\n")
    
    # 1. Zkontrolovat info o botu
    print("1. Kontrola bota:")
    url = f'https://api.telegram.org/bot{TOKEN}/getMe'
    response = requests.get(url)
    if response.status_code == 200:
        bot_info = response.json()
        if bot_info.get('ok'):
            print(f"   ✅ Bot: {bot_info['result']['first_name']} (@{bot_info['result']['username']})")
        else:
            print(f"   ❌ Chyba: {bot_info}")
            return
    else:
        print(f"   ❌ Chyba připojení: {response.status_code}")
        return
    
    # 2. Zkontrolovat updates (zprávy)
    print("\n2. Kontrola updates:")
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    response = requests.get(url)
    if response.status_code == 200:
        updates = response.json()
        if updates.get('ok') and updates.get('result'):
            print(f"   ✅ Našel jsem {len(updates['result'])} updates")
            # Najít chat ID z poslední zprávy
            for update in reversed(updates['result']):
                if 'message' in update:
                    chat = update['message']['chat']
                    found_chat_id = str(chat.get('id'))
                    print(f"   📱 Chat ID z poslední zprávy: {found_chat_id}")
                    print(f"   👤 Uživatel: {chat.get('first_name', 'N/A')} (@{chat.get('username', 'N/A')})")
                    break
        else:
            print("   ⚠️  Žádné updates - bot ještě nedostal žádnou zprávu")
            print("   💡 Pošli /start bota v Telegramu!")
    
    # 3. Zkusit odeslat zprávu
    print("\n3. Test odeslání zprávy:")
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
        'text': '🧪 Test zpráva z Garmin Bot\n\nPokud vidíš tuto zprávu, notifikace fungují! ✅'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get('ok'):
            print("   ✅ Zpráva úspěšně odeslána!")
            print("   💡 Zkontroluj Telegram - měla by přijít zpráva")
        else:
            print(f"   ❌ Chyba: {result.get('description')}")
            if 'chat not found' in result.get('description', '').lower():
                print("   💡 Řešení:")
                print("      1. Otevři bota v Telegramu")
                print("      2. Pošli /start")
                print("      3. Zkus znovu")
    else:
        print(f"   ❌ HTTP chyba: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == '__main__':
    test_bot()


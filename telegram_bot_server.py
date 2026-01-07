#!/usr/bin/env python3
"""
Telegram bot server pro interaktivní zadání MFA kódu
Běží jako webhook server, který přijímá zprávy z Telegramu
"""
import os
import logging
import json
from flask import Flask, request, jsonify
from telegram_mfa_handler import TelegramMFAHandler

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Inicializace MFA handleru
mfa_handler = TelegramMFAHandler()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint pro Telegram"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = str(message.get('chat', {}).get('id'))
            text = message.get('text', '').strip()
            
            # Zkontrolovat, jestli je to MFA kód
            if text.startswith('/mfa '):
                code = text.replace('/mfa ', '').strip()
                if code and code.isdigit() and len(code) == 6:
                    logger.info(f"✅ MFA kód přijat z Telegramu: {'*' * len(code)}")
                    mfa_handler._store_mfa_code(code)
                    return jsonify({'ok': True, 'message': 'MFA kód uložen'})
            elif text.isdigit() and len(text) == 6:
                # Možná je to odpověď na MFA žádost
                logger.info(f"✅ MFA kód přijat z Telegramu: {'*' * len(text)}")
                mfa_handler._store_mfa_code(text)
                return jsonify({'ok': True, 'message': 'MFA kód uložen'})
        
        return jsonify({'ok': True})
        
    except Exception as e:
        logger.error(f"❌ Chyba v webhook: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


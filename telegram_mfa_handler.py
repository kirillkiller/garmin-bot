"""
Telegram bot handler pro interaktivní zadání MFA kódu
"""
import os
import logging
import json
import time
from typing import Optional
import requests

logger = logging.getLogger(__name__)

class TelegramMFAHandler:
    """Handler pro interaktivní zadání MFA kódu přes Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Inicializace handleru
        
        Args:
            bot_token: Telegram bot token (nebo z env TELEGRAM_BOT_TOKEN)
            chat_id: Telegram chat ID (nebo z env TELEGRAM_CHAT_ID)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.mfa_storage_file = os.path.expanduser('~/.garmin_mfa_code')
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  Telegram MFA handler není nakonfigurován")
            self.enabled = False
        else:
            self.enabled = True
    
    def request_mfa_code(self, date: str = None) -> Optional[str]:
        """
        Požádá o MFA kód přes Telegram a čeká na odpověď
        
        Args:
            date: Datum pro kontext (volitelné)
            
        Returns:
            MFA kód nebo None pokud timeout
        """
        if not self.enabled:
            return None
        
        # Pošli zprávu s žádostí o MFA kód
        message = f"""
🔐 <b>Garmin Bot - MFA kód vyžadován</b>

Bot potřebuje MFA kód pro přihlášení k Garmin Connect.

{f'📅 Datum: {date}' if date else ''}

💡 <b>Jak zadat MFA kód:</b>
1. Zkontroluj SMS nebo e-mail pro MFA kód
2. Odpověz na tuto zprávu s MFA kódem
3. Nebo pošli zprávu: <code>/mfa TVUJ-KOD</code>

⏱️  Mám 5 minut na zadání kódu.
"""
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': {
                    'inline_keyboard': [[
                        {'text': '❌ Zrušit', 'callback_data': 'mfa_cancel'}
                    ]]
                }
            }
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info("✅ Telegram žádost o MFA kód odeslána")
            
            # Čekat na odpověď (polling)
            return self._wait_for_mfa_response(timeout=300)  # 5 minut
            
        except Exception as e:
            logger.error(f"❌ Chyba při žádosti o MFA kód: {e}")
            return None
    
    def _wait_for_mfa_response(self, timeout: int = 300) -> Optional[str]:
        """
        Čeká na MFA kód z Telegramu pomocí polling nebo uloženého souboru
        
        Args:
            timeout: Timeout v sekundách (default: 300 = 5 minut)
            
        Returns:
            MFA kód nebo None
        """
        if not self.enabled:
            return None
        
        logger.info(f"⏳ Čekám na MFA kód z Telegramu (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_update_id = None
        
        # Zkusit načíst uložený kód (pokud už byl zadán)
        stored_code = self._get_stored_mfa_code()
        if stored_code:
            logger.info("✅ Našel jsem uložený MFA kód")
            self._clear_stored_mfa_code()
            return stored_code
        
        # Polling pro nové zprávy
        while time.time() - start_time < timeout:
            try:
                # Získat updates
                url = f"{self.api_url}/getUpdates"
                params = {
                    'timeout': 10,
                    'offset': last_update_id + 1 if last_update_id else None
                }
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        last_update_id = update.get('update_id')
                        
                        # Zkontrolovat zprávu
                        if 'message' in update:
                            message = update['message']
                            chat_id = str(message.get('chat', {}).get('id'))
                            
                            if chat_id == self.chat_id:
                                text = message.get('text', '').strip()
                                
                                # Zkontrolovat, jestli je to MFA kód
                                if text.startswith('/mfa '):
                                    code = text.replace('/mfa ', '').strip()
                                    if code and code.isdigit() and len(code) == 6:
                                        logger.info(f"✅ MFA kód přijat z Telegramu: {'*' * len(code)}")
                                        self._clear_stored_mfa_code()
                                        return code
                                elif text.isdigit() and len(text) == 6:
                                    # Možná je to odpověď na naši zprávu
                                    logger.info(f"✅ MFA kód přijat z Telegramu: {'*' * len(text)}")
                                    self._clear_stored_mfa_code()
                                    return text
                        
                        # Zkontrolovat callback (zrušit)
                        if 'callback_query' in update:
                            callback = update['callback_query']
                            if callback.get('data') == 'mfa_cancel':
                                logger.info("❌ MFA žádost zrušena uživatelem")
                                return None
                
                # Zkontrolovat, jestli se mezitím neuložil kód do souboru
                stored_code = self._get_stored_mfa_code()
                if stored_code:
                    logger.info("✅ Našel jsem uložený MFA kód (z webhooku)")
                    self._clear_stored_mfa_code()
                    return stored_code
                
                # Krátká pauza před dalším dotazem
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"⚠️  Chyba při čekání na MFA kód: {e}")
                time.sleep(5)
        
        logger.warning("⏱️  Timeout - MFA kód nebyl zadán včas")
        return None
    
    def _store_mfa_code(self, code: str):
        """Uloží MFA kód do souboru (pro případ, že by bot běžel na pozadí)"""
        try:
            with open(self.mfa_storage_file, 'w') as f:
                f.write(code)
            os.chmod(self.mfa_storage_file, 0o600)  # Jen pro vlastníka
        except Exception as e:
            logger.warning(f"⚠️  Nepodařilo se uložit MFA kód: {e}")
    
    def _get_stored_mfa_code(self) -> Optional[str]:
        """Načte uložený MFA kód ze souboru"""
        try:
            if os.path.exists(self.mfa_storage_file):
                with open(self.mfa_storage_file, 'r') as f:
                    code = f.read().strip()
                    if code and code.isdigit() and len(code) == 6:
                        return code
        except Exception:
            pass
        return None
    
    def _clear_stored_mfa_code(self):
        """Smaže uložený MFA kód"""
        try:
            if os.path.exists(self.mfa_storage_file):
                os.remove(self.mfa_storage_file)
        except Exception:
            pass
    
    def send_mfa_received_confirmation(self):
        """Pošle potvrzení, že MFA kód byl přijat"""
        if not self.enabled:
            return
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': '✅ MFA kód přijat! Bot se pokouší přihlásit...',
                'parse_mode': 'HTML'
            }
            requests.post(url, json=data, timeout=10)
        except Exception:
            pass


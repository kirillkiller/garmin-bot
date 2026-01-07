"""
Telegram notifikace pro Garmin bot
"""
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Třída pro odesílání notifikací přes Telegram"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Inicializace Telegram notifikátoru
        
        Args:
            bot_token: Telegram bot token (nebo z env TELEGRAM_BOT_TOKEN)
            chat_id: Telegram chat ID (nebo z env TELEGRAM_CHAT_ID) - může být string nebo int
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id_env = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        # Zajistit, že chat_id je integer (Telegram API vyžaduje integer)
        try:
            self.chat_id = int(chat_id_env) if chat_id_env else None
        except (ValueError, TypeError):
            self.chat_id = None
        
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  Telegram notifikace nejsou nakonfigurovány (TELEGRAM_BOT_TOKEN nebo TELEGRAM_CHAT_ID chybí)")
            self.enabled = False
        else:
            self.enabled = True
            self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
            logger.info("✅ Telegram notifikace inicializovány")
    
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Odešle zprávu přes Telegram
        
        Args:
            message: Text zprávy
            parse_mode: Formátování (HTML nebo Markdown)
            
        Returns:
            True pokud úspěšné, False jinak
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info("✅ Telegram zpráva odeslána")
            return True
            
        except Exception as e:
            logger.error(f"❌ Chyba při odesílání Telegram zprávy: {e}")
            return False
    
    def notify_mfa_required(self, date: str = None):
        """Notifikace o potřebě zadat MFA kód"""
        message = f"""
🔐 <b>Garmin Bot - MFA kód vyžadován</b>

⚠️ Bot potřebuje nový MFA kód pro přihlášení k Garmin Connect.

{f'📅 Datum: {date}' if date else ''}

💡 Zkontroluj SMS nebo e-mail a zadej MFA kód.
"""
        return self.send_message(message)
    
    def notify_sync_error(self, error: str, date: str = None):
        """Notifikace o chybě při synchronizaci"""
        message = f"""
❌ <b>Garmin Bot - Chyba synchronizace</b>

Synchronizace dat selhala!

📅 Datum: {date or 'Neznámé'}
🔴 Chyba: {error}

💡 Zkontroluj logy a oprav problém.
"""
        return self.send_message(message)
    
    def notify_sync_success(self, date: str, stats: dict = None):
        """Notifikace o úspěšné synchronizaci (volitelné)"""
        if not os.getenv('TELEGRAM_NOTIFY_SUCCESS', 'false').lower() == 'true':
            return True
        
        stats_text = ""
        if stats:
            stats_text = f"""
📊 Statistiky:
• Kroky: {stats.get('steps', 'N/A')}
• Vzdálenost: {stats.get('distance_km', 'N/A')} km
• Kalorie: {stats.get('calories_total', 'N/A')}
"""
        
        message = f"""
✅ <b>Garmin Bot - Synchronizace úspěšná</b>

📅 Datum: {date}
{stats_text}
"""
        return self.send_message(message)
    
    def notify_sync_stopped(self, reason: str = "Neznámý důvod"):
        """Notifikace o zastavení synchronizace"""
        message = f"""
🛑 <b>Garmin Bot - Synchronizace zastavena</b>

Synchronizační proces byl zastaven.

🔴 Důvod: {reason}

💡 Zkontroluj stav systému a restartuj synchronizaci.
"""
        return self.send_message(message)


"""
Garmin Connect Bot - Stahuje data z Garmin Connect a posílá je do Google Sheets
"""
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from garminconnect import Garmin
import gspread
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.auth.transport.requests import Request
import json
try:
    import garth
    GARTH_AVAILABLE = True
except ImportError:
    GARTH_AVAILABLE = False

# Telegram notifikace
try:
    from telegram_notifier import TelegramNotifier
    from telegram_mfa_handler import TelegramMFAHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    TelegramNotifier = None
    TelegramMFAHandler = None

# Nastavení logování
import pathlib

# Vytvořit adresář logs/ pokud neexistuje (pro lokální použití)
log_dir = pathlib.Path('logs')
log_dir.mkdir(exist_ok=True)

# Handlers - file handler pouze pokud adresář existuje a je zapisovatelný
handlers = [logging.StreamHandler()]
try:
    handlers.append(logging.FileHandler('logs/garmin_bot.log'))
except (OSError, PermissionError):
    # Pokud nelze vytvořit log soubor (např. na Render.com), použijeme jen console
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class GarminBot:
    """Bot pro získání dat z Garmin Connect a odeslání do Google Sheets"""
    
    def __init__(
        self,
        garmin_email: str,
        garmin_password: str,
        google_sheet_id: str,
        google_credentials_path: Optional[str] = None,
        polling_interval: int = 600,  # 10 minut
        mfa_code: Optional[str] = None  # MFA kód pro přihlášení
    ):
        """
        Inicializace bota
        
        Args:
            garmin_email: Email pro Garmin Connect
            garmin_password: Heslo pro Garmin Connect
            google_sheet_id: ID Google Sheet (z URL)
            google_credentials_path: Cesta k Google Service Account JSON (nebo None pro OAuth)
            polling_interval: Interval mezi dotazy v sekundách (default 600 = 10 min)
        """
        self.garmin_email = garmin_email
        self.garmin_password = garmin_password
        self.google_sheet_id = google_sheet_id
        self.polling_interval = polling_interval
        self.mfa_code = mfa_code
        
        # Inicializace Garmin klienta
        self.garmin_client: Optional[Garmin] = None
        
        # Inicializace Google Sheets klienta
        self.sheets_client: Optional[gspread.Client] = None
        self.sheet: Optional[gspread.Spreadsheet] = None
        
        # Telegram notifikace
        self.telegram = None
        self.telegram_mfa = None
        if TELEGRAM_AVAILABLE and TelegramNotifier:
            try:
                self.telegram = TelegramNotifier()
            except Exception as e:
                logger.warning(f"⚠️  Nepodařilo se inicializovat Telegram notifikace: {e}")
        
        # Telegram MFA handler (pro interaktivní zadání MFA kódu)
        if TELEGRAM_AVAILABLE and TelegramMFAHandler:
            try:
                self.telegram_mfa = TelegramMFAHandler()
            except Exception as e:
                logger.warning(f"⚠️  Nepodařilo se inicializovat Telegram MFA handler: {e}")
        
        # Načtení Google credentials
        self._init_google_sheets(google_credentials_path)
        
    def _init_google_sheets(self, credentials_path: Optional[str] = None):
        """Inicializuje připojení k Google Sheets"""
        try:
            # Zkusit Service Account nejdřív
            if credentials_path and os.path.exists(credentials_path):
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=scope
                )
                self.sheets_client = gspread.authorize(creds)
                logger.info("✅ Google Sheets připojeno pomocí Service Account")
            elif os.path.exists('credentials.json'):
                # Zkusit credentials.json jako Service Account
                try:
                    scope = [
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    creds = Credentials.from_service_account_file(
                        'credentials.json',
                        scopes=scope
                    )
                    self.sheets_client = gspread.authorize(creds)
                    logger.info("✅ Google Sheets připojeno pomocí Service Account (credentials.json)")
                except Exception:
                    # Pokud to není Service Account, zkusit OAuth2
                    if os.path.exists('token.json'):
                        creds = OAuthCredentials.from_authorized_user_file('token.json')
                        if creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        self.sheets_client = gspread.authorize(creds)
                        logger.info("✅ Google Sheets připojeno pomocí OAuth2")
                    else:
                        raise FileNotFoundError(
                            "Google credentials nenalezeny. "
                            "Potřebujete buď Service Account JSON (credentials.json) nebo OAuth2 token.json"
                        )
            else:
                raise FileNotFoundError(
                    "Google credentials nenalezeny. "
                    "Potřebujete buď Service Account JSON (credentials.json) nebo OAuth2 token.json"
                )
            
            # Otevření sheetu
            self.sheet = self.sheets_client.open_by_key(self.google_sheet_id)
            logger.info(f"✅ Google Sheet otevřen: {self.sheet.title}")
            
        except Exception as e:
            logger.error(f"❌ Chyba při inicializaci Google Sheets: {e}")
            raise
    
    def _init_garmin(self):
        """Inicializuje připojení k Garmin Connect s robustním ukládáním session"""
        if self.garmin_client:
            return
        
        # Zkontrolovat, jestli už máme uloženou session
        import os
        garth_dir = os.path.expanduser('~/.garth')
        tokenstore_path = None
        
        if GARTH_AVAILABLE:
            # Zkontrolovat, jestli existuje ~/.garth/ adresář s validní session
            if os.path.exists(garth_dir):
                oauth1_file = os.path.join(garth_dir, 'oauth1_token.json')
                if os.path.exists(oauth1_file) and os.path.getsize(oauth1_file) > 0:
                    tokenstore_path = garth_dir
                    logger.info("🔍 Našel jsem uloženou session v ~/.garth/")
                    logger.info("💡 Zkouším ji použít - pokud funguje, nebude potřeba MFA kód")
        
        # Delay jen pokud nemáme session (kvůli rate limiting)
        if not tokenstore_path:
            logger.info("⏳ Čekám 10 sekund před připojením k Garmin...")
            logger.info("💡 Pokud budeš vyzván k zadání MFA kódu, zkontroluj SMS nebo e-mail")
            logger.info("💡 MFA kód může přijít s malým zpožděním (až 1-2 minuty)")
            time.sleep(10)  # 10 sekund - jen krátká pauza
        else:
            logger.info("🚀 Používám uloženou session - připojuji se hned...")
        
        try:
            # Vytvořit Garmin klienta
            self.garmin_client = Garmin(self.garmin_email, self.garmin_password)
            
            # Pokud máme session, zkusit ji použít přes tokenstore parametr
            if tokenstore_path:
                try:
                    # login() s tokenstore parametrem načte session automaticky
                    logger.info("🔐 Zkouším použít uloženou session...")
                    self.garmin_client.login(tokenstore=tokenstore_path)
                    logger.info("✅ Přihlášení úspěšné pomocí uložené session!")
                    logger.info("💡 Session funguje - nebyl potřeba MFA kód")
                    # Po úspěšném přihlášení počkat chvíli (rate limiting)
                    logger.info("⏳ Čekám 15 sekund po přihlášení (rate limiting)...")
                    time.sleep(15)
                    return
                except (EOFError, Exception) as e:
                    # Session nefunguje nebo expirovala - bude potřeba nové přihlášení
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        logger.warning("⚠️  Uložená session expirovala nebo je neplatná - bude potřeba MFA kód")
                        # Notifikace o potřebě MFA
                        if self.telegram:
                            self.telegram.notify_mfa_required()
                    elif "429" in error_msg or "Too Many Requests" in error_msg:
                        logger.warning("⚠️  Rate limit - zkus to znovu za chvíli")
                        raise
                    else:
                        logger.warning(f"⚠️  Uložená session nefunguje ({type(e).__name__}) - bude potřeba MFA kód")
                    logger.info("💡 To je normální - session může expirovat po několika dnech/týdnech")
                    tokenstore_path = None  # Session nefunguje, bude potřeba nové přihlášení
            
            # Nové přihlášení - bude potřeba MFA kód
            if not tokenstore_path:
                logger.info("🔐 Přihlašuji se k Garmin Connect...")
                logger.info("💡 Zobrazí se výzva k zadání MFA kódu - zkontroluj SMS nebo e-mail")
                
                # Použít monkey patching pro input() - zachytit MFA prompt a zeptat se uživatele
                import builtins
                import sys
                original_input = builtins.input
                mfa_code_used = False
                
                def mock_input(prompt=""):
                    nonlocal mfa_code_used
                    # Pokud je to MFA prompt a ještě jsme nepoužili kód
                    if not mfa_code_used:
                        # Zkontrolovat, jestli je to MFA prompt (může být prázdný nebo obsahovat "MFA"/"code")
                        is_mfa_prompt = (
                            "MFA" in prompt.upper() or 
                            "code" in prompt.lower() or 
                            prompt.strip() == "" or
                            "MFA code:" in prompt
                        )
                        
                        if is_mfa_prompt:
                            mfa_code_used = True
                            # Notifikace o potřebě MFA kódu
                            if self.telegram:
                                self.telegram.notify_mfa_required()
                            
                            # Pokud máme MFA kód z argumentu nebo env, použij ho
                            mfa_from_env = os.getenv('GARMIN_MFA_CODE')
                            if self.mfa_code:
                                logger.info(f"✅ Používám poskytnutý MFA kód: {self.mfa_code}")
                                return self.mfa_code
                            elif mfa_from_env:
                                logger.info(f"✅ Používám MFA kód z environment variable")
                                return mfa_from_env
                            
                            # Zkusit získat MFA kód přes Telegram (pokud je dostupný)
                            if self.telegram_mfa and self.telegram_mfa.enabled:
                                logger.info("📱 Žádám MFA kód přes Telegram...")
                                telegram_code = self.telegram_mfa.request_mfa_code()
                                if telegram_code:
                                    logger.info(f"✅ MFA kód přijat z Telegramu: {'*' * len(telegram_code)}")
                                    if self.telegram_mfa:
                                        self.telegram_mfa.send_mfa_received_confirmation()
                                    return telegram_code
                                else:
                                    logger.warning("⚠️  MFA kód nebyl zadán přes Telegram včas")
                            
                            # Jinak se zeptat uživatele interaktivně (pouze pokud je TTY)
                            if sys.stdin.isatty():
                                logger.info("")
                                logger.info("=" * 60)
                                logger.info("🔐 MFA KÓD JE POTŘEBNÝ")
                                logger.info("=" * 60)
                                logger.info("💡 Zkontroluj SMS nebo e-mail pro MFA kód")
                                logger.info("💡 Zadej MFA kód:")
                                sys.stdout.flush()  # Zajistit, že se zpráva zobrazí
                                code = original_input("MFA code: ")
                                logger.info(f"✅ MFA kód přijat: {'*' * len(code)}")
                                return code
                            else:
                                # Není TTY a Telegram MFA nefunguje - vyhodit chybu
                                error_msg = "MFA kód je potřeba, ale není dostupný interaktivní vstup ani Telegram MFA handler."
                                logger.error(f"❌ {error_msg}")
                                if self.telegram:
                                    self.telegram.send_message(
                                        f"🔐 <b>MFA kód vyžadován</b>\n\n"
                                        f"Bot potřebuje MFA kód, ale nemůže ho získat automaticky.\n\n"
                                        f"💡 <b>Řešení:</b>\n"
                                        f"1. Zkontroluj SMS/e-mail pro MFA kód\n"
                                        f"2. Odpověz na tuto zprávu s MFA kódem\n"
                                        f"3. Nebo přidej do Render environment variables:\n"
                                        f"   <code>GARMIN_MFA_CODE=tvuj-kod</code>\n"
                                        f"4. Bot se znovu spustí a použije kód\n"
                                        f"5. Session se uloží a příště už nebude potřeba"
                                    )
                                raise Exception(error_msg)
                    # Pro ostatní input() volání použít originální funkci
                    return original_input(prompt)
                
                builtins.input = mock_input
                try:
                    self.garmin_client.login()
                    logger.info("✅ Přihlášení úspěšné!")
                finally:
                    builtins.input = original_input
                
                # Po úspěšném přihlášení uložit session explicitně přes garth
                if GARTH_AVAILABLE:
                    try:
                        garth_dir = os.path.expanduser('~/.garth')
                        os.makedirs(garth_dir, exist_ok=True)
                        
                        # garminconnect používá self.garmin_client.garth - získat ho přímo
                        if hasattr(self.garmin_client, 'garth'):
                            garth_client = self.garmin_client.garth
                            
                            # Ověřit, že garth_client má tokeny před uložením
                            oauth1 = getattr(garth_client, 'oauth1_token', None)
                            oauth2 = getattr(garth_client, 'oauth2_token', None)
                            
                            if oauth1 or oauth2:
                                # Uložit session pomocí dump() metody
                                garth_client.dump(garth_dir)
                                logger.info("✅ Session byla explicitně uložena do ~/.garth/")
                                logger.info("💡 Příště nebude potřeba MFA kód (pokud session neexpiruje)")
                                logger.info(f"💡 Session je uložena v: {garth_dir}")
                                
                                # Ověřit, že soubory nejsou prázdné
                                oauth1_file = os.path.join(garth_dir, 'oauth1_token.json')
                                oauth2_file = os.path.join(garth_dir, 'oauth2_token.json')
                                if os.path.exists(oauth1_file) and os.path.getsize(oauth1_file) > 0:
                                    logger.info("✅ oauth1_token.json byl úspěšně uložen")
                                else:
                                    logger.warning("⚠️  oauth1_token.json je prázdný nebo neexistuje")
                                if os.path.exists(oauth2_file) and os.path.getsize(oauth2_file) > 0:
                                    logger.info("✅ oauth2_token.json byl úspěšně uložen")
                                else:
                                    logger.warning("⚠️  oauth2_token.json je prázdný nebo neexistuje")
                            else:
                                logger.warning("⚠️  garth_client nemá tokeny - nelze uložit session")
                                logger.info("💡 Zkus to znovu - tokeny by se měly nastavit po úspěšném přihlášení")
                        else:
                            logger.warning("⚠️  garmin_client nemá garth atribut - session se neuloží")
                            logger.info("💡 Zkus to znovu - garminconnect by měl automaticky uložit session")
                    except Exception as e:
                        logger.warning(f"⚠️  Chyba při ukládání session: {e}")
                        import traceback
                        logger.debug(f"Traceback: {traceback.format_exc()}")
                        logger.info("💡 Session by se měla uložit automaticky - zkus to znovu při dalším spuštění")
            
            logger.info("✅ Připojeno k Garmin Connect")
            # Po úspěšném přihlášení počkat chvíli (rate limiting)
            logger.info("⏳ Čekám 15 sekund po přihlášení (rate limiting)...")
            time.sleep(15)
            return
        except EOFError:
            # Pokud došlo k EOF, zkusit znovu s informativní zprávou
            logger.warning("⚠️  MFA kód je potřeba. Spusť skript interaktivně v terminálu.")
            logger.info("💡 Tip: Spusť 'python3 garmin_bot.py --once' přímo v terminálu (ne přes skript)")
            logger.info("💡 Po prvním úspěšném přihlášení se session uloží a další spuštění budou bez MFA")
            raise
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                logger.error(f"❌ Rate limit (429) při přihlášení: {e}")
                logger.error("💡 Garmin má velmi přísný rate limiting")
                logger.error("💡 POČKEJ 10-15 MINUT a zkus to znovu")
                logger.error("💡 Nebo zkus zítra - Garmin může mít denní limit")
                raise
            else:
                logger.error(f"❌ Chyba při připojení k Garmin Connect: {e}")
                raise
    
    def get_garmin_data(self, date: str) -> Dict[str, Any]:
        """
        Získá data z Garmin Connect pro dané datum s retry logikou
        
        Args:
            date: Datum ve formátu YYYY-MM-DD
            
        Returns:
            Slovník s daty z Garmin
        """
        if not self.garmin_client:
            self._init_garmin()
        
        max_retries = 5  # Zvýšeno z 3 na 5
        base_retry_delay = 10  # Základní delay 10 sekund
        
        for attempt in range(max_retries):
            try:
                return self._fetch_garmin_data(date)
            except Exception as e:
                error_str = str(e)
                error_type = type(e).__name__
                
                # Detekce síťových chyb
                is_network_error = (
                    "Connection reset" in error_str or
                    "Connection aborted" in error_str or
                    "ConnectionResetError" in error_str or
                    "ConnectionError" in error_str or
                    "Timeout" in error_str or
                    "timeout" in error_str.lower() or
                    "ECONNRESET" in error_str or
                    "Broken pipe" in error_str
                )
                
                # Detekce rate limiting
                is_rate_limit = (
                    "429" in error_str or
                    "Too Many Requests" in error_str or
                    "rate limit" in error_str.lower()
                )
                
                # Pokud je to síťová chyba nebo rate limit, zkusit znovu
                if (is_network_error or is_rate_limit) and attempt < max_retries - 1:
                    # Exponenciální backoff: 10s, 20s, 40s, 80s, 160s
                    wait_time = base_retry_delay * (2 ** attempt)
                    
                    if is_network_error:
                        logger.warning(f"⚠️  Síťová chyba pro {date} (pokus {attempt + 1}/{max_retries}): {error_str}")
                        logger.info(f"⏳ Čekám {wait_time} sekund před dalším pokusem...")
                    else:
                        logger.warning(f"⚠️  Rate limit (429) pro {date} (pokus {attempt + 1}/{max_retries})")
                        logger.info(f"⏳ Čekám {wait_time} sekund před dalším pokusem...")
                    
                    time.sleep(wait_time)
                    continue
                else:
                    # Jiná chyba nebo dosažen max počet pokusů
                    logger.error(f"❌ Chyba při získávání dat z Garmin pro {date} (pokus {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        # Ještě jeden pokus s kratší pauzou
                        wait_time = base_retry_delay
                        logger.info(f"⏳ Čekám {wait_time} sekund před dalším pokusem...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise
        
        # Tohle by se nemělo nikdy stát, ale pro jistotu
        raise Exception("Nepodařilo se získat data po několika pokusech")
    
    def _fetch_garmin_data(self, date: str) -> Dict[str, Any]:
        """
        Vnitřní metoda pro získání dat z Garmin Connect
        
        Args:
            date: Datum ve formátu YYYY-MM-DD
            
        Returns:
            Slovník s daty z Garmin
        """
        try:
            # Získání statistik (vrací dict s klíči jako totalSteps, totalDistanceMeters, atd.)
            stats = self.garmin_client.get_stats(date)
            
            # Získání body battery (vrací list s dict)
            body_battery_list = []
            try:
                body_battery_list = self.garmin_client.get_body_battery(date)
            except Exception:
                pass
            
            # Extrakce body battery hodnot (první prvek z listu pokud existuje)
            body_battery = body_battery_list[0] if body_battery_list and isinstance(body_battery_list, list) else {}
            
            # Získání dalších dat
            stress_data = {}
            try:
                stress_data = self.garmin_client.get_stress_data(date)
            except Exception:
                pass
            
            # Získání HRV dat (Heart Rate Variability)
            hrv_data = {}
            try:
                hrv_data = self.garmin_client.get_hrv_data(date)
                # Debug: zkontrolovat strukturu HRV dat
                if hrv_data:
                    logger.info(f"🔍 HRV data type: {type(hrv_data)}")
                    if isinstance(hrv_data, dict):
                        logger.info(f"🔍 HRV keys: {list(hrv_data.keys())}")
                        # Vytisknout celou strukturu pro debug
                        import json
                        logger.info(f"🔍 HRV data structure: {json.dumps(hrv_data, indent=2, default=str)[:1000]}")
                    elif isinstance(hrv_data, list) and len(hrv_data) > 0:
                        logger.info(f"🔍 HRV list length: {len(hrv_data)}, first item keys: {list(hrv_data[0].keys()) if isinstance(hrv_data[0], dict) else 'not dict'}")
            except Exception as e:
                logger.warning(f"⚠️ HRV data error: {e}")
                pass
            
            # Získání sleep dat (detailní data o spánku)
            sleep_data = {}
            try:
                sleep_data = self.garmin_client.get_sleep_data(date)
                # Debug: zkontrolovat strukturu Sleep dat
                if sleep_data:
                    logger.info(f"🔍 Sleep data type: {type(sleep_data)}")
                    if isinstance(sleep_data, dict):
                        logger.info(f"🔍 Sleep keys: {list(sleep_data.keys())}")
                        # Vytisknout celou strukturu pro debug
                        import json
                        logger.info(f"🔍 Sleep data structure: {json.dumps(sleep_data, indent=2, default=str)[:1000]}")
                    elif isinstance(sleep_data, list) and len(sleep_data) > 0:
                        logger.info(f"🔍 Sleep list length: {len(sleep_data)}, first item keys: {list(sleep_data[0].keys()) if isinstance(sleep_data[0], dict) else 'not dict'}")
            except Exception as e:
                logger.warning(f"⚠️ Sleep data error: {e}")
                pass
            
            # Debug: zkontrolovat sleep klíče v stats
            sleep_keys_in_stats = [k for k in stats.keys() if 'sleep' in k.lower()]
            if sleep_keys_in_stats:
                logger.info(f"🔍 Sleep-related keys in stats: {sleep_keys_in_stats}")
                for key in sleep_keys_in_stats:
                    logger.info(f"🔍   {key}: {stats.get(key)}")
            
            # Získání respiration dat (detailní data o dýchání)
            respiration_data = {}
            try:
                respiration_data = self.garmin_client.get_respiration_data(date)
            except Exception:
                pass
            
            # Získání heart rates dat (detailní data o tepu)
            heart_rates_data = {}
            try:
                heart_rates_data = self.garmin_client.get_heart_rates(date)
            except Exception:
                pass
            
            # Získání aktivit pro daný den
            activities = []
            try:
                activities = self.garmin_client.get_activities_by_date(date, date)
            except Exception:
                try:
                    activities = self.garmin_client.get_activities_fordate(date)
                except Exception:
                    pass
            
            # Získání training readiness a status
            training_readiness = {}
            training_status = {}
            try:
                training_readiness = self.garmin_client.get_training_readiness(date)
            except Exception:
                pass
            try:
                training_status = self.garmin_client.get_training_status(date)
            except Exception:
                pass
            
            # Získání dalších metrik
            endurance_score = {}
            hill_score = {}
            blood_pressure = {}
            hydration_data = {}
            body_composition = {}
            weigh_ins = []
            daily_weigh_ins = []
            spo2_data = {}
            max_metrics = {}
            
            try:
                endurance_score = self.garmin_client.get_endurance_score(date)
            except Exception:
                pass
            try:
                hill_score = self.garmin_client.get_hill_score(date)
            except Exception:
                pass
            try:
                blood_pressure = self.garmin_client.get_blood_pressure(date)
            except Exception:
                pass
            try:
                hydration_data = self.garmin_client.get_hydration_data(date)
            except Exception:
                pass
            try:
                body_composition = self.garmin_client.get_body_composition(date)
            except Exception:
                pass
            try:
                # get_weigh_ins() potřebuje startdate a enddate
                weigh_ins = self.garmin_client.get_weigh_ins(date, date)
            except Exception:
                pass
            try:
                daily_weigh_ins = self.garmin_client.get_daily_weigh_ins(date)
            except Exception:
                pass
            try:
                spo2_data = self.garmin_client.get_spo2_data(date)
            except Exception:
                pass
            # Max Metrics - zkusit z get_max_metrics nebo z training_status
            max_metrics = None
            try:
                max_metrics = self.garmin_client.get_max_metrics(date)
            except Exception:
                pass
            
            # Pokud max_metrics je prázdný, zkusit z training_status.mostRecentVO2Max
            vo2_max_val = None
            fitness_age_val = None
            
            # Zkusit z training_status nejdřív
            if isinstance(training_status, dict):
                most_recent_vo2 = training_status.get('mostRecentVO2Max', {})
                if isinstance(most_recent_vo2, dict):
                    # Zkusit generic nebo cycling - musí být číslo, ne dict
                    generic_val = most_recent_vo2.get('generic')
                    cycling_val = most_recent_vo2.get('cycling')
                    if isinstance(generic_val, (int, float)):
                        vo2_max_val = generic_val
                    elif isinstance(cycling_val, (int, float)):
                        vo2_max_val = cycling_val
                    
                    # Fitness věk může být v heatAltitudeAcclimation nebo jinde
                    heat_alt = most_recent_vo2.get('heatAltitudeAcclimation', {})
                    if isinstance(heat_alt, dict):
                        age_val = heat_alt.get('fitnessAge') or heat_alt.get('age')
                        if isinstance(age_val, (int, float)):
                            fitness_age_val = age_val
            
            # Pokud stále nemáme hodnoty, použít max_metrics
            if vo2_max_val is None:
                if isinstance(max_metrics, dict):
                    vo2_val = max_metrics.get('vo2Max') or max_metrics.get('vo2')
                    # Zajistit, že je to číslo, ne dict
                    if isinstance(vo2_val, (int, float)):
                        vo2_max_val = vo2_val
                elif isinstance(max_metrics, list) and len(max_metrics) > 0:
                    # Pokud je to list, zkusit z prvního prvku
                    first_item = max_metrics[0]
                    if isinstance(first_item, dict):
                        vo2_val = first_item.get('vo2Max') or first_item.get('vo2') or first_item.get('vo2MaxValue')
                        if isinstance(vo2_val, (int, float)):
                            vo2_max_val = vo2_val
            
            if fitness_age_val is None:
                if isinstance(max_metrics, dict):
                    age_val = max_metrics.get('fitnessAge') or max_metrics.get('age')
                    # Zajistit, že je to číslo, ne dict
                    if isinstance(age_val, (int, float)):
                        fitness_age_val = age_val
                elif isinstance(max_metrics, list) and len(max_metrics) > 0:
                    # Pokud je to list, zkusit z prvního prvku
                    first_item = max_metrics[0]
                    if isinstance(first_item, dict):
                        age_val = first_item.get('fitnessAge') or first_item.get('age') or first_item.get('fitnessAgeValue')
                        if isinstance(age_val, (int, float)):
                            fitness_age_val = age_val
            
            # Extrakce všech dostupných metrik ze stats (podle skutečné struktury API)
            data = {
                # Základní info
                'date': date,
                'timestamp': datetime.now().isoformat(),
                
                # Aktivita
                'steps': stats.get('totalSteps', 0) or 0,
                'step_goal': stats.get('dailyStepGoal', 0) or 0,
                'distance_km': round((stats.get('totalDistanceMeters', 0) or 0) / 1000, 2),
                'floors_ascended': round(stats.get('floorsAscended', 0) or 0, 0),
                'floors_descended': round(stats.get('floorsDescended', 0) or 0, 0),
                'floors_goal': stats.get('userFloorsAscendedGoal', 0) or 0,
                
                # Kalorie
                'calories_total': stats.get('totalKilocalories', 0) or 0,
                'calories_active': stats.get('activeKilocalories', 0) or 0,
                'calories_bmr': stats.get('bmrKilocalories', 0) or 0,
                
                # Tepová frekvence
                'heart_rate_resting': stats.get('restingHeartRate', 0) or 0,
                'heart_rate_avg_7d': stats.get('lastSevenDaysAvgRestingHeartRate', 0) or 0,
                'heart_rate_min': stats.get('minHeartRate', 0) or 0,
                'heart_rate_max': stats.get('maxHeartRate', 0) or 0,
                'heart_rate_min_avg': stats.get('minAvgHeartRate', 0) or 0,
                'heart_rate_max_avg': stats.get('maxAvgHeartRate', 0) or 0,
                
                # Stres
                'stress_avg': stats.get('averageStressLevel', 0) or 0,
                'stress_max': stats.get('maxStressLevel', 0) or 0,
                'stress_duration': round((stats.get('stressDuration', 0) or 0) / 60, 1),  # minuty
                'stress_rest_duration': round((stats.get('restStressDuration', 0) or 0) / 60, 1),
                'stress_activity_duration': round((stats.get('activityStressDuration', 0) or 0) / 60, 1),
                'stress_total_duration': round((stats.get('totalStressDuration', 0) or 0) / 60, 1),
                'stress_low_duration': round((stats.get('lowStressDuration', 0) or 0) / 60, 1),
                'stress_medium_duration': round((stats.get('mediumStressDuration', 0) or 0) / 60, 1),
                'stress_high_duration': round((stats.get('highStressDuration', 0) or 0) / 60, 1),
                'stress_percentage': round(stats.get('stressPercentage', 0) or 0, 2),
                
                # Body Battery
                'body_battery_charged': body_battery.get('charged', 0) or stats.get('bodyBatteryChargedValue', 0) or 0,
                'body_battery_drained': body_battery.get('drained', 0) or stats.get('bodyBatteryDrainedValue', 0) or 0,
                'body_battery_highest': stats.get('bodyBatteryHighestValue', 0) or 0,
                'body_battery_lowest': stats.get('bodyBatteryLowestValue', 0) or 0,
                'body_battery_most_recent': stats.get('bodyBatteryMostRecentValue', 0) or 0,
                'body_battery_during_sleep': stats.get('bodyBatteryDuringSleep', 0) or 0,
                'body_battery_at_wake': stats.get('bodyBatteryAtWakeTime', 0) or 0,
                
                # Kyslík v krvi (SpO2)
                'spo2_avg': stats.get('averageSpo2', 0) or 0,
                'spo2_lowest': stats.get('lowestSpo2', 0) or 0,
                'spo2_latest': stats.get('latestSpo2', 0) or 0,
                
                # Dýchání
                'respiration_avg_waking': stats.get('avgWakingRespirationValue', 0) or 0,
                'respiration_highest': stats.get('highestRespirationValue', 0) or 0,
                'respiration_lowest': stats.get('lowestRespirationValue', 0) or 0,
                'respiration_latest': stats.get('latestRespirationValue', 0) or 0,
                
                # Čas aktivity (sekundy -> minuty)
                'time_highly_active': round((stats.get('highlyActiveSeconds', 0) or 0) / 60, 1),
                'time_active': round((stats.get('activeSeconds', 0) or 0) / 60, 1),
                'time_sedentary': round((stats.get('sedentarySeconds', 0) or 0) / 60, 1),
                'time_sleeping': round((stats.get('sleepingSeconds', 0) or 0) / 60, 1),
                'time_awake': round((stats.get('measurableAwakeDuration', 0) or 0) / 60, 1),
                'time_asleep': round((stats.get('measurableAsleepDuration', 0) or 0) / 60, 1),
                
                # Intenzita cvičení
                'intensity_moderate_min': stats.get('moderateIntensityMinutes', 0) or 0,
                'intensity_vigorous_min': stats.get('vigorousIntensityMinutes', 0) or 0,
                'intensity_goal_min': stats.get('intensityMinutesGoal', 0) or 0,
            }
            
            # HRV (Heart Rate Variability) - variabilita srdečního tepu
            # HRV data obsahují hrvSummary a hrvReadings
            hrv_summary = {}
            hrv_readings = []
            if isinstance(hrv_data, dict):
                hrv_summary = hrv_data.get('hrvSummary', {})
                hrv_readings = hrv_data.get('hrvReadings', [])
            elif isinstance(hrv_data, list) and len(hrv_data) > 0:
                if isinstance(hrv_data[0], dict):
                    hrv_summary = hrv_data[0].get('hrvSummary', hrv_data[0])
                    hrv_readings = hrv_data[0].get('hrvReadings', [])
            
            # HRV hodnoty z hrvSummary - pokud nejsou data, vrátit None (ne 0)
            hrv_last_night = None
            if isinstance(hrv_summary, dict) and hrv_summary.get('lastNightAvg') is not None:
                hrv_last_night = hrv_summary.get('lastNightAvg')
            
            hrv_weekly = None
            if isinstance(hrv_summary, dict) and hrv_summary.get('weeklyAvg') is not None:
                hrv_weekly = hrv_summary.get('weeklyAvg')
            
            # HRV max/min z hrvReadings (seznam hodnot)
            hrv_values = []
            if isinstance(hrv_readings, list):
                hrv_values = [r.get('hrvValue') for r in hrv_readings if isinstance(r, dict) and r.get('hrvValue') is not None]
            
            hrv_max_val = max(hrv_values) if hrv_values else None
            hrv_min_val = min(hrv_values) if hrv_values else None
            hrv_avg_val = round(sum(hrv_values) / len(hrv_values), 1) if hrv_values else None
            
            # Sleep (Spánek) - detailní data
            # Sleep data obsahují dailySleepDTO s detailními informacemi
            daily_sleep = {}
            sleep_stress_data = {}
            sleep_heart_rate_data = {}
            if isinstance(sleep_data, dict):
                daily_sleep = sleep_data.get('dailySleepDTO', {})
                if not daily_sleep:
                    daily_sleep = sleep_data.get('sleepSummary', {})
                    if not daily_sleep:
                        daily_sleep = sleep_data
                # Sleep stress a heart rate jsou v samostatných klíčích
                sleep_stress_data = sleep_data.get('sleepStress', {})
                sleep_heart_rate_data = sleep_data.get('sleepHeartRate', {})
                
                # Debug: zkontrolovat, co obsahují sleepStress a sleepScore
                if sleep_stress_data:
                    logger.info(f"🔍 sleepStress exists, type: {type(sleep_stress_data)}")
                    if isinstance(sleep_stress_data, list):
                        logger.info(f"🔍 sleepStress is list with {len(sleep_stress_data)} items")
                        import json
                        logger.info(f"🔍 sleepStress FULL CONTENT: {json.dumps(sleep_stress_data, indent=2, default=str)}")
                        if len(sleep_stress_data) > 0:
                            logger.info(f"🔍 First sleepStress item type: {type(sleep_stress_data[0])}")
                            logger.info(f"🔍 First sleepStress item: {sleep_stress_data[0]}")
                            if isinstance(sleep_stress_data[0], dict):
                                logger.info(f"🔍 First sleepStress item keys: {list(sleep_stress_data[0].keys())}")
                    elif isinstance(sleep_stress_data, dict):
                        logger.info(f"🔍 sleepStress keys: {list(sleep_stress_data.keys())}")
                        logger.info(f"🔍 sleepStress content: {sleep_stress_data}")
                
                # Zkusit najít sleep score v různých místech
                sleep_score_obj = sleep_data.get('sleepScore')
                if sleep_score_obj is None:
                    # Zkusit v dailySleepDTO - může být 'sleepScores' (plural) nebo 'sleepScore'
                    sleep_score_obj = (daily_sleep.get('sleepScores') or 
                                     daily_sleep.get('sleepScore') or 
                                     daily_sleep.get('overallSleepScore'))
                if sleep_score_obj is None:
                    # Zkusit v jiných klíčích
                    for key in ['sleepScore', 'sleepScores', 'overallSleepScore', 'score', 'sleep_score']:
                        if key in sleep_data:
                            sleep_score_obj = sleep_data[key]
                            logger.info(f"🔍 Found sleep score in key '{key}': {sleep_score_obj}")
                            break
                
                if sleep_score_obj is not None:
                    logger.info(f"🔍 sleepScore exists, type: {type(sleep_score_obj)}, value: {sleep_score_obj}")
                else:
                    logger.info("🔍 sleepScore is None or not found - checking all sleep_data keys...")
                    # Zkontrolovat všechny klíče, které obsahují "score"
                    score_keys = [k for k in sleep_data.keys() if 'score' in k.lower()]
                    if score_keys:
                        logger.info(f"🔍 Keys with 'score' in sleep_data: {score_keys}")
                    # Zkontrolovat dailySleepDTO klíče
                    score_keys_dto = [k for k in daily_sleep.keys() if 'score' in k.lower()]
                    if score_keys_dto:
                        logger.info(f"🔍 Keys with 'score' in dailySleepDTO: {score_keys_dto}")
            elif isinstance(sleep_data, list) and len(sleep_data) > 0:
                if isinstance(sleep_data[0], dict):
                    daily_sleep = sleep_data[0].get('dailySleepDTO', sleep_data[0])
                    sleep_stress_data = sleep_data[0].get('sleepStress', {})
                    sleep_heart_rate_data = sleep_data[0].get('sleepHeartRate', {})
            
            # Sleep hodnoty z dailySleepDTO - pokud nebyl spánek, vrátit None (ne 0)
            sleep_duration_sec = None
            sleep_awake_sec = None
            sleep_light_sec = None
            sleep_deep_sec = None
            sleep_rem_sec = None
            if isinstance(daily_sleep, dict) and daily_sleep.get('sleepTimeSeconds') is not None:
                sleep_duration_sec = daily_sleep.get('sleepTimeSeconds')
                sleep_awake_sec = daily_sleep.get('awakeSleepSeconds')
                sleep_light_sec = daily_sleep.get('lightSleepSeconds')
                sleep_deep_sec = daily_sleep.get('deepSleepSeconds')
                sleep_rem_sec = daily_sleep.get('remSleepSeconds')
            
            # Sleep score a další hodnoty - mohou být v různých místech
            # Zkusit dailySleepDTO, sleepStress, nebo přímo v sleep_data
            # Pokud nejsou data, vrátit None (ne 0)
            sleep_score_val = None
            if isinstance(sleep_data, dict):
                # Sleep score může být v různých formátech - zkusit všechny možnosti
                # Nejdřív zkusit v dailySleepDTO - může být 'sleepScores' (dict) nebo 'sleepScore' (číslo)
                sleep_scores_obj = daily_sleep.get('sleepScores')
                if sleep_scores_obj:
                    logger.info(f"🔍 Found sleepScores, type: {type(sleep_scores_obj)}")
                    import json
                    logger.info(f"🔍 sleepScores content (first 1000 chars): {json.dumps(sleep_scores_obj, indent=2, default=str)[:1000]}")
                    if isinstance(sleep_scores_obj, dict):
                        # sleepScores může mít strukturu: sleepScores.get('overall', {}).get('value', 0)
                        # nebo může být přímo hodnota v různých klíčích
                        overall_obj = sleep_scores_obj.get('overall')
                        if overall_obj and isinstance(overall_obj, dict):
                            sleep_score_val = (overall_obj.get('value') or overall_obj.get('score'))
                            logger.info(f"🔍 Extracted sleep score from sleepScores.overall: {sleep_score_val}")
                        else:
                            # Zkusit přímo v sleepScores dict
                            sleep_score_val = (sleep_scores_obj.get('value') or 
                                             sleep_scores_obj.get('score') or 
                                             sleep_scores_obj.get('overall') or
                                             sleep_scores_obj.get('overallSleepScore') or
                                             sleep_scores_obj.get('total') or
                                             sleep_scores_obj.get('totalSleepScore'))
                            logger.info(f"🔍 Extracted sleep score from sleepScores dict: {sleep_score_val}")
                    elif isinstance(sleep_scores_obj, (int, float)):
                        sleep_score_val = sleep_scores_obj
                        logger.info(f"🔍 sleepScores is number: {sleep_score_val}")
                
                # Pokud stále None, zkusit přímo sleepScore jako číslo
                if sleep_score_val is None:
                    sleep_score_obj = (daily_sleep.get('sleepScore') if isinstance(daily_sleep, dict) else None) or \
                                     (sleep_data.get('sleepScore') if isinstance(sleep_data, dict) else None) or \
                                     (daily_sleep.get('overallSleepScore') if isinstance(daily_sleep, dict) else None)
                    if sleep_score_obj is not None:
                        if isinstance(sleep_score_obj, dict):
                            sleep_score_val = (sleep_score_obj.get('value') or 
                                             sleep_score_obj.get('score'))
                        elif isinstance(sleep_score_obj, (int, float)):
                            sleep_score_val = sleep_score_obj
                        logger.info(f"🔍 Extracted sleep score from sleepScore: {sleep_score_val}")
            
            # Sleep quality - pokud nejsou data, vrátit None (ne 0)
            sleep_quality = None
            if isinstance(daily_sleep, dict):
                sleep_quality = (daily_sleep.get('sleepQualityScore') or 
                               daily_sleep.get('qualityScore') or
                               daily_sleep.get('sleepQualityTypePK'))
                # Pokud je 0, zkontrolovat jestli to není skutečná nula nebo chybějící data
                # sleepQualityTypePK může být 0 jako skutečná hodnota, ale pokud je None, data nejsou k dispozici
                if sleep_quality == 0 and daily_sleep.get('sleepQualityScore') is None and daily_sleep.get('qualityScore') is None:
                    # Pokud sleepQualityTypePK je 0, ale ostatní klíče jsou None, zkontrolovat jestli sleepQualityTypePK existuje
                    if daily_sleep.get('sleepQualityTypePK') is None:
                        sleep_quality = None  # Data nejsou k dispozici
                    # Jinak sleep_quality zůstane 0 (skutečná nula)
            
            # Sleep stress - může být v sleepStress jako list, dict nebo přímo hodnota
            # Pokud nejsou data, vrátit None (ne 0)
            sleep_stress = None
            if isinstance(sleep_stress_data, list) and sleep_stress_data:
                # sleepStress je list - zkusit extrahovat průměrnou hodnotu nebo první prvek
                logger.info(f"🔍 sleepStress is list with {len(sleep_stress_data)} items")
                # Zkusit najít průměrnou hodnotu v listu
                stress_values = []
                for item in sleep_stress_data:
                    if isinstance(item, dict):
                        # Zkusit různé klíče
                        val = (item.get('value') or item.get('stressLevel') or 
                              item.get('averageStressLevel') or item.get('avgStress') or
                              item.get('stress') or item.get('level'))
                        if val is not None:
                            stress_values.append(val)
                    elif isinstance(item, (int, float)):
                        stress_values.append(item)
                
                if stress_values:
                    sleep_stress = round(sum(stress_values) / len(stress_values), 1)
                    logger.info(f"🔍 Calculated sleep stress from list: {sleep_stress}")
                else:
                    # Pokud list obsahuje dicty bez hodnot, zkusit první prvek
                    if isinstance(sleep_stress_data[0], dict):
                        logger.info(f"🔍 First sleepStress item: {sleep_stress_data[0]}")
            elif isinstance(sleep_stress_data, dict) and sleep_stress_data:
                # Debug: zkontrolovat sleep stress strukturu
                logger.info(f"🔍 Sleep stress data type: {type(sleep_stress_data)}, keys: {list(sleep_stress_data.keys())}")
                logger.info(f"🔍 Sleep stress data content: {sleep_stress_data}")
                
                # sleepStress může obsahovat různé hodnoty
                sleep_stress = (sleep_stress_data.get('averageStressLevel') or 
                              sleep_stress_data.get('avgStress') or
                              sleep_stress_data.get('value') or
                              sleep_stress_data.get('average') or
                              sleep_stress_data.get('stressAvg') or
                              sleep_stress_data.get('avg'))
            elif isinstance(sleep_stress_data, (int, float)):
                sleep_stress = sleep_stress_data
            else:
                # Zkusit v dailySleepDTO nebo přímo v sleep_data
                sleep_stress = (daily_sleep.get('averageStressDuringSleep') if isinstance(daily_sleep, dict) else None) or \
                              (sleep_data.get('averageStressDuringSleep') if isinstance(sleep_data, dict) else None)
            
            # Debug: zkontrolovat výsledné hodnoty
            logger.info(f"🔍 Sleep score: {sleep_score_val}, quality: {sleep_quality}, stress: {sleep_stress}")
            
            # Sleep start/end timestamps
            sleep_start_ts = daily_sleep.get('sleepStartTimestampGMT') or daily_sleep.get('sleepStartTimestampLocal')
            sleep_end_ts = daily_sleep.get('sleepEndTimestampGMT') or daily_sleep.get('sleepEndTimestampLocal')
            
            # Převod timestamp na string (pokud je číslo, převést na ISO string)
            if sleep_start_ts:
                if isinstance(sleep_start_ts, (int, float)):
                    # Timestamp je v milisekundách, převést na sekundy
                    ts_seconds = sleep_start_ts / 1000 if sleep_start_ts > 1000000000000 else sleep_start_ts
                    sleep_start_val = datetime.fromtimestamp(ts_seconds).isoformat()
                else:
                    sleep_start_val = str(sleep_start_ts)
            else:
                sleep_start_val = ''
            
            if sleep_end_ts:
                if isinstance(sleep_end_ts, (int, float)):
                    # Timestamp je v milisekundách, převést na sekundy
                    ts_seconds = sleep_end_ts / 1000 if sleep_end_ts > 1000000000000 else sleep_end_ts
                    sleep_end_val = datetime.fromtimestamp(ts_seconds).isoformat()
                else:
                    sleep_end_val = str(sleep_end_ts)
            else:
                sleep_end_val = ''
            
            # Respiration (Dýchání) - detailní data
            # API vrací: avgWakingRespirationValue, avgSleepRespirationValue, lowestRespirationValue, highestRespirationValue
            # Pokud nejsou data, vrátit None (ne 0)
            respiration_avg_val = None
            respiration_max_val = None
            respiration_min_val = None
            if isinstance(respiration_data, dict):
                # Použít avgSleepRespirationValue nebo avgWakingRespirationValue
                respiration_avg_val = (respiration_data.get('avgSleepRespirationValue') or 
                                     respiration_data.get('avgWakingRespirationValue') or 
                                     respiration_data.get('avgRespirationValue'))
                respiration_max_val = (respiration_data.get('highestRespirationValue') or 
                                     respiration_data.get('maxRespirationValue'))
                respiration_min_val = (respiration_data.get('lowestRespirationValue') or 
                                     respiration_data.get('minRespirationValue'))
            
            # Heart Rates (Tep) - detailní data
            # API vrací: maxHeartRate, minHeartRate, restingHeartRate, ale NEMÁ averageHeartRate
            # Musíme vypočítat průměr z heartRateValues nebo použít sleepHeartRate ze sleep_data
            # Pokud nejsou data, vrátit None (ne 0)
            heart_rate_avg_hrv_val = None
            heart_rate_resting_hrv_val = None
            heart_rate_max_hrv_val = None
            heart_rate_min_hrv_val = None
            
            if isinstance(heart_rates_data, dict):
                # Zkusit získat průměr z heartRateValues array
                heart_rate_values = heart_rates_data.get('heartRateValues', [])
                if heart_rate_values and isinstance(heart_rate_values, list):
                    # heartRateValues je array arrays: [[timestamp, heartrate], ...]
                    hr_values = [hr[1] for hr in heart_rate_values if len(hr) > 1 and hr[1] is not None and isinstance(hr[1], (int, float))]
                    if hr_values:
                        heart_rate_avg_hrv_val = round(sum(hr_values) / len(hr_values), 0)
                
                # Získat ostatní hodnoty
                if heart_rates_data.get('restingHeartRate') is not None:
                    heart_rate_resting_hrv_val = heart_rates_data.get('restingHeartRate')
                if heart_rates_data.get('maxHeartRate') is not None:
                    heart_rate_max_hrv_val = heart_rates_data.get('maxHeartRate')
                if heart_rates_data.get('minHeartRate') is not None:
                    heart_rate_min_hrv_val = heart_rates_data.get('minHeartRate')
            
            # Fallback: zkusit sleepHeartRate ze sleep_data (je to LIST!)
            if heart_rate_avg_hrv_val is None and isinstance(sleep_data, dict):
                sleep_heart_rate_data = sleep_data.get('sleepHeartRate', [])
                if isinstance(sleep_heart_rate_data, list) and sleep_heart_rate_data:
                    # sleepHeartRate je list dictů: [{'value': 50, 'startGMT': ...}, ...]
                    sleep_hr_values = [item.get('value') for item in sleep_heart_rate_data if isinstance(item, dict) and item.get('value') is not None]
                    if sleep_hr_values:
                        heart_rate_avg_hrv_val = round(sum(sleep_hr_values) / len(sleep_hr_values), 0)
                elif isinstance(sleep_heart_rate_data, dict):
                    # Fallback na starý formát (dict)
                    heart_rate_avg_hrv_val = (sleep_heart_rate_data.get('averageHeartRate') or 
                                             sleep_heart_rate_data.get('avgHeartRate'))
            
            # Training Readiness & Status
            # training_readiness může být list nebo dict
            # Pokud nejsou data, vrátit None (ne 0)
            training_readiness_score_val = None
            if isinstance(training_readiness, list) and len(training_readiness) > 0:
                # Vezmout první (nejnovější) záznam
                if isinstance(training_readiness[0], dict) and training_readiness[0].get('score') is not None:
                    training_readiness_score_val = training_readiness[0].get('score')
            elif isinstance(training_readiness, dict):
                training_readiness_score_val = (training_readiness.get('trainingReadinessScore') or 
                                               training_readiness.get('score'))
            
            # training_status vrací mostRecentTrainingStatus
            training_status_val = ''
            training_status_label_val = ''
            if isinstance(training_status, dict):
                most_recent = training_status.get('mostRecentTrainingStatus', {})
                if isinstance(most_recent, dict):
                    training_status_val = most_recent.get('trainingStatus', most_recent.get('status', ''))
                    training_status_label_val = most_recent.get('trainingStatusLabel', most_recent.get('label', ''))
                else:
                    training_status_val = training_status.get('trainingStatus', training_status.get('status', ''))
                    training_status_label_val = training_status.get('trainingStatusLabel', training_status.get('label', ''))
            
            # Blood Pressure
            # API vrací measurementSummaries list - zkusit získat z prvního záznamu
            # Pokud nejsou data, vrátit None (ne 0)
            bp_systolic = None
            bp_diastolic = None
            bp_avg = None
            if isinstance(blood_pressure, dict):
                measurement_summaries = blood_pressure.get('measurementSummaries', [])
                if isinstance(measurement_summaries, list) and len(measurement_summaries) > 0:
                    first_measurement = measurement_summaries[0]
                    if isinstance(first_measurement, dict):
                        bp_systolic = first_measurement.get('systolic') or first_measurement.get('systolicBP')
                        bp_diastolic = first_measurement.get('diastolic') or first_measurement.get('diastolicBP')
                        bp_avg = first_measurement.get('average') or first_measurement.get('avgBP')
                else:
                    # Fallback na starý formát
                    bp_systolic = blood_pressure.get('systolic') or blood_pressure.get('systolicBP')
                    bp_diastolic = blood_pressure.get('diastolic') or blood_pressure.get('diastolicBP')
                    bp_avg = blood_pressure.get('average') or blood_pressure.get('avgBP')
            
            # Body Composition (složení těla)
            # API vrací dict s totalAverage dict
            # Pokud jsou hodnoty null, vrátit None (ne 0)
            body_comp_total_avg = {}
            if isinstance(body_composition, dict):
                body_comp_total_avg = body_composition.get('totalAverage', {})
                if not body_comp_total_avg:
                    # Fallback - zkusit přímo v body_composition
                    body_comp_total_avg = body_composition
            
            # Daily Weigh Ins (denní vážení - souhrn)
            # API vrací dict s totalAverage dict
            daily_weigh_avg = {}
            if isinstance(daily_weigh_ins, dict):
                daily_weigh_avg = daily_weigh_ins.get('totalAverage', {})
            elif isinstance(daily_weigh_ins, list) and len(daily_weigh_ins) > 0:
                daily_weigh_avg = daily_weigh_ins[0] if isinstance(daily_weigh_ins[0], dict) else {}
            
            # Hydration - před data.update
            hydration_total = None
            if isinstance(hydration_data, dict):
                hydration_total = hydration_data.get('valueInML')
                if hydration_total is None:
                    hydration_total = hydration_data.get('totalFluidIntake') or hydration_data.get('total')
            
            hydration_goal = None
            if isinstance(hydration_data, dict):
                hydration_goal = hydration_data.get('goalInML')
                if hydration_goal is None:
                    hydration_goal = hydration_data.get('goal') or hydration_data.get('goalFluidIntake')
            
            # Body Composition values - před data.update
            body_weight_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('weight') is not None:
                body_weight_val = body_comp_total_avg.get('weight') / 1000
            elif isinstance(body_composition, dict):
                weight = body_composition.get('weight')
                if weight is None:
                    weight = body_composition.get('weightInGrams')
                if weight is not None:
                    body_weight_val = weight / 1000 if weight > 1000 else weight
            
            body_fat_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bodyFat') is not None:
                body_fat_val = body_comp_total_avg.get('bodyFat')
            elif isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bodyFatPercentage') is not None:
                body_fat_val = body_comp_total_avg.get('bodyFatPercentage')
            elif isinstance(body_composition, dict):
                body_fat_val = body_composition.get('bodyFat') or body_composition.get('bodyFatPercentage')
            
            body_muscle_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('muscleMass') is not None:
                body_muscle_val = body_comp_total_avg.get('muscleMass') / 1000
            elif isinstance(body_composition, dict):
                muscle = body_composition.get('muscleMass')
                if muscle is None:
                    muscle = body_composition.get('muscleMassInGrams')
                if muscle is not None:
                    body_muscle_val = muscle / 1000 if muscle > 1000 else muscle
            
            body_bone_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('boneMass') is not None:
                body_bone_val = body_comp_total_avg.get('boneMass') / 1000
            elif isinstance(body_composition, dict):
                bone = body_composition.get('boneMass')
                if bone is None:
                    bone = body_composition.get('boneMassInGrams')
                if bone is not None:
                    body_bone_val = bone / 1000 if bone > 1000 else bone
            
            body_water_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bodyWater') is not None:
                body_water_val = body_comp_total_avg.get('bodyWater')
            elif isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bodyWaterPercentage') is not None:
                body_water_val = body_comp_total_avg.get('bodyWaterPercentage')
            elif isinstance(body_composition, dict):
                body_water_val = body_composition.get('bodyWater') or body_composition.get('bodyWaterPercentage')
            
            body_metabolic_age_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('metabolicAge') is not None:
                body_metabolic_age_val = body_comp_total_avg.get('metabolicAge')
            elif isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('age') is not None:
                body_metabolic_age_val = body_comp_total_avg.get('age')
            elif isinstance(body_composition, dict):
                body_metabolic_age_val = body_composition.get('metabolicAge') or body_composition.get('age')
            
            body_visceral_fat_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('visceralFat') is not None:
                body_visceral_fat_val = body_comp_total_avg.get('visceralFat')
            elif isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('visceralFatRating') is not None:
                body_visceral_fat_val = body_comp_total_avg.get('visceralFatRating')
            elif isinstance(body_composition, dict):
                body_visceral_fat_val = body_composition.get('visceralFat') or body_composition.get('visceralFatRating')
            
            body_bmi_val = None
            if isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bmi') is not None:
                body_bmi_val = body_comp_total_avg.get('bmi')
            elif isinstance(body_comp_total_avg, dict) and body_comp_total_avg.get('bodyMassIndex') is not None:
                body_bmi_val = body_comp_total_avg.get('bodyMassIndex')
            elif isinstance(body_composition, dict):
                body_bmi_val = body_composition.get('bmi') or body_composition.get('bodyMassIndex')
            
            # Weigh Ins values - před data.update
            weigh_in_count_val = len(weigh_ins) if isinstance(weigh_ins, list) else 0
            
            weigh_in_kg_val = None
            weigh_in_fat_val = None
            weigh_in_muscle_val = None
            weigh_in_bone_val = None
            weigh_in_water_val = None
            weigh_in_bmi_val = None
            weigh_in_metabolic_age_val = None
            weigh_in_visceral_fat_val = None
            
            if isinstance(weigh_ins, list) and len(weigh_ins) > 0 and isinstance(weigh_ins[0], dict):
                first_weigh_in = weigh_ins[0]
                weight = first_weigh_in.get('weight')
                if weight is not None:
                    weigh_in_kg_val = weight / 1000
                
                weigh_in_fat_val = first_weigh_in.get('bodyFat') or first_weigh_in.get('bodyFatPercentage')
                
                muscle = first_weigh_in.get('muscleMass')
                if muscle is None:
                    muscle = first_weigh_in.get('muscleMassInGrams')
                if muscle is not None:
                    weigh_in_muscle_val = muscle / 1000 if muscle > 1000 else muscle
                
                bone = first_weigh_in.get('boneMass')
                if bone is None:
                    bone = first_weigh_in.get('boneMassInGrams')
                if bone is not None:
                    weigh_in_bone_val = bone / 1000 if bone > 1000 else bone
                
                weigh_in_water_val = first_weigh_in.get('bodyWater') or first_weigh_in.get('bodyWaterPercentage')
                weigh_in_bmi_val = first_weigh_in.get('bmi') or first_weigh_in.get('bodyMassIndex')
                weigh_in_metabolic_age_val = first_weigh_in.get('metabolicAge') or first_weigh_in.get('age')
                weigh_in_visceral_fat_val = first_weigh_in.get('visceralFat') or first_weigh_in.get('visceralFatRating')
            
            # Daily Weigh Ins values - před data.update
            daily_weigh_in_kg_val = None
            daily_weigh_in_fat_val = None
            
            if isinstance(daily_weigh_avg, dict) and daily_weigh_avg.get('weight') is not None:
                daily_weigh_in_kg_val = daily_weigh_avg.get('weight') / 1000
            elif isinstance(daily_weigh_ins, list) and len(daily_weigh_ins) > 0 and isinstance(daily_weigh_ins[0], dict):
                weight = daily_weigh_ins[0].get('weight')
                if weight is not None:
                    daily_weigh_in_kg_val = weight / 1000
            
            if isinstance(daily_weigh_avg, dict):
                daily_weigh_in_fat_val = daily_weigh_avg.get('bodyFat') or daily_weigh_avg.get('bodyFatPercentage')
            elif isinstance(daily_weigh_ins, list) and len(daily_weigh_ins) > 0 and isinstance(daily_weigh_ins[0], dict):
                daily_weigh_in_fat_val = daily_weigh_ins[0].get('bodyFat') or daily_weigh_ins[0].get('bodyFatPercentage')
            
            # Aktivity values - před data.update
            activities_count_val = len(activities) if isinstance(activities, list) else 0
            
            activities_duration_val = None
            activities_distance_val = None
            activities_calories_val = None
            activities_avg_hr_val = None
            activities_max_hr_val = None
            
            if isinstance(activities, list) and len(activities) > 0:
                # Jsou aktivity - vypočítat hodnoty
                durations = [a.get('duration', 0) for a in activities if isinstance(a, dict) and a.get('duration') is not None]
                if durations:
                    activities_duration_val = round(sum(durations) / 60, 1)
                
                distances = [a.get('distance', 0) for a in activities if isinstance(a, dict) and a.get('distance') is not None]
                if distances:
                    activities_distance_val = round(sum(distances) / 1000, 2)
                
                calories_list = [a.get('calories', 0) for a in activities if isinstance(a, dict) and a.get('calories') is not None]
                if calories_list:
                    activities_calories_val = sum(calories_list)
                
                heart_rates = [a.get('averageHeartRate', 0) for a in activities if isinstance(a, dict) and a.get('averageHeartRate') is not None]
                if heart_rates:
                    activities_avg_hr_val = round(sum(heart_rates) / len(heart_rates), 0)
                
                max_hrs = [a.get('maxHeartRate', 0) for a in activities if isinstance(a, dict) and a.get('maxHeartRate') is not None]
                if max_hrs:
                    activities_max_hr_val = max(max_hrs)
            
            # Max Metrics values - před data.update
            # Zajistit, že jsou to čísla, ne dict nebo jiné objekty
            max_vo2_final = vo2_max_val if isinstance(vo2_max_val, (int, float)) else None
            if max_vo2_final is None and isinstance(max_metrics, dict):
                vo2_val = max_metrics.get('vo2Max') or max_metrics.get('vo2')
                if isinstance(vo2_val, (int, float)):
                    max_vo2_final = vo2_val
            
            max_fitness_age_final = fitness_age_val if isinstance(fitness_age_val, (int, float)) else None
            if max_fitness_age_final is None and isinstance(max_metrics, dict):
                age_val = max_metrics.get('fitnessAge') or max_metrics.get('age')
                if isinstance(age_val, (int, float)):
                    max_fitness_age_final = age_val
            
            # SpO2 (detailní)
            # API vrací averageSpO2, lowestSpO2, latestSpO2, avgSleepSpO2
            # Pokud nejsou data, vrátit None (ne 0)
            spo2_avg_detail_val = None
            spo2_min_detail_val = None
            spo2_max_detail_val = None
            if isinstance(spo2_data, dict):
                spo2_avg_detail_val = (spo2_data.get('averageSpO2') or 
                                     spo2_data.get('avgSleepSpO2') or 
                                     spo2_data.get('avg'))
                spo2_min_detail_val = (spo2_data.get('lowestSpO2') or 
                                     spo2_data.get('min'))
                # Pro max zkusit z hourly averages nebo použít latest
                spo2_max_detail_val = (spo2_data.get('latestSpO2') or 
                                      spo2_data.get('highestSpO2') or 
                                      spo2_data.get('max'))
                # Pokud máme hourly averages, zkusit najít max
                if spo2_max_detail_val is None:
                    hourly_avgs = spo2_data.get('spO2HourlyAverages', [])
                    if hourly_avgs and isinstance(hourly_avgs, list):
                        # hourly_avgs je array arrays: [[timestamp, spo2], ...]
                        spo2_values = [avg[1] for avg in hourly_avgs if len(avg) > 1 and avg[1] is not None and isinstance(avg[1], (int, float))]
                        if spo2_values:
                            spo2_max_detail_val = max(spo2_values)
            
            # Přidání HRV a Sleep dat do data dict
            data.update({
                'hrv_avg': hrv_avg_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'hrv_max': hrv_max_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'hrv_min': hrv_min_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'hrv_last_night_avg': hrv_last_night,  # None = data nejsou k dispozici, 0 = skutečná nula
                'hrv_weekly_avg': hrv_weekly,  # None = data nejsou k dispozici, 0 = skutečná nula
                
                'sleep_duration_min': round(sleep_duration_sec / 60, 1) if sleep_duration_sec is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_awake_min': round(sleep_awake_sec / 60, 1) if sleep_awake_sec is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_light_min': round(sleep_light_sec / 60, 1) if sleep_light_sec is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_deep_min': round(sleep_deep_sec / 60, 1) if sleep_deep_sec is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_rem_min': round(sleep_rem_sec / 60, 1) if sleep_rem_sec is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_score': sleep_score_val if sleep_score_val is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_quality_score': sleep_quality,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_stress_avg': sleep_stress if sleep_stress is not None else None,  # None = data nejsou k dispozici, 0 = skutečná nula
                'sleep_start': sleep_start_val or '',
                'sleep_end': sleep_end_val or '',
                
                # Respiration (Dýchání) - detailní data
                'respiration_avg': respiration_avg_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'respiration_max': respiration_max_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'respiration_min': respiration_min_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                
                # Heart Rates (Tep) - detailní data
                'heart_rate_resting_hrv': heart_rate_resting_hrv_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'heart_rate_avg_hrv': heart_rate_avg_hrv_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'heart_rate_max_hrv': heart_rate_max_hrv_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'heart_rate_min_hrv': heart_rate_min_hrv_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                
                # Aktivity (souhrn za den)
                'activities_count': activities_count_val,  # 0 = žádné aktivity (to je OK, není to None)
                'activities_total_duration_min': activities_duration_val,  # None = data nejsou k dispozici
                'activities_total_distance_km': activities_distance_val,  # None = data nejsou k dispozici
                'activities_total_calories': activities_calories_val,  # None = data nejsou k dispozici
                'activities_avg_heart_rate': activities_avg_hr_val,  # None = data nejsou k dispozici
                'activities_max_heart_rate': activities_max_hr_val,  # None = data nejsou k dispozici
                
                # Training Readiness & Status
                'training_readiness_score': training_readiness_score_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'training_status': training_status_val,
                'training_status_label': training_status_label_val,
                
                # Endurance & Hill Score
                # Endurance score vrací overallScore - pokud nejsou data, vrátit None (ne 0)
                'endurance_score': (endurance_score.get('overallScore') or 
                                  endurance_score.get('enduranceScore') or 
                                  endurance_score.get('score')) if isinstance(endurance_score, dict) else None,
                # Hill score vrací overallScore - pokud nejsou data, vrátit None (ne 0)
                'hill_score': (hill_score.get('overallScore') or 
                             hill_score.get('hillScore') or 
                             hill_score.get('score')) if isinstance(hill_score, dict) else None,
                
                # Blood Pressure
                'blood_pressure_systolic': bp_systolic,
                'blood_pressure_diastolic': bp_diastolic,
                'blood_pressure_avg': bp_avg,
                
                # Hydration
                'hydration_total_ml': hydration_total,  # None = data nejsou k dispozici, 0 = skutečná nula
                'hydration_goal_ml': hydration_goal,  # None = data nejsou k dispozici, 0 = skutečná nula
                
                # Body Composition (složení těla)
                'body_weight_kg': body_weight_val,
                'body_fat_percent': body_fat_val,
                'body_muscle_mass_kg': body_muscle_val,
                'body_bone_mass_kg': body_bone_val,
                'body_water_percent': body_water_val,
                'body_metabolic_age': body_metabolic_age_val,
                'body_visceral_fat': body_visceral_fat_val,
                'body_bmi': body_bmi_val,
                
                # Weigh Ins (vážení - všechny vážení za den)
                'weigh_in_count': weigh_in_count_val,
                'weigh_in_kg': weigh_in_kg_val,
                'weigh_in_fat_percent': weigh_in_fat_val,
                'weigh_in_muscle_mass_kg': weigh_in_muscle_val,
                'weigh_in_bone_mass_kg': weigh_in_bone_val,
                'weigh_in_water_percent': weigh_in_water_val,
                'weigh_in_bmi': weigh_in_bmi_val,
                'weigh_in_metabolic_age': weigh_in_metabolic_age_val,
                'weigh_in_visceral_fat': weigh_in_visceral_fat_val,
                
                # Daily Weigh Ins (denní vážení - souhrn)
                'daily_weigh_in_kg': daily_weigh_in_kg_val,
                'daily_weigh_in_fat_percent': daily_weigh_in_fat_val,
                
                # SpO2 (detailní)
                'spo2_avg_detail': spo2_avg_detail_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'spo2_min_detail': spo2_min_detail_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                'spo2_max_detail': spo2_max_detail_val,  # None = data nejsou k dispozici, 0 = skutečná nula
                
                # Max Metrics
                'max_vo2': max_vo2_final,  # None = data nejsou k dispozici, 0 = skutečná nula
                'max_fitness_age': max_fitness_age_final,  # None = data nejsou k dispozici, 0 = skutečná nula
            })
            
            logger.info(f"✅ Data získána pro {date}: {data.get('steps', 0)} kroků")
            return data
            
        except Exception as e:
            logger.error(f"❌ Chyba při získávání dat z Garmin: {e}")
            raise
    
    def ensure_sheet_headers(self, worksheet_name: str = 'Garmin Data'):
        """
        Zajistí, že worksheet existuje a má správné hlavičky
        
        Args:
            worksheet_name: Název worksheetu
        """
        try:
            # Zkusit otevřít existující worksheet
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                # Vytvořit nový worksheet
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=120  # Více sloupců pro všechny metriky včetně aktivit a dalších
                )
                logger.info(f"✅ Vytvořen nový worksheet: {worksheet_name}")
            
            # Zkontrolovat hlavičky
            headers = worksheet.row_values(1)
            expected_headers = [
                'Datum', 'Čas záznamu',
                # Aktivita
                'Kroky', 'Cíl kroků', 'Vzdálenost (km)', 'Schody nahoru', 'Schody dolů', 'Cíl schodů',
                # Kalorie
                'Kalorie celkem', 'Kalorie aktivní', 'Kalorie BMR',
                # Tepová frekvence
                'Tep klidový', 'Tep průměr 7d', 'Tep min', 'Tep max', 'Tep min průměr', 'Tep max průměr',
                # Stres
                'Stres průměr', 'Stres max', 'Stres doba (min)', 'Stres odpočinek (min)', 'Stres aktivita (min)',
                'Stres celkem (min)', 'Stres nízký (min)', 'Stres střední (min)', 'Stres vysoký (min)', 'Stres %',
                # Body Battery
                'BB nabito', 'BB vybito', 'BB nejvyšší', 'BB nejnižší', 'BB aktuální', 'BB během spánku', 'BB při probuzení',
                # Kyslík v krvi
                'SpO2 průměr', 'SpO2 nejnižší', 'SpO2 poslední',
                # Dýchání
                'Dýchání průměr', 'Dýchání nejvyšší', 'Dýchání nejnižší', 'Dýchání poslední',
                # Čas aktivity
                'Čas velmi aktivní (min)', 'Čas aktivní (min)', 'Čas sedavý (min)', 'Čas spánek (min)', 'Čas vzhůru (min)', 'Čas spánek měřeno (min)',
                # Intenzita
                'Intenzita střední (min)', 'Intenzita vysoká (min)', 'Cíl intenzita (min)',
                # HRV (Variabilita srdečního tepu)
                'HRV průměr', 'HRV max', 'HRV min', 'HRV včera průměr', 'HRV týden průměr',
                # Spánek (detailní)
                'Spánek celkem (min)', 'Spánek vzhůru (min)', 'Spánek lehký (min)', 'Spánek hluboký (min)', 'Spánek REM (min)',
                'Spánek skóre', 'Spánek kvalita', 'Spánek stres průměr', 'Spánek začátek', 'Spánek konec',
                # Dýchání (detailní)
                'Dýchání průměr detail', 'Dýchání max detail', 'Dýchání min detail',
                # Tep (detailní)
                'Tep klidový HRV', 'Tep průměr HRV', 'Tep max HRV', 'Tep min HRV',
                # Aktivity
                'Aktivity počet', 'Aktivity doba (min)', 'Aktivity vzdálenost (km)', 'Aktivity kalorie',
                'Aktivity tep průměr', 'Aktivity tep max',
                # Trénink
                'Trénink připravenost', 'Trénink status', 'Trénink status label',
                # Skóre
                'Endurance skóre', 'Hill skóre',
                # Krevní tlak
                'TK systolický', 'TK diastolický', 'TK průměr',
                # Hydratace
                'Hydratace celkem (ml)', 'Hydratace cíl (ml)',
                # Složení těla
                'Váha (kg)', 'Tuk %', 'Svaly (kg)', 'Kosti (kg)', 'Voda %', 'Metabolický věk', 'Viscerální tuk', 'BMI',
                # Vážení (detailní)
                'Vážení počet', 'Vážení (kg)', 'Vážení tuk %', 'Vážení svaly (kg)', 'Vážení kosti (kg)', 'Vážení voda %',
                'Vážení BMI', 'Vážení metabolický věk', 'Vážení viscerální tuk',
                # Denní vážení
                'Denní vážení (kg)', 'Denní vážení tuk %',
                # SpO2 detailní
                'SpO2 průměr detail', 'SpO2 min detail', 'SpO2 max detail',
                # Max metriky
                'VO2 max', 'Fitness věk',
            ]
            
            if not headers or headers != expected_headers:
                worksheet.clear()
                worksheet.append_row(expected_headers)
                logger.info("✅ Hlavičky nastaveny")
            
            return worksheet
            
        except Exception as e:
            logger.error(f"❌ Chyba při nastavení worksheet: {e}")
            raise
    
    def send_to_sheets(self, data: Dict[str, Any], worksheet_name: str = 'Garmin Data'):
        """
        Odešle data do Google Sheets
        
        Args:
            data: Slovník s daty
            worksheet_name: Název worksheetu
        """
        try:
            worksheet = self.ensure_sheet_headers(worksheet_name)
            
            # Pomocná funkce pro převod hodnoty na buňku
            # None → prázdná buňka (''), 0 → 0, ostatní → hodnota
            def to_cell_value(val):
                """Převod hodnoty na hodnotu pro Google Sheets buňku"""
                if val is None:
                    return ''  # Prázdná buňka = data nejsou k dispozici
                return val  # 0 nebo jiná hodnota = skutečná hodnota
            
            # Převod dat na řádek (v pořadí podle hlaviček)
            row = [
                data.get('date', ''),
                data.get('timestamp', ''),
                # Aktivita
                data.get('steps', 0),
                data.get('step_goal', 0),
                data.get('distance_km', 0),
                data.get('floors_ascended', 0),
                data.get('floors_descended', 0),
                data.get('floors_goal', 0),
                # Kalorie
                data.get('calories_total', 0),
                data.get('calories_active', 0),
                data.get('calories_bmr', 0),
                # Tepová frekvence
                data.get('heart_rate_resting', 0),
                data.get('heart_rate_avg_7d', 0),
                data.get('heart_rate_min', 0),
                data.get('heart_rate_max', 0),
                data.get('heart_rate_min_avg', 0),
                data.get('heart_rate_max_avg', 0),
                # Stres
                data.get('stress_avg', 0),
                data.get('stress_max', 0),
                data.get('stress_duration', 0),
                data.get('stress_rest_duration', 0),
                data.get('stress_activity_duration', 0),
                data.get('stress_total_duration', 0),
                data.get('stress_low_duration', 0),
                data.get('stress_medium_duration', 0),
                data.get('stress_high_duration', 0),
                data.get('stress_percentage', 0),
                # Body Battery
                data.get('body_battery_charged', 0),
                data.get('body_battery_drained', 0),
                data.get('body_battery_highest', 0),
                data.get('body_battery_lowest', 0),
                data.get('body_battery_most_recent', 0),
                data.get('body_battery_during_sleep', 0),
                data.get('body_battery_at_wake', 0),
                # Kyslík v krvi
                data.get('spo2_avg', 0),
                data.get('spo2_lowest', 0),
                data.get('spo2_latest', 0),
                # Dýchání
                data.get('respiration_avg_waking', 0),
                data.get('respiration_highest', 0),
                data.get('respiration_lowest', 0),
                data.get('respiration_latest', 0),
                # Čas aktivity
                data.get('time_highly_active', 0),
                data.get('time_active', 0),
                data.get('time_sedentary', 0),
                data.get('time_sleeping', 0),
                data.get('time_awake', 0),
                data.get('time_asleep', 0),
                # Intenzita
                data.get('intensity_moderate_min', 0),
                data.get('intensity_vigorous_min', 0),
                data.get('intensity_goal_min', 0),
                # HRV
                to_cell_value(data.get('hrv_avg')),
                to_cell_value(data.get('hrv_max')),
                to_cell_value(data.get('hrv_min')),
                to_cell_value(data.get('hrv_last_night_avg')),
                to_cell_value(data.get('hrv_weekly_avg')),
                # Spánek
                to_cell_value(data.get('sleep_duration_min')),
                to_cell_value(data.get('sleep_awake_min')),
                to_cell_value(data.get('sleep_light_min')),
                to_cell_value(data.get('sleep_deep_min')),
                to_cell_value(data.get('sleep_rem_min')),
                to_cell_value(data.get('sleep_score')),
                to_cell_value(data.get('sleep_quality_score')),
                to_cell_value(data.get('sleep_stress_avg')),
                data.get('sleep_start', ''),
                data.get('sleep_end', ''),
                # Dýchání detailní
                to_cell_value(data.get('respiration_avg')),
                to_cell_value(data.get('respiration_max')),
                to_cell_value(data.get('respiration_min')),
                # Tep detailní
                to_cell_value(data.get('heart_rate_resting_hrv')),
                to_cell_value(data.get('heart_rate_avg_hrv')),
                to_cell_value(data.get('heart_rate_max_hrv')),
                to_cell_value(data.get('heart_rate_min_hrv')),
                # Aktivity
                data.get('activities_count', 0),  # 0 = žádné aktivity (to je OK)
                to_cell_value(data.get('activities_total_duration_min')),
                to_cell_value(data.get('activities_total_distance_km')),
                to_cell_value(data.get('activities_total_calories')),
                to_cell_value(data.get('activities_avg_heart_rate')),
                to_cell_value(data.get('activities_max_heart_rate')),
                # Trénink
                to_cell_value(data.get('training_readiness_score')),
                data.get('training_status', ''),
                data.get('training_status_label', ''),
                # Skóre
                to_cell_value(data.get('endurance_score')),
                to_cell_value(data.get('hill_score')),
                # Krevní tlak
                to_cell_value(data.get('blood_pressure_systolic')),
                to_cell_value(data.get('blood_pressure_diastolic')),
                to_cell_value(data.get('blood_pressure_avg')),
                # Hydratace
                to_cell_value(data.get('hydration_total_ml')),
                to_cell_value(data.get('hydration_goal_ml')),
                # Složení těla
                round(data.get('body_weight_kg'), 2) if data.get('body_weight_kg') is not None else '',
                round(data.get('body_fat_percent'), 2) if data.get('body_fat_percent') is not None else '',
                round(data.get('body_muscle_mass_kg'), 2) if data.get('body_muscle_mass_kg') is not None else '',
                round(data.get('body_bone_mass_kg'), 2) if data.get('body_bone_mass_kg') is not None else '',
                round(data.get('body_water_percent'), 2) if data.get('body_water_percent') is not None else '',
                round(data.get('body_metabolic_age'), 0) if data.get('body_metabolic_age') is not None else '',
                round(data.get('body_visceral_fat'), 1) if data.get('body_visceral_fat') is not None else '',
                round(data.get('body_bmi'), 2) if data.get('body_bmi') is not None else '',
                # Vážení (detailní)
                data.get('weigh_in_count', 0),  # 0 = žádné vážení (to je OK)
                round(data.get('weigh_in_kg'), 2) if data.get('weigh_in_kg') is not None else '',
                round(data.get('weigh_in_fat_percent'), 2) if data.get('weigh_in_fat_percent') is not None else '',
                round(data.get('weigh_in_muscle_mass_kg'), 2) if data.get('weigh_in_muscle_mass_kg') is not None else '',
                round(data.get('weigh_in_bone_mass_kg'), 2) if data.get('weigh_in_bone_mass_kg') is not None else '',
                round(data.get('weigh_in_water_percent'), 2) if data.get('weigh_in_water_percent') is not None else '',
                round(data.get('weigh_in_bmi'), 2) if data.get('weigh_in_bmi') is not None else '',
                round(data.get('weigh_in_metabolic_age'), 0) if data.get('weigh_in_metabolic_age') is not None else '',
                round(data.get('weigh_in_visceral_fat'), 1) if data.get('weigh_in_visceral_fat') is not None else '',
                # Denní vážení
                round(data.get('daily_weigh_in_kg'), 2) if data.get('daily_weigh_in_kg') is not None else '',
                round(data.get('daily_weigh_in_fat_percent'), 2) if data.get('daily_weigh_in_fat_percent') is not None else '',
                # SpO2 detailní
                to_cell_value(data.get('spo2_avg_detail')),
                to_cell_value(data.get('spo2_min_detail')),
                to_cell_value(data.get('spo2_max_detail')),
                # Max metriky
                to_cell_value(data.get('max_vo2')),
                to_cell_value(data.get('max_fitness_age')),
            ]
            
            # Pomocná funkce pro převod čísla na Excel sloupec (A, B, ..., Z, AA, AB, ...)
            def num_to_col(num):
                """Převod čísla na Excel sloupec (1=A, 2=B, ..., 27=AA, ...)"""
                col = ''
                while num > 0:
                    num -= 1
                    col = chr(65 + (num % 26)) + col
                    num //= 26
                return col
            
            # Kontrola duplicit - zkontrolovat, zda už tento den není záznam
            existing_dates = worksheet.col_values(1)
            target_date = data.get('date')
            
            if target_date in existing_dates:
                # Najít všechny výskyty tohoto data (pro případ duplicit)
                all_indices = [i + 1 for i, d in enumerate(existing_dates) if d == target_date]
                
                if len(all_indices) > 1:
                    # Duplicitní datumy nalezeny - upozornit a smazat všechny kromě posledního
                    logger.warning(f"⚠️  Duplicitní datumy nalezeny pro {target_date} na řádcích: {all_indices}")
                    logger.info(f"🗑️  Mažu duplicitní řádky (ponechávám poslední: řádek {all_indices[-1]})...")
                    
                    # Smazat všechny řádky kromě posledního (od konce, aby se indexy neposunuly)
                    for idx in reversed(all_indices[:-1]):
                        worksheet.delete_rows(idx)
                        logger.info(f"   ✅ Smazán duplicitní řádek {idx}")
                    
                    # Aktualizovat poslední řádek
                    row_index = all_indices[-1]
                else:
                    # Normální případ - jen jeden výskyt
                    row_index = all_indices[0]
                
                # Aktualizovat všechny sloupce (A až poslední)
                last_col = num_to_col(len(row))
                worksheet.update(range_name=f'A{row_index}:{last_col}{row_index}', values=[row])
                logger.info(f"✅ Data aktualizována pro {target_date} (řádek {row_index})")
            else:
                # Přidat nový řádek
                worksheet.append_row(row)
                logger.info(f"✅ Data přidána pro {target_date}")
            
        except Exception as e:
            logger.error(f"❌ Chyba při odesílání do Google Sheets: {e}")
            raise
    
    def run_once(self, date: Optional[str] = None):
        """
        Spustí jeden cyklus získání a odeslání dat
        
        Args:
            date: Datum ve formátu YYYY-MM-DD (pokud None, použije se dnešní datum)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Varování pokud stahujeme data pro dnešní den
        today = datetime.now().strftime('%Y-%m-%d')
        if date == today:
            logger.warning("⚠️  Stahuješ data pro dnešní den - data mohou být neúplná!")
            logger.info("💡 Pro kompletní data stáhni data až po skončení dne (po půlnoci)")
            logger.info("💡 Nebo stáhni data pro včerejšek: --date " + (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
        
        try:
            logger.info(f"🔄 Získávám data pro {date}...")
            data = self.get_garmin_data(date)
            self.send_to_sheets(data)
            logger.info(f"✅ Hotovo pro {date}")
            
            # Volitelná notifikace o úspěchu
            if self.telegram:
                self.telegram.notify_sync_success(date, {
                    'steps': data.get('steps', 0),
                    'distance_km': data.get('distance_km', 0),
                    'calories_total': data.get('calories_total', 0)
                })
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Chyba při zpracování: {error_msg}")
            
            # Notifikace o chybě
            if self.telegram:
                self.telegram.notify_sync_error(error_msg, date)
            raise
    
    def run_polling(self):
        """Spustí nekonečný polling cyklus"""
        logger.info("🚀 Garmin Bot spuštěn (polling mode)")
        logger.info(f"⏰ Interval: {self.polling_interval} sekund ({self.polling_interval // 60} minut)")
        
        while True:
            try:
                self.run_once()
                logger.info(f"⏳ Čekám {self.polling_interval} sekund do dalšího dotazu...")
                time.sleep(self.polling_interval)
            except KeyboardInterrupt:
                logger.info("🛑 Zastaveno uživatelem")
                break
            except Exception as e:
                logger.error(f"❌ Chyba v polling cyklu: {e}")
                logger.info(f"⏳ Čekám {self.polling_interval} sekund před opakováním...")
                time.sleep(self.polling_interval)


def main():
    """Hlavní funkce pro spuštění bota"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Garmin Connect Bot - Stahuje data do Google Sheets')
    parser.add_argument('--once', action='store_true', help='Spustit pouze jednou (ne polling)')
    parser.add_argument('--date', type=str, help='Datum ve formátu YYYY-MM-DD (default: dnes)')
    parser.add_argument('--interval', type=int, default=600, help='Interval mezi dotazy v sekundách (default: 600)')
    parser.add_argument('--mfa-code', type=str, help='MFA kód pro přihlášení (pokud je k dispozici)')
    
    args = parser.parse_args()
    
    # Načtení konfigurace z environment variables
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')
    google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
    google_credentials = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    mfa_code = args.mfa_code or os.getenv('GARMIN_MFA_CODE')
    
    if not all([garmin_email, garmin_password, google_sheet_id]):
        logger.error("❌ Chybí povinné environment variables:")
        logger.error("   GARMIN_EMAIL - Email pro Garmin Connect")
        logger.error("   GARMIN_PASSWORD - Heslo pro Garmin Connect")
        logger.error("   GOOGLE_SHEET_ID - ID Google Sheet (z URL)")
        logger.error("   GOOGLE_CREDENTIALS_PATH - (volitelné) Cesta k Service Account JSON")
        logger.error("\nPříklad nastavení:")
        logger.error("   export GARMIN_EMAIL='vas@email.cz'")
        logger.error("   export GARMIN_PASSWORD='heslo'")
        logger.error("   export GOOGLE_SHEET_ID='1abc123def456...'")
        return
    
    # Vytvoření bota
    bot = GarminBot(
        garmin_email=garmin_email,
        garmin_password=garmin_password,
        google_sheet_id=google_sheet_id,
        google_credentials_path=google_credentials if os.path.exists(google_credentials) else None,
        polling_interval=args.interval,
        mfa_code=mfa_code
    )
    
    # Spuštění
    if args.once:
        bot.run_once(args.date)
    else:
        bot.run_polling()


if __name__ == '__main__':
    # Vytvoření složky pro logy pokud neexistuje
    os.makedirs('logs', exist_ok=True)
    main()


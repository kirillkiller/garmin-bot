"""
Scheduler pro měsíční reporty
"""
import time
import threading
import logging
from datetime import datetime
from typing import Callable

from report_generator import ReportGenerator


class MonthlyScheduler:
    """Scheduler pro automatické měsíční reporty"""
    
    def __init__(self):
        self.running = False
        self.thread: threading.Thread = None
        self.logger = logging.getLogger(__name__)
        self.report_generator = ReportGenerator()
    
    def start(self):
        """Spustí scheduler"""
        if self.running:
            self.logger.warning("⚠️  Monthly Scheduler již běží")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info("✅ Monthly Scheduler spuštěn")
    
    def stop(self):
        """Zastaví scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("⏹️  Monthly Scheduler zastaven")
    
    def _run(self):
        """Hlavní smyčka scheduleru"""
        last_month = None
        
        while self.running:
            try:
                current_month = datetime.now().strftime('%Y-%m')
                
                # Pokud se změnil měsíc, vygeneruj report
                if last_month and current_month != last_month:
                    self.logger.info(f"📊 Nový měsíc detekován: {current_month}")
                    self.logger.info(f"📧 Generuji měsíční report pro {last_month}...")
                    
                    try:
                        self.report_generator.send_monthly_report(last_month)
                    except Exception as e:
                        self.logger.error(f"❌ Chyba při generování měsíčního reportu: {e}")
                
                last_month = current_month
                
                # Kontroluj každou hodinu
                time.sleep(3600)
                
            except KeyboardInterrupt:
                self.logger.info("⚠️  Přerušeno uživatelem")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ Chyba v monthly scheduleru: {e}")
                time.sleep(3600)  # Počkej před dalším pokusem


"""
Task Scheduler pro pravidelné spouštění monitoringu
"""
import time
import threading
import logging
from typing import Callable, Optional


class TaskScheduler:
    """Jednoduchý scheduler pro pravidelné spouštění úloh"""
    
    def __init__(
        self,
        task: Callable,
        interval: int = 3600,
        run_immediately: bool = True
    ):
        """
        Inicializace scheduleru
        
        Args:
            task: Funkce, která se má spustit
            interval: Interval v sekundách
            run_immediately: Spustit okamžitě při startu
        """
        self.task = task
        self.interval = interval
        self.run_immediately = run_immediately
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Spustí scheduler"""
        if self.running:
            self.logger.warning("⚠️  Scheduler již běží")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info(f"✅ Scheduler spuštěn (interval: {self.interval}s)")
    
    def stop(self):
        """Zastaví scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("⏹️  Scheduler zastaven")
    
    def _run(self):
        """Hlavní smyčka scheduleru"""
        if self.run_immediately:
            try:
                self.logger.info("▶️  Spouštím úlohu okamžitě...")
                self.task()
            except Exception as e:
                self.logger.error(f"❌ Chyba při spuštění úlohy: {e}")
        
        while self.running:
            try:
                time.sleep(self.interval)
                if not self.running:
                    break
                
                self.logger.info("▶️  Spouštím naplánovanou úlohu...")
                self.task()
                
            except KeyboardInterrupt:
                self.logger.info("⚠️  Přerušeno uživatelem")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"❌ Chyba při spuštění úlohy: {e}")
                # Pokračujeme i při chybě


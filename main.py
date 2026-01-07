"""
Hlavní orchestrator pro Web Monitoring aplikaci
"""
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import komponent
from config import load_config
from scraper import WebScraper, ScrapedContent
from analyzer import GeminiAnalyzer
from storage import Database
from email_service import EmailSender


class WebMonitor:
    """Hlavní třída pro monitoring webů"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Inicializace monitoru
        
        Args:
            config_path: Cesta k konfiguračnímu souboru
        """
        # Načtení konfigurace
        self.config = load_config(config_path)
        
        # Nastavení logování
        self._setup_logging()
        
        # Inicializace komponent
        self.scraper = None
        self.analyzer = None
        self.database = None
        self.email_sender = None
        
        self._init_components()
    
    def _setup_logging(self):
        """Nastaví logování"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/monitoring.log')
        
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _init_components(self):
        """Inicializuje všechny komponenty"""
        try:
            # AI Analyzer (Gemini)
            ai_config = self.config.get('ai', {})
            self.analyzer = GeminiAnalyzer(
                api_key=ai_config.get('api_key'),
                model=ai_config.get('model', 'gemini-pro'),
                temperature=ai_config.get('temperature', 0.7),
                interesting_categories=self.config.get('interesting_categories', []),
                relevance_threshold=self.config.get('relevance_threshold', 0.7)
            )
            self.logger.info("✅ Gemini Analyzer inicializován")
            
            # Database
            db_config = self.config.get('database', {})
            self.database = Database(db_path=db_config.get('path', 'data/monitoring.db'))
            self.logger.info("✅ Database inicializována")
            
            # Email Sender
            email_config = self.config.get('email', {})
            if email_config.get('enabled', True):
                self.email_sender = EmailSender(
                    smtp_server=email_config.get('smtp_server'),
                    smtp_port=email_config.get('smtp_port', 587),
                    username=email_config.get('username'),
                    password=email_config.get('password'),
                    from_address=email_config.get('from_address'),
                    use_tls=email_config.get('use_tls', True)
                )
                self.logger.info("✅ Email Sender inicializován")
            
            # Web Scraper (bude inicializován při použití)
            scraping_config = self.config.get('scraping', {})
            self.scraping_config = scraping_config
            
        except Exception as e:
            self.logger.error(f"❌ Chyba při inicializaci komponent: {e}")
            raise
    
    def monitor_websites(self) -> List[Dict[str, Any]]:
        """
        Monitoruje všechny weby z konfigurace
        
        Returns:
            Seznam relevantních obsahů
        """
        websites = self.config.get('websites', [])
        all_relevant_contents = []
        
        # Inicializace scraperu
        self.scraper = WebScraper(
            user_agent=self.scraping_config.get('user_agent'),
            timeout=self.scraping_config.get('timeout', 30),
            headless=True
        )
        
        try:
            for website in websites:
                try:
                    self.logger.info(f"🔍 Monitoruji: {website.get('name', website.get('url'))}")
                    
                    # Scraping
                    scraped_contents = self.scraper.scrape(
                        url=website['url'],
                        selectors=website.get('selectors')
                    )
                    
                    self.logger.info(f"   Nalezeno {len(scraped_contents)} obsahů")
                    
                    # Inteligentní filtrování pomocí Gemini (pokud je zapnuto)
                    ai_config = self.config.get('ai', {})
                    if ai_config.get('use_intelligent_filtering', False) and len(scraped_contents) > 10:
                        self.logger.info("   🤖 Používám AI filtrování...")
                        contents_to_analyze = []
                        for scraped in scraped_contents:
                            contents_to_analyze.append({
                                'url': scraped.url,
                                'title': scraped.title,
                                'content': scraped.content
                            })
                        
                        filtered = self.analyzer.intelligent_filter(contents_to_analyze, max_results=20)
                        # Mapování zpět na ScrapedContent objekty
                        filtered_titles = {c['title']: c for c in filtered}
                        scraped_contents = [s for s in scraped_contents if s.title in filtered_titles]
                        self.logger.info(f"   ✅ AI vybralo {len(scraped_contents)} nejrelevantnějších obsahů")
                    
                    # Zpracování každého obsahu
                    for scraped in scraped_contents:
                        # Kontrola duplicit
                        if self.database.content_exists(scraped.hash):
                            self.logger.debug(f"   Přeskočeno (duplicitní): {scraped.title[:50]}")
                            continue
                        
                        # Uložení do databáze
                        content_id = self.database.save_scraped_content({
                            'url': scraped.url,
                            'title': scraped.title,
                            'content': scraped.content,
                            'hash': scraped.hash,
                            'timestamp': scraped.timestamp,
                            'metadata': scraped.metadata
                        })
                        
                        if content_id is None:
                            continue
                        
                        # AI analýza pomocí Gemini
                        self.logger.info(f"   🤖 Analyzuji pomocí Gemini: {scraped.title[:50]}...")
                        # Získej web-specifický prompt
                        website_prompt = website.get('ai_prompt', '')
                        analysis = self.analyzer.analyze_content(
                            url=scraped.url,
                            title=scraped.title,
                            content=scraped.content,
                            website_prompt=website_prompt
                        )
                        
                        # Vylepšení shrnutí pomocí AI (pokud je zapnuto)
                        if ai_config.get('enhance_summaries', False):
                            original_summary = analysis.get('summary', '')
                            if original_summary:
                                enhanced = self.analyzer.enhance_summary(
                                    original_summary,
                                    context=analysis
                                )
                                analysis['summary'] = enhanced
                                analysis['original_summary'] = original_summary
                        
                        # Extrakce entit (pokud je zapnuto)
                        if ai_config.get('extract_entities', False):
                            entities = self.analyzer.extract_key_entities(scraped.content)
                            analysis['entities'] = entities
                        
                        # Uložení analýzy
                        self.database.save_analysis(scraped.hash, analysis)
                        
                        # Pokud je relevantní, přidáme do seznamu
                        if analysis.get('is_relevant', False):
                            all_relevant_contents.append({
                                'scraped': {
                                    'url': scraped.url,
                                    'title': scraped.title,
                                    'content': scraped.content[:500],
                                    'hash': scraped.hash
                                },
                                'analysis': analysis
                            })
                            self.logger.info(f"   ✅ Relevantní obsah nalezen: {scraped.title[:50]}")
                        
                        # Delay mezi požadavky
                        delay = self.scraping_config.get('delay_between_requests', 2)
                        time.sleep(delay)
                    
                except Exception as e:
                    self.logger.error(f"❌ Chyba při monitorování {website.get('url')}: {e}")
                    continue
            
        finally:
            if self.scraper:
                self.scraper.close()
        
        return all_relevant_contents
    
    def send_reports(self, relevant_contents: List[Dict[str, Any]]):
        """Pošle emailové reporty pro relevantní obsahy"""
        if not self.email_sender or not relevant_contents:
            return
        
        email_config = self.config.get('email', {})
        to_addresses = email_config.get('to_addresses', [])
        
        if not to_addresses:
            self.logger.warning("⚠️  Žádné emailové adresy v konfiguraci")
            return
        
        # Seskupení podle kategorie
        by_category = {}
        for content in relevant_contents:
            category = content['analysis'].get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(content)
        
        # Odeslání reportů
        for category, contents in by_category.items():
            subject_template = email_config.get('subject_template', 'Nový relevantní obsah')
            subject = subject_template.format(category=category)
            
            # AI generované agregované shrnutí pomocí Gemini
            ai_config = self.config.get('ai', {})
            if ai_config.get('enhance_summaries', False) and len(contents) > 1:
                self.logger.info(f"   🤖 Vytvářím AI shrnutí pro {len(contents)} obsahů...")
                analyses = [c['analysis'] for c in contents]
                summary = self.analyzer.summarize_multiple(analyses)
            else:
                summary = f"Nalezeno {len(contents)} relevantních obsahů v kategorii '{category}'"
            
            # Odeslání
            success = self.email_sender.send_report(
                to_addresses=to_addresses,
                subject=subject,
                relevant_contents=contents,
                summary=summary
            )
            
            if success:
                # Označení jako odeslané
                for content in contents:
                    self.database.mark_report_sent(
                        content['scraped']['hash'],
                        subject
                    )
                self.logger.info(f"✅ Email odeslán pro kategorii: {category}")
    
    def run(self):
        """Spustí monitoring cyklus"""
        self.logger.info("🚀 Spouštím Web Monitoring...")
        
        try:
            # Monitoring
            relevant_contents = self.monitor_websites()
            
            self.logger.info(f"📊 Nalezeno {len(relevant_contents)} relevantních obsahů")
            
            # Odeslání reportů
            if relevant_contents:
                self.send_reports(relevant_contents)
            
            # Statistiky
            stats = self.database.get_statistics()
            self.logger.info(f"📈 Statistiky: {stats}")
            
        except Exception as e:
            self.logger.error(f"❌ Chyba při běhu monitoringu: {e}")
            raise


def main():
    """Hlavní funkce"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Monitoring s AI agentem')
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Cesta k konfiguračnímu souboru'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Spustit pouze jednou (bez scheduleru)'
    )
    
    args = parser.parse_args()
    
    # Vytvoření monitoru
    monitor = WebMonitor(config_path=args.config)
    
    if args.once:
        # Jednorázové spuštění
        monitor.run()
    else:
        # Scheduler
        from scheduler.task_scheduler import TaskScheduler
        
        scheduler_config = monitor.config.get('scheduler', {})
        if scheduler_config.get('enabled', True):
            scheduler = TaskScheduler(
                task=monitor.run,
                interval=scheduler_config.get('check_interval', 3600)
            )
            scheduler.start()
        else:
            monitor.run()


if __name__ == "__main__":
    main()


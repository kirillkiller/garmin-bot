"""
LinkedIn Monitoring Agent - Sleduje aktivitu konkrétních LinkedIn účtů
"""
import os
import time
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import yaml

from linkedin_scraper import LinkedInScraper
from storage.database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInMonitor:
    """Agent pro monitoring LinkedIn účtů"""
    
    def __init__(
        self,
        config_path: str = "config/linkedin_config.yaml",
        db_path: str = "data/monitoring.db"
    ):
        """
        Inicializace monitoru
        
        Args:
            config_path: Cesta ke konfiguračnímu souboru
            db_path: Cesta k databázi
        """
        self.config = self._load_config(config_path)
        self.db = Database(db_path)
        self.scraper: Optional[LinkedInScraper] = None
        self.monitored_profiles = self.config.get('monitored_profiles', [])
        
    def _load_config(self, config_path: str) -> Dict:
        """Načte konfiguraci"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            logger.warning(f"⚠️ Konfigurační soubor {config_path} neexistuje, používám výchozí nastavení")
            return {
                'monitored_profiles': [],
                'check_interval': 3600,
                'headless': False,
                'slow_mo': 100
            }
    
    def start(self):
        """Spustí monitor"""
        logger.info("🚀 Spouštění LinkedIn Monitoru...")
        
        # Získat přihlašovací údaje
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            logger.error("❌ Nastav LINKEDIN_EMAIL a LINKEDIN_PASSWORD environment variables")
            return False
        
        # Inicializovat scraper
        self.scraper = LinkedInScraper(
            headless=self.config.get('headless', False),
            slow_mo=self.config.get('slow_mo', 100)
        )
        self.scraper.start()
        
        # Přihlásit se
        if not self.scraper.login(email, password):
            logger.error("❌ Nepodařilo se přihlásit na LinkedIn")
            self.scraper.stop()
            return False
        
        logger.info("✅ LinkedIn Monitor připraven")
        return True
    
    def stop(self):
        """Zastaví monitor"""
        if self.scraper:
            self.scraper.stop()
        logger.info("✅ LinkedIn Monitor zastaven")
    
    def monitor_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Sleduje jeden profil
        
        Args:
            profile_url: URL LinkedIn profilu
            
        Returns:
            Slovník s výsledky monitoringu
        """
        logger.info(f"👁️ Monitoring profilu: {profile_url}")
        
        try:
            # Získat aktivitu profilu
            activity = self.scraper.get_profile_activity(profile_url, days_back=7)
            
            if not activity:
                logger.warning(f"⚠️ Nepodařilo se získat aktivitu pro {profile_url}")
                return {}
            
            # Uložit info o profilu
            if activity.get('profile_info'):
                self.db.save_linkedin_profile(activity['profile_info'])
            
            # Uložit posty
            new_posts = []
            existing_posts = self.db.get_linkedin_profile_posts(profile_url)
            existing_hashes = {post['post_hash'] for post in existing_posts if post.get('post_hash')}
            
            for post in activity.get('posts', []):
                post_hash = post.get('post_hash')
                if post_hash and post_hash not in existing_hashes:
                    # Nový post!
                    post_id = self.db.save_linkedin_post(post)
                    if post_id:
                        new_posts.append(post)
                        logger.info(f"🆕 Nový post nalezen: {post.get('post_url', 'N/A')}")
                        
                        # Zalogovat aktivitu
                        self.db.log_linkedin_activity(
                            profile_url,
                            'new_post',
                            {
                                'post_url': post.get('post_url'),
                                'post_text': post.get('text', '')[:200],
                                'likes': post.get('likes', 0),
                                'comments': post.get('comments', 0)
                            }
                        )
            
            # Uložit interakce
            for interaction_data in activity.get('interactions', []):
                self.db.save_linkedin_interactions(interaction_data)
                
                # Zkontrolovat nové interakce
                post_url = interaction_data.get('post_url')
                if post_url:
                    new_likes = len(interaction_data.get('likes', []))
                    new_comments = len(interaction_data.get('comments', []))
                    
                    if new_likes > 0 or new_comments > 0:
                        self.db.log_linkedin_activity(
                            profile_url,
                            'new_interactions',
                            {
                                'post_url': post_url,
                                'new_likes': new_likes,
                                'new_comments': new_comments
                            }
                        )
            
            return {
                'profile_url': profile_url,
                'new_posts': len(new_posts),
                'total_posts': len(activity.get('posts', [])),
                'interactions': len(activity.get('interactions', []))
            }
            
        except Exception as e:
            logger.error(f"❌ Chyba při monitoringu profilu {profile_url}: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def monitor_all(self) -> Dict[str, Any]:
        """
        Sleduje všechny konfigurované profily
        
        Returns:
            Slovník s výsledky
        """
        if not self.scraper or not self.scraper.is_logged_in:
            logger.error("❌ Scraper není připraven nebo není přihlášen")
            return {}
        
        results = {
            'profiles_monitored': 0,
            'total_new_posts': 0,
            'profiles': []
        }
        
        for profile_url in self.monitored_profiles:
            try:
                result = self.monitor_profile(profile_url)
                if result:
                    results['profiles_monitored'] += 1
                    results['total_new_posts'] += result.get('new_posts', 0)
                    results['profiles'].append(result)
                
                # Rate limiting mezi profily
                time.sleep(self.config.get('delay_between_profiles', 5))
                
            except Exception as e:
                logger.error(f"❌ Chyba při monitoringu {profile_url}: {e}")
                continue
        
        logger.info(f"✅ Monitoring dokončen: {results['profiles_monitored']} profilů, {results['total_new_posts']} nových postů")
        return results
    
    def get_activity_summary(self, profile_url: str, hours: int = 24) -> Dict[str, Any]:
        """
        Získá shrnutí aktivity profilu
        
        Args:
            profile_url: URL profilu
            hours: Kolik hodin zpět
            
        Returns:
            Shrnutí aktivity
        """
        activities = self.db.get_linkedin_recent_activity(profile_url, hours)
        
        summary = {
            'profile_url': profile_url,
            'period_hours': hours,
            'total_activities': len(activities),
            'new_posts': 0,
            'new_interactions': 0,
            'activities': []
        }
        
        for activity in activities:
            activity_type = activity.get('activity_type')
            if activity_type == 'new_post':
                summary['new_posts'] += 1
            elif activity_type == 'new_interactions':
                summary['new_interactions'] += 1
            
            summary['activities'].append(activity)
        
        return summary
    
    def run_once(self):
        """Spustí jeden cyklus monitoringu"""
        if not self.start():
            return
        
        try:
            results = self.monitor_all()
            logger.info(f"📊 Výsledky: {json.dumps(results, indent=2, ensure_ascii=False)}")
        finally:
            self.stop()
    
    def run_continuous(self, interval_seconds: Optional[int] = None):
        """
        Spustí kontinuální monitoring
        
        Args:
            interval_seconds: Interval mezi kontrolami (nebo z config)
        """
        if not interval_seconds:
            interval_seconds = self.config.get('check_interval', 3600)
        
        logger.info(f"🔄 Spouštění kontinuálního monitoringu (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.run_once()
                logger.info(f"⏳ Čekám {interval_seconds} sekund do další kontroly...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("🛑 Zastavování monitoringu...")
                break
            except Exception as e:
                logger.error(f"❌ Chyba v monitoringu: {e}")
                time.sleep(60)  # Krátká pauza před opakováním


def main():
    """Hlavní funkce pro spuštění z příkazové řádky"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Monitoring Agent')
    parser.add_argument('--once', action='store_true', help='Spustit pouze jednou')
    parser.add_argument('--config', default='config/linkedin_config.yaml', help='Cesta ke konfiguračnímu souboru')
    parser.add_argument('--interval', type=int, help='Interval v sekundách (pro kontinuální režim)')
    
    args = parser.parse_args()
    
    monitor = LinkedInMonitor(config_path=args.config)
    
    if args.once:
        monitor.run_once()
    else:
        monitor.run_continuous(interval_seconds=args.interval)


if __name__ == "__main__":
    main()


"""
LinkedIn Scraper - Automatizace prohlížeče pro monitoring LinkedIn účtů
"""
import time
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInScraper:
    """Scraper pro LinkedIn pomocí Playwright"""
    
    def __init__(
        self,
        headless: bool = False,
        slow_mo: int = 100,
        timeout: int = 30000
    ):
        """
        Inicializace scraperu
        
        Args:
            headless: Spustit prohlížeč v headless módu
            slow_mo: Zpoždění mezi akcemi (ms) - pomáhá vypadat přirozeněji
            timeout: Timeout pro operace (ms)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
    
    def start(self):
        """Spustí prohlížeč"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = context.new_page()
        self.context = context  # Uložit context pro pozdější použití
        logger.info("✅ Prohlížeč spuštěn")
    
    def stop(self):
        """Zastaví prohlížeč"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("✅ Prohlížeč zastaven")
    
    def login(self, email: str, password: str) -> bool:
        """
        Přihlásí se na LinkedIn
        
        Args:
            email: LinkedIn email
            password: LinkedIn heslo
            
        Returns:
            True pokud úspěšné, False jinak
        """
        try:
            logger.info("🔐 Přihlašování na LinkedIn...")
            self.page.goto("https://www.linkedin.com/login", timeout=self.timeout)
            time.sleep(2)
            
            # Vyplnění emailu
            self.page.fill('input[name="session_key"]', email)
            time.sleep(1)
            
            # Vyplnění hesla
            self.page.fill('input[name="session_password"]', password)
            time.sleep(1)
            
            # Kliknutí na přihlášení
            self.page.click('button[type="submit"]')
            time.sleep(5)
            
            # Kontrola, zda jsme přihlášeni (kontrola URL nebo elementu)
            current_url = self.page.url
            if "feed" in current_url or "linkedin.com/in/" in current_url:
                self.is_logged_in = True
                logger.info("✅ Úspěšně přihlášeno na LinkedIn")
                return True
            else:
                logger.warning("⚠️ Přihlášení možná selhalo - zkontroluj manuálně")
                return False
                
        except Exception as e:
            logger.error(f"❌ Chyba při přihlašování: {e}")
            return False
    
    def get_profile_url(self, profile_identifier: str) -> str:
        """
        Získá URL profilu z identifikátoru
        
        Args:
            profile_identifier: LinkedIn URL nebo username
            
        Returns:
            URL profilu
        """
        if profile_identifier.startswith("http"):
            return profile_identifier
        elif "/" in profile_identifier:
            return f"https://www.linkedin.com/in/{profile_identifier}"
        else:
            return f"https://www.linkedin.com/in/{profile_identifier}"
    
    def get_profile_info(self, profile_url: str) -> Dict[str, Any]:
        """
        Získá základní informace o profilu
        
        Args:
            profile_url: URL LinkedIn profilu
            
        Returns:
            Slovník s informacemi o profilu
        """
        try:
            logger.info(f"📄 Načítání profilu: {profile_url}")
            self.page.goto(profile_url, timeout=self.timeout)
            time.sleep(3)
            
            # Extrakce jména
            name = ""
            try:
                name_element = self.page.query_selector('h1.text-heading-xlarge')
                if name_element:
                    name = name_element.inner_text().strip()
            except:
                pass
            
            # Extrakce titulku
            headline = ""
            try:
                headline_element = self.page.query_selector('.text-body-medium.break-words')
                if headline_element:
                    headline = headline_element.inner_text().strip()
            except:
                pass
            
            # Extrakce počtu followerů
            followers = ""
            try:
                followers_element = self.page.query_selector('.t-black--light.t-normal')
                if followers_element:
                    followers = followers_element.inner_text().strip()
            except:
                pass
            
            return {
                "profile_url": profile_url,
                "name": name,
                "headline": headline,
                "followers": followers,
                "scraped_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Chyba při načítání profilu: {e}")
            return {}
    
    def get_recent_posts(self, profile_url: str, max_posts: int = 10) -> List[Dict[str, Any]]:
        """
        Získá nedávné posty z profilu
        
        Args:
            profile_url: URL LinkedIn profilu
            max_posts: Maximální počet postů
            
        Returns:
            Seznam postů
        """
        try:
            logger.info(f"📝 Načítání postů z: {profile_url}")
            
            # Jít na profil a scrollovat dolů
            self.page.goto(profile_url, timeout=self.timeout)
            time.sleep(3)
            
            # Scrollovat dolů pro načtení více postů
            for _ in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            posts = []
            
            # Najít všechny posty (LinkedIn struktura se může měnit)
            # Použijeme locator API pro spolehlivější práci s elementy
            post_locators = self.page.locator('.feed-shared-update-v2')
            post_count = post_locators.count()
            
            for i in range(min(post_count, max_posts)):
                try:
                    post_element = post_locators.nth(i)
                    
                    # Extrakce textu postu
                    text = ""
                    try:
                        text_locator = post_element.locator('.feed-shared-text')
                        if text_locator.count() > 0:
                            text = text_locator.first.inner_text().strip()
                    except:
                        pass
                    
                    # Extrakce času
                    post_time = ""
                    try:
                        time_locator = post_element.locator('time')
                        if time_locator.count() > 0:
                            time_elem = time_locator.first
                            post_time = time_elem.get_attribute('datetime') or time_elem.inner_text().strip()
                    except:
                        pass
                    
                    # Extrakce URL postu
                    post_url = ""
                    try:
                        link_locator = post_element.locator('a[href*="/posts/"]')
                        if link_locator.count() > 0:
                            href = link_locator.first.get_attribute('href')
                            if href:
                                post_url = f"https://www.linkedin.com{href}" if href.startswith('/') else href
                    except:
                        pass
                    
                    # Extrakce statistik (likes, comments, shares)
                    stats = self._extract_post_stats_locator(post_element)
                    
                    if text or post_url:
                        post_data = {
                            "profile_url": profile_url,
                            "text": text,
                            "post_url": post_url,
                            "post_time": post_time,
                            "likes": stats.get("likes", 0),
                            "comments": stats.get("comments", 0),
                            "shares": stats.get("shares", 0),
                            "scraped_at": datetime.now().isoformat(),
                            "post_hash": self._hash_content(text + post_url)
                        }
                        posts.append(post_data)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Chyba při extrakci postu {i}: {e}")
                    continue
            
            logger.info(f"✅ Nalezeno {len(posts)} postů")
            return posts
            
        except Exception as e:
            logger.error(f"❌ Chyba při načítání postů: {e}")
            return []
    
    def _extract_post_stats(self, post_element) -> Dict[str, int]:
        """Extrahuje statistiky postu (likes, comments, shares) - starší API"""
        stats = {"likes": 0, "comments": 0, "shares": 0}
        
        try:
            # Likes
            likes_element = post_element.query_selector('.social-actions-button--reactions')
            if likes_element:
                likes_text = likes_element.inner_text().strip()
                stats["likes"] = self._parse_number(likes_text)
        except:
            pass
        
        try:
            # Comments
            comments_element = post_element.query_selector('.social-actions-button--comments')
            if comments_element:
                comments_text = comments_element.inner_text().strip()
                stats["comments"] = self._parse_number(comments_text)
        except:
            pass
        
        try:
            # Shares
            shares_element = post_element.query_selector('.social-actions-button--share')
            if shares_element:
                shares_text = shares_element.inner_text().strip()
                stats["shares"] = self._parse_number(shares_text)
        except:
            pass
        
        return stats
    
    def _extract_post_stats_locator(self, post_locator) -> Dict[str, int]:
        """Extrahuje statistiky postu pomocí Locator API"""
        stats = {"likes": 0, "comments": 0, "shares": 0}
        
        try:
            # Likes - zkus různé selektory
            likes_selectors = [
                '.social-actions-button--reactions',
                'button[aria-label*="reaction"]',
                '.reactions-count'
            ]
            for selector in likes_selectors:
                likes_locator = post_locator.locator(selector)
                if likes_locator.count() > 0:
                    likes_text = likes_locator.first.inner_text().strip()
                    parsed = self._parse_number(likes_text)
                    if parsed > 0:
                        stats["likes"] = parsed
                        break
        except:
            pass
        
        try:
            # Comments
            comments_selectors = [
                '.social-actions-button--comments',
                'button[aria-label*="comment"]',
                '.comments-count'
            ]
            for selector in comments_selectors:
                comments_locator = post_locator.locator(selector)
                if comments_locator.count() > 0:
                    comments_text = comments_locator.first.inner_text().strip()
                    parsed = self._parse_number(comments_text)
                    if parsed > 0:
                        stats["comments"] = parsed
                        break
        except:
            pass
        
        try:
            # Shares
            shares_selectors = [
                '.social-actions-button--share',
                'button[aria-label*="share"]',
                '.shares-count'
            ]
            for selector in shares_selectors:
                shares_locator = post_locator.locator(selector)
                if shares_locator.count() > 0:
                    shares_text = shares_locator.first.inner_text().strip()
                    parsed = self._parse_number(shares_text)
                    if parsed > 0:
                        stats["shares"] = parsed
                        break
        except:
            pass
        
        return stats
    
    def _parse_number(self, text: str) -> int:
        """Parsuje číslo z textu (např. '1.2K' -> 1200)"""
        if not text:
            return 0
        
        text = text.strip().upper()
        
        # Odstranění nečíselných znaků kromě K, M
        if 'K' in text:
            num = float(text.replace('K', '').replace(',', ''))
            return int(num * 1000)
        elif 'M' in text:
            num = float(text.replace('M', '').replace(',', ''))
            return int(num * 1000000)
        else:
            # Pouze čísla
            try:
                return int(text.replace(',', ''))
            except:
                return 0
    
    def get_post_interactions(self, post_url: str) -> Dict[str, Any]:
        """
        Získá interakce na konkrétní post (komentáře, lajky, sdílení)
        
        Args:
            post_url: URL postu
            
        Returns:
            Slovník s interakcemi
        """
        try:
            logger.info(f"💬 Načítání interakcí z: {post_url}")
            self.page.goto(post_url, timeout=self.timeout)
            time.sleep(3)
            
            # Scrollovat pro načtení komentářů
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            interactions = {
                "post_url": post_url,
                "likes": [],
                "comments": [],
                "shares": [],
                "scraped_at": datetime.now().isoformat()
            }
            
            # Extrakce lajků (zobrazit všechny)
            try:
                # Kliknout na počet lajků pro zobrazení seznamu
                likes_button = self.page.query_selector('button[aria-label*="reaction"]')
                if likes_button:
                    likes_button.click()
                    time.sleep(2)
                    
                    # Extrakce jmen uživatelů, kteří lajkovali
                    likers = self.page.query_selector_all('.reactions-member-item')
                    for liker in likers:
                        try:
                            name = liker.query_selector('.reactions-member-name').inner_text().strip()
                            profile_url = ""
                            link = liker.query_selector('a')
                            if link:
                                profile_url = link.get_attribute('href')
                            interactions["likes"].append({
                                "name": name,
                                "profile_url": profile_url
                            })
                        except:
                            pass
            except:
                pass
            
            # Extrakce komentářů
            try:
                comment_elements = self.page.query_selector_all('.comments-comment-item')
                for comment_element in comment_elements:
                    try:
                        author_name = ""
                        author_url = ""
                        comment_text = ""
                        
                        author_link = comment_element.query_selector('.comments-post-meta__actor-text')
                        if author_link:
                            author_name = author_link.inner_text().strip()
                            link = author_link.query_selector('a')
                            if link:
                                author_url = link.get_attribute('href')
                        
                        text_element = comment_element.query_selector('.comments-comment-item__main-content')
                        if text_element:
                            comment_text = text_element.inner_text().strip()
                        
                        if author_name and comment_text:
                            interactions["comments"].append({
                                "author_name": author_name,
                                "author_url": author_url,
                                "comment_text": comment_text,
                                "timestamp": datetime.now().isoformat()
                            })
                    except:
                        pass
            except:
                pass
            
            logger.info(f"✅ Nalezeno {len(interactions['likes'])} lajků, {len(interactions['comments'])} komentářů")
            return interactions
            
        except Exception as e:
            logger.error(f"❌ Chyba při načítání interakcí: {e}")
            return {}
    
    def get_profile_activity(self, profile_url: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Získá kompletní aktivitu profilu
        
        Args:
            profile_url: URL LinkedIn profilu
            days_back: Kolik dní zpět sledovat
            
        Returns:
            Slovník s aktivitou
        """
        activity = {
            "profile_url": profile_url,
            "profile_info": {},
            "posts": [],
            "interactions": [],
            "scraped_at": datetime.now().isoformat()
        }
        
        # Získat info o profilu
        activity["profile_info"] = self.get_profile_info(profile_url)
        
        # Získat posty
        activity["posts"] = self.get_recent_posts(profile_url, max_posts=20)
        
        # Získat interakce pro každý post
        for post in activity["posts"][:5]:  # Limit na 5 postů pro interakce
            if post.get("post_url"):
                interactions = self.get_post_interactions(post["post_url"])
                if interactions:
                    activity["interactions"].append(interactions)
                time.sleep(2)  # Rate limiting
        
        return activity
    
    def _hash_content(self, content: str) -> str:
        """Vytvoří hash z obsahu pro detekci duplicit"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


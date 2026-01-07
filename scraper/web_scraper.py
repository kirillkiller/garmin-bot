"""
Web Scraper s podporou scrollování
"""
import time
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium není nainstalován. Pro scraping potřebuješ: pip install selenium")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️  BeautifulSoup není nainstalován. Pro lepší parsing: pip install beautifulsoup4")


@dataclass
class ScrapedContent:
    """Datová třída pro extrahovaný obsah"""
    url: str
    title: str
    content: str
    links: List[str]
    timestamp: str
    hash: str
    metadata: Dict[str, Any]


class WebScraper:
    """Web scraper s podporou scrollování a extrakce obsahu"""
    
    def __init__(
        self,
        user_agent: str = None,
        timeout: int = 30,
        headless: bool = True,
        scroll_depth: int = 3,
        wait_time: float = 2.0
    ):
        """
        Inicializace scraperu
        
        Args:
            user_agent: User agent string
            timeout: Timeout v sekundách
            headless: Spustit browser v headless módu
            scroll_depth: Kolikrát scrollovat (0 = nekonečně)
            wait_time: Čekání mezi scrollováním
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium není nainstalován")
        
        self.user_agent = user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.timeout = timeout
        self.headless = headless
        self.scroll_depth = scroll_depth
        self.wait_time = wait_time
        self.driver = None
        
    def _init_driver(self):
        """Inicializuje Selenium driver"""
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.user_agent}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as e:
                print(f"❌ Chyba při inicializaci Chrome driveru: {e}")
                print("💡 Zkontroluj, zda máš nainstalovaný ChromeDriver")
                raise
    
    def scrape(
        self,
        url: str,
        selectors: Optional[Dict[str, str]] = None
    ) -> List[ScrapedContent]:
        """
        Scrapuje web s scrollováním
        
        Args:
            url: URL k scrapování
            selectors: CSS selektory pro extrakci (title, content, links)
        
        Returns:
            Seznam extrahovaného obsahu
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium není nainstalován")
        
        self._init_driver()
        
        try:
            print(f"🔍 Scrapuji: {url}")
            self.driver.get(url)
            
            # Čekání na načtení
            time.sleep(2)
            
            # Scrollování
            self._scroll_page()
            
            # Extrakce obsahu
            contents = self._extract_content(url, selectors)
            
            return contents
            
        except Exception as e:
            print(f"❌ Chyba při scrapování {url}: {e}")
            return []
        finally:
            # Driver zůstane otevřený pro další použití
            pass
    
    def _scroll_page(self):
        """Scrolluje stránku dolů"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while True:
            # Scroll dolů
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.wait_time)
            
            # Nová výška
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            scroll_count += 1
            
            # Kontrola, zda jsme na konci nebo dosáhli scroll_depth
            if new_height == last_height:
                break
            
            if self.scroll_depth > 0 and scroll_count >= self.scroll_depth:
                break
            
            last_height = new_height
        
        # Scroll zpět nahoru
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
    
    def _extract_content(
        self,
        base_url: str,
        selectors: Optional[Dict[str, str]] = None
    ) -> List[ScrapedContent]:
        """Extrahuje obsah ze stránky"""
        if selectors is None:
            selectors = {
                "title": "h1, h2, h3",
                "content": "article, .content, p, .post, .article",
                "links": "a[href]"
            }
        
        contents = []
        
        try:
            # Použití BeautifulSoup pro lepší parsing
            if BS4_AVAILABLE:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            else:
                # Fallback na Selenium
                soup = None
            
            # Extrakce nadpisů a obsahu
            title_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors.get("title", "h1, h2"))
            content_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors.get("content", "p, article"))
            
            # Extrakce odkazů
            link_elements = self.driver.find_elements(By.CSS_SELECTOR, selectors.get("links", "a[href]"))
            links = []
            for link in link_elements:
                href = link.get_attribute("href")
                if href:
                    full_url = urljoin(base_url, href)
                    links.append(full_url)
            
            # Kombinace nadpisů a obsahu
            for i, title_elem in enumerate(title_elements[:10]):  # Max 10 článků
                title = title_elem.text.strip()
                if not title:
                    continue
                
                # Najít související obsah
                content_parts = []
                if i < len(content_elements):
                    content_parts.append(content_elements[i].text.strip())
                
                # Pokud máme BeautifulSoup, zkusíme najít více obsahu
                if soup and title_elem:
                    # Najít rodičovský element
                    try:
                        parent = title_elem.find_element(By.XPATH, "./..")
                        if parent:
                            content_parts.append(parent.text.strip())
                    except:
                        pass
                
                content = " ".join(content_parts).strip()
                if not content:
                    continue
                
                # Vytvoření hash pro detekci duplicit
                content_hash = hashlib.sha256(
                    f"{title}{content}".encode('utf-8')
                ).hexdigest()
                
                # Vytvoření ScrapedContent
                scraped = ScrapedContent(
                    url=base_url,
                    title=title,
                    content=content[:5000],  # Omezíme délku
                    links=links[:20],  # Max 20 odkazů
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    hash=content_hash,
                    metadata={
                        "selector_used": selectors,
                        "content_length": len(content)
                    }
                )
                
                contents.append(scraped)
            
            # Pokud jsme nenašli nic, zkusíme extrahovat celou stránku
            if not contents:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if page_text:
                    content_hash = hashlib.sha256(page_text.encode('utf-8')).hexdigest()
                    scraped = ScrapedContent(
                        url=base_url,
                        title=self.driver.title or "Bez nadpisu",
                        content=page_text[:5000],
                        links=links[:20],
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                        hash=content_hash,
                        metadata={"full_page": True}
                    )
                    contents.append(scraped)
            
        except Exception as e:
            print(f"⚠️  Chyba při extrakci obsahu: {e}")
        
        return contents
    
    def close(self):
        """Zavře driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


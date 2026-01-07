"""
Testovací skript pro LinkedIn monitoring
"""
import os
import sys
from linkedin_scraper import LinkedInScraper
from storage.database import Database

def test_scraper():
    """Test základní funkčnosti scraperu"""
    print("🧪 Testování LinkedIn Scraperu...\n")
    
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("❌ Nastav LINKEDIN_EMAIL a LINKEDIN_PASSWORD")
        print("   export LINKEDIN_EMAIL='tvuj-email@example.com'")
        print("   export LINKEDIN_PASSWORD='tvoje-heslo'")
        return False
    
    # Test URL (můžeš změnit)
    test_profile = "https://www.linkedin.com/in/williamhgates"
    
    print(f"📄 Testování profilu: {test_profile}\n")
    
    try:
        with LinkedInScraper(headless=False, slow_mo=200) as scraper:
            # Přihlášení
            print("🔐 Přihlašování...")
            if not scraper.login(email, password):
                print("❌ Nepodařilo se přihlásit")
                return False
            
            print("✅ Přihlášeno\n")
            
            # Získat info o profilu
            print("📊 Získávání informací o profilu...")
            profile_info = scraper.get_profile_info(test_profile)
            print(f"✅ Profil info: {profile_info.get('name', 'N/A')}")
            print(f"   Headline: {profile_info.get('headline', 'N/A')}\n")
            
            # Získat posty
            print("📝 Získávání postů...")
            posts = scraper.get_recent_posts(test_profile, max_posts=3)
            print(f"✅ Nalezeno {len(posts)} postů\n")
            
            for i, post in enumerate(posts[:2], 1):
                print(f"Post {i}:")
                print(f"  Text: {post.get('text', '')[:100]}...")
                print(f"  Likes: {post.get('likes', 0)}")
                print(f"  Comments: {post.get('comments', 0)}\n")
            
            print("✅ Test úspěšný!")
            return True
            
    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test databázových funkcí"""
    print("\n🧪 Testování databáze...\n")
    
    try:
        db = Database()
        
        # Test uložení profilu
        test_profile = {
            "profile_url": "https://www.linkedin.com/in/test",
            "name": "Test User",
            "headline": "Test Headline",
            "followers": "1000",
            "scraped_at": "2024-01-01T12:00:00"
        }
        
        profile_id = db.save_linkedin_profile(test_profile)
        print(f"✅ Profil uložen (ID: {profile_id})")
        
        # Test uložení postu
        test_post = {
            "profile_url": "https://www.linkedin.com/in/test",
            "post_url": "https://www.linkedin.com/posts/test-123",
            "text": "Test post",
            "post_time": "2024-01-01T12:00:00",
            "likes": 10,
            "comments": 5,
            "shares": 2,
            "post_hash": "test_hash_123",
            "scraped_at": "2024-01-01T12:00:00"
        }
        
        post_id = db.save_linkedin_post(test_post)
        print(f"✅ Post uložen (ID: {post_id})")
        
        # Test získání postů
        posts = db.get_linkedin_profile_posts("https://www.linkedin.com/in/test")
        print(f"✅ Získáno {len(posts)} postů z databáze")
        
        print("\n✅ Test databáze úspěšný!")
        return True
        
    except Exception as e:
        print(f"❌ Chyba: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 LinkedIn Monitoring - Test")
    print("=" * 60)
    print()
    
    # Test databáze (nevyžaduje LinkedIn přihlášení)
    db_ok = test_database()
    
    if not db_ok:
        print("\n❌ Test databáze selhal")
        sys.exit(1)
    
    # Test scraperu (vyžaduje LinkedIn přihlášení)
    print("\n" + "=" * 60)
    scraper_ok = test_scraper()
    
    if scraper_ok:
        print("\n" + "=" * 60)
        print("✅ Všechny testy úspěšné!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ Test scraperu selhal (možná chybí přihlašovací údaje)")
        print("=" * 60)


"""
Test script pro YouTube bota
"""
import sys
from youtube_bot import YouTubeBot


def test_add_channel():
    """Test přidání kanálu"""
    print("🧪 Test: Přidání kanálu")
    
    bot = YouTubeBot()
    
    # Test kanál (můžeš změnit na vlastní)
    test_channel = "https://www.youtube.com/@mkbhd"  # MKBHD jako test
    
    print(f"   Přidávám kanál: {test_channel}")
    result = bot.add_channel(test_channel)
    
    if result:
        print("   ✅ Kanál úspěšně přidán")
    else:
        print("   ❌ Chyba při přidávání kanálu")
    
    return result


def test_list_channels():
    """Test zobrazení kanálů"""
    print("\n🧪 Test: Seznam kanálů")
    
    bot = YouTubeBot()
    channels = bot.db.get_youtube_channels()
    
    print(f"   Nalezeno {len(channels)} kanálů:")
    for channel in channels:
        print(f"   - {channel['channel_name'] or channel['channel_url']}")
        print(f"     URL: {channel['channel_url']}")
    
    return len(channels) > 0


def test_get_videos():
    """Test získání videí z kanálu"""
    print("\n🧪 Test: Získání videí z kanálu")
    
    bot = YouTubeBot()
    channels = bot.db.get_youtube_channels()
    
    if not channels:
        print("   ⚠️  Žádné kanály k testování")
        return False
    
    channel_url = channels[0]['channel_url']
    print(f"   Kontroluji kanál: {channel_url}")
    
    videos = bot.get_channel_videos(channel_url, max_results=5)
    print(f"   ✅ Nalezeno {len(videos)} videí")
    
    if videos:
        print(f"   První video: {videos[0]['video_title']}")
    
    return len(videos) > 0


def test_download_transcript():
    """Test stahování transkriptu"""
    print("\n🧪 Test: Stahování transkriptu")
    
    bot = YouTubeBot()
    
    # Test video (můžeš změnit na vlastní)
    test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll jako test
    
    print(f"   Testuji video: {test_video}")
    transcript = bot.download_transcript(test_video)
    
    if transcript:
        print(f"   ✅ Transkript stažen")
        print(f"   Jazyk: {transcript['transcript_language']}")
        print(f"   Délka textu: {len(transcript['transcript_text'])} znaků")
        print(f"   Ukázka: {transcript['transcript_text'][:100]}...")
        return True
    else:
        print("   ⚠️  Transkript není dostupný (může být normální)")
        return False


def test_process_channel():
    """Test zpracování kanálu"""
    print("\n🧪 Test: Zpracování kanálu")
    
    bot = YouTubeBot()
    channels = bot.db.get_youtube_channels()
    
    if not channels:
        print("   ⚠️  Žádné kanály k testování")
        return False
    
    channel_url = channels[0]['channel_url']
    print(f"   Zpracovávám kanál: {channel_url}")
    
    stats = bot.process_channel(channel_url, max_videos=3)
    print(f"   ✅ Zpracování dokončeno:")
    print(f"      - Kontrolováno videí: {stats['videos_checked']}")
    print(f"      - Nových videí: {stats['videos_new']}")
    print(f"      - Transkriptů staženo: {stats['transcripts_downloaded']}")
    
    return True


def main():
    """Hlavní test funkce"""
    print("🚀 Spouštím testy YouTube bota\n")
    
    tests = [
        ("Přidání kanálu", test_add_channel),
        ("Seznam kanálů", test_list_channels),
        ("Získání videí", test_get_videos),
        ("Stahování transkriptu", test_download_transcript),
        ("Zpracování kanálu", test_process_channel),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Chyba: {e}")
            results.append((test_name, False))
    
    # Shrnutí
    print("\n" + "="*50)
    print("📊 Shrnutí testů:")
    print("="*50)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n✅ Úspěšných: {passed}/{total}")
    
    if passed == total:
        print("🎉 Všechny testy prošly!")
        return 0
    else:
        print("⚠️  Některé testy selhaly")
        return 1


if __name__ == "__main__":
    sys.exit(main())


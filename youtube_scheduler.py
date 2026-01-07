"""
Scheduler pro YouTube bota - automatické periodické kontroly kanálů
"""
import yaml
import logging
from pathlib import Path
from youtube_bot import YouTubeBot
from scheduler.task_scheduler import TaskScheduler


def load_config():
    """Načte konfiguraci"""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_youtube_channels():
    """Funkce pro kontrolu YouTube kanálů"""
    bot = YouTubeBot()
    config = load_config()
    
    if not config or not config.get('youtube', {}).get('enabled', False):
        logging.warning("⚠️  YouTube bot není povolen v konfiguraci")
        return
    
    youtube_config = config.get('youtube', {})
    max_videos = youtube_config.get('max_videos_per_channel', 50)
    
    # Zkontroluj všechny kanály
    stats = bot.check_all_channels(max_videos_per_channel=max_videos)
    
    logging.info(f"✅ YouTube kontrola dokončena: {stats}")


def main():
    """Hlavní funkce pro spuštění scheduleru"""
    import sys
    
    config = load_config()
    
    if not config or not config.get('youtube', {}).get('enabled', False):
        print("❌ YouTube bot není povolen v config/config.yaml")
        print("   Nastav youtube.enabled: true")
        return
    
    youtube_config = config.get('youtube', {})
    check_interval = youtube_config.get('check_interval', 3600)
    
    # Nastav logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/youtube_bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Spusť jednou a skonči
        logging.info("▶️  Spouštím jednorázovou kontrolu...")
        check_youtube_channels()
    else:
        # Spusť scheduler
        scheduler = TaskScheduler(
            task=check_youtube_channels,
            interval=check_interval,
            run_immediately=True
        )
        
        scheduler.start()
        
        try:
            print(f"✅ YouTube scheduler spuštěn (interval: {check_interval}s)")
            print("   Stiskni Ctrl+C pro zastavení")
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Zastavuji scheduler...")
            scheduler.stop()


if __name__ == "__main__":
    main()


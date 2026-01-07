"""
YouTube Bot - Monitoruje YouTube kanály a stahuje transkripty videí
"""
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

import yt_dlp
from storage.database import Database


class YouTubeBot:
    """Bot pro monitorování YouTube kanálů a stahování transkriptů"""
    
    def __init__(self, db_path: str = "data/monitoring.db", cookies_file: Optional[str] = None):
        """
        Inicializace YouTube bota
        
        Args:
            db_path: Cesta k databázi
            cookies_file: Cesta k cookies souboru (volitelné, pro obejití věkového omezení)
        """
        self.db = Database(db_path)
        self.logger = self._setup_logging()
        self.cookies_file = cookies_file or self._find_cookies_file()
        
        # Realistický user-agent (Chrome na macOS)
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        # Základní options
        base_opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'user_agent': user_agent,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],  # Použij Android client (méně restrikcí)
                }
            },
        }
        
        # Přidej cookies pokud existují
        if self.cookies_file and Path(self.cookies_file).exists():
            base_opts['cookiefile'] = self.cookies_file
            self.logger.info(f"🍪 Používám cookies z: {self.cookies_file}")
        else:
            # Zkus cookies z prohlížeče (pokud máme oprávnění)
            try:
                # Zkus Chrome cookies (nejčastější)
                base_opts['cookiesfrombrowser'] = ('chrome',)
                self.logger.info("🍪 Zkouším cookies z Chrome...")
            except:
                pass
        
        # yt-dlp options pro získání informací o videích
        self.ydl_opts_info = {
            **base_opts,
            'extract_flat': False,
        }
        
        # yt-dlp options pro stahování transkriptů
        self.ydl_opts_transcript = {
            **base_opts,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['cs', 'en', 'sk'],  # Preferujeme češtinu, angličtinu, slovenštinu
            'subtitlesformat': 'vtt',
            'skip_download': True,
        }
    
    def _find_cookies_file(self) -> Optional[str]:
        """Najde cookies soubor v běžných umístěních"""
        possible_paths = [
            'cookies.txt',
            'youtube_cookies.txt',
            'data/cookies.txt',
            Path.home() / '.youtube_cookies.txt',
        ]
        
        for path in possible_paths:
            if isinstance(path, str):
                path_obj = Path(path)
            else:
                path_obj = path
            
            if path_obj.exists():
                return str(path_obj)
        
        return None
    
    def _setup_logging(self) -> logging.Logger:
        """Nastaví logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            handler = logging.FileHandler(log_dir / "youtube_bot.log", encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Také do konzole
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def extract_channel_id(self, channel_url: str) -> Optional[str]:
        """
        Extrahuje channel ID z URL
        
        Podporuje formáty:
        - https://www.youtube.com/channel/UCxxxxx
        - https://www.youtube.com/@channelname
        - https://youtube.com/c/channelname
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_info) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                return info.get('channel_id')
        except Exception as e:
            self.logger.error(f"❌ Chyba při extrakci channel ID z {channel_url}: {e}")
            return None
    
    def extract_channel_name(self, channel_url: str) -> Optional[str]:
        """Extrahuje název kanálu z URL"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_info) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                return info.get('channel')
        except Exception as e:
            self.logger.error(f"❌ Chyba při extrakci názvu kanálu z {channel_url}: {e}")
            return None
    
    def add_channel(self, channel_url: str, channel_name: str = None) -> bool:
        """
        Přidá kanál do monitorování
        
        Args:
            channel_url: URL kanálu (různé formáty podporovány)
            channel_name: Název kanálu (volitelné, pokud se nepodaří extrahovat)
        
        Returns:
            True pokud úspěšné
        """
        self.logger.info(f"📺 Přidávám kanál: {channel_url}")
        
        # Normalizace URL
        if not channel_url.startswith('http'):
            channel_url = f"https://www.youtube.com/{channel_url}"
        
        # Zkus extrahovat channel ID a název
        channel_id = None
        extracted_name = None
        
        try:
            channel_id = self.extract_channel_id(channel_url)
            extracted_name = self.extract_channel_name(channel_url)
        except Exception as e:
            self.logger.warning(f"⚠️  Nepodařilo se extrahovat metadata, přidávám kanál bez ID: {e}")
        
        # Použij poskytnutý název nebo extrahovaný
        final_name = channel_name or extracted_name
        
        # Přidej do databáze i bez channel ID (pokud se nepodařilo extrahovat)
        db_id = self.db.add_youtube_channel(channel_url, channel_id, final_name)
        
        if db_id:
            self.logger.info(f"✅ Kanál přidán: {final_name or channel_url} (ID: {channel_id or 'N/A'})")
            return True
        else:
            self.logger.warning(f"⚠️  Kanál již existuje nebo chyba při přidávání: {channel_url}")
            return False
    
    def get_channel_videos(self, channel_url: str, max_results: int = 50, delay: float = 2.0) -> List[Dict]:
        """
        Získá seznam videí z kanálu
        
        Args:
            channel_url: URL kanálu
            max_results: Maximální počet videí
            delay: Delay mezi requesty v sekundách (pro obejití rate limitů)
        
        Returns:
            Seznam videí s metadaty
        """
        self.logger.info(f"🔍 Kontroluji kanál: {channel_url}")
        
        # Delay před requestem (simulace lidského chování)
        if delay > 0:
            time.sleep(delay)
        
        try:
            # Použijeme yt-dlp pro získání videí z kanálu
            # Použij /videos endpoint pro lepší kompatibilitu
            videos_url = channel_url.rstrip('/')
            if not videos_url.endswith('/videos'):
                videos_url = f"{videos_url}/videos"
            
            opts = {
                **self.ydl_opts_info,
                'extract_flat': 'in_playlist',
                'playlistend': max_results,
                'ignoreerrors': True,  # Ignoruj chyby u jednotlivých videí
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Získej playlist kanálu (všechna videa)
                try:
                    info = ydl.extract_info(videos_url, download=False)
                except:
                    # Zkus bez /videos
                    info = ydl.extract_info(channel_url, download=False)
                
                videos = []
                entries = info.get('entries', [])
                
                if not entries:
                    self.logger.warning("⚠️  Žádná videa nalezena")
                    return []
                
                for entry in entries:
                    if not entry:
                        continue
                    
                    video_id = entry.get('id')
                    if not video_id:
                        continue
                    
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    # Získej upload_date pokud není v flat extractu
                    upload_date = entry.get('upload_date') or entry.get('release_date', '')
                    
                    videos.append({
                        'video_id': video_id,
                        'video_url': video_url,
                        'video_title': entry.get('title', 'Neznámý název'),
                        'published_at': upload_date,
                        'duration_seconds': entry.get('duration'),
                        'view_count': entry.get('view_count'),
                    })
                
                self.logger.info(f"✅ Nalezeno {len(videos)} videí na kanálu")
                return videos
                
        except Exception as e:
            self.logger.error(f"❌ Chyba při získávání videí z kanálu {channel_url}: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return []
    
    def get_video_info(self, video_url: str, delay: float = 1.5) -> Optional[Dict]:
        """
        Získá detailní informace o videu
        
        Args:
            video_url: URL videa
            delay: Delay před requestem v sekundách
        
        Returns:
            Slovník s informacemi o videu nebo None
        """
        # Delay před requestem
        if delay > 0:
            time.sleep(delay)
        
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_info) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    return None
                
                return {
                    'video_id': info.get('id'),
                    'video_url': video_url,
                    'video_title': info.get('title', ''),
                    'video_description': info.get('description', ''),
                    'published_at': info.get('upload_date', ''),
                    'duration_seconds': info.get('duration'),
                    'view_count': info.get('view_count'),
                }
        except Exception as e:
            self.logger.error(f"❌ Chyba při získávání informací o videu {video_url}: {e}")
            return None
    
    def download_transcript(self, video_url: str, delay: float = 1.5) -> Optional[Dict]:
        """
        Stáhne transkript videa
        
        Args:
            video_url: URL videa
            delay: Delay před requestem v sekundách
        
        Returns:
            Slovník s transkriptem a jazykem, nebo None
        """
        self.logger.info(f"📝 Stahuji transkript: {video_url}")
        
        # Delay před requestem
        if delay > 0:
            time.sleep(delay)
        
        try:
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as tmpdir:
                opts = {
                    **self.ydl_opts_transcript,
                    'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                }
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    if not info:
                        return None
                    video_id = info.get('id')
                    if not video_id:
                        return None
                    
                    # Zkus stáhnout transkript
                    ydl.download([video_url])
                    
                    # Najdi stažený soubor
                    transcript_file = None
                    transcript_lang = None
                    
                    for lang in ['cs', 'en', 'sk']:
                        for ext in ['vtt', 'srt']:
                            potential_file = os.path.join(tmpdir, f"{video_id}.{lang}.{ext}")
                            if os.path.exists(potential_file):
                                transcript_file = potential_file
                                transcript_lang = lang
                                break
                        if transcript_file:
                            break
                    
                    # Pokud není žádný jazyk, zkus automatické titulky
                    if not transcript_file:
                        for ext in ['vtt', 'srt']:
                            potential_file = os.path.join(tmpdir, f"{video_id}.{ext}")
                            if os.path.exists(potential_file):
                                transcript_file = potential_file
                                transcript_lang = 'auto'
                                break
                    
                    if not transcript_file:
                        self.logger.warning(f"⚠️  Transkript není dostupný pro {video_url}")
                        return None
                    
                    # Přečti a zpracuj transkript
                    with open(transcript_file, 'r', encoding='utf-8') as f:
                        transcript_raw = f.read()
                    
                    # Zpracuj VTT formát (odstraní časové značky a formátování)
                    transcript_text = self._parse_vtt(transcript_raw)
                    
                    return {
                        'transcript_text': transcript_text,
                        'transcript_language': transcript_lang,
                        'transcript_downloaded_at': datetime.now().isoformat(),
                    }
                    
        except Exception as e:
            self.logger.error(f"❌ Chyba při stahování transkriptu {video_url}: {e}")
            return None
    
    def _parse_vtt(self, vtt_content: str) -> str:
        """
        Parsuje VTT formát a extrahuje čistý text
        
        Args:
            vtt_content: Obsah VTT souboru
        
        Returns:
            Čistý text transkriptu
        """
        lines = vtt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Přeskoč prázdné řádky, časové značky a metadata
            if not line or line.startswith('WEBVTT') or '-->' in line or line.startswith('<'):
                continue
            
            # Odstraň HTML tagy
            line = re.sub(r'<[^>]+>', '', line)
            
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)
    
    def process_channel(self, channel_url: str, max_videos: int = 50) -> Dict:
        """
        Zpracuje kanál - zkontroluje nová videa a stáhne transkripty
        
        Args:
            channel_url: URL kanálu
            max_videos: Maximální počet videí ke kontrole
        
        Returns:
            Slovník se statistikami zpracování
        """
        self.logger.info(f"🔄 Zpracovávám kanál: {channel_url}")
        
        stats = {
            'channel_url': channel_url,
            'videos_checked': 0,
            'videos_new': 0,
            'transcripts_downloaded': 0,
            'transcripts_failed': 0,
        }
        
        # Získej videa z kanálu
        videos = self.get_channel_videos(channel_url, max_videos)
        stats['videos_checked'] = len(videos)
        
        for video in videos:
            video_id = video['video_id']
            
            # Zkontroluj, zda video už máme
            if self.db.video_exists(video_id):
                continue
            
            stats['videos_new'] += 1
            self.logger.info(f"📹 Nové video: {video['video_title']}")
            
            # Získej detailní informace
            video_info = self.get_video_info(video['video_url'])
            if not video_info:
                continue
            
            # Stáhni transkript
            transcript_data = self.download_transcript(video['video_url'])
            
            if transcript_data:
                stats['transcripts_downloaded'] += 1
                video_info.update(transcript_data)
                self.logger.info(f"✅ Transkript stažen ({transcript_data['transcript_language']})")
            else:
                stats['transcripts_failed'] += 1
                self.logger.warning(f"⚠️  Nepodařilo se stáhnout transkript")
                # Ulož video i bez transkriptu
                video_info.update({
                    'transcript_text': None,
                    'transcript_language': None,
                    'transcript_downloaded_at': None,
                })
            
            # Ulož do databáze
            video_info['channel_url'] = channel_url
            self.db.save_youtube_video(video_info)
        
        # Aktualizuj čas poslední kontroly
        self.db.update_channel_last_checked(channel_url)
        
        self.logger.info(
            f"✅ Kanál zpracován: {stats['videos_new']} nových videí, "
            f"{stats['transcripts_downloaded']} transkriptů staženo"
        )
        
        return stats
    
    def check_all_channels(self, max_videos_per_channel: int = 50) -> Dict:
        """
        Zkontroluje všechny aktivní kanály
        
        Args:
            max_videos_per_channel: Maximální počet videí ke kontrole na kanál
        
        Returns:
            Celkové statistiky
        """
        self.logger.info("🚀 Spouštím kontrolu všech kanálů")
        
        channels = self.db.get_youtube_channels(active_only=True)
        
        if not channels:
            self.logger.warning("⚠️  Žádné aktivní kanály k monitorování")
            return {'channels_checked': 0, 'total_new_videos': 0, 'total_transcripts': 0}
        
        total_stats = {
            'channels_checked': len(channels),
            'total_new_videos': 0,
            'total_transcripts': 0,
            'channel_stats': [],
        }
        
        for channel in channels:
            channel_url = channel['channel_url']
            stats = self.process_channel(channel_url, max_videos_per_channel)
            total_stats['total_new_videos'] += stats['videos_new']
            total_stats['total_transcripts'] += stats['transcripts_downloaded']
            total_stats['channel_stats'].append(stats)
        
        self.logger.info(
            f"✅ Kontrola dokončena: {total_stats['channels_checked']} kanálů, "
            f"{total_stats['total_new_videos']} nových videí, "
            f"{total_stats['total_transcripts']} transkriptů"
        )
        
        return total_stats


def main():
    """Hlavní funkce pro spuštění bota"""
    import sys
    
    bot = YouTubeBot()
    
    if len(sys.argv) > 1:
        # Přidání kanálu
        if sys.argv[1] == 'add':
            if len(sys.argv) < 3:
                print("❌ Použití: python youtube_bot.py add <channel_url>")
                return
            
            channel_url = sys.argv[2]
            bot.add_channel(channel_url)
        
        # Kontrola všech kanálů
        elif sys.argv[1] == 'check':
            bot.check_all_channels()
        
        # Zobrazení kanálů
        elif sys.argv[1] == 'list':
            channels = bot.db.get_youtube_channels()
            print(f"\n📺 Monitorované kanály ({len(channels)}):\n")
            for channel in channels:
                status = "✅ Aktivní" if channel['is_active'] else "⏸️  Neaktivní"
                print(f"  {status} - {channel['channel_name'] or channel['channel_url']}")
                print(f"    URL: {channel['channel_url']}")
                if channel['last_checked_at']:
                    print(f"    Poslední kontrola: {channel['last_checked_at']}")
                print()
        
        # Zobrazení videí
        elif sys.argv[1] == 'videos':
            channel_url = sys.argv[2] if len(sys.argv) > 2 else None
            videos = bot.db.get_youtube_videos(channel_url=channel_url, limit=20)
            print(f"\n📹 Videa ({len(videos)}):\n")
            for video in videos:
                has_transcript = "✅" if video['transcript_text'] else "❌"
                print(f"  {has_transcript} {video['video_title']}")
                print(f"    URL: {video['video_url']}")
                print(f"    Publikováno: {video['published_at']}")
                if video['transcript_language']:
                    print(f"    Transkript: {video['transcript_language']}")
                print()
        
        else:
            print("❌ Neznámý příkaz")
            print("Použití:")
            print("  python youtube_bot.py add <channel_url>  - Přidá kanál")
            print("  python youtube_bot.py check              - Zkontroluje všechny kanály")
            print("  python youtube_bot.py list               - Zobrazí kanály")
            print("  python youtube_bot.py videos [channel]   - Zobrazí videa")
    else:
        # Výchozí: kontrola všech kanálů
        bot.check_all_channels()


if __name__ == "__main__":
    main()


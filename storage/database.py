"""
Database modul pro ukládání zpracovaných informací
"""
import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class Database:
    """Třída pro práci s databází"""
    
    def __init__(self, db_path: str = "data/monitoring.db"):
        """
        Inicializace databáze
        
        Args:
            db_path: Cesta k SQLite databázi
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializuje databázové tabulky"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabulka pro extrahovaný obsah
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                content_hash TEXT UNIQUE NOT NULL,
                timestamp TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabulka pro analýzy
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT NOT NULL,
                category TEXT,
                relevance_score REAL,
                summary TEXT,
                key_points TEXT,
                is_relevant INTEGER,
                reasoning TEXT,
                analysis_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_hash) REFERENCES scraped_content(content_hash)
            )
        """)
        
        # Tabulka pro odeslané emaily
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT NOT NULL,
                email_subject TEXT,
                sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_hash) REFERENCES scraped_content(content_hash)
            )
        """)
        
        # Tabulka pro uložené reporty
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                report_data TEXT,
                summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabulka pro email reporty
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                start_date TEXT NOT NULL,
                period_days INTEGER DEFAULT 30,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # LinkedIn Monitoring tabulky
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT UNIQUE NOT NULL,
                name TEXT,
                headline TEXT,
                followers TEXT,
                last_scraped_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT NOT NULL,
                post_url TEXT UNIQUE,
                post_text TEXT,
                post_time TEXT,
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                post_hash TEXT UNIQUE NOT NULL,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_url) REFERENCES linkedin_profiles(profile_url)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_url TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                actor_name TEXT,
                actor_url TEXT,
                interaction_content TEXT,
                timestamp TEXT,
                scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_url) REFERENCES linkedin_posts(post_url)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linkedin_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_url) REFERENCES linkedin_profiles(profile_url)
            )
        """)
        
        # Indexy pro rychlejší vyhledávání
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON scraped_content(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_hash ON analyses(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_hash ON sent_reports(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_relevant ON analyses(is_relevant)")
        
        # LinkedIn indexy
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_profile_url ON linkedin_profiles(profile_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_post_url ON linkedin_posts(post_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_post_hash ON linkedin_posts(post_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_interaction_post ON linkedin_interactions(post_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_activity_profile ON linkedin_activity_log(profile_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_linkedin_activity_detected ON linkedin_activity_log(detected_at)")
        
        # YouTube Monitoring tabulky
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_url TEXT UNIQUE NOT NULL,
                channel_id TEXT,
                channel_name TEXT,
                last_checked_at TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_url TEXT NOT NULL,
                video_id TEXT UNIQUE NOT NULL,
                video_url TEXT NOT NULL,
                video_title TEXT,
                video_description TEXT,
                published_at TEXT,
                duration_seconds INTEGER,
                view_count INTEGER,
                transcript_text TEXT,
                transcript_language TEXT,
                transcript_downloaded_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_url) REFERENCES youtube_channels(channel_url)
            )
        """)
        
        # Indexy pro YouTube
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_youtube_channel_url ON youtube_channels(channel_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_youtube_video_id ON youtube_videos(video_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_youtube_video_channel ON youtube_videos(channel_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_youtube_video_published ON youtube_videos(published_at)")
        
        conn.commit()
        conn.close()
    
    def content_exists(self, content_hash: str) -> bool:
        """Zkontroluje, zda obsah již existuje"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM scraped_content WHERE content_hash = ?", (content_hash,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_scraped_content(self, scraped_data: Dict) -> Optional[int]:
        """
        Uloží extrahovaný obsah
        
        Args:
            scraped_data: Slovník s daty (url, title, content, hash, timestamp, metadata)
        
        Returns:
            ID uloženého záznamu nebo None pokud již existuje
        """
        content_hash = scraped_data.get('hash')
        if not content_hash:
            return None
        
        if self.content_exists(content_hash):
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO scraped_content 
                (url, title, content, content_hash, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                scraped_data.get('url'),
                scraped_data.get('title'),
                scraped_data.get('content'),
                content_hash,
                scraped_data.get('timestamp'),
                json.dumps(scraped_data.get('metadata', {}))
            ))
            
            content_id = cursor.lastrowid
            conn.commit()
            return content_id
            
        except sqlite3.IntegrityError:
            # Duplicitní hash
            return None
        finally:
            conn.close()
    
    def save_analysis(self, content_hash: str, analysis: Dict) -> Optional[int]:
        """
        Uloží analýzu obsahu
        
        Args:
            content_hash: Hash obsahu
            analysis: Slovník s analýzou
        
        Returns:
            ID uložené analýzy
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO analyses 
                (content_hash, category, relevance_score, summary, key_points, 
                 is_relevant, reasoning, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_hash,
                analysis.get('category'),
                analysis.get('relevance_score'),
                analysis.get('summary'),
                json.dumps(analysis.get('key_points', [])),
                1 if analysis.get('is_relevant') else 0,
                analysis.get('reasoning'),
                json.dumps(analysis)
            ))
            
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id
            
        except Exception as e:
            print(f"❌ Chyba při ukládání analýzy: {e}")
            return None
        finally:
            conn.close()
    
    def mark_report_sent(self, content_hash: str, email_subject: str):
        """Označí, že report byl odeslán"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sent_reports (content_hash, email_subject)
            VALUES (?, ?)
        """, (content_hash, email_subject))
        
        conn.commit()
        conn.close()
    
    def get_all_analyses(
        self,
        limit: int = 1000,
        since: Optional[str] = None,
        exclude_months: Optional[List[str]] = None,
        only_relevant: bool = False
    ) -> List[Dict]:
        """
        Získá všechny analýzy (nebo jen relevantní)
        
        Args:
            limit: Maximální počet záznamů
            since: Datum od (YYYY-MM-DD)
            exclude_months: Seznam měsíců (YYYY-MM), které se mají vyloučit
            only_relevant: Pokud True, pouze relevantní obsahy
        
        Returns:
            Seznam obsahů s analýzami
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                sc.id, sc.url, sc.title, sc.content, sc.content_hash, sc.timestamp,
                a.category, a.relevance_score, a.summary, a.key_points, 
                a.is_relevant, a.reasoning, a.analysis_data, a.created_at
            FROM scraped_content sc
            JOIN analyses a ON sc.content_hash = a.content_hash
            WHERE 1=1
        """
        
        params = []
        if only_relevant:
            query += " AND a.is_relevant = 1"
        
        if since:
            query += " AND a.created_at >= ?"
            params.append(since)
        
        # Vyloučit obsahy z předchozích měsíců, které už byly v reportech
        if exclude_months:
            placeholders = ','.join(['?' for _ in exclude_months])
            query += f" AND strftime('%Y-%m', a.created_at) NOT IN ({placeholders})"
            params.extend(exclude_months)
        
        query += " ORDER BY a.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'url': row['url'],
                'title': row['title'],
                'content': row['content'],
                'hash': row['content_hash'],
                'timestamp': row['timestamp'],
                'created_at': row['created_at'],
                'analysis': {
                    'category': row['category'],
                    'relevance_score': row['relevance_score'],
                    'summary': row['summary'],
                    'key_points': json.loads(row['key_points']) if row['key_points'] else [],
                    'is_relevant': bool(row['is_relevant']),
                    'reasoning': row['reasoning'],
                    'full_data': json.loads(row['analysis_data']) if row['analysis_data'] else {}
                }
            })
        
        return results
    
    def get_relevant_contents(
        self,
        limit: int = 100,
        since: Optional[str] = None,
        exclude_months: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Získá relevantní obsahy
        
        Args:
            limit: Maximální počet záznamů
            since: Datum od (YYYY-MM-DD)
            exclude_months: Seznam měsíců (YYYY-MM), které se mají vyloučit
        
        Returns:
            Seznam relevantních obsahů s analýzami
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                sc.id, sc.url, sc.title, sc.content, sc.content_hash, sc.timestamp,
                a.category, a.relevance_score, a.summary, a.key_points, 
                a.is_relevant, a.reasoning, a.analysis_data, a.created_at
            FROM scraped_content sc
            JOIN analyses a ON sc.content_hash = a.content_hash
            WHERE a.is_relevant = 1
        """
        
        params = []
        if since:
            query += " AND a.created_at >= ?"
            params.append(since)
        
        # Vyloučit obsahy z předchozích měsíců, které už byly v reportech
        if exclude_months:
            placeholders = ','.join(['?' for _ in exclude_months])
            query += f" AND strftime('%Y-%m', a.created_at) NOT IN ({placeholders})"
            params.extend(exclude_months)
        
        query += " ORDER BY a.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'url': row['url'],
                'title': row['title'],
                'content': row['content'],
                'hash': row['content_hash'],
                'timestamp': row['timestamp'],
                'created_at': row['created_at'],
                'analysis': {
                    'category': row['category'],
                    'relevance_score': row['relevance_score'],
                    'summary': row['summary'],
                    'key_points': json.loads(row['key_points']) if row['key_points'] else [],
                    'is_relevant': bool(row['is_relevant']),
                    'reasoning': row['reasoning'],
                    'full_data': json.loads(row['analysis_data']) if row['analysis_data'] else {}
                }
            })
        
        return results
    
    def _get_connection(self):
        """Vrátí connection pro externí použití"""
        return sqlite3.connect(self.db_path)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Získá statistiky z databáze"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Celkový počet obsahů
        cursor.execute("SELECT COUNT(*) FROM scraped_content")
        stats['total_contents'] = cursor.fetchone()[0]
        
        # Počet analýz
        cursor.execute("SELECT COUNT(*) FROM analyses")
        stats['total_analyses'] = cursor.fetchone()[0]
        
        # Počet relevantních
        cursor.execute("SELECT COUNT(*) FROM analyses WHERE is_relevant = 1")
        stats['relevant_contents'] = cursor.fetchone()[0]
        
        # Počet odeslaných reportů
        cursor.execute("SELECT COUNT(*) FROM sent_reports")
        stats['sent_reports'] = cursor.fetchone()[0]
        
        # Kategorie
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM analyses 
            WHERE is_relevant = 1 
            GROUP BY category 
            ORDER BY count DESC
        """)
        stats['categories'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    # YouTube metody
    def add_youtube_channel(self, channel_url: str, channel_id: str = None, channel_name: str = None) -> Optional[int]:
        """Přidá YouTube kanál do databáze"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO youtube_channels (channel_url, channel_id, channel_name)
                VALUES (?, ?, ?)
            """, (channel_url, channel_id, channel_name))
            
            if cursor.rowcount > 0:
                channel_id_db = cursor.lastrowid
            else:
                cursor.execute("SELECT id FROM youtube_channels WHERE channel_url = ?", (channel_url,))
                row = cursor.fetchone()
                channel_id_db = row[0] if row else None
            
            conn.commit()
            return channel_id_db
        except Exception as e:
            print(f"❌ Chyba při přidávání kanálu: {e}")
            return None
        finally:
            conn.close()
    
    def get_youtube_channels(self, active_only: bool = True) -> List[Dict]:
        """Získá seznam YouTube kanálů"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM youtube_channels"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_channel_last_checked(self, channel_url: str):
        """Aktualizuje čas poslední kontroly kanálu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE youtube_channels 
            SET last_checked_at = CURRENT_TIMESTAMP 
            WHERE channel_url = ?
        """, (channel_url,))
        
        conn.commit()
        conn.close()
    
    def video_exists(self, video_id: str) -> bool:
        """Zkontroluje, zda video již existuje v databázi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM youtube_videos WHERE video_id = ?", (video_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_youtube_video(self, video_data: Dict) -> Optional[int]:
        """Uloží YouTube video a jeho transkript"""
        if self.video_exists(video_data.get('video_id')):
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO youtube_videos 
                (channel_url, video_id, video_url, video_title, video_description,
                 published_at, duration_seconds, view_count, transcript_text,
                 transcript_language, transcript_downloaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_data.get('channel_url'),
                video_data.get('video_id'),
                video_data.get('video_url'),
                video_data.get('video_title'),
                video_data.get('video_description'),
                video_data.get('published_at'),
                video_data.get('duration_seconds'),
                video_data.get('view_count'),
                video_data.get('transcript_text'),
                video_data.get('transcript_language'),
                video_data.get('transcript_downloaded_at')
            ))
            
            video_id_db = cursor.lastrowid
            conn.commit()
            return video_id_db
        except Exception as e:
            print(f"❌ Chyba při ukládání videa: {e}")
            return None
        finally:
            conn.close()
    
    def get_youtube_videos(
        self,
        channel_url: str = None,
        limit: int = 100,
        with_transcript: bool = None
    ) -> List[Dict]:
        """Získá seznam YouTube videí"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM youtube_videos WHERE 1=1"
        params = []
        
        if channel_url:
            query += " AND channel_url = ?"
            params.append(channel_url)
        
        if with_transcript is not None:
            if with_transcript:
                query += " AND transcript_text IS NOT NULL AND transcript_text != ''"
            else:
                query += " AND (transcript_text IS NULL OR transcript_text = '')"
        
        query += " ORDER BY published_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # LinkedIn Monitoring metody
    
    def save_linkedin_profile(self, profile_data: Dict) -> Optional[int]:
        """Uloží nebo aktualizuje LinkedIn profil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO linkedin_profiles 
                (profile_url, name, headline, followers, last_scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                profile_data.get('profile_url'),
                profile_data.get('name'),
                profile_data.get('headline'),
                profile_data.get('followers'),
                profile_data.get('scraped_at')
            ))
            
            profile_id = cursor.lastrowid
            conn.commit()
            return profile_id
        except Exception as e:
            print(f"❌ Chyba při ukládání profilu: {e}")
            return None
        finally:
            conn.close()
    
    def save_linkedin_post(self, post_data: Dict) -> Optional[int]:
        """Uloží LinkedIn post (pokud ještě neexistuje)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            post_hash = post_data.get('post_hash')
            if not post_hash:
                return None
            
            # Zkontrolovat, zda už existuje
            cursor.execute("SELECT id FROM linkedin_posts WHERE post_hash = ?", (post_hash,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
            
            cursor.execute("""
                INSERT INTO linkedin_posts 
                (profile_url, post_url, post_text, post_time, likes_count, 
                 comments_count, shares_count, post_hash, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data.get('profile_url'),
                post_data.get('post_url'),
                post_data.get('text'),
                post_data.get('post_time'),
                post_data.get('likes', 0),
                post_data.get('comments', 0),
                post_data.get('shares', 0),
                post_hash,
                post_data.get('scraped_at')
            ))
            
            post_id = cursor.lastrowid
            conn.commit()
            return post_id
        except sqlite3.IntegrityError:
            # Duplicitní post
            return None
        except Exception as e:
            print(f"❌ Chyba při ukládání postu: {e}")
            return None
        finally:
            conn.close()
    
    def save_linkedin_interactions(self, interactions_data: Dict):
        """Uloží interakce z postu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        post_url = interactions_data.get('post_url')
        if not post_url:
            conn.close()
            return
        
        try:
            # Uložit lajky
            for like in interactions_data.get('likes', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO linkedin_interactions
                    (post_url, interaction_type, actor_name, actor_url, timestamp)
                    VALUES (?, 'like', ?, ?, ?)
                """, (
                    post_url,
                    like.get('name'),
                    like.get('profile_url'),
                    interactions_data.get('scraped_at')
                ))
            
            # Uložit komentáře
            for comment in interactions_data.get('comments', []):
                cursor.execute("""
                    INSERT OR IGNORE INTO linkedin_interactions
                    (post_url, interaction_type, actor_name, actor_url, interaction_content, timestamp)
                    VALUES (?, 'comment', ?, ?, ?, ?)
                """, (
                    post_url,
                    comment.get('author_name'),
                    comment.get('author_url'),
                    comment.get('comment_text'),
                    comment.get('timestamp')
                ))
            
            conn.commit()
        except Exception as e:
            print(f"❌ Chyba při ukládání interakcí: {e}")
        finally:
            conn.close()
    
    def log_linkedin_activity(self, profile_url: str, activity_type: str, activity_data: Dict):
        """Zaloguje novou aktivitu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO linkedin_activity_log
                (profile_url, activity_type, activity_data)
                VALUES (?, ?, ?)
            """, (
                profile_url,
                activity_type,
                json.dumps(activity_data)
            ))
            conn.commit()
        except Exception as e:
            print(f"❌ Chyba při logování aktivity: {e}")
        finally:
            conn.close()
    
    def get_linkedin_profile_posts(self, profile_url: str, limit: int = 50) -> List[Dict]:
        """Získá posty z profilu"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM linkedin_posts
            WHERE profile_url = ?
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (profile_url, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_linkedin_recent_activity(self, profile_url: str, hours: int = 24) -> List[Dict]:
        """Získá nedávnou aktivitu profilu"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM linkedin_activity_log
            WHERE profile_url = ? 
            AND datetime(detected_at) >= datetime('now', '-' || ? || ' hours')
            ORDER BY detected_at DESC
        """, (profile_url, hours))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            result = dict(row)
            result['activity_data'] = json.loads(result['activity_data']) if result['activity_data'] else {}
            results.append(result)
        
        return results
    
    def get_linkedin_new_posts(self, profile_url: str, since: str) -> List[Dict]:
        """Získá nové posty od určitého času"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM linkedin_posts
            WHERE profile_url = ? 
            AND datetime(scraped_at) >= datetime(?)
            ORDER BY scraped_at DESC
        """, (profile_url, since))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


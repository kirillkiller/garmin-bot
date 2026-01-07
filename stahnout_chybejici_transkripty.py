#!/usr/bin/env python3
"""Stáhne chybějící transkripty s cookies"""
from youtube_bot import YouTubeBot
from storage.database import Database
import sqlite3

def main():
    bot = YouTubeBot()
    db = Database()
    
    # Najdi videa bez transkriptů z kanálu Vojta Zizka
    videos = db.get_youtube_videos(
        channel_url='https://www.youtube.com/@VojtaZizka', 
        with_transcript=False
    )
    
    print(f'📹 Nalezeno {len(videos)} videí bez transkriptů\n')
    
    success = 0
    failed = 0
    
    for i, video in enumerate(videos, 1):
        print(f'[{i}/{len(videos)}] {video["video_title"][:60]}...')
        
        transcript = bot.download_transcript(video['video_url'])
        if transcript:
            print(f'   ✅ Transkript stažen ({transcript["transcript_language"]})')
            # Aktualizuj v databázi
            conn = sqlite3.connect('data/monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE youtube_videos 
                SET transcript_text = ?, transcript_language = ?, transcript_downloaded_at = ?
                WHERE video_id = ?
            ''', (
                transcript['transcript_text'], 
                transcript['transcript_language'], 
                transcript['transcript_downloaded_at'], 
                video['video_id']
            ))
            conn.commit()
            conn.close()
            success += 1
        else:
            print(f'   ⚠️  Transkript nedostupný')
            failed += 1
        print()
    
    print(f'\n✅ Hotovo: {success} staženo, {failed} nedostupných')

if __name__ == "__main__":
    main()


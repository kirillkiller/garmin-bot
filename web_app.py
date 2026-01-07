"""
Webové rozhraní pro správu Web Monitoring aplikace
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import yaml
from typing import Dict, List, Any

from config import load_config
from main import WebMonitor
from storage import Database
import sqlite3

app = Flask(__name__)
CORS(app)

# Globální instance monitoru
monitor = None
db = None

def init_app():
    """Inicializace aplikace"""
    global monitor, db
    
    try:
        config_path = "config/config.yaml"
        monitor = WebMonitor(config_path=config_path)
        db = monitor.database
    except Exception as e:
        print(f"⚠️  Chyba při inicializaci: {e}")
        print("💡 Použijeme pouze databázi bez monitoru")
        from storage import Database
        db = Database()

@app.route('/')
def index():
    """Hlavní stránka"""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Získá status aplikace"""
    try:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/websites', methods=['GET'])
def get_websites():
    """Získá seznam monitorovaných webů"""
    try:
        config = load_config()
        websites = config.get('websites', [])
        return jsonify({
            'success': True,
            'websites': websites
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/websites', methods=['POST'])
def add_website():
    """Přidá nový web k monitorování"""
    try:
        data = request.json
        config_path = Path("config/config.yaml")
        
        # Načti konfiguraci
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Přidej nový web
        new_website = {
            'url': data.get('url'),
            'name': data.get('name', data.get('url')),
            'scroll_depth': data.get('scroll_depth', 5),
            'wait_time': data.get('wait_time', 2),
            'ai_prompt': data.get('ai_prompt', ''),  # AI prompt pro tento web
            'selectors': data.get('selectors', {
                'title': 'h1, h2, h3',
                'content': 'article, .content, p',
                'links': 'a[href]'
            })
        }
        
        if 'websites' not in config:
            config['websites'] = []
        
        config['websites'].append(new_website)
        
        # Ulož konfiguraci
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        # Reinit monitor
        global monitor
        monitor = WebMonitor(config_path=str(config_path))
        
        return jsonify({
            'success': True,
            'message': 'Web přidán úspěšně',
            'website': new_website
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/websites/<int:index>', methods=['DELETE'])
def delete_website(index):
    """Odstraní web z monitorování"""
    try:
        config_path = Path("config/config.yaml")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if 'websites' in config and 0 <= index < len(config['websites']):
            deleted = config['websites'].pop(index)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            
            # Reinit monitor
            global monitor
            monitor = WebMonitor(config_path=str(config_path))
            
            return jsonify({
                'success': True,
                'message': 'Web odstraněn',
                'website': deleted
            })
        else:
            return jsonify({'success': False, 'error': 'Index mimo rozsah'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/prompt', methods=['GET'])
def get_prompt():
    """Získá aktuální AI prompt"""
    try:
        # Načti prompt z analyzer souboru nebo konfigurace
        prompt_file = Path("config/ai_prompt.txt")
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            # Default prompt
            prompt = """Analyzuj následující webový obsah a poskytni strukturovanou analýzu v JSON formátu."""
        
        return jsonify({
            'success': True,
            'prompt': prompt
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/prompt', methods=['POST'])
def update_prompt():
    """Aktualizuje AI prompt"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        # Ulož prompt
        prompt_file = Path("config/ai_prompt.txt")
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        return jsonify({
            'success': True,
            'message': 'Prompt aktualizován'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Získá seznam reportů"""
    try:
        # Získej relevantní obsahy z posledního měsíce
        since = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        contents = db.get_relevant_contents(limit=1000, since=since)
        
        # Seskup podle měsíce
        reports_by_month = {}
        for content in contents:
            timestamp = content.get('timestamp', '')
            if timestamp:
                month_key = timestamp[:7]  # YYYY-MM
                if month_key not in reports_by_month:
                    reports_by_month[month_key] = []
                reports_by_month[month_key].append(content)
        
        return jsonify({
            'success': True,
            'reports': reports_by_month,
            'total': len(contents)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Vygeneruje report na požádání"""
    try:
        from report_enhancer import ReportEnhancer
        from report_generator import ReportGenerator
        
        data = request.json or {}
        month = data.get('month')  # YYYY-MM formát nebo prázdné pro poslední měsíc
        
        # Pokud není měsíc, použij poslední měsíc
        if not month:
            from datetime import datetime, timedelta
            last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
            month = last_month
        
        generator = ReportGenerator()
        report_data = generator.generate_monthly_report(month)
        
        # Vytvoř vylepšený report s highlights
        enhancer = ReportEnhancer()
        enhanced_report = enhancer.create_enhanced_report(
            month, 
            report_data['contents'],  # Všechny obsahy
            report_data.get('relevant', [])  # Relevantní pro highlights
        )
        
        # Ulož report do databáze
        try:
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO saved_reports (month, report_data, summary)
                VALUES (?, ?, ?)
            """, (month, json.dumps(enhanced_report, ensure_ascii=False), enhanced_report.get('highlights', '')[:500]))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Chyba při ukládání reportu: {e}")
        
        return jsonify({
            'success': True,
            'report': enhanced_report
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/list', methods=['GET'])
def list_reports():
    """Získá seznam uložených reportů"""
    try:
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT month, summary, created_at 
            FROM saved_reports 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        reports = []
        for row in rows:
            reports.append({
                'month': row['month'],
                'summary_preview': row['summary'][:200] + '...' if len(row['summary']) > 200 else row['summary'],
                'created_at': row['created_at']
            })
        
        return jsonify({
            'success': True,
            'reports': reports
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/<month>', methods=['GET'])
def get_report(month):
    """Získá detail reportu pro konkrétní měsíc"""
    try:
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT report_data, summary 
            FROM saved_reports 
            WHERE month = ?
        """, (month,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            report_data = json.loads(row['report_data'])
            return jsonify({
                'success': True,
                'report': report_data
            })
        else:
            return jsonify({'success': False, 'error': 'Report nenalezen'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Získá seznam email subscriptions"""
    try:
        conn = db._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, start_date, period_days, is_active, created_at
            FROM email_subscriptions
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        emails = []
        for row in rows:
            emails.append({
                'id': row['id'],
                'email': row['email'],
                'start_date': row['start_date'],
                'period_days': row['period_days'],
                'is_active': bool(row['is_active']),
                'created_at': row['created_at']
            })
        
        return jsonify({
            'success': True,
            'emails': emails
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emails', methods=['POST'])
def add_email():
    """Přidá email subscription"""
    try:
        data = request.json
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO email_subscriptions (email, start_date, period_days)
            VALUES (?, ?, ?)
        """, (
            data.get('email'),
            data.get('start_date'),
            data.get('period_days', 30)
        ))
        conn.commit()
        conn.close()
        
        # Vygeneruj report hned
        from report_enhancer import ReportEnhancer
        from report_generator import ReportGenerator
        
        generator = ReportGenerator()
        enhancer = ReportEnhancer()
        
        # Získej aktuální měsíc
        current_month = datetime.now().strftime('%Y-%m')
        report_data = generator.generate_monthly_report(current_month)
        enhanced_report = enhancer.create_enhanced_report(current_month, report_data['contents'])
        
        # Pošli email
        email_config = load_config().get('email', {})
        if email_config.get('enabled', False):
            from email_service import EmailSender
            email_sender = EmailSender(
                smtp_server=email_config.get('smtp_server'),
                smtp_port=email_config.get('smtp_port', 587),
                username=email_config.get('username'),
                password=email_config.get('password'),
                from_address=email_config.get('from_address'),
                use_tls=email_config.get('use_tls', True)
            )
            
            email_sender.send_report(
                to_addresses=[data.get('email')],
                subject=f"📊 Daňový Report - {current_month}",
                relevant_contents=enhanced_report['all_contents'],
                summary=enhanced_report['legal_summary']
            )
        
        return jsonify({
            'success': True,
            'message': 'Email přidán a report odeslán'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/emails/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    """Odstraní email subscription"""
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM email_subscriptions WHERE id = ?", (email_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Email odstraněn'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/monitor/run', methods=['POST'])
def run_monitoring():
    """Spustí monitoring na požádání"""
    try:
        global monitor
        if monitor is None:
            monitor = WebMonitor()
        
        # Spusť monitoring
        relevant_contents = monitor.monitor_websites()
        
        return jsonify({
            'success': True,
            'message': 'Monitoring dokončen',
            'relevant_contents': len(relevant_contents),
            'contents': relevant_contents[:10]  # Prvních 10 pro náhled
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# YouTube endpoints
@app.route('/api/youtube/channels', methods=['GET'])
def get_youtube_channels():
    """Získá seznam monitorovaných YouTube kanálů"""
    try:
        channels = db.get_youtube_channels(active_only=False)
        return jsonify({
            'success': True,
            'channels': channels
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/youtube/videos', methods=['GET'])
def get_youtube_videos():
    """Získá seznam YouTube videí"""
    try:
        channel_url = request.args.get('channel_url')
        limit = int(request.args.get('limit', 100))
        with_transcript = request.args.get('with_transcript')
        
        with_transcript_bool = None
        if with_transcript is not None:
            with_transcript_bool = with_transcript.lower() == 'true'
        
        videos = db.get_youtube_videos(
            channel_url=channel_url,
            limit=limit,
            with_transcript=with_transcript_bool
        )
        
        return jsonify({
            'success': True,
            'videos': videos,
            'total': len(videos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/youtube/videos/<video_id>/transcript', methods=['GET'])
def get_video_transcript(video_id):
    """Získá transkript konkrétního videa"""
    try:
        videos = db.get_youtube_videos(limit=10000)  # Získej všechna videa
        video = next((v for v in videos if v['video_id'] == video_id), None)
        
        if not video:
            return jsonify({'success': False, 'error': 'Video nenalezeno'}), 404
        
        return jsonify({
            'success': True,
            'video': {
                'video_id': video['video_id'],
                'video_title': video['video_title'],
                'video_url': video['video_url'],
                'transcript_text': video.get('transcript_text'),
                'transcript_language': video.get('transcript_language'),
                'transcript_downloaded_at': video.get('transcript_downloaded_at'),
                'published_at': video.get('published_at'),
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/youtube/stats', methods=['GET'])
def get_youtube_stats():
    """Získá statistiky YouTube videí"""
    try:
        conn = db._get_connection()
        cursor = conn.cursor()
        
        # Celkový počet videí
        cursor.execute("SELECT COUNT(*) FROM youtube_videos")
        total_videos = cursor.fetchone()[0]
        
        # Videa s transkripty
        cursor.execute("SELECT COUNT(*) FROM youtube_videos WHERE transcript_text IS NOT NULL AND transcript_text != ''")
        videos_with_transcripts = cursor.fetchone()[0]
        
        # Videa bez transkriptů
        videos_without_transcripts = total_videos - videos_with_transcripts
        
        # Počet kanálů
        cursor.execute("SELECT COUNT(*) FROM youtube_channels WHERE is_active = 1")
        active_channels = cursor.fetchone()[0]
        
        # Videa podle kanálu
        cursor.execute("""
            SELECT channel_url, COUNT(*) as count 
            FROM youtube_videos 
            GROUP BY channel_url
        """)
        videos_by_channel = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_videos': total_videos,
                'videos_with_transcripts': videos_with_transcripts,
                'videos_without_transcripts': videos_without_transcripts,
                'active_channels': active_channels,
                'videos_by_channel': videos_by_channel
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    try:
        init_app()
        port = 8080
        print("="*60)
        print("🌐 Webové rozhraní spuštěno!")
        print("="*60)
        print(f"📝 Otevři Safari a jdi na:")
        print(f"   http://127.0.0.1:{port}")
        print(f"   nebo")
        print(f"   http://localhost:{port}")
        print("="*60)
        print("🛑 Pro zastavení stiskni Ctrl+C")
        print("="*60)
        print()
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Chyba při spuštění: {e}")
        import traceback
        traceback.print_exc()


"""
Generátor měsíčních reportů
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from storage import Database
from email_service import EmailSender
from config import load_config


class ReportGenerator:
    """Generuje měsíční reporty s filtrováním duplicit"""
    
    def __init__(self):
        self.db = Database()
        self.config = load_config()
        self.email_sender = None
        
        email_config = self.config.get('email', {})
        if email_config.get('enabled', False):
            self.email_sender = EmailSender(
                smtp_server=email_config.get('smtp_server'),
                smtp_port=email_config.get('smtp_port', 587),
                username=email_config.get('username'),
                password=email_config.get('password'),
                from_address=email_config.get('from_address'),
                use_tls=email_config.get('use_tls', True)
            )
    
    def generate_monthly_report(self, month: Optional[str] = None) -> Dict:
        """
        Vygeneruje měsíční report
        
        Args:
            month: Měsíc ve formátu YYYY-MM (pokud None, použije aktuální měsíc)
        
        Returns:
            Slovník s reportem
        """
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        # Získej všechny předchozí měsíce (pro vyloučení duplicit)
        current_date = datetime.strptime(f"{month}-01", "%Y-%m-%d")
        previous_months = []
        for i in range(1, 13):  # Posledních 12 měsíců
            prev_month = (current_date - timedelta(days=30*i)).strftime('%Y-%m')
            previous_months.append(prev_month)
        
        # Získej VŠECHNY obsahy pro daný měsíc (ne jen relevantní)
        start_date = f"{month}-01"
        all_contents = self.db.get_all_analyses(
            limit=1000,
            since=start_date,
            exclude_months=previous_months,
            only_relevant=False  # Všechny, ne jen relevantní
        )
        
        # Filtruj pouze obsahy z daného měsíce
        month_contents = []
        for c in all_contents:
            created_at = c.get('created_at', '') or c.get('timestamp', '')
            if created_at.startswith(month):
                month_contents.append(c)
        
        # Pokud není žádný obsah z daného měsíce, zkus poslední měsíc
        if not month_contents:
            last_month = (datetime.strptime(f"{month}-01", "%Y-%m-%d") - timedelta(days=30)).strftime('%Y-%m')
            start_date = f"{last_month}-01"
            all_contents = self.db.get_all_analyses(
                limit=1000,
                since=start_date,
                exclude_months=[],
                only_relevant=False
            )
            for c in all_contents:
                created_at = c.get('created_at', '') or c.get('timestamp', '')
                if created_at.startswith(last_month):
                    month_contents.append(c)
            month = last_month  # Aktualizuj měsíc
        
        # Relevantní obsahy pro highlights
        relevant_contents = [c for c in month_contents if c.get('analysis', {}).get('is_relevant', False)]
        
        # Seskup podle kategorie
        by_category = {}
        for content in month_contents:
            category = content['analysis'].get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(content)
        
        report = {
            'month': month,
            'total_contents': len(month_contents),
            'relevant_contents': len(relevant_contents),
            'by_category': by_category,
            'contents': month_contents,
            'relevant': relevant_contents
        }
        
        return report
    
    def send_monthly_report(self, month: Optional[str] = None) -> bool:
        """
        Vygeneruje a pošle měsíční report emailem
        
        Args:
            month: Měsíc ve formátu YYYY-MM
        
        Returns:
            True pokud se email úspěšně odeslal
        """
        if not self.email_sender:
            print("⚠️  Email není povolen v konfiguraci")
            return False
        
        report = self.generate_monthly_report(month)
        
        if report['total_contents'] == 0:
            print(f"ℹ️  Pro měsíc {month} nebyly nalezeny žádné nové relevantní obsahy")
            return True
        
        email_config = self.config.get('email', {})
        to_addresses = email_config.get('to_addresses', [])
        
        if not to_addresses:
            print("⚠️  Žádné emailové adresy v konfiguraci")
            return False
        
        # Vytvoř shrnutí
        summary = f"Měsíční report pro {month}: {report['total_contents']} relevantních obsahů"
        
        # Připrav obsahy pro email (seskupené podle kategorií)
        all_contents = []
        for category, contents in report['by_category'].items():
            all_contents.extend(contents)
        
        # Odeslání
        subject = f"📊 Měsíční report - {month}"
        success = self.email_sender.send_report(
            to_addresses=to_addresses,
            subject=subject,
            relevant_contents=all_contents,
            summary=summary
        )
        
        if success:
            # Označ obsahy jako odeslané v reportu
            for content in all_contents:
                self.db.mark_report_sent(content['hash'], subject)
            print(f"✅ Měsíční report pro {month} odeslán")
        
        return success
    
    def save_report_to_file(self, month: Optional[str] = None, format: str = 'json') -> str:
        """
        Uloží report do souboru
        
        Args:
            month: Měsíc ve formátu YYYY-MM
            format: Formát souboru ('json' nebo 'html')
        
        Returns:
            Cesta k uloženému souboru
        """
        report = self.generate_monthly_report(month)
        
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        if format == 'json':
            import json
            file_path = reports_dir / f"report_{month}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        else:
            # HTML format
            file_path = reports_dir / f"report_{month}.html"
            html = self._generate_html_report(report)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        return str(file_path)
    
    def _generate_html_report(self, report: Dict) -> str:
        """Vygeneruje HTML report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report {report['month']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
        .category {{ margin: 20px 0; }}
        .item {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
    </style>
</head>
<body>
    <h1>📊 Měsíční Report - {report['month']}</h1>
    <p>Celkem: {report['total_contents']} relevantních obsahů</p>
"""
        for category, contents in report['by_category'].items():
            html += f'<div class="category"><h2>{category}</h2>'
            for content in contents:
                html += f"""
                <div class="item">
                    <h3>{content['title']}</h3>
                    <p><strong>Relevance:</strong> {content['analysis']['relevance_score']:.2f}</p>
                    <p>{content['analysis']['summary']}</p>
                    <p><a href="{content['url']}">{content['url']}</a></p>
                </div>
                """
            html += '</div>'
        
        html += '</body></html>'
        return html


if __name__ == "__main__":
    generator = ReportGenerator()
    
    # Vygeneruj report pro aktuální měsíc
    report = generator.generate_monthly_report()
    print(f"Report pro {report['month']}: {report['total_contents']} obsahů")
    
    # Ulož do souboru
    file_path = generator.save_report_to_file()
    print(f"Report uložen: {file_path}")


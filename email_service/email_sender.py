"""
Email Service pro posílání reportů
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime


class EmailSender:
    """Třída pro posílání emailových reportů"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str,
        use_tls: bool = True
    ):
        """
        Inicializace email senderu
        
        Args:
            smtp_server: SMTP server (např. smtp.gmail.com)
            smtp_port: SMTP port (např. 587)
            username: Uživatelské jméno/email
            password: Heslo nebo app password
            from_address: Email adresa odesílatele
            use_tls: Použít TLS
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls
    
    def send_report(
        self,
        to_addresses: List[str],
        subject: str,
        relevant_contents: List[Dict],
        summary: Optional[str] = None
    ) -> bool:
        """
        Pošle email report s relevantními obsahy
        
        Args:
            to_addresses: Seznam emailových adres příjemců
            subject: Předmět emailu
            relevant_contents: Seznam relevantních obsahů s analýzou
            summary: Volitelné shrnutí
        
        Returns:
            True pokud se email úspěšně odeslal
        """
        try:
            # Vytvoření emailu
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_address
            msg['To'] = ", ".join(to_addresses)
            msg['Subject'] = subject
            
            # HTML verze
            html_body = self._create_html_report(relevant_contents, summary)
            text_body = self._create_text_report(relevant_contents, summary)
            
            msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Odeslání
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email odeslán na {', '.join(to_addresses)}")
            return True
            
        except Exception as e:
            print(f"❌ Chyba při odesílání emailu: {e}")
            return False
    
    def _create_html_report(
        self,
        relevant_contents: List[Dict],
        summary: Optional[str] = None
    ) -> str:
        """Vytvoří HTML verzi reportu"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px; }}
        .content-item {{ background-color: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
        .title {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
        .category {{ display: inline-block; background-color: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin: 5px 0; }}
        .score {{ color: #27ae60; font-weight: bold; }}
        .summary {{ background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .key-points {{ margin: 10px 0; }}
        .key-points li {{ margin: 5px 0; }}
        .url {{ color: #3498db; text-decoration: none; }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 Nový relevantní obsah nalezen</h1>
            <p>Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        </div>
"""
        
        if summary:
            html += f'<div class="summary"><strong>Shrnutí:</strong> {summary}</div>'
        
        html += f'<p>Nalezeno <strong>{len(relevant_contents)}</strong> relevantních obsahů:</p>'
        
        for i, content in enumerate(relevant_contents, 1):
            analysis = content.get('analysis', {})
            scraped = content.get('scraped', {})
            
            html += f"""
        <div class="content-item">
            <div class="title">{i}. {scraped.get('title', 'Bez nadpisu')}</div>
            <div>
                <span class="category">{analysis.get('category', 'unknown')}</span>
                <span class="score">Relevance: {analysis.get('relevance_score', 0):.2f}</span>
            </div>
            <p><strong>Shrnutí:</strong> {analysis.get('summary', 'Není k dispozici')}</p>
            <div class="key-points">
                <strong>Klíčové body:</strong>
                <ul>
"""
            for point in analysis.get('key_points', [])[:5]:
                html += f"                    <li>{point}</li>\n"
            
            html += f"""
                </ul>
            </div>
            <p><strong>Zdroj:</strong> <a href="{scraped.get('url', '#')}" class="url">{scraped.get('url', 'N/A')}</a></p>
            <p><em>{analysis.get('reasoning', '')}</em></p>
        </div>
"""
        
        html += f"""
        <div class="footer">
            <p>Tento email byl automaticky vygenerován Web Monitoring aplikací.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _create_text_report(
        self,
        relevant_contents: List[Dict],
        summary: Optional[str] = None
    ) -> str:
        """Vytvoří textovou verzi reportu"""
        text = f"""
🔔 NOVÝ RELEVANTNÍ OBSAH NALEZEN
{'=' * 50}
Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}

"""
        
        if summary:
            text += f"Shrnutí: {summary}\n\n"
        
        text += f"Nalezeno {len(relevant_contents)} relevantních obsahů:\n\n"
        
        for i, content in enumerate(relevant_contents, 1):
            analysis = content.get('analysis', {})
            scraped = content.get('scraped', {})
            
            text += f"""
{i}. {scraped.get('title', 'Bez nadpisu')}
   Kategorie: {analysis.get('category', 'unknown')}
   Relevance: {analysis.get('relevance_score', 0):.2f}
   
   Shrnutí: {analysis.get('summary', 'Není k dispozici')}
   
   Klíčové body:
"""
            for point in analysis.get('key_points', [])[:5]:
                text += f"   - {point}\n"
            
            text += f"""
   Zdroj: {scraped.get('url', 'N/A')}
   {analysis.get('reasoning', '')}
   
{'-' * 50}
"""
        
        text += "\nTento email byl automaticky vygenerován Web Monitoring aplikací.\n"
        
        return text


"""
Vylepšený generátor reportů s právním/daňovým shrnutím
"""
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from storage import Database
from analyzer import GeminiAnalyzer
from config import load_config


class ReportEnhancer:
    """Vytváří vylepšené reporty s právním/daňovým shrnutím"""
    
    def __init__(self):
        self.db = Database()
        self.config = load_config()
        
        # Inicializace Gemini pro vylepšené shrnutí
        ai_config = self.config.get('ai', {})
        self.analyzer = GeminiAnalyzer(
            api_key=ai_config.get('api_key') or os.getenv("GEMINI_API_KEY"),
            model=ai_config.get('model', 'gemini-2.0-flash'),
            temperature=0.5  # Nižší teplota pro konzistentnější právní analýzu
        )
    
    def create_business_highlights(self, all_contents: List[Dict]) -> str:
        """
        Vytvoří highlights pro podnikatele a investory z VŠECH analyzovaných obsahů
        
        Args:
            all_contents: Seznam všech analyzovaných obsahů
        
        Returns:
            Highlights shrnutí
        """
        if not all_contents:
            return "Žádné obsahy k analýze."
        
        # Filtruj obsahy relevantní pro podnikatele a investory
        business_relevant = []
        for content in all_contents:
            analysis = content.get('analysis', {})
            category = analysis.get('category', '').lower()
            summary = analysis.get('summary', '').lower()
            relevance = analysis.get('relevance_score', 0)
            
            # Klíčová slova pro podnikatele a investory
            keywords = ['daň', 'daně', 'podnikatel', 'investice', 'právní', 'zákon', 'změna', 
                       'dph', 'příjem', 'odpočet', 'úleva', 'povinnost', 'sankce', 'změna']
            
            is_business_relevant = (
                relevance >= 0.5 or
                any(kw in category or kw in summary for kw in keywords)
            )
            
            if is_business_relevant:
                business_relevant.append(content)
        
        # Pokud není žádný business relevantní, použij všechny s relevance > 0.3
        if not business_relevant:
            business_relevant = [c for c in all_contents if c.get('analysis', {}).get('relevance_score', 0) >= 0.3]
        
        # Pokud stále nic, použij top 10 podle relevance
        if not business_relevant:
            business_relevant = sorted(all_contents, key=lambda x: x.get('analysis', {}).get('relevance_score', 0), reverse=True)[:10]
        
        # Příprava dat pro analýzu
        documents_summary = []
        for i, content in enumerate(business_relevant[:25], 1):  # Max 25 dokumentů
            analysis = content.get('analysis', {})
            documents_summary.append(
                f"{i}. {content.get('title', 'Bez nadpisu')}\n"
                f"   Kategorie: {analysis.get('category', 'N/A')}\n"
                f"   Relevance: {analysis.get('relevance_score', 0):.2f}\n"
                f"   Shrnutí: {analysis.get('summary', 'N/A')}\n"
                f"   URL: {content.get('url', 'N/A')}\n"
            )
        
        prompt = f"""Jsi zkušený daňový poradce a advokát specializující se na daňové právo pro podnikatele a investory.

Analyzuj následující dokumenty a vytvoř HIGHLIGHTS - nejdůležitější informace pro podnikatele a investory:

DOKUMENTY:
{chr(10).join(documents_summary)}

Vytvoř strukturované HIGHLIGHTS v následujícím formátu:

1. EXECUTIVE SUMMARY (2-3 věty)
   - Hlavní zjištění a nejdůležitější změny pro podnikatele a investory

2. NEJDŮLEŽITĚJŠÍ PRÁVNÍ A DAŇOVÉ ZÁVĚRY PRO PODNIKATELE A INVESTORY
   - Vypiš 5-10 nejdůležitějších právních závěrů
   - Zaměř se na praktické dopady pro podnikání a investice
   - Každý závěr by měl být jasný, stručný a praktický
   - Uveď konkrétní dopad na podnikatele/investory

3. DOPORUČENÍ PRO PODNIKATELE A INVESTORY
   - Praktická doporučení
   - Na co si dát pozor
   - Jaké kroky podniknout
   - Kdy jednat

4. KLÍČOVÉ ZDROJE
   - Seznam nejdůležitějších zdrojů s odkazy

Buď profesionální, přesný a praktický. Zaměř se na to, co je důležité pro podnikatele a investory."""
        
        try:
            import google.generativeai as genai
            response = self.analyzer.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=3000
                )
            )
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            # Fallback shrnutí
            return f"""EXECUTIVE SUMMARY:
Analyzováno {len(contents)} relevantních dokumentů.

NEJDŮLEŽITĚJŠÍ ZÁVĚRY:
{chr(10).join([f"- {c.get('title', 'N/A')}: {c.get('analysis', {}).get('summary', 'N/A')[:100]}" for c in contents[:5]])}

ZDROJE:
{chr(10).join([f"- {c.get('title', 'N/A')}: {c.get('url', 'N/A')}" for c in contents[:10]])}"""
    
    def create_enhanced_report(self, month: str, all_contents: List[Dict], relevant_contents: List[Dict] = None) -> Dict[str, Any]:
        """
        Vytvoří vylepšený report s highlights pro podnikatele/investory
        
        Args:
            month: Měsíc (YYYY-MM)
            all_contents: Seznam VŠECH analyzovaných obsahů
            relevant_contents: Seznam relevantních obsahů (pro kompatibilitu)
        
        Returns:
            Vylepšený report
        """
        # Vytvoř highlights pro podnikatele a investory z VŠECH obsahů
        highlights = self.create_business_highlights(all_contents)
        
        # Seskup podle kategorií
        by_category = {}
        for content in all_contents:
            category = content.get('analysis', {}).get('category', 'unknown')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(content)
        
        # Relevantní obsahy pro highlights (top podle relevance)
        relevant = relevant_contents or [c for c in all_contents if c.get('analysis', {}).get('is_relevant', False)]
        if not relevant:
            # Pokud není žádný relevantní, vezmi top podle relevance score
            relevant = sorted(all_contents, key=lambda x: x.get('analysis', {}).get('relevance_score', 0), reverse=True)[:10]
        
        # Top findings pro podnikatele/investory
        top_findings = sorted(relevant, key=lambda x: x.get('analysis', {}).get('relevance_score', 0), reverse=True)[:10]
        
        report = {
            'month': month,
            'total_contents': len(all_contents),
            'relevant_contents': len(relevant),
            'highlights': highlights,  # Highlights nahoře
            'by_category': by_category,
            'top_findings': [
                {
                    'title': c.get('title', 'N/A'),
                    'summary': c.get('analysis', {}).get('summary', 'N/A'),
                    'relevance': c.get('analysis', {}).get('relevance_score', 0),
                    'url': c.get('url', 'N/A'),
                    'key_points': c.get('analysis', {}).get('key_points', []),
                    'category': c.get('analysis', {}).get('category', 'N/A')
                }
                for c in top_findings
            ],
            'all_contents': all_contents  # Všechny analyzované obsahy dole
        }
        
        return report


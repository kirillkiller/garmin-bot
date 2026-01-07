"""
AI Analyzer používající Google Gemini API
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
try:
    import google.generativeai as genai
except ImportError:
    print("⚠️  Instaluj: pip install google-generativeai")
    genai = None


class GeminiAnalyzer:
    """Analyzer používající Gemini API pro analýzu obsahu"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        interesting_categories: Optional[List[str]] = None,
        relevance_threshold: float = 0.7
    ):
        """
        Inicializace analyzátoru
        
        Args:
            api_key: Gemini API klíč (nebo použije GEMINI_API_KEY z env)
            model: Název Gemini modelu
            temperature: Teplota pro generování
            interesting_categories: Seznam zajímavých kategorií
            relevance_threshold: Práh relevance (0-1)
        """
        if genai is None:
            raise ImportError("google-generativeai není nainstalován")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY musí být nastaven")
        
        genai.configure(api_key=self.api_key)
        # Použij správný formát názvu modelu
        model_name = model if model.startswith("models/") else f"models/{model}"
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.interesting_categories = interesting_categories or []
        self.relevance_threshold = relevance_threshold
        
    def analyze_content(
        self,
        url: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None,
        website_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzuje obsah pomocí Gemini
        
        Args:
            url: URL zdroje
            title: Nadpis
            content: Textový obsah
            metadata: Další metadata
        
        Returns:
            Slovník s analýzou:
            {
                "category": str,
                "relevance_score": float,
                "summary": str,
                "key_points": List[str],
                "is_relevant": bool,
                "reasoning": str
            }
        """
        # Příprava promptu
        prompt = self._create_analysis_prompt(title, content, website_prompt)
        
        try:
            # Volání Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2000
                )
            )
            
            # Parsování odpovědi
            analysis = self._parse_response(response.text, url, title)
            return analysis
            
        except Exception as e:
            print(f"❌ Chyba při analýze: {e}")
            return {
                "category": "unknown",
                "relevance_score": 0.0,
                "summary": f"Chyba při analýze: {str(e)}",
                "key_points": [],
                "is_relevant": False,
                "reasoning": f"Chyba: {str(e)}"
            }
    
    def _create_analysis_prompt(self, title: str, content: str, website_prompt: Optional[str] = None) -> str:
        """Vytvoří prompt pro analýzu"""
        # Zkus načíst custom prompt
        custom_prompt_file = Path("config/ai_prompt.txt")
        if custom_prompt_file.exists():
            try:
                with open(custom_prompt_file, 'r', encoding='utf-8') as f:
                    custom_prompt = f.read().strip()
                if custom_prompt:
                    # Použij custom prompt a doplň proměnné
                    prompt = custom_prompt.replace("{title}", title)
                    prompt = prompt.replace("{content}", content[:5000])
                    categories_str = ", ".join(self.interesting_categories) if self.interesting_categories else "žádné"
                    prompt = prompt.replace("{categories}", categories_str)
                    prompt = prompt.replace("{threshold}", str(self.relevance_threshold))
                    return prompt
            except Exception as e:
                print(f"⚠️  Chyba při načítání custom promptu: {e}, použiji default")
        
        # Default prompt
        categories_str = ", ".join(self.interesting_categories) if self.interesting_categories else "žádné"
        
        # Přidej web-specifický prompt, pokud existuje
        website_instruction = ""
        if website_prompt:
            website_instruction = f"\n\nDŮLEŽITÉ PRO TENTO WEB:\n{website_prompt}\n\n"
        
        prompt = f"""Analyzuj následující webový obsah a poskytni strukturovanou analýzu v JSON formátu.{website_instruction}

Nadpis: {title}

Obsah:
{content[:5000]}  # Omezíme na 5000 znaků

Zajímavé kategorie: {categories_str}

Vrať JSON s následující strukturou:
{{
    "category": "název kategorie (např. technologie, AI, startupy, atd.)",
    "relevance_score": 0.0-1.0 (jak relevantní je obsah pro zajímavé kategorie),
    "summary": "stručné shrnutí obsahu (2-3 věty)",
    "key_points": ["klíčový bod 1", "klíčový bod 2", "klíčový bod 3"],
    "is_relevant": true/false (true pokud relevance_score >= {self.relevance_threshold}),
    "reasoning": "stručné vysvětlení, proč je/není relevantní"
}}

Důležité:
- Buď objektivní a přesný
- Kategorizuj obsah do nejvhodnější kategorie
- Relevance score: 0.0 = vůbec nerelevantní, 1.0 = velmi relevantní
- Pokud obsah spadá do některé ze zajímavých kategorií, nastav is_relevant na true
- Vrať POUZE validní JSON, žádný další text

JSON:"""
        return prompt
    
    def _parse_response(self, response_text: str, url: str, title: str) -> Dict[str, Any]:
        """Parsuje odpověď z Gemini"""
        try:
            # Pokus o extrakci JSON z odpovědi
            response_text = response_text.strip()
            
            # Odstranění markdown code blocks pokud existují
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parsování JSON
            analysis = json.loads(response_text)
            
            # Validace a normalizace
            analysis.setdefault("category", "unknown")
            analysis.setdefault("relevance_score", 0.0)
            analysis.setdefault("summary", "Shrnutí není k dispozici")
            analysis.setdefault("key_points", [])
            analysis.setdefault("is_relevant", False)
            analysis.setdefault("reasoning", "")
            
            # Zajištění správných typů
            analysis["relevance_score"] = float(analysis["relevance_score"])
            analysis["is_relevant"] = bool(analysis["is_relevant"])
            if not isinstance(analysis["key_points"], list):
                analysis["key_points"] = []
            
            # Přidání metadat
            analysis["url"] = url
            analysis["title"] = title
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Chyba při parsování JSON: {e}")
            print(f"Odpověď: {response_text[:200]}...")
            
            # Fallback analýza
            return {
                "category": "unknown",
                "relevance_score": 0.0,
                "summary": response_text[:500] if response_text else "Nelze analyzovat",
                "key_points": [],
                "is_relevant": False,
                "reasoning": f"Chyba parsování: {str(e)}",
                "url": url,
                "title": title
            }
    
    def batch_analyze(self, contents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyzuje více obsahů najednou
        
        Args:
            contents: Seznam slovníků s klíči: url, title, content
        
        Returns:
            Seznam analýz
        """
        results = []
        for content in contents:
            analysis = self.analyze_content(
                url=content.get("url", ""),
                title=content.get("title", ""),
                content=content.get("content", "")
            )
            results.append(analysis)
        return results
    
    def summarize_multiple(self, analyses: List[Dict[str, Any]]) -> str:
        """
        Vytvoří agregované shrnutí více analýz pomocí Gemini
        
        Args:
            analyses: Seznam analýz
        
        Returns:
            Agregované shrnutí
        """
        if not analyses:
            return "Žádné analýzy k sumarizaci"
        
        # Příprava dat pro sumarizaci
        summaries = []
        for i, analysis in enumerate(analyses, 1):
            summaries.append(
                f"{i}. {analysis.get('title', 'Bez nadpisu')}\n"
                f"   Kategorie: {analysis.get('category', 'unknown')}\n"
                f"   Relevance: {analysis.get('relevance_score', 0):.2f}\n"
                f"   Shrnutí: {analysis.get('summary', '')}\n"
            )
        
        prompt = f"""Vytvoř stručné agregované shrnutí následujících {len(analyses)} analýz obsahu.

Analýzy:
{chr(10).join(summaries)}

Vytvoř:
1. Celkové shrnutí hlavních témat (2-3 věty)
2. Nejvýznamnější kategorie
3. Klíčové poznatky (3-5 bodů)
4. Celkové hodnocení relevance

Odpověz v strukturovaném formátu, jasně a stručně."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Nižší teplota pro konzistentnější shrnutí
                    max_output_tokens=1000
                )
            )
            return response.text
        except Exception as e:
            return f"Chyba při vytváření shrnutí: {str(e)}"
    
    def extract_key_entities(self, content: str) -> Dict[str, List[str]]:
        """
        Extrahuje klíčové entity z obsahu pomocí Gemini
        
        Args:
            content: Textový obsah
        
        Returns:
            Slovník s entitami: {"people": [], "companies": [], "topics": []}
        """
        prompt = f"""Extrahuj klíčové entity z následujícího textu a vrať je v JSON formátu.

Text:
{content[:3000]}

Vrať JSON s následující strukturou:
{{
    "people": ["jméno 1", "jméno 2"],
    "companies": ["společnost 1", "společnost 2"],
    "topics": ["téma 1", "téma 2"],
    "locations": ["místo 1", "místo 2"]
}}

Vrať POUZE validní JSON, žádný další text."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500
                )
            )
            
            # Parsování JSON
            response_text = response.text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            entities = json.loads(response_text)
            return entities
            
        except Exception as e:
            print(f"⚠️  Chyba při extrakci entit: {e}")
            return {"people": [], "companies": [], "topics": [], "locations": []}
    
    def intelligent_filter(
        self,
        contents: List[Dict[str, str]],
        max_results: int = 10
    ) -> List[Dict[str, str]]:
        """
        Inteligentně filtruje obsahy pomocí Gemini před analýzou
        
        Args:
            contents: Seznam obsahů
            max_results: Maximální počet výsledků
        
        Returns:
            Filtrovaný seznam nejrelevantnějších obsahů
        """
        if len(contents) <= max_results:
            return contents
        
        # Vytvoření promptu pro filtrování
        contents_text = []
        for i, content in enumerate(contents, 1):
            contents_text.append(
                f"{i}. {content.get('title', 'Bez nadpisu')}\n"
                f"   {content.get('content', '')[:200]}...\n"
            )
        
        categories_str = ", ".join(self.interesting_categories) if self.interesting_categories else "žádné"
        
        prompt = f"""Z následujících {len(contents)} obsahů vyber {max_results} nejrelevantnějších pro kategorie: {categories_str}

Obsahy:
{chr(10).join(contents_text)}

Vrať JSON s čísly vybraných obsahů (1-{len(contents)}):
{{
    "selected_indices": [1, 5, 7, ...]
}}

Vrať POUZE validní JSON, žádný další text."""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=200
                )
            )
            
            # Parsování
            response_text = response.text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(response_text)
            selected_indices = result.get("selected_indices", [])
            
            # Konverze na 0-based indexy a filtrování
            filtered = []
            for idx in selected_indices:
                if 1 <= idx <= len(contents):
                    filtered.append(contents[idx - 1])
            
            return filtered[:max_results]
            
        except Exception as e:
            print(f"⚠️  Chyba při inteligentním filtrování: {e}")
            # Fallback: vrať první max_results
            return contents[:max_results]
    
    def enhance_summary(self, summary: str, context: Optional[Dict] = None) -> str:
        """
        Vylepší shrnutí pomocí Gemini s kontextem
        
        Args:
            summary: Původní shrnutí
            context: Volitelný kontext
        
        Returns:
            Vylepšené shrnutí
        """
        context_text = ""
        if context:
            context_text = f"\nKontext:\n- Kategorie: {context.get('category', 'N/A')}\n"
            if context.get('key_points'):
                context_text += f"- Klíčové body: {', '.join(context.get('key_points', [])[:3])}\n"
        
        prompt = f"""Vylepši následující shrnutí, aby bylo jasnější, stručnější a informativnější.

Původní shrnutí:
{summary}
{context_text}

Vytvoř vylepšené shrnutí (2-3 věty), které:
- Je jasné a srozumitelné
- Obsahuje nejdůležitější informace
- Je stručné ale informativní
- Používá profesionální jazyk

Vylepšené shrnutí:"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.6,
                    max_output_tokens=300
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"⚠️  Chyba při vylepšování shrnutí: {e}")
            return summary


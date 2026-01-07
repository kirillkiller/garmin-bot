"""
Jednoduchý AI agent s OpenAI API (bez LangChain)
"""
import os
import json
from typing import Optional, List, Dict, Any
try:
    from openai import OpenAI
except ImportError:
    print("⚠️  Instaluj openai: pip install openai")
    exit(1)


class SimpleAgent:
    """Základní AI agent s podporou nástrojů"""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        """
        Inicializace agenta
        
        Args:
            model_name: Název modelu OpenAI
            temperature: Teplota pro generování (0-1)
            api_key: OpenAI API klíč (nebo použije OPENAI_API_KEY z env)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY musí být nastaven (env variable nebo parametr)")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.tools = []
        self.conversation_history: List[Dict[str, str]] = []
        
    def add_tool(self, name: str, description: str, func: callable):
        """
        Přidá nástroj agentovi
        
        Args:
            name: Název nástroje
            description: Popis nástroje
            func: Funkce, která se má zavolat
        """
        self.tools.append({
            "name": name,
            "description": description,
            "func": func
        })
        
    def _get_tools_schema(self) -> List[Dict]:
        """Vytvoří schéma nástrojů pro OpenAI"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Vstup pro nástroj"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
            for tool in self.tools
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """Spustí nástroj"""
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    result = tool["func"](arguments.get("query", ""))
                    return str(result)
                except Exception as e:
                    return f"Chyba při spuštění nástroje: {e}"
        return f"Nástroj '{tool_name}' nebyl nalezen"
    
    def run(self, query: str) -> str:
        """
        Spustí agenta s daným dotazem
        
        Args:
            query: Dotaz uživatele
            
        Returns:
            Odpověď agenta
        """
        # Přidá uživatelský dotaz do historie
        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        
        messages = [
            {
                "role": "system",
                "content": """Jsi užitečný AI asistent. 
Máš přístup k různým nástrojům, které můžeš použít k odpovědím na otázky.
Používej nástroje, když je to potřeba, a poskytuj užitečné a přesné odpovědi."""
            }
        ] + self.conversation_history
        
        tools = self._get_tools_schema() if self.tools else None
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )
            
            message = response.choices[0].message
            messages.append(message.model_dump())
            
            # Pokud agent chce použít nástroj
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except:
                        arguments = {}
                    
                    tool_result = self._execute_tool(tool_name, arguments)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result
                    })
                
                iteration += 1
                continue
            
            # Pokud máme finální odpověď
            if message.content:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
                return message.content
        
        return "Dosáhl jsem maximálního počtu iterací."
    
    def reset(self):
        """Vymaže historii konverzace"""
        self.conversation_history = []


# Příklad použití
if __name__ == "__main__":
    import os
    
    # Zkontroluj, zda je nastaven API klíč
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Nastav OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='tvůj-klíč'")
        print("\nNebo spusť:")
        print("   python agent_simple.py")
        exit(1)
    
    try:
        # Vytvoření agenta
        agent = SimpleAgent()
        
        # Přidání příkladu nástroje - kalkulačka
        def kalkulacka(query: str) -> str:
            """Vypočítá matematický výraz"""
            try:
                # Bezpečné vyhodnocení pouze číselných výrazů
                allowed_chars = set("0123456789+-*/()., ")
                if all(c in allowed_chars for c in query):
                    result = eval(query)
                    return str(result)
                else:
                    return "Chyba: Neplatný výraz"
            except Exception as e:
                return f"Chyba při výpočtu: {e}"
        
        agent.add_tool(
            name="kalkulacka",
            description="Vypočítá matematický výraz (např. '2+2', '10*5', '15/3')",
            func=kalkulacka
        )
        
        # Spuštění agenta
        print("🤖 Agent je připraven!")
        print("Zadej 'quit' pro ukončení")
        print("Zadej 'reset' pro vymazání historie\n")
        
        while True:
            user_input = input("Ty: ")
            if user_input.lower() in ['quit', 'exit', 'konec']:
                print("Na shledanou!")
                break
            elif user_input.lower() == 'reset':
                agent.reset()
                print("Historie vymazána.\n")
                continue
            
            try:
                response = agent.run(user_input)
                print(f"Agent: {response}\n")
            except Exception as e:
                print(f"❌ Chyba: {e}\n")
    
    except ValueError as e:
        print(f"❌ {e}")


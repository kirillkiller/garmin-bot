"""
Jednoduchý AI agent s LangChain
"""
from typing import Optional, List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.schema import BaseMessage


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
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )
        self.tools = []
        self.agent_executor: Optional[AgentExecutor] = None
        
    def add_tool(self, tool: Tool):
        """Přidá nástroj agentovi"""
        self.tools.append(tool)
        
    def _create_agent(self):
        """Vytvoří agent executor s aktuálními nástroji"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Jsi užitečný AI asistent. 
            Máš přístup k různým nástrojům, které můžeš použít k odpovědím na otázky.
            Používej nástroje, když je to potřeba, a poskytuj užitečné a přesné odpovědi."""),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            self.llm,
            self.tools,
            prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
    def run(self, query: str) -> str:
        """
        Spustí agenta s daným dotazem
        
        Args:
            query: Dotaz uživatele
            
        Returns:
            Odpověď agenta
        """
        if not self.agent_executor:
            self._create_agent()
            
        result = self.agent_executor.invoke({"input": query})
        return result["output"]
    
    def chat(self, message: str, conversation_history: Optional[List[BaseMessage]] = None) -> Dict[str, Any]:
        """
        Chat režim s podporou historie konverzace
        
        Args:
            message: Zpráva uživatele
            conversation_history: Historie předchozích zpráv
            
        Returns:
            Slovník s odpovědí a aktualizovanou historií
        """
        if not self.agent_executor:
            self._create_agent()
            
        inputs = {"input": message}
        if conversation_history:
            inputs["chat_history"] = conversation_history
            
        result = self.agent_executor.invoke(inputs)
        return {
            "response": result["output"],
            "history": conversation_history or []
        }


# Příklad použití
if __name__ == "__main__":
    import os
    
    # Zkontroluj, zda je nastaven API klíč
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Nastav OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY='tvůj-klíč'")
    else:
        # Vytvoření agenta
        agent = SimpleAgent()
        
        # Můžeš přidat vlastní nástroje
        # from langchain.tools import DuckDuckGoSearchRun
        # search = DuckDuckGoSearchRun()
        # agent.add_tool(Tool(
        #     name="search",
        #     func=search.run,
        #     description="Vyhledávání na internetu"
        # ))
        
        # Spuštění agenta
        print("🤖 Agent je připraven!")
        print("Zadej 'quit' pro ukončení\n")
        
        while True:
            user_input = input("Ty: ")
            if user_input.lower() in ['quit', 'exit', 'konec']:
                print("Na shledanou!")
                break
            
            try:
                response = agent.run(user_input)
                print(f"Agent: {response}\n")
            except Exception as e:
                print(f"❌ Chyba: {e}\n")


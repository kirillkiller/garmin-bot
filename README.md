# AI Agent

Jednoduchý AI agent vytvořený s OpenAI API.

## Rychlá instalace

### Automatická instalace (doporučeno)

```bash
chmod +x setup.sh
./setup.sh
```

### Ruční instalace

1. Nainstaluj závislosti:
```bash
pip3 install openai
# nebo
python3 -m pip install --user openai
```

2. Nastav OpenAI API klíč:
```bash
export OPENAI_API_KEY='tvůj-api-klíč'
```

**Poznámka:** Pokud instalace selže kvůli chybějícím Xcode Command Line Tools, nainstaluj je:
```bash
xcode-select --install
```

## Použití

### Jednoduchá verze (doporučeno)

```bash
python3 agent_simple.py
```

### Základní použití v Pythonu

```python
from agent_simple import SimpleAgent

# Vytvoření agenta
agent = SimpleAgent()

# Spuštění dotazu
response = agent.run("Kolik je 2+2?")
print(response)
```

### Pokročilá verze s LangChain

```bash
pip3 install langchain langchain-openai
python3 agent.py
```

### Přidání vlastních nástrojů

```python
from agent import SimpleAgent
from langchain.tools import Tool

agent = SimpleAgent()

# Vytvoření vlastního nástroje
def kalkulacka(vyraz: str) -> str:
    """Vypočítá matematický výraz"""
    try:
        result = eval(vyraz)
        return str(result)
    except:
        return "Chyba při výpočtu"

agent.add_tool(Tool(
    name="kalkulacka",
    func=kalkulacka,
    description="Vypočítá matematický výraz (např. '2+2', '10*5')"
))

response = agent.run("Kolik je 15 * 23?")
```

## Struktura

- `agent.py` - Hlavní soubor s implementací agenta
- `requirements.txt` - Python závislosti
- `README.md` - Tato dokumentace

## Rozšíření

Agent můžeš rozšířit o:
- Vlastní nástroje (tools)
- Různé LLM modely
- Persistenci konverzace
- Web scraping
- Databázové dotazy
- A další...


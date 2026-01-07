# 📋 Instrukce k instalaci

## Krok 1: Nainstaluj Xcode Command Line Tools (pokud ještě nejsou)

Na macOS potřebuješ Xcode Command Line Tools pro instalaci Python balíčků:

```bash
xcode-select --install
```

Po spuštění tohoto příkazu se otevře dialog - klikni na "Install" a počkej na dokončení instalace (může to trvat několik minut).

## Krok 2: Nainstaluj závislosti

Po instalaci Xcode Command Line Tools:

```bash
pip3 install openai
```

Nebo pokud máš problémy s oprávněními:

```bash
pip3 install --user openai
```

## Krok 3: Nastav API klíč

Získej API klíč z [OpenAI](https://platform.openai.com/api-keys) a nastav ho:

```bash
export OPENAI_API_KEY='tvůj-api-klíč'
```

Aby se klíč nastavil trvale, přidej tento řádek do `~/.zshrc`:

```bash
echo 'export OPENAI_API_KEY="tvůj-api-klíč"' >> ~/.zshrc
source ~/.zshrc
```

## Krok 4: Ověř nastavení

```bash
python3 check_setup.py
```

## Krok 5: Spusť agenta

```bash
python3 agent_simple.py
```

---

## Alternativní řešení

Pokud nemůžeš nainstalovat Xcode Command Line Tools, můžeš použít:

1. **Homebrew** (pokud je nainstalován):
   ```bash
   brew install python3
   pip3 install openai
   ```

2. **Anaconda/Miniconda**:
   ```bash
   conda install -c conda-forge openai
   ```

3. **Docker** (pokud máš Docker):
   ```bash
   docker run -it -e OPENAI_API_KEY='tvůj-klíč' python:3.11 bash
   pip install openai
   ```

---

## Rychlý start (pokud máš vše nainstalované)

```bash
./setup.sh
python3 check_setup.py
python3 agent_simple.py
```


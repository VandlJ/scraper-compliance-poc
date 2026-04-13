import json
import os
import sys
import warnings
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# 1. Importujeme tool přímo z našeho MCP serveru
from mcp_server.compliance_server import query_compliance_docs

# 0. Potlačení varování frameworku
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1. Načtení environment proměnných (API klíč)
load_dotenv()

def run_agent():
    # --- CESTY K SOUBORŮM ---
    base_dir = os.path.dirname(os.path.abspath(__file__)) # složka agent/
    project_root = os.path.dirname(base_dir)              # kořen projektu
    
    metrics_path = os.path.join(project_root, "metrics.json")
    scraper_path = os.path.join(project_root, "src", "scraper.py")
    prompt_path = os.path.join(base_dir, "prompt.txt")

    # --- NAČÍTÁNÍ DAT ---
    try:
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        with open(scraper_path, "r") as f:
            code_snippet = f.read()
        # Načítáme prompt z externího textového souboru
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except FileNotFoundError as e:
        print(f"Error: Chybí soubor - {e}", file=sys.stderr)
        sys.exit(1)

    # --- KONFIGURACE AI ---
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        temperature=0.0
    )

    # Tady je ta změna: Už žádné get_api_rules v tomhle souboru.
    # Používáme tool, který se umí podívat do PDF.
    tools = [query_compliance_docs]

    # Vytvoření agenta
    agent_executor = create_react_agent(llm, tools)

    print("Agent konzultuje pravidla přes MCP server (PDF dokumenty)...", file=sys.stderr)
    
    # --- SPUŠTĚNÍ ANALÝZY ---
    user_message = (
        f"TEST ALERT! Status: {metrics['test_status']}\n"
        f"Metrics: {json.dumps(metrics['metrics'])}\n\n"
        f"SOURCE CODE K REVIZI:\n{code_snippet}"
    )
    
    response = agent_executor.invoke({
        "messages": [
            ("system", system_prompt),
            ("user", user_message)
        ]
    })

    # --- VÝSTUP PRO GITHUB ---
    final_content = response["messages"][-1].content
    output_text = final_content[0]["text"] if isinstance(final_content, list) else final_content
    
    # Vypíšeme čistý Markdown, který GitHub Actions uloží do souboru
    print(output_text)

    # --- CI/CD LOGIKA ---
    # Pokud harness nahlásil chybu, shodíme pipeline (exit 1)
    if metrics.get("test_status") != "SUCCESS":
        print("\n[!] PIPELINE FAILED: Compliance violation detected.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_agent()
import json
import os
import sys
import warnings
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

# 0. Suppress noisy framework deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# 1. Load environment variables
load_dotenv()

# Tool 1: Mock MCP for API Rules
@tool
def get_api_rules() -> str:
    """Fetches the external API rate limit rules and terms of service."""
    return "API Terms of Service: Maximum allowed requests per second is 5. Exceeding this limit will result in an immediate IP ban."

# Tool 2: Mock MCP for Internal Policies
@tool
def get_internal_policies() -> str:
    """Fetches the internal company guidelines for writing scraper bots."""
    return "Internal Policy A1: All automated web scrapers must implement a delay (e.g., time.sleep) between requests to prevent accidental DDoS and ensure graceful degradation."

def run_agent():
    # Dynamically calculate absolute paths for CI/CD environment compatibility
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    
    metrics_path = os.path.join(project_root, "metrics.json")
    scraper_path = os.path.join(project_root, "src", "scraper.py")

    # Read metrics
    try:
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print(f"Error: Metrics file not found at {metrics_path}", file=sys.stderr)
        sys.exit(1)

    # Read code
    try:
        with open(scraper_path, "r") as f:
            code_snippet = f.read()
    except FileNotFoundError:
        print(f"Error: Source code file not found at {scraper_path}", file=sys.stderr)
        sys.exit(1)

    # 2. Initialize Gemini 
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        temperature=0.0
    )

    tools = [get_api_rules, get_internal_policies]

    # 3. Define the System Prompt
    system_prompt = (
        "You are a Principal Compliance Architect reviewing code in a CI/CD pipeline.\n"
        "You must ALWAYS use the provided tools to check external rules and internal policies before making a judgment.\n"
        "Analyze the provided test metrics and source code.\n"
        "If the code violates any rules, write a professional, technical comment for a GitHub Pull Request.\n"
        "Include specific rule references and suggest a concrete code fix.\n"
        "Output ONLY the final Markdown comment text."
    )

    # 4. Create the LangGraph Agent
    agent_executor = create_react_agent(llm, tools)

    # Logging to stderr so it doesn't pollute the redirected output file
    print("Agent is analyzing the alert and consulting knowledge bases...", file=sys.stderr)
    
    user_message = f"Test Alert! Status: {metrics['test_status']}.\nMetrics: {json.dumps(metrics['metrics'])}.\n\nSource Code to review:\n{code_snippet}"
    
    # 5. Invoke the agent
    response = agent_executor.invoke({
        "messages": [
            ("system", system_prompt),
            ("user", user_message)
        ]
    })

    # 6. Extract and print ONLY the Markdown content to stdout
    final_content = response["messages"][-1].content
    
    if isinstance(final_content, list):
        # Handle multimodal response format
        print(final_content[0]["text"])
    else:
        # Handle standard string response
        print(final_content)

if __name__ == "__main__":
    run_agent()
import json
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Load environment variables from .env file automatically
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
    # Read metrics
    try:
        with open("../metrics.json", "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print("Metrics file not found. Please run the test harness first.")
        return

    # Read code
    try:
        with open("../src/scraper.py", "r") as f:
            code_snippet = f.read()
    except FileNotFoundError:
        print("Source code file not found.")
        return

    # Initialize Gemini with your specific model
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite-preview", 
        temperature=0.0
    )

    tools = [get_api_rules, get_internal_policies]

    # FIXED PROMPT: Added MessagesPlaceholder for the agent's internal thought process
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Principal Compliance Architect reviewing code in a CI/CD pipeline.\n"
                   "You must ALWAYS use the provided tools to check external rules and internal policies before making a judgment.\n"
                   "Analyze the provided test metrics and source code.\n"
                   "If the code violates any rules, write a professional, technical comment for a GitLab Merge Request.\n"
                   "Include specific rule references and suggest a concrete code fix.\n"
                   "Output ONLY the final Markdown comment text."),
        ("user", "Test Alert! Status: {status}.\nMetrics: {metrics}.\n\nSource Code to review:\n{code}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Agent is analyzing the alert and consulting knowledge bases...\n" + "-"*50)
    
    result = agent_executor.invoke({
        "status": metrics["test_status"],
        "metrics": json.dumps(metrics["metrics"]),
        "code": code_snippet
    })

    print("\n" + "="*50)
    print("FINAL GITLAB MR COMMENT:")
    print("="*50 + "\n")
    print(result["output"])

if __name__ == "__main__":
    run_agent()
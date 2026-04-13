from fastmcp import FastMCP
import PyPDF2
import os

# Initialize FastMCP server
mcp = FastMCP("ComplianceServer")

def extract_text_from_pdf(file_path):
    """Internal helper to read PDF content."""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

@mcp.tool()
def query_compliance_docs(topic: str) -> str:
    """
    Search and read compliance documents from the local PDF storage.
    """
    docs_dir = "compliance_docs"
    results = []
    
    # Rozbijeme dotaz na jednotlivá slova (keywords)
    keywords = topic.lower().split()
    
    for filename in os.listdir(docs_dir):
        if filename.endswith(".pdf"):
            content = extract_text_from_pdf(os.path.join(docs_dir, filename)).lower()
            filename_l = filename.lower()
            
            # Pokud dokument obsahuje ASPOŇ JEDNO z klíčových slov
            if any(word in content for word in keywords) or any(word in filename_l for word in keywords):
                results.append(f"--- Source: {filename} ---\n{content}")
    
    if not results:
        return f"No documents found matching the topic: {topic}. Try searching for broader terms like 'limit' or 'policy'."
    
    return "\n\n".join(results)

if __name__ == "__main__":
    mcp.run()
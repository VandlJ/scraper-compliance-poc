from fpdf import FPDF
import os

def create_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(40, 10, title)
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    
    os.makedirs("compliance_docs", exist_ok=True)
    pdf.output(f"compliance_docs/{filename}")
    print(f"Created: compliance_docs/{filename}")

# 1. Internal Policy
create_pdf(
    "internal_policy.pdf", 
    "Internal Policy A1: Scraper Development",
    "All automated web scrapers must implement a mandatory delay (time.sleep) between requests. "
    "This prevents accidental DDoS attacks and ensures graceful degradation of our infrastructure."
)

# 2. API Terms
create_pdf(
    "api_terms.pdf", 
    "External API Terms of Service",
    "Target: dummy-api.cez.cz. Rate Limit: Maximum 5 requests per second. "
    "Violation Policy: Exceeding this limit will result in an immediate and permanent IP ban."
)
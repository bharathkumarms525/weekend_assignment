import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ListStyle

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def parse_summary_to_flowables(summary: str):
    """
    Converts structured plain text summary into reportlab flowables
    with bold headers and bullet lists.
    """
    styles = getSampleStyleSheet()
    list_style = ListStyle(name='BulletListStyle', leftIndent=15, bulletIndent=0)

    lines = summary.strip().split("\n")
    flowables = []
    current_bullets = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Section titles: start and end with **
        if line.startswith("**") and line.endswith("**"):
            if current_bullets:
                flowables.append(ListFlowable(current_bullets, bulletType='bullet', style=list_style))
                flowables.append(Spacer(1, 6))
                current_bullets = []

            section_title = line.replace("**", "").strip()
            flowables.append(Paragraph(f"<b>{section_title}</b>", styles["Heading3"]))
            flowables.append(Spacer(1, 4))

        # Bullet line
        elif line.startswith(("*", "+", "-")):
            bullet_text = line.lstrip("*+- ").strip()
            current_bullets.append(Paragraph(bullet_text, styles["BodyText"]))

        # Normal paragraph
        else:
            if current_bullets:
                flowables.append(ListFlowable(current_bullets, bulletType='bullet', style=list_style))
                flowables.append(Spacer(1, 6))
                current_bullets = []

            flowables.append(Paragraph(line, styles["BodyText"]))
            flowables.append(Spacer(1, 4))

    if current_bullets:
        flowables.append(ListFlowable(current_bullets, bulletType='bullet', style=list_style))

    return flowables

async def process_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url
    }

    with requests.Session() as session:
        session.headers.update(headers)
        response = session.get(url)

    if response.status_code == 403:
        return {"error": "Access denied. The server returned a 403 Forbidden error."}

    if response.status_code != 200:
        return {"error": f"Failed to fetch the URL. Status code: {response.status_code}"}

    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all(["p", "div", "span"])
    text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

    if not text:
        return {"error": "No text content found on the page."}

    ai_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes content in structured format using section titles and bullet points. Use bold for section headers."},
            {"role": "user", "content": f"Summarize this webpage into clearly structured sections using bullet points and bold section headers:\n{text}"}
        ],
        temperature=0.5,
        max_tokens=800
    )

    summary = ai_response.choices[0].message.content.strip()

    # Generate PDF
    output_pdf = os.path.join(os.getcwd(), "url_summary.pdf")
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    elements = []

    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Web Page Summary", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Add summary content
    flowables = parse_summary_to_flowables(summary)
    elements.extend(flowables)

    doc.build(elements)

    return {
        "summary": summary,
        "report_path": output_pdf
    }

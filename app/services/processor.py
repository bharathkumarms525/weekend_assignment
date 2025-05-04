import tempfile, os, logging
from pathlib import Path
from fastapi import UploadFile
from app.utils.ocr import extract_text
from groq import Groq
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import re

# Load API key from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

def convert_markdown_to_html(text):
    """
    Convert **bold** markdown to HTML <b>bold</b>
    """
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

def create_structured_pdf(summary_text, output_pdf_path):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        spaceAfter=8,
        spaceBefore=12,
        alignment=TA_LEFT,
        textColor="black"
    )
    normal_style = styles["BodyText"]

    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    elements = []

    # Title
    elements.append(Paragraph("Document Summary", title_style))
    elements.append(Spacer(1, 12))

    # Process lines
    lines = summary_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        html_line = convert_markdown_to_html(line)

        if line.startswith("* "):
            # bullet point
            bullet_text = convert_markdown_to_html(line[2:])
            elements.append(ListFlowable([ListItem(Paragraph(bullet_text, normal_style))], bulletType='bullet'))
        else:
            elements.append(Paragraph(html_line, normal_style))

    doc.build(elements)

async def process_document(file: UploadFile):
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text from file
    text = extract_text(tmp_path)
    logging.info(f"Extracted text from file: {text[:500]}")

    # Summarize
    ai_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts key details and summarizes texts."},
            {"role": "user", "content": f"Summarize this: {text}"}
        ],
        temperature=0.5,
        max_tokens=500
    )
    summary = ai_response.choices[0].message.content
    logging.info(f"Generated summary: {summary}")

    # Output structured PDF with formatting
    output_pdf = os.path.join(os.getcwd(), "document_summary.pdf")
    create_structured_pdf(summary, output_pdf)

    return {"summary": summary, "report_path": output_pdf}

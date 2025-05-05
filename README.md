# AI Document Summariser

A FastAPI-based microservice that processes:
- Uploaded PDF or Image files (extracts + summarizes content)
- Web URLs (scrapes + summarizes content)

Then generates a styled PDF report using Groq AI and ReportLab.

## Features
- **Upload PDF or Image**: Extracts text and generates an AI-powered summary.
- **Submit URL**: Scrapes webpage content and generates a structured summary.
- **Styled PDF Reports**: Generates structured PDF reports with bold section headers and bullet points using ReportLab.

## Setup
```bash
git clone <repo-url>
cd ai_document_processor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Add `.env`
Create a `.env` file in the root directory and add the following:
```
GROQ_API_KEY=your-groq-api-key-here
```

### Run the App
```bash
uvicorn main:app --reload
```

## API Endpoints
### `POST /api/upload`
- **Description**: Upload a PDF or image file to extract text and generate an AI-powered summary.
- **Response**:
  - `summary`: The AI-generated summary of the document.
  - `report_path`: Path to the generated PDF report.

### `POST /api/url-to-report`
- **Description**: Submit a URL to scrape webpage content and generate an AI-powered summary.
- **Response**:
  - `summary`: The AI-generated summary of the webpage.
  - `report_path`: Path to the generated PDF report.

## PDF Report Features
- **Bold Section Headers**: Section titles are bolded for clarity.
- **Bullet Points**: Key details are presented as bullet points.
- **Structured Layout**: Clean and professional layout using ReportLab.

## Project Structure
```
f:\weekend
│
├── app
│   ├── api
│   │   └── router.py          # FastAPI routes for handling requests
│   ├── services
│   │   ├── processor.py       # Handles file uploads and generates summaries
│   │   └── url_processor.py   # Handles URL scraping and generates summaries
│   ├── utils
│       ├── ocr.py             # Extracts text from PDFs and images
│       └── templates.py       # Renders HTML templates
│          
├── main.py                    # Entry point for the FastAPI application
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (e.g., GROQ_API_KEY)
└── README.md                  # Project documentation
```


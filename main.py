from fastapi import FastAPI
from app.api.router import router as api_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Document Processor")
app.include_router(api_router)
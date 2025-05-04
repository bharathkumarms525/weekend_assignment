from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.processor import process_document
from app.services.url_processor import process_url
from pydantic import BaseModel

router = APIRouter(prefix="/api")

class URLRequest(BaseModel):
    url: str

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    result = await process_document(file)
    return result

@router.post("/url-to-report")
async def url_to_report(payload: URLRequest):
    try:
        result = await process_url(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
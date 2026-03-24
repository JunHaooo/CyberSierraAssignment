from pydantic import BaseModel
from typing import Optional

class UploadFileResponse(BaseModel):
    filename: str
    success: bool
    message: Optional[str] = None

class QueryRequest(BaseModel):
    filename: str
    query: str
    sheet_name: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
from pydantic import BaseModel
from typing import List

class TopRowsRequest(BaseModel):
    filename: str
    sheet_name: str = None
    n: int = 5

class TopRowsResponse(BaseModel):
    columns: List[str]
    rows: List[List]
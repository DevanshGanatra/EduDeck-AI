from uuid import UUID
from pydantic import BaseModel
from typing import List, Dict, Any

class RetrievalQuery(BaseModel):
    query: str
    top_k: int = 5

class RetrievalResponse(BaseModel):
    chunk_id: str
    document_id: str
    page_number: int | None
    text: str
    similarity_score: float

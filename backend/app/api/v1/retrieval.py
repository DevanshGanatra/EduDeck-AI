from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from app.schemas.base import StandardResponse, success_response
from app.schemas.retrieval import RetrievalQuery, RetrievalResponse
from app.models.core import User
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.vectorization import VectorizationService
from app.services.retrieval import RetrievalService

router = APIRouter()

@router.post("/project/{project_id}/vectorize", response_model=StandardResponse[str])
async def vectorize_document(
    project_id: UUID,
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # In a real app this would be a background task or part of the Document processing pipeline
    # We expose it here for easy re-indexing and testing.
    svc = VectorizationService(db)
    await svc.vectorize_document(document_id, project_id)
    return success_response(data="Success", message="Document vectorized and stored in ChromaDB")

@router.post("/project/{project_id}/playground", response_model=StandardResponse[List[RetrievalResponse]])
async def retrieval_playground(
    project_id: UUID,
    req: RetrievalQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    svc = RetrievalService(db)
    results = await svc.retrieve(query=req.query, project_id=project_id, top_k=req.top_k)
    return success_response(data=results, message="Retrieval successful")

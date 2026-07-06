import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import UUID
from app.services.vectorization import VectorizationService
from google.api_core.exceptions import ResourceExhausted

@pytest.mark.asyncio
async def test_vectorization_retry_logic():
    service = VectorizationService(db=AsyncMock())
    
    # Mock the DB repository to return a chunk
    mock_chunk = MagicMock()
    mock_chunk.chunk_text = "test text"
    service.chunk_repo.get_paginated_by_document = AsyncMock(return_value=([mock_chunk], 1))
    
    # Mock update_batch so we don't try to save to the fake DB
    service.chunk_repo.update_batch = AsyncMock()
    
    with patch("app.services.vectorization.genai.embed_content") as mock_embed:
        # Raise ResourceExhausted 2 times, then succeed
        mock_embed.side_effect = [
            ResourceExhausted("429 Quota Exceeded"),
            ResourceExhausted("429 Quota Exceeded"),
            {"embedding": [[0.1, 0.2, 0.3]]}
        ]
        
        with patch("app.services.vectorization.time.sleep") as mock_sleep:
            document_id = UUID("00000000-0000-0000-0000-000000000000")
            project_id = UUID("00000000-0000-0000-0000-000000000000")
            
            await service.vectorize_document(document_id, project_id)
            
            # Verify embed was called 3 times
            assert mock_embed.call_count == 3
            
            # Verify sleep was called 2 times
            assert mock_sleep.call_count == 2

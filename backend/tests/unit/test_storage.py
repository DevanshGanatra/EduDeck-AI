import pytest
import os
import io
import aioboto3
from moto import mock_aws
from app.services.storage import LocalStorageService, S3StorageService
from app.core.config import settings

@pytest.mark.asyncio
async def test_local_storage_service(tmp_path):
    # Set up a temporary upload directory
    upload_dir = str(tmp_path / "uploads")
    service = LocalStorageService(upload_dir=upload_dir)
    
    # Create a dummy file stream
    file_content = b"dummy pdf content"
    file_stream = io.BytesIO(file_content)
    
    # Save upload
    file_path, checksum = await service.save_upload(file_stream, filename="test.pdf")
    
    # Assertions
    assert os.path.exists(file_path)
    assert file_path.endswith("test.pdf")
    with open(file_path, "rb") as f:
        assert f.read() == file_content
    
    # Check public URL generation
    url = service.get_file_path(file_path)
    assert url == "http://localhost:8080/downloads/test.pdf"

@pytest.mark.asyncio
async def test_s3_storage_service(monkeypatch):
    from unittest.mock import AsyncMock, patch, MagicMock
    
    # Mock settings
    monkeypatch.setattr(settings, "AWS_S3_BUCKET_NAME", "test-bucket")
    monkeypatch.setattr(settings, "AWS_REGION_NAME", "us-east-1")
    monkeypatch.setattr(settings, "AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setattr(settings, "AWS_SECRET_ACCESS_KEY", "testing")
    
    # Create mocked s3 client
    mock_s3 = AsyncMock()
    mock_s3.put_object = AsyncMock()
    
    # Create a mock session that returns our mock_s3 client
    mock_session = MagicMock()
    mock_session.client.return_value.__aenter__.return_value = mock_s3
    
    with patch("app.services.storage.aioboto3.Session", return_value=mock_session):
        service = S3StorageService()
        
        file_content = b"dummy s3 content"
        file_stream = io.BytesIO(file_content)
        
        # Save upload
        file_reference, checksum = await service.save_upload(file_stream, filename="test_s3.pdf")
        
        # Assertions
        assert file_reference == "test_s3.pdf"
        
        # Verify put_object was called correctly
        mock_s3.put_object.assert_called_once()
        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs["Bucket"] == "test-bucket"
        assert call_kwargs["Key"] == "test_s3.pdf"
        assert call_kwargs["Body"] == file_content
        
        # Check public URL generation
        url = service.get_file_path(file_reference)
        assert "test-bucket.s3.us-east-1.amazonaws.com/test_s3.pdf" in url

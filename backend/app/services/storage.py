import os
import uuid
import hashlib
from typing import BinaryIO, Tuple
from abc import ABC, abstractmethod
import aioboto3
from app.core.config import settings

class StorageService(ABC):
    @abstractmethod
    async def save_upload(self, file_stream: BinaryIO) -> Tuple[str, str]:
        """Saves a file and returns (file_reference, sha256_checksum)"""
        pass
        
    @abstractmethod
    def get_file_path(self, file_reference: str) -> str:
        """Returns the local file path or public URL for the file"""
        pass

class LocalStorageService(StorageService):
    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_upload(self, file_stream: BinaryIO) -> Tuple[str, str]:
        secure_filename = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(self.upload_dir, secure_filename)
        
        sha256_hash = hashlib.sha256()
        with open(file_path, "wb") as buffer:
            while chunk := file_stream.read(8192):
                sha256_hash.update(chunk)
                buffer.write(chunk)
                
        return file_path, sha256_hash.hexdigest()
        
    def get_file_path(self, file_reference: str) -> str:
        return file_reference

class S3StorageService(StorageService):
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_REGION_NAME
        self.session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region
        )

    async def save_upload(self, file_stream: BinaryIO) -> Tuple[str, str]:
        secure_filename = f"{uuid.uuid4()}.pdf"
        
        # We need to compute checksum while keeping the file stream intact for upload
        sha256_hash = hashlib.sha256()
        file_data = file_stream.read()
        sha256_hash.update(file_data)
        
        async with self.session.client('s3') as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=secure_filename,
                Body=file_data,
                ContentType="application/pdf"
            )
            
        return secure_filename, sha256_hash.hexdigest()

    def get_file_path(self, file_reference: str) -> str:
        # Generate a public URL based on the bucket and region
        # For a truly private bucket, this should generate a presigned URL asynchronously
        # But since get_file_path is synchronous, we return the direct S3 URL assuming bucket is public,
        # or you can use this reference later in async code to get presigned URL.
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{file_reference}"

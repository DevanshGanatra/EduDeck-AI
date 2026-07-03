import os
import uuid
import hashlib
from typing import BinaryIO, Tuple
from abc import ABC, abstractmethod

class StorageService(ABC):
    @abstractmethod
    async def save_upload(self, file_stream: BinaryIO) -> Tuple[str, str]:
        """Saves a file and returns (file_path, sha256_checksum)"""
        pass
        
    @abstractmethod
    def get_file_path(self, file_reference: str) -> str:
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

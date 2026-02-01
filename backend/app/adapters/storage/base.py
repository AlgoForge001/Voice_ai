from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorage(ABC):
    """
    Abstract storage interface.
    Allows swapping between local, S3, GCS, etc.
    """
    
    @abstractmethod
    async def upload_file(self, file_path: str, destination: str) -> str:
        """
        Upload file to storage.
        
        Args:
            file_path: Local file path
            destination: Destination path/key
        
        Returns:
            Public URL to access the file
        """
        pass
    
    @abstractmethod
    async def download_file(self, source: str, destination: str):
        """Download file from storage."""
        pass
    
    @abstractmethod
    async def delete_file(self, path: str):
        """Delete file from storage."""
        pass
    
    @abstractmethod
    async def get_url(self, path: str) -> str:
        """Get public URL for file."""
        pass

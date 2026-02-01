import shutil
from pathlib import Path
from .base import BaseStorage


class LocalStorage(BaseStorage):
    """
    Local filesystem storage adapter.
    Use for development or single-server deployments.
    """
    
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(self, file_path: str, destination: str) -> str:
        """Copy file to local storage."""
        dest_path = self.base_path / destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, dest_path)
        
        # Return full backend URL so frontend can access it
        return f"http://localhost:8000/storage/{destination}"
    
    async def download_file(self, source: str, destination: str):
        """Copy file from storage to destination."""
        source_path = self.base_path / source
        shutil.copy2(source_path, destination)
    
    async def delete_file(self, path: str):
        """Delete file from storage."""
        file_path = self.base_path / path
        if file_path.exists():
            file_path.unlink()
    
    async def get_url(self, path: str) -> str:
        """Get URL for file."""
        return f"http://localhost:8000/storage/{path}"


def get_storage_adapter() -> BaseStorage:
    """
    Factory function to get storage adapter based on config.
    """
    from app.config import get_settings
    settings = get_settings()
    
    if settings.STORAGE_TYPE == "local":
        return LocalStorage()
    elif settings.STORAGE_TYPE == "s3":
        # TODO: Implement S3Storage adapter
        raise NotImplementedError("S3 storage not yet implemented")
    else:
        raise ValueError(f"Unknown storage type: {settings.STORAGE_TYPE}")

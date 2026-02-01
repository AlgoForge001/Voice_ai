# Models module
from app.utils.database import Base, get_db, engine
from .user import User
from .tts_job import TTSJob
from .usage_log import UsageLog

__all__ = ["Base", "get_db", "engine", "User", "TTSJob", "UsageLog"]


def create_tables():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

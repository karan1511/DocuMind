import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env in root directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

class Settings:
    # Azure OpenAI
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "text-embedding-3-small")
    AZURE_OPENAI_CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL", "gpt-4.1")

    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://vector-db:6333")
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "rag_documents")

    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:admin@localhost:27017/")
    MONGODB_DB = os.getenv("MONGODB_DB", "rag_jobs")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "job_status")

    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "valkey")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    # Documents
    DOCUMENTS_DIR = Path(__file__).parent.parent / "documents"

settings = Settings()

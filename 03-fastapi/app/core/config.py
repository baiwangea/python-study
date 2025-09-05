from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = "A modern FastAPI project structure"
    
    DATABASE_URL: str = "sqlite:///./test.db"

    class Config:
        case_sensitive = True

settings = Settings()
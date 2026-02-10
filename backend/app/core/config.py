from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str 
    
    #security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 Hours
    
    #cloudinary 
    CLOUDINARY_URL: Optional[str] = None

    #this tells pydantic to look for a .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
    
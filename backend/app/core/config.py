from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    #db
    DATABASE_URL: str 
    REDIS_URL: str
    
    #security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 Hours
    
    #cloudinary 
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    #email
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str 
    MAIL_FROM_NAME: str 

    #this tells pydantic to look for a .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
    
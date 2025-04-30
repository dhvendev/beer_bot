from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER:str
    DB_PASSWORD:str
    DB_HOST:str
    DB_NAME:str
    DB_PORT: int
    TOKEN:str

    ADMIN_USERNAME:str
    LINK_BOT:str
    LINK_CHAT:str
    LINK_NEWS:str

    ID_CHAT:int
    ID_NEWS:int
    
    class Config:
        env_file = ".env"

settings = Settings()
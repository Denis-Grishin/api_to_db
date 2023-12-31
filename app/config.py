from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load the .env file

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_password: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    api_football_key: str

    class Config:
        env_file = ".env"

settings = Settings()

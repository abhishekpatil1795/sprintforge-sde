from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./sprintforge.db"
    jwt_secret: str = "development-only-change-this-secret"
    jwt_expire_minutes: int = 120
    client_origin: str = "http://localhost:5173"
    environment: str = "development"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

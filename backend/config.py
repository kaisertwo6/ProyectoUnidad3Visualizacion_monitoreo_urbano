from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Lee del .env, sin defaults
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_TITLE: str = "Sistema de Monitoreo Urbano"
    API_VERSION: str = "1.0.0"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

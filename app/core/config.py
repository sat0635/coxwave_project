from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    embedding_model: str
    llm_model: str
    session_secret_key: str

    class Config:
        env_file = "app/.env" 

# static value
settings = Settings()
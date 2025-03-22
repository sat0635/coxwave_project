from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    embedding_model: str
    llm_model: str

    class Config:
        env_file = ".env" 

# static value
settings = Settings()
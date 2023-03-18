from pydantic import BaseSettings

class _Settings(BaseSettings):
    openai_api_key: str
    slack_endpoint: str

    class Config:
        env_file = '.env'


settings = _Settings()

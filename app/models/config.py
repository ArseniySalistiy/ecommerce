from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    algorithm: str = 'HS256'
    secret_key: str = '18d697b04feee9b66eac281ad03d86d8c00d99af6e8772412d15fc7b92197a15'

settings = Settings()
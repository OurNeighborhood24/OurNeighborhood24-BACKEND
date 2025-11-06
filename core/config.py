from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 환경 설정"""

    # 애플리케이션 설정
    app_name: str = "Joint Hackathon API"
    debug: bool = True
    api_prefix: str = ""

    # JWT 설정
    secret_key: str = os.getenv("JWT_SECRET_KEY", "asdadsadsadsd")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))  # 30일 (시연용)
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 7))

    # 데이터베이스 설정
    database_url: str = os.getenv("mysql+pymysql://root:kdoornega0128@localhost:3306/OurNeighborhood", "mysql+pymysql://user:password@localhost:3306/dbname")
    db_echo: bool = False

    # CORS 설정
    cors_origins: list = ["*"]  # 모든 origin 허용
    cors_credentials: bool = False
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # 파일 업로드 설정
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

    # AWS S3 설정
    aws_access_key: str = os.getenv("AWS_ACCESS_KEY", "")
    aws_secret_key: str = os.getenv("AWS_SECRET_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "ap-northeast-2")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "")

    google_api_key : str = os.getenv("GOOGLE_API_KEY", "")

    tmap_api_key : str = os.getenv("TMAP_API_KEY", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "marketplace"
    debug: bool = False

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "marketplace"
    postgres_user: str = "marketplace"
    postgres_password: str = "password"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    s3_endpoint_url: str = "http://rustfs:9000"
    s3_access_key: str = "rustfsadmin"
    s3_secret_key: str = "rustfsadmin"
    s3_bucket_name: str = "post-images"
    s3_region: str = "us-east-1"
    s3_public_url: str = "http://localhost:9000"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

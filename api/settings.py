from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "enade_db"
    postgres_user: str = "enade_user"
    postgres_password: str = "enade_password"

    api_port: int = 8000

    # Execuções de benchmark a ocultar por padrão (`?apenas_validas=true`).
    # Vazio por padrão: os ids são um BIGSERIAL e voltam a 1 a cada
    # `05_criar_schema_postgres.py --reset`, então uma lista fixa acaba
    # escondendo justamente as execuções válidas da rodada atual.
    # Para ocultar execuções inválidas de uma rodada específica, defina a
    # variável de ambiente BENCHMARK_IDS_EXCLUIR (JSON), ex.: '[1,2,3]'.
    benchmark_ids_excluir: list[int] = Field(default_factory=list)
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )

    pool_minconn: int = 1
    pool_maxconn: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

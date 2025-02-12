"""settings."""
from functools import cache
from queue import Queue

from neomodel import config, db, install_all_labels
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  # 追加
    )

    NEO4J_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    PORT: int = 8000

    def setup_db(self) -> None:
        """DB設定."""
        config.DATABASE_URL = self.NEO4J_URL
        install_all_labels()

    def terdown_db(self) -> None:
        """DB切断."""
        if db.driver is not None:
            db.close_connection()


@cache
def response_queue() -> Queue:
    """レスポンスを保存するためのグローバルキュー."""
    return Queue()

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    allowed_users: str = ""
    allowed_chat_id: int | None = None
    default_currency: str = "EUR"
    db_path: str = "expenses.db"
    webapp_url: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def allowed_user_ids(self) -> set[int]:
        if not self.allowed_users.strip():
            return set()
        return {int(x.strip()) for x in self.allowed_users.split(",") if x.strip()}


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Example: mysql+pymysql://fem_app:ALElucas@localhost:3306/fem_trucking
    mysql_url: str

    app_name: str = "FEM Trucking API"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
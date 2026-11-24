"""Nạp và kiểm tra cấu hình từ biến môi trường (pydantic-settings).

Biến môi trường: xem .env.example.
Cấu hình cửa hàng hard-code (hotline, Zalo, người gửi, tài khoản nhận chuyển khoản,
ngưỡng tồn kho thấp) đặt ở đây hoặc trong module dùng nó, không sửa trên hệ thống (BR).
"""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SHIPPING_FEE: str
    SEPAY_API_KEY: str

    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int = Field(default=587, ge=1, le=65535)
    SMTP_SECURITY: Literal["starttls", "ssl"] = "starttls"
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = Field(default="", repr=False)
    GOOGLE_REDIRECT_URI: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


Config = Settings()

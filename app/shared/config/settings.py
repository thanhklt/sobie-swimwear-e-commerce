"""Nạp và kiểm tra cấu hình từ biến môi trường (pydantic-settings); chưa triển khai.

Biến môi trường: xem .env.example (DATABASE_URL, SHIPPING_FEE, SEPAY_API_KEY, SECRET_KEY).
Cấu hình cửa hàng hard-code (hotline, Zalo, người gửi, tài khoản nhận chuyển khoản,
ngưỡng tồn kho thấp) đặt ở đây hoặc trong module dùng nó, không sửa trên hệ thống (BR).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SHIPPING_FEE: str
    SEPAY_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()


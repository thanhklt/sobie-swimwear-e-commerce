"""Nạp và kiểm tra cấu hình từ biến môi trường (pydantic-settings); chưa triển khai.

Biến môi trường: xem .env.example (DATABASE_URL, SHIPPING_FEE, SEPAY_API_KEY, SECRET_KEY,
VIETQR_*). Tài khoản nhận VietQR nạp qua env (mặc định demo); hotline/Zalo/người gửi/
ngưỡng tồn kho thấp hard-code ở module dùng chúng, không sửa trên hệ thống (BR).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SHIPPING_FEE: str
    SEPAY_API_KEY: str
    # Tài khoản nhận VietQR (UC-20 hard-code cửa hàng) — giá trị demo an toàn [GD]
    VIETQR_BANK_ID: str = "970422"  # BIN ngân hàng (vd. MB)
    VIETQR_ACCOUNT_NO: str = "0123456789"
    VIETQR_ACCOUNT_NAME: str = "SOBIE SWIMWEAR"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()


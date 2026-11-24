"""Tầng Route của module shopping: nhận request, kiểm tra dữ liệu đầu vào, gọi service,
trả response (FastAPI + Jinja SSR).

Chưa gắn HTML/SSR trong vòng service+repo+test (feature/shopping).
Nghiệp vụ giỏ / wishlist nằm ở service.py — router sẽ gọi service khi làm UI.
Không gọi repository hoặc database trực tiếp.
"""

"""Promotion dùng truy vấn SQL tường minh tới schema promotion, theo data model v2.

DTO request/response nằm trong schemas.py; model PostgreSQL chuẩn được định nghĩa
ở infra/postgres/init.sql để module không tự tạo bảng hoặc cột ngoài nguồn chuẩn.
"""

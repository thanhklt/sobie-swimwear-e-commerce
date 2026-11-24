"""Dữ liệu PostgreSQL dùng cho các ca nghiệm thu của reporting."""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from os import environ
from pathlib import Path
from secrets import token_urlsafe

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.routing import Match

from app.shared.web.session import PORTAL_SESSION_COOKIE, STOREFRONT_SESSION_COOKIE

INIT_SQL = Path(__file__).resolve().parents[2] / "infra" / "postgres" / "init.sql"


@pytest.fixture
def reporting_test_url():
    return environ.get("REPORTING_TEST_DATABASE_URL") or environ.get(
        "UC37_TEST_DATABASE_URL"
    )


@pytest.fixture
def dashboard_app(monkeypatch, reporting_test_url):
    monkeypatch.setenv(
        "DATABASE_URL", reporting_test_url or "postgresql://localhost/uc37_test"
    )
    for setting in ("SECRET_KEY", "SEPAY_API_KEY"):
        monkeypatch.setenv(setting, token_urlsafe())
    monkeypatch.setenv("SHIPPING_FEE", "12000")

    from app.main import app

    return app


@pytest.fixture
def dashboard_path(dashboard_app):
    path = environ.get("UC37_TEST_DASHBOARD_PATH", "/admin/dashboard")
    scope = {"type": "http", "method": "GET", "path": path, "app": dashboard_app}
    if not any(route.matches(scope)[0] is Match.FULL for route in dashboard_app.routes):
        pytest.fail(f"UC-37 chưa đăng ký GET {path} trên ứng dụng.", pytrace=False)
    return path


@pytest.fixture
def reporting_db(dashboard_app, reporting_test_url, monkeypatch):
    if not reporting_test_url:
        pytest.skip(
            "Cần REPORTING_TEST_DATABASE_URL trỏ tới một database PostgreSQL trống dành cho test."
        )
    url = make_url(reporting_test_url)
    if url.drivername not in {"postgresql", "postgres", "postgresql+asyncpg"}:
        pytest.fail(
            "URL database test của reporting phải là URL PostgreSQL dùng asyncpg.",
            pytrace=False,
        )

    from app.shared.database import engine as database

    test_engine = create_async_engine(
        url.set(drivername="postgresql+asyncpg"), hide_parameters=True
    )
    monkeypatch.setattr(database, "engine", test_engine)

    async def open_database():
        connection = await test_engine.connect()
        transaction = await connection.begin()
        # Bắt đầu transaction ở driver trước khi chạy các câu lệnh SQL trực tiếp.
        await connection.exec_driver_sql("SELECT 1")
        return connection, transaction

    with TestClient(dashboard_app, base_url="https://testserver") as client:
        connection, transaction = client.portal.call(open_database)
        try:

            async def install_schema():
                raw = await connection.get_raw_connection()
                driver = raw.driver_connection
                existing_schema = await driver.fetchval(
                    """
                    SELECT nspname FROM pg_namespace
                    WHERE nspname IN ('identity', 'catalog', 'shopping', 'ordering',
                                      'payment', 'promotion', 'inventory')
                    LIMIT 1
                    """
                )
                if existing_schema:
                    pytest.fail(
                        f"Database test phải trống, đã có schema {existing_schema!r}."
                    )
                # pgcrypto phục vụ crypt() trong seed.sql. Fixture tự tạo dữ liệu;
                # gen_random_uuid() đã có sẵn trong PostgreSQL từ phiên bản 13.
                schema = INIT_SQL.read_text(encoding="utf-8").replace(
                    "CREATE EXTENSION IF NOT EXISTS pgcrypto;", "", 1
                )
                await driver.execute(schema)
                return driver

            driver = client.portal.call(install_schema)
            monkeypatch.setattr(
                database,
                "session_factory",
                async_sessionmaker(
                    connection,
                    class_=AsyncSession,
                    join_transaction_mode="create_savepoint",
                ),
            )
            data = DashboardData(client.portal, driver)
            data.seed_lookups()
            yield client, data
        finally:
            client.portal.call(transaction.rollback)
            client.portal.call(connection.close)
            client.portal.call(test_engine.dispose)


@pytest.fixture
def dashboard_db(dashboard_path, reporting_db):
    return reporting_db


class DashboardData:
    def __init__(self, portal, connection):
        self.portal = portal
        self.connection = connection
        self.accounts = {}
        self.next_order = 1
        self.next_product = 1
        self.next_receipt = 1

    def account(self, role):
        if role not in self.accounts:
            account_id = {
                "customer": "KH-20261122-0001",
                "employee": "NV-TEST-19900101-0001",
                "admin": "AD-TEST-19900101-0001",
            }[role]
            self.accounts[role] = self._value(
                """
                WITH role AS (
                    INSERT INTO identity.role (role_code, role_name) VALUES ($1, $1) RETURNING role_key
                )
                INSERT INTO identity.account (account_id, account_role_key, account_email,
                    account_phone_number, account_hash_password, account_name, account_date_of_birth)
                SELECT $2, role_key, $3, $4, $5, $1, DATE '1990-01-01' FROM role
                RETURNING account_key
                """,
                role,
                account_id,
                f"{role}@example.test",
                f"090000000{len(self.accounts)}",
                token_urlsafe(),
            )
        return self.accounts[role]

    def sign_in(self, client, role):
        token = token_urlsafe()
        self._execute(
            """
            INSERT INTO identity.session (session_account_key, session_token_hash, session_expires_at)
            VALUES ($1, $2, $3)
            """,
            self.account(role),
            sha256(token.encode()).hexdigest(),
            datetime.now(UTC) + timedelta(minutes=30),
        )
        cookie = (
            STOREFRONT_SESSION_COOKIE if role == "customer" else PORTAL_SESSION_COOKIE
        )
        client.cookies.set(cookie, token)

    def product(self, name, *, stock=20, variant_status="ACTIVE"):
        product_code = f"SP-{self.next_product:04d}"
        self.next_product += 1
        sku = f"{product_code}-DO-M"
        variant_key = self._value(
            """
            WITH product AS (
                INSERT INTO catalog.product (product_id, product_name, product_status,
                                             product_category_key, product_gender_key)
                SELECT $1, $2, 'ACTIVE', category_key, gender_key
                FROM catalog.category CROSS JOIN catalog.gender RETURNING product_key
            )
            INSERT INTO catalog.variant (variant_id, variant_product_key, variant_size_key,
                                         variant_color_key, variant_sell_price, variant_status)
            SELECT $3, product_key, size_key, color_key, 200000, $4
            FROM product CROSS JOIN catalog.size CROSS JOIN catalog.color
            WHERE catalog.size.size_name = 'M' AND catalog.color.color_name = 'Đỏ'
            RETURNING variant_key
            """,
            product_code,
            name,
            sku,
            variant_status,
        )
        self._execute(
            """
            INSERT INTO inventory.stock (stock_variant_key, stock_quantity, stock_cost_price)
            VALUES ($1, $2, 90000)
            """,
            variant_key,
            stock,
        )
        return variant_key, sku

    def add_large_variant(self, source_variant_key):
        return self._value(
            """
            WITH large_size AS (
                INSERT INTO catalog.size (size_name) VALUES ('L')
                ON CONFLICT (size_name) DO UPDATE SET size_name = EXCLUDED.size_name
                RETURNING size_key
            ), large_variant AS (
                INSERT INTO catalog.variant (variant_id, variant_product_key, variant_size_key,
                                             variant_color_key, variant_sell_price)
                SELECT product.product_id || '-DO-L', source.variant_product_key,
                       large_size.size_key, source.variant_color_key, source.variant_sell_price
                FROM catalog.variant AS source
                JOIN catalog.product AS product ON product.product_key = source.variant_product_key
                CROSS JOIN large_size
                WHERE source.variant_key = $1
                RETURNING variant_key
            )
            INSERT INTO inventory.stock (stock_variant_key, stock_quantity, stock_cost_price)
            SELECT variant_key, 20, 90000 FROM large_variant
            RETURNING stock_variant_key
            """,
            source_variant_key,
        )

    def order(
        self,
        status,
        placed_at,
        *,
        delivered_at=None,
        lines=(),
        subtotal=0,
        discount=0,
        unit_price=200_000,
    ):
        code = f"{self.next_order:08d}"
        self.next_order += 1
        order_key = self._value(
            """
            INSERT INTO ordering."order" (order_code, order_account_key, order_payment_key,
                order_customer_name, order_customer_phone_number, order_customer_house_number,
                order_customer_ward, order_customer_city, order_customer_country, order_shipping_fee,
                order_total_price, order_payment_status, order_status, order_created_date,
                order_updated_date, order_discount_amount)
            SELECT $1, $2, payment_key, 'Khách', '0900000000', '1', 'Phường', 'TP.HCM', 'Việt Nam',
                12000, $3, CASE WHEN $4 = 'DELIVERED' THEN 'PAID' ELSE 'UNPAID' END, $4, $5, $6, $7
            FROM ordering.payment RETURNING order_key
            """,
            code,
            self.account("customer"),
            subtotal + 12_000,
            status,
            placed_at,
            delivered_at or placed_at,
            discount,
        )
        for variant_key, quantity, unit_cost in lines:
            self._execute(
                """
                INSERT INTO ordering.order_detail (order_detail_order_key, order_detail_variant_key,
                    order_detail_quantity, order_detail_unit_price, order_detail_cost_price)
                VALUES ($1, $2, $3, $4, $5)
                """,
                order_key,
                variant_key,
                quantity,
                unit_price,
                unit_cost,
            )
        self._execute(
            """
            INSERT INTO ordering.order_status_history (order_status_history_order_key,
                order_status_history_to_value, order_status_history_source, order_status_history_changed_time)
            VALUES ($1, 'PENDING', 'CUSTOMER', $2)
            """,
            order_key,
            placed_at,
        )
        if delivered_at is not None:
            self._execute(
                """
                INSERT INTO ordering.order_status_history (order_status_history_order_key,
                    order_status_history_from_value, order_status_history_to_value, order_status_history_source,
                    order_status_history_changed_time)
                VALUES ($1, 'SHIPPING', 'DELIVERED', 'SHIPPING_SIMULATOR', $2)
                """,
                order_key,
                delivered_at,
            )
            self._execute(
                """
                INSERT INTO ordering.invoice (invoice_id, invoice_order_key, invoice_created_date, invoice_snapshot_json)
                VALUES ($1, $2, $3, '{}'::jsonb)
                """,
                f"HD-{code}",
                order_key,
                delivered_at,
            )

    def receipt(self, supplier_key, variant_key, status, total, created_at):
        code = f"PN-{self.next_receipt:04d}"
        self.next_receipt += 1
        self._execute(
            """
            WITH receipt AS (
                INSERT INTO inventory.goods_receipt (goods_receipt_id, goods_receipt_supplier_key,
                    goods_receipt_account_key, goods_receipt_status, goods_receipt_final_price,
                    goods_receipt_created_date)
                VALUES ($1, $2, $3, $4, $5, $6) RETURNING goods_receipt_key
            )
            INSERT INTO inventory.goods_receipt_detail (goods_receipt_detail_goods_receipt_key,
                goods_receipt_detail_variant_key, goods_receipt_detail_quantity,
                goods_receipt_detail_unit_price, goods_receipt_detail_total_price)
            SELECT goods_receipt_key, $7, 1, $5, $5 FROM receipt
            """,
            code,
            supplier_key,
            self.account("employee"),
            status,
            total,
            created_at,
            variant_key,
        )

    def seed_lookups(self):
        self._execute("""
            INSERT INTO catalog.category (category_name) VALUES ('Đồ bơi');
            INSERT INTO catalog.gender (gender_name) VALUES ('Unisex');
            INSERT INTO catalog.size (size_name) VALUES ('M');
            INSERT INTO catalog.color (color_name) VALUES ('Đỏ');
            INSERT INTO ordering.payment (payment_name) VALUES ('COD');
        """)

    def supplier(self):
        return self._value("""
            INSERT INTO inventory.supplier (supplier_id, supplier_name, supplier_phone_number)
            VALUES ('NCC-0001', 'Nhà cung cấp X', '0900000009') RETURNING supplier_key
        """)

    def _value(self, sql, *params):
        return self.portal.call(self.connection.fetchval, sql, *params)

    def _execute(self, sql, *params):
        self.portal.call(self.connection.execute, sql, *params)

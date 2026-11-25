"""Input rules: UC-32 AC-1/2/9 and UC-33 AC-1/2/3/4/10."""

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.inventory.schemas import ReceiptInput, ReceiptLineInput, SupplierInput


def test_uc32_ac1_ac9_valid_supplier():
    data = SupplierInput(name="  Công ty Biển Xanh  ", phone_number=" 0901234567 ", email="contact@example.com")
    assert data.name == "Công ty Biển Xanh"
    assert data.phone_number == "0901234567"


@pytest.mark.parametrize("values", [{"name": ""}, {"name": "  "}, {"phone_number": ""}, {"email": "invalid"}])
def test_uc32_ac2_invalid_supplier(values):
    with pytest.raises(ValidationError):
        SupplierInput(**({"name": "Nhà cung cấp", "phone_number": "0901234567"} | values))


@pytest.mark.parametrize("quantity,price", [(0, 1), (-1, 0), (1, -1), ("1.5", 0), (1.0, 0), (True, 0), (1, Decimal("1")), (1, "1e3")])
def test_uc33_ac3_invalid_integer_quantity_or_price(quantity, price):
    with pytest.raises(ValidationError):
        ReceiptLineInput(variant_key=uuid4(), quantity=quantity, unit_price=price)


def test_uc33_ac1_ac10_exact_totals():
    data = ReceiptInput(supplier_key=uuid4(), lines=[{"variant_key": uuid4(), "quantity": "20", "unit_price": "130000"}])
    assert data.total_price == 2600000
    assert ReceiptLineInput(variant_key=uuid4(), quantity="1", unit_price="0").total_price == 0


def test_uc33_ac2_ac4_empty_and_duplicate_lines():
    key = uuid4()
    for lines in ([], [{"variant_key": key, "quantity": 1, "unit_price": 0}] * 2):
        with pytest.raises(ValidationError):
            ReceiptInput(supplier_key=uuid4(), lines=lines)

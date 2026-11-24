"""UC-18 AC-5: giỏ khách vãng lai lưu localStorage (phía trình duyệt).

AC này thuộc FE; backend shopping không lưu giỏ guest vào DB.
Test đánh dấu manual — gộp giỏ khi login phủ bởi AC-6/9/10/11.
"""

from __future__ import annotations

import pytest


@pytest.mark.manual
def test_uc18_ac5_guest_cart_persists_in_localstorage() -> None:
    pytest.skip(
        "UC-18 AC-5: giỏ khách vãng lai nằm ở localStorage — kiểm tra thủ công trên UI; "
        "BE chỉ nhận payload khi merge (AC-6+)."
    )

"""Dữ liệu mẫu tạm thời. Thay bằng truy vấn thật khi triển khai UC-09."""

from decimal import ROUND_HALF_UP, Decimal

from app.modules.catalog.schemas import (
    HomeCategoryTile,
    HomeCollectionBanner,
    HomeCoupon,
    HomePage,
    HomeProductCard,
)

_HOME_IMAGES = "/static/images/home"
_PRODUCT_IMAGES = "/static/images/products"


def _product_card(
    slug: str,
    name: str,
    price: int,
    colors: tuple[str, ...],
    discount_percent: int | None = None,
) -> HomeProductCard:
    sale_price = None
    if discount_percent is not None:
        discounted = Decimal(price) * (100 - discount_percent) / 100
        sale_price = int(discounted.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    return HomeProductCard(
        product_id=f"sample-{slug}",
        name=name,
        image_url=f"{_PRODUCT_IMAGES}/sample-{slug}.jpg",
        price=price,
        sale_price=sale_price,
        discount_percent=discount_percent,
        colors=colors,
        out_of_stock=False,
        detail_url="#",
    )


HOME_PAGE = HomePage(
    best_sellers=(
        _product_card("bikini-hoa-nhi", "Bikini Hoa Nhí", 290_000, ("#aa162b", "#12253d"), 15),
        _product_card("olive-ribbed", "Olive Ribbed", 520_000, ("#566340", "#171a16")),
        _product_card("cat-vang-bandeau", "Cát Vàng Bandeau", 460_000, ("#d7bc9f", "#fffdf6")),
    ),
    new_arrivals=(
        _product_card("terracotta", "Terracotta", 550_000, ("#b65e48", "#c9a987")),
        _product_card("tailored-olive", "Tailored Olive", 395_000, ("#596745", "#12253d")),
        _product_card("bikini-xanh-bien", "Bikini Xanh Biển", 440_000, ("#176b92", "#b6d4e2")),
        _product_card("seafoam", "Seafoam", 340_000, ("#9abfb4", "#fffdf6")),
    ),
    categories=(
        HomeCategoryTile(("Bikini",), f"{_HOME_IMAGES}/cat-bikini.jpg", "Bikini đỏ hoa nhí bên biển", "#"),
        HomeCategoryTile(
            ("Đồ bơi", "một mảnh"),
            f"{_HOME_IMAGES}/cat-one-piece.jpg",
            "Đồ bơi một mảnh màu olive bên bờ đá",
            "#",
        ),
        HomeCategoryTile(
            ("Quần bơi", "nam"),
            f"{_HOME_IMAGES}/cat-men.jpg",
            "Quần bơi nam màu olive bên bãi biển",
            "#",
        ),
        HomeCategoryTile(
            ("Đồ bơi", "trẻ em"),
            f"{_HOME_IMAGES}/cat-kids.jpg",
            "Bộ đồ bơi tay dài sọc xanh seafoam trên cát",
            "#",
        ),
    ),
    collection=HomeCollectionBanner(
        name="Resort Essentials",
        description="Những thiết kế linh hoạt cho kỳ nghỉ và mọi chuyến đi bên làn nước.",
        image_url=f"{_HOME_IMAGES}/collection-resort.jpg",
        image_alt="Người mẫu đeo kính râm mặc đồ bơi olive bên hồ bơi",
        url="#",
    ),
    coupon=HomeCoupon(code="HE2026", discount_percent=15, minimum_order=300_000),
)

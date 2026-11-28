"""Schema đầu vào / đầu ra của module catalog, tách biệt với model lưu trữ."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HomeProductCard:
    product_id: str
    name: str
    image_url: str
    price: int
    sale_price: int | None
    discount_percent: int | None
    colors: tuple[str, ...]
    out_of_stock: bool
    detail_url: str


@dataclass(frozen=True)
class HomeCategoryTile:
    label_lines: tuple[str, ...]
    image_url: str
    image_alt: str
    url: str

    @property
    def name(self) -> str:
        return " ".join(self.label_lines)


@dataclass(frozen=True)
class HomeCollectionBanner:
    name: str
    description: str
    image_url: str
    image_alt: str
    url: str


@dataclass(frozen=True)
class HomeCoupon:
    code: str
    discount_percent: int
    minimum_order: int


@dataclass(frozen=True)
class HomePage:
    best_sellers: tuple[HomeProductCard, ...]
    new_arrivals: tuple[HomeProductCard, ...]
    categories: tuple[HomeCategoryTile, ...]
    collection: HomeCollectionBanner | None
    coupon: HomeCoupon | None

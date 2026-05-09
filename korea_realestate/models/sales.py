from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator


class LandSaleRecord(BaseModel):
    deal_date: str
    region: str
    dong: str
    land_category: str
    area_sqm: Decimal
    price_10k_won: int
    price_per_sqm: Optional[Decimal] = None
    zoning: Optional[str] = None
    buyer_type: Optional[str] = None
    cancelled: bool = False

    @field_validator("price_per_sqm", mode="before")
    @classmethod
    def compute_price_per_sqm(cls, v, info):
        if v is not None:
            return v
        data = info.data
        area = data.get("area_sqm")
        price = data.get("price_10k_won")
        if area and price and Decimal(str(area)) > 0:
            return round(Decimal(str(price)) / Decimal(str(area)), 2)
        return None

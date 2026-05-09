from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ZoningRecord(BaseModel):
    region: str
    dong: Optional[str] = None
    parcel: Optional[str] = None
    land_category: Optional[str] = None
    zoning_class: Optional[str] = None
    zoning_detail: Optional[str] = None
    area_sqm: Optional[Decimal] = None
    restrictions: Optional[str] = None


class AppraisedValueRecord(BaseModel):
    region: str
    dong: Optional[str] = None
    parcel: Optional[str] = None
    area_sqm: Optional[Decimal] = None
    value_per_sqm: Optional[int] = None
    total_value: Optional[int] = None
    reference_year: Optional[int] = None

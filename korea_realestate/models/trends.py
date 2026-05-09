from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PriceTrendRecord(BaseModel):
    period: str
    region: str
    index_value: Optional[Decimal] = None
    change_pct_mom: Optional[Decimal] = None
    change_pct_yoy: Optional[Decimal] = None

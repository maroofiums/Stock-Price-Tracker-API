from pydantic import BaseModel
from datetime import datetime


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime


class AlertRequest(BaseModel):
    symbol: str
    currency: str = "usd"
    target_price: float
    email: str

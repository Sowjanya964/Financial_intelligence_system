from typing import List, Optional
from pydantic import BaseModel

class InsightRequest(BaseModel):
    ticker: str

class PriceResult(BaseModel):
    type: str = "price"
    ticker: str
    price: Optional[float] = None
    change_percent: Optional[float] = None
    company_name: Optional[str] = None
    error: Optional[str] = None

class NewsResult(BaseModel):
    type: str = "news"
    ticker: str
    headlines: List[str] = []
    error: Optional[str] = None

class SentimentResult(BaseModel):
    type: str = "sentiment"
    ticker: str
    score: Optional[float] = None
    label: Optional[str] = None
    summary: Optional[str] = None
    error: Optional[str] = None



from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Location(BaseModel):
    text: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    country: Optional[str] = None

class Organization(BaseModel):
    text: str
    start_char: int
    end_char: int
    confidence: float = 1.0

class Person(BaseModel):
    text: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    role: Optional[str] = None

class DateEntity(BaseModel):
    text: str
    start_char: int
    end_char: int
    parsed_date: Optional[datetime] = None
    confidence: float = 1.0

class AmountEntity(BaseModel):
    text: str
    start_char: int
    end_char: int
    currency: str  # "LKR", "USD", etc.
    amount: float
    normalized_lkr: Optional[float] = None
    confidence: float = 1.0

class PercentageEntity(BaseModel):
    text: str
    start_char: int
    end_char: int
    value: float
    confidence: float = 1.0

class ExtractedEntities(BaseModel):
    article_id: str
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    locations: List[Location] = []
    organizations: List[Organization] = []
    persons: List[Person] = []
    dates: List[DateEntity] = []
    amounts: List[AmountEntity] = []
    percentages: List[PercentageEntity] = []
    processing_time_ms: Optional[float] = None

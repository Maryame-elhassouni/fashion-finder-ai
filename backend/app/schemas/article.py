from pydantic import BaseModel, Field, field_validator , ConfigDict
from datetime import datetime
import re

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:         int
    name:       str
    slug:       str
    icon_emoji: str

   
class ArticleCreate(BaseModel):
    name:        str   = Field(..., min_length=2, max_length=200)
    description: str   = Field(..., min_length=10, max_length=2000)
    price:       float = Field(..., gt=0, le=10000)
    brand:       str | None = Field(None, max_length=100)
    image_url:   str | None = Field(None, max_length=500)
    category_id: int  = Field(..., ge=1)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return " ".join(v.strip().split())

    @field_validator("price")
    @classmethod
    def round_price(cls, v: float) -> float:
        return round(v, 2)
    @field_validator("image_url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^https?://.+\.(jpg|jpeg|png|webp|gif)(\?.*)?$", v, re.I):
            raise ValueError("image_url doit être une URL vers une image valide")
        return v

class ArticleUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=200)
    description: str | None = Field(None, min_length=10)
    price: float | None = Field(None, gt=0, le=10000)
    brand: str | None = Field(None, max_length=100)
    image_url: str | None = Field(None, max_length=500)
    category_id: int | None = Field(None, ge=1)

    @field_validator("price")
    @classmethod
    def round_price(cls, v):
        if v is None:
            return v
        return round(v)

    def to_update_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}
class ArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:           int
    name:         str
    description:  str
    price:        float
    brand:        str | None
    image_url:    str | None
    embedding_id: str | None
    category:     CategoryResponse
    created_at:   datetime



class ArticleListResponse(BaseModel):
    total:    int
    page:     int
    size:     int
    articles: list[ArticleResponse]            

class ArticleStats(BaseModel):
    total_articles: int
    total_categories: int
    avg_price: float
    min_price: float
    max_price: float
    by_category: dict[str, int]

    

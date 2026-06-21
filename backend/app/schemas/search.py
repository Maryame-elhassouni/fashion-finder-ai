from pydantic import BaseModel, Field
from enum import Enum
from backend.app.schemas.article import ArticleResponse

class SortBy(str, Enum):
    relevance  = "relevance"
    price_asc  = "price_asc"
    price_desc = "price_desc"
    newest     = "newest"

class SearchRequest(BaseModel):
    description:     str = Field(..., min_length=2, max_length=500)
    category_filter: str | None = None
    price_min:       float | None = Field(None, ge=0)
    price_max:       float | None = Field(None, ge=0)
    sort_by:         SortBy = SortBy.relevance
    page:            int = Field(1, ge=1)
    size:            int = Field(8, ge=1, le=50)
class ArticleWithScore(BaseModel):
    article:     ArticleResponse
    score:       float
    score_label: str

class SearchResponse(BaseModel):
    description:     str
    total:           int
    page:            int
    size:            int
    total_pages:     int
    results:         list[ArticleWithScore]
    search_type:     str = "keywords"
    duration_ms:     int
    filters_applied: dict    
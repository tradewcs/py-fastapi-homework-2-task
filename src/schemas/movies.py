from pydantic import BaseModel, Field, field_validator
from datetime import date
from dateutil.relativedelta import relativedelta


class MovieResponseSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str

    class Config:
        from_attributes = True


class MovieListResponseSchema(BaseModel):
    movies: list[MovieResponseSchema]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int


class MovieCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    date: date
    score: float = Field(..., ge=0, le=100)
    overview: str
    status: str
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]

    @field_validator("date")
    @classmethod
    def date_not_too_far(cls, v: date) -> date:
        today = date.today()
        max_date = today + relativedelta(years=1)
        if v > max_date:
            raise ValueError("Movie date cannot be more than 1 year in the future")
        return v


class MovieUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    date: date | None
    score: float | None = Field(None, ge=0, le=100)
    overview: str | None
    status: str | None
    budget: float | None = Field(None, ge=0)
    revenue: float | None = Field(None, ge=0)
    country: str | None
    genres: list[str] | None
    actors: list[str] | None
    languages: list[str] | None

    @field_validator("date")
    @classmethod
    def date_not_too_far(cls, v: date | None) -> date | None:
        if v is None:
            return v
        today = date.today()
        max_date = today + relativedelta(years=1)
        if v > max_date:
            raise ValueError("Movie date cannot be more than 1 year in the future")
        return v


class MovieDetailSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: str
    genres: list[str]
    actors: list[str]
    languages: list[str]

    class Config:
        from_attributes = True


class MovieListItemSchema(BaseModel):
    id: int
    name: str
    date: date
    score: float

    class Config:
        from_attributes = True

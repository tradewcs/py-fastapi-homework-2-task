from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
)
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from crud.movies import (
    get_movie_by_id,
    get_movies_page,
)
from crud.exceptions import (
    MovieNotFoundException,
)

from database import get_db, MovieModel
from database.models import (
    CountryModel,
    GenreModel,
    ActorModel,
    LanguageModel,
)
from schemas.movies import (
    MovieResponseSchema,
    MovieListResponseSchema,
    MovieDetailSchema,
)


router = APIRouter()


@router.get("/", response_model=MovieListResponseSchema)
async def list_movies(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(0, ge=0),
    per_page: int = Query(10, ge=1, le=100)
):
    offset = page * per_page
    movies, total = await get_movies_page(db, offset, per_page)
    if offset >= total and total > 0:
        raise HTTPException(status_code=404, detail="Movie page not found")

    prev_page = None
    if page > 0:
        prev_page = str(
            request.url.include_query_params(
                page=page - 1,
                per_page=per_page
            )
        )

    next_page = None
    if offset + per_page < total:
        next_page = str(
            request.url.include_query_params(
                page=page + 1,
                per_page=per_page
            )
        )

    total_pages = (total + per_page - 1) // per_page

    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total
    )


@router.get("/{movie_id}", response_model=MovieDetailSchema)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db)
) -> MovieDetailSchema:
    try:
        movie = await get_movie_by_id(movie_id, db)
        return movie
    except MovieNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

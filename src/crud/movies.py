from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, func

from database.models import (
    MovieModel,
    GenreModel,
    ActorModel,
    LanguageModel,
    CountryModel,
)
from schemas.movies import (
    MovieCreateSchema,
)
from .exceptions import MovieNotFoundException


async def _get_or_create(db: AsyncSession, model, **kwargs):
    stmt = select(model)
    for key, value in kwargs.items():
        stmt = stmt.where(getattr(model, key) == value)

    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()

    if instance:
        return instance

    instance = model(**kwargs)
    db.add(instance)
    await db.flush()
    return instance


async def get_movie_by_id(movie_id: int, db: AsyncSession) -> MovieModel:
    result = await db.execute(
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        )
        .where(MovieModel.id == movie_id)
    )
    movie = result.scalars().first()
    if not movie:
        raise MovieNotFoundException(
            f"Movie with ID {movie_id} does not exist."
        )

    return movie


async def get_all_movies(db: AsyncSession) -> list[MovieModel]:
    result = await db.execute(
        select(MovieModel)
    )
    movies = result.scalars().all()
    return movies


async def get_movies_page(
    db: AsyncSession,
    offset: int,
    limit: int
) -> tuple[list[MovieModel], int]:
    total = await db.scalar(
        select(func.count()).select_from(MovieModel)
    )

    result = await db.execute(
        select(MovieModel)
        .options(
            joinedload(MovieModel.country),
            selectinload(MovieModel.genres),
            selectinload(MovieModel.actors),
            selectinload(MovieModel.languages),
        )
        .order_by(MovieModel.id)
        .offset(offset)
        .limit(limit)
    )

    movies = result.scalars().all()
    return movies, total


async def create_movie(
    movie_data: MovieCreateSchema,
    db: AsyncSession
) -> MovieModel:
    country = await _get_or_create(
        db,
        CountryModel,
        code=movie_data.country
    )

    genres = []
    for genre_name in movie_data.genres:
        genre = await _get_or_create(
            db,
            GenreModel,
            name=genre_name
        )
        genres.append(genre)

    actors = []
    for actor_name in movie_data.actors:
        actor = await _get_or_create(
            db,
            ActorModel,
            name=actor_name
        )
        actors.append(actor)

    languages = []
    for language_name in movie_data.languages:
        language = await _get_or_create(
            db,
            LanguageModel,
            name=language_name
        )
        languages.append(language)

    movie = MovieModel(
        name=movie_data.name,
        date=movie_data.date,
        score=movie_data.score,
        overview=movie_data.overview,
        status=movie_data.status,
        budget=movie_data.budget,
        revenue=movie_data.revenue,
        country=country,
        genre=genres,
        actors=actors,
        languages=languages
    )

    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


async def delete_movie(movie_id: int, db: AsyncSession) -> None:
    movie = await get_movie_by_id(movie_id, db)
    if not movie:
        raise MovieNotFoundException(
            f"Movie with ID {movie_id} does not exist."
        )

    await db.delete(movie)
    await db.commit()

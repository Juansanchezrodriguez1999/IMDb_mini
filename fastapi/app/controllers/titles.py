from fastapi import APIRouter, HTTPException
from app.db import get_connection
from app.models import Title, CastMember
from app.utils.queries import (
    QUERY_SEARCH_TITLE, QUERY_TITLE_DETAILS, QUERY_TITLE_CAST
)

router = APIRouter()

@router.get("/search")
async def search_titles(title: str):
    conn = await get_connection()
    rows = await conn.fetch(QUERY_SEARCH_TITLE, title)
    await conn.close()
    return rows


@router.get("/{tconst}", response_model=Title)
async def get_title(tconst: str):
    conn = await get_connection()

    row = await conn.fetchrow(QUERY_TITLE_DETAILS, tconst)
    if not row:
        await conn.close()
        raise HTTPException(404, "Title not found")

    cast_rows = await conn.fetch(QUERY_TITLE_CAST, tconst)

    cast = [
        CastMember(
            person_name=r["primary_name"],
            category=r["category"],
            job=r["job"],
            characters=r["characters"]
        )
        for r in cast_rows
    ]

    await conn.close()

    return Title(
        tconst=row["tconst"],
        primary_title=row["primary_title"],
        original_title=row["original_title"],
        title_type=row["title_type"],
        start_year=row["start_year"],
        end_year=row["end_year"],
        runtime_minutes=row["runtime_minutes"],
        genres=row["genres"],
        average_rating=row["average_rating"],
        num_votes=row["num_votes"],
        cast=cast
    )

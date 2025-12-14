from fastapi import APIRouter, HTTPException
from app.db import get_connection
from app.models import Person
from app.utils.queries import (
    QUERY_SEARCH_PERSON, QUERY_PERSON_DETAILS, QUERY_KNOWN_FOR
)

router = APIRouter()


@router.get("/search")
async def search_people(name: str):
    conn = await get_connection()

    rows = await conn.fetch(QUERY_SEARCH_PERSON, name)
    people = []

    for row in rows:
        known_for_titles = []

        if row["known_for_titles"]:
            ids = row["known_for_titles"].split(",")
            known_for_rows = await conn.fetch(QUERY_KNOWN_FOR, ids)
            known_for_titles = [r["primary_title"] for r in known_for_rows]

        has_profession = row["primary_profession"] not in (None, "")
        has_known_for = len(known_for_titles) > 0
        has_dates = row["birth_year"] is not None or row["death_year"] is not None

        if not (has_profession or has_known_for or has_dates):
            continue 

        people.append({
            "nconst": row["nconst"],
            "primary_name": row["primary_name"],
            "birth_year": row["birth_year"],
            "death_year": row["death_year"],
            "primary_profession": row["primary_profession"],
            "known_for_titles": known_for_titles
        })

    await conn.close()
    return people


@router.get("/{nconst}", response_model=Person)
async def get_person(nconst: str):
    conn = await get_connection()
    
    row = await conn.fetchrow(QUERY_PERSON_DETAILS, nconst)
    if not row:
        await conn.close()
        raise HTTPException(404, "Person not found")

    known_for = []
    if row["known_for_titles"]:
        ids = row["known_for_titles"].split(",")
        known_for_rows = await conn.fetch(QUERY_KNOWN_FOR, ids)

        known_for = [
            {
                "tconst": r["tconst"],
                "primary_title": r["primary_title"]
            }
            for r in known_for_rows
        ]

    await conn.close()

    return Person(
        nconst=row["nconst"],
        primary_name=row["primary_name"],
        birth_year=row["birth_year"],
        death_year=row["death_year"],
        primary_profession=row["primary_profession"],
        known_for=known_for
    )

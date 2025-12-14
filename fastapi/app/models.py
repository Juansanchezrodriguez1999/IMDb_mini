from pydantic import BaseModel
from typing import Optional, List

class KnownForTitle(BaseModel):
    tconst: str
    primary_title: str

class Person(BaseModel):
    nconst: str
    primary_name: str
    birth_year: Optional[int]
    death_year: Optional[int]
    primary_profession: Optional[str]
    known_for: List[KnownForTitle]

class CastMember(BaseModel):
    person_name: str
    category: str
    job: Optional[str]
    characters: Optional[str]

class Title(BaseModel):
    tconst: str
    primary_title: str
    original_title: Optional[str]
    title_type: str
    start_year: Optional[int]
    end_year: Optional[int]
    runtime_minutes: Optional[int]
    genres: Optional[str]
    average_rating: Optional[float]
    num_votes: Optional[int]
    cast: List[CastMember]

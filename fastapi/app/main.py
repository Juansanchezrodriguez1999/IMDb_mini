from fastapi import FastAPI
from app.controllers import people, titles

app = FastAPI(title="IMDb API", version="1.0")

app.include_router(people.router, prefix="/people", tags=["people"])
app.include_router(titles.router, prefix="/titles", tags=["titles"])

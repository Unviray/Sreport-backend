from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import Preacher, Tag
from .config import working_month
from . import const


app = FastAPI()

origins = [
    # "http://localhost:3000",
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/list-preacher")
def list_preacher():
    result = [_.id for _ in Preacher.select(Preacher.id)]
    result.sort()

    return result


@app.get("/api/preacher/{id}")
def get_preacher(id:int):
    return Preacher.get(Preacher.id == id).__data__


@app.get("/api/working-month")
def get_working_month():
    return str(working_month)


@app.get("/api/list-tag")
def list_tag():
    result = [_.id for _ in Tag.select(Tag.id)]
    result.sort()

    return result


@app.get("/api/tag/{id}")
def get_tag(id:int):
    return Tag.get(Tag.id == id).__data__

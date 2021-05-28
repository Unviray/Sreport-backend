from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import Preacher, Tag, PreacherTag
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


@app.get("/api/preacher-tag/{id}")
def get_preacher_tags(id:int):
    tags = PreacherTag \
        .select() \
        .join(Preacher, on=(PreacherTag.preacher == Preacher.id)) \
        .join(Tag, on=(PreacherTag.tag == Tag.id)) \
        .where(PreacherTag.preacher.id == id) \
        .where((PreacherTag.start <= working_month.data) | (PreacherTag.start == None)) \
        .where((PreacherTag.end >= working_month.data) | (PreacherTag.end == None))

    result_tag = [_.tag.id for _ in tags]
    result_time = []

    for tag in tags:
        print(tag.start)
        print(tag.end)
        result_time.append(tag.end is not None)

    return zip(result_tag, result_time)


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

from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import Preacher, Tag, PreacherTag, Report
from .config import MonthBase, working_month


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
    tags = PreacherTag.select() \
        .join(Preacher, on=(PreacherTag.preacher == Preacher.id)) \
        .join(Tag, on=(PreacherTag.tag == Tag.id)) \
        .where(PreacherTag.preacher.id == id) \
        .where((PreacherTag.start <= working_month.data) | (PreacherTag.start == None)) \
        .where((PreacherTag.end >= working_month.data) | (PreacherTag.end == None))

    result_tag = [_.tag.id for _ in tags]
    result_time = []

    for tag in tags:
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


@app.get("/api/service-months")
def list_service_months(month:int=Query(0, ge=0, le=12), year:int=Query(0, ge=0, le=9999)):
    if (month == 0) or (year == 0):
        wm = working_month
    else:
        wm = MonthBase({"year": year, "month": month})

    if wm.month in (9, 10, 11, 12):
        result = [
            MonthBase({"year": wm.year, "month": 9}) + n for n in range(12)
        ]

    else:
        result = [
            MonthBase({"year": wm.year - 1, "month": 9}) + n for n in range(12)
        ]

    return list(map(lambda x: x.to_dict(), result))


@app.get("/api/report/{preacher_id}")
def get_report(preacher_id:int, month:int=Query(0, ge=0, le=12), year:int=Query(0, ge=0, le=9999)):
    if (month == 0) or (year == 0):
        wm = working_month
    else:
        wm = MonthBase({"year": year, "month": month})

    report = Report.select() \
        .join(Preacher, on=(Report.preacher == Preacher.id)) \
        .where(Report.preacher == Preacher.get_by_id(preacher_id)) \
        .where(Report.month == date(wm.year, wm.month, 1))

    if len(report) == 0:
        return {
            "month": str(MonthBase({"year": wm.year, "month":wm.month})),

            "publication": 0,
            "video": 0,
            "hour": 0,
            "visit": 0,
            "study": 0,
        }

    report = report[0]

    return {
        "month": str(MonthBase({"year": wm.year, "month":wm.month})),

        "publication": report.publication,
        "video": report.video,
        "hour": report.hour,
        "visit": report.visit,
        "study": report.study,
    }

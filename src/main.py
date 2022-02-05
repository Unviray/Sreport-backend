from datetime import date
from functools import lru_cache

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from slugify import slugify

from .utils import Cache, update_cache
from .config import MonthBase, working_month
from .models import (
    Tag,
    Preacher,
    PreacherTag,
    Report,
    ReportTag,
    PostReport,
    PostMonth
)


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


def in_month(month:int=Query(0, ge=0, le=12), year:int=Query(0, ge=0, le=9999)):
    if (month == 0) or (year == 0):
        return working_month
    else:
        return MonthBase({"year": year, "month": month})


@app.get("/api/list-preacher")
@Cache(deps=[Preacher])
def list_preacher(search:str=""):
    preachers = Preacher.select(Preacher.id)
    if search:
        preachers = preachers.where(
            Preacher.firstname.contains(search) |
            Preacher.lastname.contains(search) |
            Preacher.display_name.contains(search)
        )

    result = [_.id for _ in preachers]
    result.sort()

    return result


@app.get("/api/preacher/{id}")
@Cache(deps=[Preacher])
def get_preacher(id:int):
    return Preacher.get(Preacher.id == id).__data__


@app.get("/api/preacher-tag/{id}")
@Cache(deps=[Preacher, Tag, PreacherTag])
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

    return dict(zip(result_tag, result_time))


@app.get("/api/report/{preacher_id}")
@Cache(deps=[Report, Preacher, MonthBase])
def get_report(preacher_id:int, wm:MonthBase=Depends(in_month)):
    """
    :param preacher_id: preacher id. 0 for all
    """

    reports = Report.select() \
        .join(Preacher, on=(Report.preacher == Preacher.id)) \
        .where(Report.month == date(wm.year, wm.month, 1)) \

    if preacher_id != 0:
        reports = reports.where(Report.preacher == Preacher.get_by_id(preacher_id))

    if len(reports) == 0:
        return {
            "id": 0,
            "month": wm.to_dict(),

            "publication": 0,
            "video": 0,
            "hour": 0,
            "visit": 0,
            "study": 0,
        }

    if preacher_id != 0:
        report = reports[0]

        return {
            "id": report.id,
            "month": wm.to_dict(),

            "publication": report.publication,
            "video": report.video,
            "hour": report.hour,
            "visit": report.visit,
            "study": report.study,
        }
    else:
        data = {
            "id": [],
            "month": wm.to_dict(),

            "publication": 0,
            "video": 0,
            "hour": 0,
            "visit": 0,
            "study": 0,
        }

        for report in reports:
            data["id"].append(report.id)

            data["publication"] += report.publication
            data["video"] += report.video
            data["hour"] += report.hour
            data["visit"] += report.visit
            data["study"] += report.study

        return data


@app.post("/api/report/{preacher_id}")
@Cache(deps=get_report.cache.deps, updates=[Report, ReportTag, Tag])
def set_report(preacher_id:int, post_report:PostReport, wm:MonthBase=Depends(in_month)):
    report_id = get_report(preacher_id, wm)["id"]

    if report_id != 0:
        report = Report.get(Report.id == report_id)

        report.publication = post_report.publication
        report.video = post_report.video
        report.hour = post_report.hour
        report.visit = post_report.visit
        report.study = post_report.study
        report.note = post_report.note

        report.save()
    else:
        report = Report.create(
            preacher=Preacher.get(Preacher.id == preacher_id),
            month=wm.data,

            publication=post_report.publication,
            video=post_report.video,
            hour=post_report.hour,
            visit=post_report.visit,
            study=post_report.study,

            note=post_report.note,
        )

    return {
        "id": report.id,
        "month": wm.to_dict(),

        "publication": report.publication,
        "video": report.video,
        "hour": report.hour,
        "visit": report.visit,
        "study": report.study,
        "note": report.note
    }


@app.get("/api/report-tag/{preacher_id}")
@Cache(deps=([Report, Tag, ReportTag, MonthBase] + get_report.cache.deps))
def get_report_tags(preacher_id:int, wm:MonthBase=Depends(in_month)):
    """
    :param preacher_id: preacher id. 0 for all
    """

    report_id = get_report(preacher_id, wm)["id"]

    tags = ReportTag.select() \
        .join(Report, on=(ReportTag.report == Report.id)) \
        .join(Tag, on=(ReportTag.tag == Tag.id))

    if isinstance(report_id, int):
        tags = tags.where(ReportTag.report.id == report_id)

    else:  # maybe a list
        def where_or(rep_id, last=None):
            if last is None:
                return (ReportTag.report.id == rep_id)
            else:
                return (last | (ReportTag.report.id == rep_id))

        query = None
        for rep_id in report_id:
            query = where_or(rep_id, query)

        tags = tags.where(query)

    return [_.tag.id for _ in tags]


@app.get("/api/working-month")
@Cache(deps=[MonthBase])
def get_working_month():
    return working_month.to_dict()


@app.post("/api/working-month")
@Cache(deps=[MonthBase], updates=[MonthBase])
def set_working_month(post_month:PostMonth):
    working_month.__init__(post_month)


@app.get("/api/list-tag")
@Cache(deps=[Tag])
def list_tag():
    result = [_.id for _ in Tag.select(Tag.id)]
    result.sort()

    return result


@app.get("/api/tag/{ids}")
@Cache(deps=[Tag])
def get_tag(ids:str):
    result = []
    for _id in ids.split(","):
        result.append(Tag.get(Tag.id == _id).__data__)

    return result


@app.get("/api/year-service")
@Cache(deps=[MonthBase])
def year_service(wm:MonthBase=Depends(in_month)):
    if wm.month in (9, 10, 11, 12):
        return wm.year + 1
    else:
        return wm.year


@app.get("/api/service-months")
@Cache(deps=[MonthBase])
def list_service_months(wm:MonthBase=Depends(in_month)):
    if wm.month in (9, 10, 11, 12):
        result = [
            MonthBase({"year": wm.year, "month": 9}) + n for n in range(12)
        ]

    else:
        result = [
            MonthBase({"year": wm.year - 1, "month": 9}) + n for n in range(12)
        ]

    return list(map(lambda x: x.to_dict(), result))


@app.get("/api/returned/{preacher_id}")
@Cache(deps=[MonthBase] + get_report.cache.deps)
def returned(preacher_id:int, wm:MonthBase=Depends(in_month)):
    return get_report(preacher_id, wm)["hour"] != 0


@app.get("/api/service-hour/{preacher_id}")
@Cache(deps=[MonthBase] + list_service_months.cache.deps + get_report.cache.deps)
def service_hour(preacher_id:int, wm:MonthBase=Depends(in_month)):
    """
    :param preacher_id: preacher id. 0 for all
    """

    service_months = list_service_months(wm)

    def get_hour_label(month):
        mb = MonthBase(month)
        mb.FORMAT = "{short_month} {short_year}"

        return str(mb)

    def get_hour_value(month):
        return get_report(preacher_id, MonthBase(month))["hour"]

    return {get_hour_label(month): get_hour_value(month) for month in service_months}


@app.get("/api/total-month")
@Cache(deps=[Report, ReportTag, Tag, MonthBase])
def total_month(with_tag:str="", without_tag:str="", wm:MonthBase=Depends(in_month)):
    # report = Report.select() \
    #     .join(ReportTag, on=(ReportTag.report == Report.id)) \
    #     .join(Tag, on=(ReportTag.tag == Tag.id)) \
    #     .where(slugify(ReportTag.tag.name) == selected)
    reports = Report.select() \
        .where(Report.month == date(wm.year, wm.month, 1))

    def filterer(report):
        if with_tag:
            for report_tag in report.tags:
                if report_tag.tag.id in [int(tag_id) for tag_id in with_tag.split(",")]:
                    return True
            return False
        if without_tag:
            for report_tag in report.tags:
                if report_tag.tag.id in [int(tag_id) for tag_id in without_tag.split(",")]:
                    return False
            return True

        return True

    data = {
        "number": 0,

        "publication": 0,
        "video": 0,
        "hour": 0,
        "visit": 0,
        "study": 0,
    }

    reports = list(filter(filterer, reports))

    for report in reports:
        data["number"] += 1

        data["publication"] += report.publication
        data["video"] += report.video
        data["hour"] += report.hour
        data["visit"] += report.visit
        data["study"] += report.study

    return data

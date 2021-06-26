from datetime import date

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from slugify import slugify

from .models import Tag, Preacher, PreacherTag, Report, ReportTag
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


def in_month(month:int=Query(0, ge=0, le=12), year:int=Query(0, ge=0, le=9999)):
    if (month == 0) or (year == 0):
        return working_month
    else:
        return MonthBase({"year": year, "month": month})


@app.get("/api/list-preacher")
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


@app.get("/api/report-tag/{preacher_id}")
def get_report_tags(preacher_id:int, wm:MonthBase=Depends(in_month)):
    report_id = get_report(preacher_id, wm)["id"]

    tags = ReportTag.select() \
        .join(Report, on=(ReportTag.report == Report.id)) \
        .join(Tag, on=(ReportTag.tag == Tag.id)) \
        .where(ReportTag.report.id == report_id)

    return [_.tag.id for _ in tags]


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


@app.get("/api/year-service")
def year_service(wm:MonthBase=Depends(in_month)):
    if wm.month in (9, 10, 11, 12):
        return wm.year + 1
    else:
        return wm.year


@app.get("/api/service-months")
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


@app.get("/api/report/{preacher_id}")
def get_report(preacher_id:int, wm:MonthBase=Depends(in_month)):
    report = Report.select() \
        .join(Preacher, on=(Report.preacher == Preacher.id)) \
        .where(Report.preacher == Preacher.get_by_id(preacher_id)) \
        .where(Report.month == date(wm.year, wm.month, 1))

    if len(report) == 0:
        return {
            "id": 0,
            "month": str(MonthBase({"year": wm.year, "month":wm.month})),

            "publication": 0,
            "video": 0,
            "hour": 0,
            "visit": 0,
            "study": 0,
        }

    report = report[0]

    return {
        "id": report.id,
        "month": str(MonthBase({"year": wm.year, "month":wm.month})),

        "publication": report.publication,
        "video": report.video,
        "hour": report.hour,
        "visit": report.visit,
        "study": report.study,
    }


@app.get("/api/returned/{preacher_id}")
def returned(preacher_id:int, wm:MonthBase=Depends(in_month)):
    return get_report(preacher_id, wm)["hour"] != 0


@app.get("/api/service-hour/{preacher_id}")
def service_hour(preacher_id:int, wm:MonthBase=Depends(in_month)):
    service_months = list_service_months(wm)

    def get_hour_label(month):
        mb = MonthBase(month)
        mb.FORMAT = "{short_month} {short_year}"

        return str(mb)

    def get_hour_value(month):
        return get_report(preacher_id, MonthBase(month))["hour"]

    return {get_hour_label(month): get_hour_value(month) for month in service_months}


@app.get("/api/total-month/{selected}")
def total_month(selected, wm:MonthBase=Depends(in_month)):
    # report = Report.select() \
    #     .join(ReportTag, on=(ReportTag.report == Report.id)) \
    #     .join(Tag, on=(ReportTag.tag == Tag.id)) \
    #     .where(slugify(ReportTag.tag.name) == selected)
    reports = Report.select() \
        .where(Report.month == date(wm.year, wm.month, 1))

    def filterer(report):
        if selected == "mpisavalalana-maharitra":
            for report_tag in report.tags:
                if slugify(report_tag.tag.name) == selected:
                    return True
            return False

        if selected == "mpisavalalana-mpanampy":
            for report_tag in report.tags:
                if slugify(report_tag.tag.name) == selected:
                    return True
            return False

        if selected == "mpitory":
            for report_tag in report.tags:
                if slugify(report_tag.tag.name) in ["mpisavalalana-maharitra", "mpisavalalana-mpanampy"]:
                    return False
            return True

        if selected == "total":
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

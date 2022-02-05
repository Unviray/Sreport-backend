import json
from pathlib import Path
from pprint import pprint
from random import randint
from datetime import date, datetime

from src.models import Group, Tag, Preacher, PreacherTag, Report, ReportTag

from peewee import IntegrityError


import_from = Path.home() / ".es21" / "db.json"


def _int(n):
    """
    Like int() but avoid errors.
    """

    try:
        return int(n)
    except ValueError:
        return 0
    except TypeError:
        return 0


month_name = {
    # short_month
    'jan': 'jan',
    'feb': 'feb',
    'mar': 'mar',
    'apr': 'apr',
    'may': 'may',
    'jun': 'jun',
    'jul': 'jul',
    'aug': 'aug',
    'sep': 'sep',
    'oct': 'oct',
    'nov': 'nov',
    'dec': 'dec',

    # long_month
    'january': 'january',
    'february': 'february',
    'march': 'march',
    'april': 'april',
    'may': 'may',
    'june': 'june',
    'july': 'july',
    'august': 'august',
    'september': 'september',
    'october': 'october',
    'november': 'november',
    'december': 'december', }

month_short2long = {
    'jan': 'january',
    'feb': 'february',
    'mar': 'march',
    'apr': 'april',
    'may': 'may',
    'jun': 'june',
    'jul': 'july',
    'aug': 'august',
    'sep': 'september',
    'oct': 'october',
    'nov': 'november',
    'dec': 'december', }


class MonthBase(object):
    """
    Dynamic class for working month
    """

    MONTH_NAME = (
        'jan',
        'feb',
        'mar',
        'apr',
        'may',
        'jun',
        'jul',
        'aug',
        'sep',
        'oct',
        'nov',
        'dec', )

    FORMAT = '{short_month}_{year}'

    def __init__(self, obj):
        """
        :param obj: A date or str object
        """

        if isinstance(obj, date):
            self.data = obj

        elif isinstance(obj, str):
            month, year = obj.split('_' if '_' in obj else '-')

            if month.isdigit():
                self.data = date(_int(year), _int(month), 1)  # day 1 is ignored
            else:
                self.data = date(
                    year=_int(year),
                    month=self.MONTH_NAME.index(month) + 1,
                    day=1, )  # day 1 is ignored

    @property
    def month(self):
        return self.data.month

    @property
    def year(self):
        return self.data.year

    def prettie(self, _format=None):
        """
        Return month string in requested :param _format:
        """

        _format = _format or '{month} {year}'

        # - 1 because index start with 0
        m = self.MONTH_NAME[self.data.month - 1]
        y = self.data.year

        return _format.format(
            short_month=month_name.get(m),
            month=month_short2long.get(m).title(),
            short_year=str(y)[2:],
            year=y
        )

    def __str__(self):
        # - 1 because index start with 0
        m = self.MONTH_NAME[self.data.month - 1]
        y = self.data.year

        return self.FORMAT.format(
            # short_month=month_name.get(m),
            short_month=m,
            month=month_short2long.get(m).title(),
            short_year=str(y)[2:],
            year=y
        )

    def __repr__(self):
        return f'<MonthBase month: {str(self)}>'

    def __sub__(self, n):
        """
        Use to jump {n} month behind
        """

        y = self.data.year
        m = self.data.month

        if n > 0:
            self.data = date(
                year=y - 1 if m == 1 else y,  # last year if today is jan
                month=m - 1 if m > 1 else 12,  # avoid month 0
                day=1, )  # day 1 is ignored

            self - (n - 1)  # recursive until {n} reach 0

        return self

    def __add__(self, n):
        """
        Use to jump {n} month forward
        """

        y = self.data.year
        m = self.data.month

        if n > 0:
            self.data = date(
                year=y + 1 if m == 12 else y,  # last year if today is jan
                month=m + 1 if m < 12 else 1,  # avoid month 0
                day=1, )  # day 1 is ignored

            self + (n - 1)  # recursive until {n} reach 0

        return self

    def new_me(self, obj=None):
        if obj is not None:
            return MonthBase(obj)
        else:
            return MonthBase(self.data)



def rand_color():
    result = hex(randint(0, 16777215)).split("x")[1]

    while(len(result) < 6):
        result = f"0{result}"

    return result


def convert_date(tinydate):
    if tinydate is None:
        return None

    tinydate = tinydate.split("{TinyDate}:")[-1]

    try:
        return datetime.strptime(tinydate, '%Y-%m-%d')
    except ValueError:
        return None


def create_group(preacher):
    try:
        Group.create(
            id=preacher["groupe"]
        )
    except IntegrityError:
        pass


def create_tag(preacher):
    try:
        Tag.create(
            name="Mpisavalalana Maharitra",
            color=rand_color()
        )
        Tag.create(
            name="Mpisavalalana Mpanampy",
            color=rand_color()
        )
    except IntegrityError:
        pass

    if preacher["tombotsoa"]:
        try:
            Tag.create(
                name=preacher["tombotsoa"],
                color=rand_color()
            )
        except IntegrityError:
            pass


def auxiler(p, preacher, auxiliar):
    for key in auxiliar:
        if len(auxiliar[key]["mpitory"]) == 0:
            continue

        ak = auxiliar[key]

        if preacher["id"] in ak["mpitory"]:
            start_month = MonthBase(ak["volana"])
            end_month = MonthBase(ak["volana"]) + 1
            PreacherTag.create(
                preacher = p,
                tag = Tag.get(Tag.name == "Mpisavalalana Mpanampy"),

                start = date(
                    year=start_month.year,
                    month=start_month.month,
                    day=1,
                ),
                end = date(
                    year=end_month.year,
                    month=end_month.month,
                    day=1,
                )
            )


def create_report(p, preacher):
    tatitra = preacher["tatitra"]

    for key_month in tatitra:
        month = MonthBase(key_month)
        current_report = tatitra[key_month]

        r = Report.create(
            preacher = p,
            month = date(
                year=month.year,
                month=month.month,
                day=1,
            ),

            publication = current_report["zavatra_napetraka"],
            video = current_report["video"],
            hour = current_report["ora"],
            visit = current_report["fitsidihana"],
            study = current_report["fampianarana"],

            note = current_report["fanamarihana"],
        )

        if current_report["mpisavalalana"] == "Reg":
            ReportTag.create(
                report = r,
                tag = Tag.get(Tag.name == "Mpisavalalana Maharitra"),
            )
        elif current_report["mpisavalalana"] == "Aux":
            ReportTag.create(
                report = r,
                tag = Tag.get(Tag.name == "Mpisavalalana Mpanampy"),
            )



def create_preacher(preacher, n, auxiliar):
    display_name = preacher.get("anarana_feno", "")

    if display_name == "":
        display_name = f'{preacher["anarana"]} {preacher["fanampinanarana"]}'

    try:
        p = Preacher.create(
            id = n,
            firstname = preacher["fanampinanarana"],
            lastname = preacher["anarana"],
            display_name = display_name,

            phone1 = preacher["finday"][0],
            phone2 = preacher["finday"][1],
            phone3 = preacher["finday"][2],

            address = preacher["adiresy"],

            birth = convert_date(preacher["teraka"]),
            baptism = convert_date(preacher["batisa"]),

            group = Group.get(Group.id == preacher["groupe"]),

            gender = 0 if preacher["lahy_sa_vavy"] == "Lahy" else 1,
        )

        if preacher["tombotsoa"]:
            PreacherTag.create(
                preacher = p,
                tag = Tag.get(Tag.name == preacher["tombotsoa"])
            )

        if preacher["maharitra"]:
            PreacherTag.create(
                preacher = p,
                tag = Tag.get(Tag.name == "Mpisavalalana Maharitra")
            )

        auxiler(p, preacher, auxiliar)
        create_report(p, preacher)

    except IntegrityError as e:
        print(e)


def main():
    with open(import_from, "r") as fp:
        loaded = json.load(fp)

    pprint(loaded["_default"].keys())

    for n, key in enumerate(loaded["_default"]):
        print(f"{n+1}/{len(loaded['_default'])}", flush=True)
        preacher = loaded["_default"][key]

        create_group(preacher)
        create_tag(preacher)
        create_preacher(preacher, n+1, loaded["mpanampy"])


if __name__ == "__main__":
    main()

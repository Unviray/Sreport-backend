from datetime import date


from . import const


class MonthBase(object):
    """
    Dynamic class for working month
    """

    FORMAT = '{month} {year}'

    def __init__(self, obj=None, mutable=True):
        """
        :param obj: A date object
        """
        self.mutable = mutable

        if obj is not None:
            if isinstance(obj, date):
                self.data = obj
            elif isinstance(obj, dict):
                self.data = date(obj["year"], obj["month"], 1)
        else:
            self.data = date.today()

    @property
    def month(self):
        return self.data.month

    @property
    def year(self):
        return self.data.year

    def __str__(self):
        # - 1 because index start with 0
        m = const.month_list[self.data.month - 1]
        y = self.data.year

        return self.FORMAT.format(
            month=m.title(),
            short_year=str(y)[2:],
            year=y
        )

    def __repr__(self):
        return f'<MonthBase month: {str(self)}>'

    def to_dict(self):
        return {
            "month": self.month,
            "year": self.year,
        }

    def __sub__(self, n):
        """
        Use to jump {n} month behind
        """

        y = self.data.year
        m = self.data.month

        if self.mutable:

            if n > 0:
                self.data = date(
                    year=y - 1 if m == 1 else y,  # last year if today is jan
                    month=m - 1 if m > 1 else 12,  # avoid month 0
                    day=1, )  # day 1 is ignored

                self - (n - 1)  # recursive until {n} reach 0

            return self
        else:
            new_date = date(year=y, month=m, day=1)

            while n > 0:
                new_date = date(
                    year=new_date.year - 1 if new_date.month == 1 else new_date.year,  # last year if today is jan
                    month=new_date.month - 1 if new_date.month > 1 else 12,  # avoid month 0
                    day=1, )  # day 1 is ignored

                n -= 1

            return MonthBase(new_date, mutable=False)

    def __add__(self, n):
        """
        Use to jump {n} month forward
        """

        y = self.data.year
        m = self.data.month

        if self.mutable:

            if n > 0:
                self.data = date(
                    year=y + 1 if m == 12 else y,  # last year if today is jan
                    month=m + 1 if m < 12 else 1,  # avoid month 0
                    day=1, )  # day 1 is ignored

                self + (n - 1)  # recursive until {n} reach 0

            return self
        else:
            new_date = date(year=y, month=m, day=1)

            while n > 0:
                new_date = date(
                    year=new_date.year + 1 if new_date.month == 12 else new_date.year,  # last year if today is jan
                    month=new_date.month + 1 if new_date.month < 12 else 1,  # avoid month 0
                    day=1, )  # day 1 is ignored

                n -= 1

            return MonthBase(new_date, mutable=False)


working_month = MonthBase() - 1
static_working_month = MonthBase(working_month.data, mutable=False)

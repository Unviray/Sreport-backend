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
            self.data = obj
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

    def __sub__(self, n):
        """
        Use to jump {n} month behind
        """

        if self.mutable:
            y = self.data.year
            m = self.data.month

            if n > 0:
                self.data = date(
                    year=y - 1 if m == 1 else y,  # last year if today is jan
                    month=m - 1 if m > 1 else 12,  # avoid month 0
                    day=1, )  # day 1 is ignored

                self - (n - 1)  # recursive until {n} reach 0

            return self
        else:
            raise ArithmeticError("I'm immutable")

    def __add__(self, n):
        """
        Use to jump {n} month forward
        """

        if self.mutable:
            y = self.data.year
            m = self.data.month

            if n > 0:
                self.data = date(
                    year=y + 1 if m == 12 else y,  # last year if today is jan
                    month=m + 1 if m < 12 else 1,  # avoid month 0
                    day=1, )  # day 1 is ignored

                self + (n - 1)  # recursive until {n} reach 0

            return self
        else:
            raise ArithmeticError("I'm immutable")


working_month = MonthBase() - 1
static_working_month = MonthBase(working_month.data, False)

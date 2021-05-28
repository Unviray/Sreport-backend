from peewee import (BooleanField, CharField, DateField, ForeignKeyField,
                    IntegerField, Model, SqliteDatabase)


db = SqliteDatabase('database.sqlite', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    # id = IntegerField(unique=True)

    def __str__(self):
        return str(self.id)


class Tag(BaseModel):
    name = CharField(unique=True)
    color = CharField(max_length=6)

    def __str__(self):
        return self.name


class Preacher(BaseModel):
    firstname = CharField()
    lastname = CharField()
    display_name = CharField(unique=True)

    phone1 = CharField(max_length=10)
    phone2 = CharField(max_length=10)
    phone3 = CharField(max_length=10)

    address = CharField()

    birth = DateField(null=True)
    baptism = DateField(null=True)

    group = ForeignKeyField(Group, backref="preachers")

    gender = BooleanField()

    def __str__(self):
        return f"{self.id} {self.display_name}"


class PreacherTag(BaseModel):
    preacher = ForeignKeyField(Preacher, backref="tags")
    tag = ForeignKeyField(Tag, backref="preachers")

    start = DateField('%m %Y', null=True)
    end = DateField('%m %Y', null=True)

    def __str__(self):
        return f"{str(self.tag)} of {str(self.preacher)}"


class Report(BaseModel):
    preacher = ForeignKeyField(Preacher, backref="reports")
    month = DateField('%m %Y')

    publication = IntegerField()
    video = IntegerField()
    hour = IntegerField()
    visit = IntegerField()
    study = IntegerField()

    note = CharField()

    # pionner = IntegerField(choices=[0, 1, 2])
    # Handled by ReportTag

    def __str__(self):
        month = str(self.month)
        preacher_name = self.preacher.display_name

        return f"{month} {preacher_name}"


class ReportTag(BaseModel):
    report = ForeignKeyField(Report, backref="tags")
    tag = ForeignKeyField(Tag, backref="reports")


db.create_tables([
    Group,
    Tag,
    Preacher,
    PreacherTag,
    Report,
    ReportTag
])

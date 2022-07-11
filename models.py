from peewee import (SqliteDatabase, Model, IntegerField, DoubleField, DateTimeField, datetime as peewee_datetime,
                    CharField, TextField)

from config import DB_PATH, LOGS_DB_PATH

db = SqliteDatabase(DB_PATH)
db_logs = SqliteDatabase(LOGS_DB_PATH)


class _Model(Model):
    class Meta:
        database = db


class _LogModel(Model):
    class Meta:
        database = db_logs


class XRate(_Model):
    class Meta:
        db_table = "xrates"
        indexes = (
            (("from_currency", "to_currency"), True),
        )

    from_currency = IntegerField()
    to_currency = IntegerField()
    rate = DoubleField()
    updated = DateTimeField(default=peewee_datetime.datetime.now)

    def __str__(self):
        return "XRate(%s=>%s): %s" % (self.from_currency, self.to_currency, self.rate)


class ApiLog(_LogModel):
    class Meta:
        db_table = "api_logs"

    request_url = CharField()
    request_data = TextField(null=True)
    request_method = CharField(max_length=100)
    request_headers = TextField(null=True)
    response_text = TextField(null=True)
    created = DateTimeField(index=True, default=peewee_datetime.datetime.now)
    finished = DateTimeField()
    error = TextField(null=True)


class ErrorLog(_LogModel):
    class Meta:
        db_table = "error_logs"

    request_data = TextField(null=True)
    request_url = TextField()
    request_method = CharField(max_length=100)
    error = TextField()
    traceback = TextField(null=True)
    created = DateTimeField(default=peewee_datetime.datetime.now, index=True)


def init_db():
    XRate.drop_table()
    XRate.create_table()
    XRate.create(from_currency=840, to_currency=980, rate=1)
    XRate.create(from_currency=840, to_currency=643, rate=1)
    XRate.create(from_currency=978, to_currency=980, rate=1)
    XRate.create(from_currency=1000, to_currency=840, rate=1)
    XRate.create(from_currency=1000, to_currency=980, rate=1)
    XRate.create(from_currency=1000, to_currency=643, rate=1)

    for model in ApiLog, ErrorLog:
        model.drop_table()
        model.create_table()

    print("db created!")
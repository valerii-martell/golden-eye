import config
from config import DB_CONN
from peewee import SqliteDatabase, Model, IntegerField, DoubleField, DateTimeField, datetime as peewee_datetime, \
    CharField, TextField, PostgresqlDatabase


if DB_CONN['host'] and DB_CONN['user'] and DB_CONN['password'] \
    and DB_CONN['port'] and DB_CONN['database'] and DB_CONN['sslmode']:
    db = PostgresqlDatabase(host=DB_CONN['host'],
                            user=DB_CONN['user'],
                            password=DB_CONN['password'],
                            port=DB_CONN['port'],
                            database=DB_CONN['database'],
                            sslmode=DB_CONN['sslmode'])
else:
    db = SqliteDatabase(config.DB_PATH)

if DB_CONN['host'] and DB_CONN['user'] and DB_CONN['password'] \
    and DB_CONN['port'] and DB_CONN['database_logs'] and DB_CONN['sslmode']:
    db_logs = PostgresqlDatabase(host=DB_CONN['host'],
                            user=DB_CONN['user'],
                            password=DB_CONN['password'],
                            port=DB_CONN['port'],
                            database=DB_CONN['database_logs'],
                            sslmode=DB_CONN['sslmode'])
else:
    db_logs = SqliteDatabase(config.LOGS_DB_PATH)

# if os.environ.get("DATABASE_URL"):
#     url = urllib.parse.urlparse(os.environ.get("DATABASE_URL"))
#     db = PostgresqlDatabase(host=url.hostname,
#                             user=url.username,
#                             password=url.password,
#                             port=url.port,
#                             database=url.path[1:])
#     # db = MySQLDatabase()
# else:
#     db = SqliteDatabase(config.DB_PATH)


class _Model(Model):
    class Meta:
        database = db


class _LogModel(Model):
    class Meta:
        database = db_logs

    def json(self):
        data = self.__data__
        return data


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
    module = CharField(max_length=100)

    def __str__(self):
        return "XRate(%s=>%s): %s" % (self.from_currency, self.to_currency, self.rate)


class LatestUpdate(_LogModel):
    class Meta:
        db_table = "latest_update"

    datetime = DateTimeField(default=peewee_datetime.datetime.now, index=True)

    def __str__(self):
        return str(self.datetime)


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


def start_db():
    if not XRate.table_exists():
        XRate.create_table()
        XRate.create(from_currency=840, to_currency=980, rate=1, module="privat_api")
        XRate.create(from_currency=840, to_currency=643, rate=1, module="cbr_api")
        XRate.create(from_currency=1000, to_currency=840, rate=1, module="privat_api")
        XRate.create(from_currency=1000, to_currency=980, rate=1, module="coinmarketcap_api")
        XRate.create(from_currency=1000, to_currency=643, rate=1, module="blockchaininfo_api")

        print("Main table created!")

    if not ApiLog.table_exists():
        ApiLog.drop_table()
        ApiLog.create_table()
        print("API logs table created!")

    if not ErrorLog.table_exists():
        ErrorLog.drop_table()
        ErrorLog.create_table()
        print("Errors table created!")

    if not LatestUpdate.table_exists():
        LatestUpdate.drop_table()
        LatestUpdate.create_table()
        LatestUpdate.create(datetime=peewee_datetime.datetime.now())
        print("Latest update table created!")


def init_db():
    XRate.drop_table()
    LatestUpdate.drop_table()
    ApiLog.drop_table()
    ErrorLog.drop_table()
    start_db()
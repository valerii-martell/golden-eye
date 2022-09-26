"""This module contains all app's database models."""

import config
from config import DB_CONN
from peewee import SqliteDatabase, Model, IntegerField, DoubleField, DateTimeField, datetime as peewee_datetime, \
    CharField, TextField, PostgresqlDatabase

# Initialize an app's DB
if DB_CONN['host'] and DB_CONN['user'] and DB_CONN['password'] and \
        DB_CONN['port'] and DB_CONN['database'] and DB_CONN['sslmode']:
    db = PostgresqlDatabase(host=DB_CONN['host'],
                            user=DB_CONN['user'],
                            password=DB_CONN['password'],
                            port=DB_CONN['port'],
                            database=DB_CONN['database'],
                            sslmode=DB_CONN['sslmode'])
else:
    # If PostgreSQL connection cannot be established init SQLlite DB
    db = SqliteDatabase(config.DB_PATH)

# Initialize separated DB for API logs
if DB_CONN['host'] and DB_CONN['user'] and DB_CONN['password'] and \
        DB_CONN['port'] and DB_CONN['database_logs'] and DB_CONN['sslmode']:
    db_logs = PostgresqlDatabase(host=DB_CONN['host'],
                                 user=DB_CONN['user'],
                                 password=DB_CONN['password'],
                                 port=DB_CONN['port'],
                                 database=DB_CONN['database_logs'],
                                 sslmode=DB_CONN['sslmode'])
else:
    # If PostgreSQL connection cannot be established init SQLlite DB
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
    """The internal base class for DB model description.

    The main purpose is specifying particular DB where entities, described in
    derived classes, will be stored using nested class Meta declaration

    """

    class Meta:
        """A nested class for DB Model base class for DB specifying.

        Attributes:
            database (Database): a link to particular DB.

        """
        database = db


class _LogModel(Model):
    """The internal base class for DB Log model description.

    The main purpose is specifying particular DB where log entities, described in
    derived classes, will be stored using nested class Meta declaration

    """
    class Meta:
        """The nested class for DB Model base class for DB specifying.

        Attributes:
            database (Database): a link to particular DB for storing logs.

        """
        database = db_logs

    def json(self):
        """This method represents data like a dict to easy convert in json format then.

        Returns:
            All entities in dict format

        """
        data = self.__data__
        return data


class XRate(_Model):
    """The class that represents an exchange rate entity in the DB.

    International digital currency codes are used instead of abbreviations because they are always the same
    in all banks, while abbreviations could be slightly different (for example, RUB or RUR for the Russian ruble)

    Attributes:
        from_currency (IntegerField): an international code of base currency.
        to_currency (IntegerField): an international code of target currency.
        rate (DoubleField): an exchange rate.
        updated (DateTimeField): date and time of the last update.
        module (CharField): a name of the module that handle the data retrieving form an external API.

    """
    class Meta:
        """The nested class for XRate Model Class for table specifying.

        Attributes:
            db_table (str): the name of the corresponding table in the DB.
            indexes (tuple): table indexes.

        """
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
    """The class that represents the latest update entity in the DB

    This model represents the table that contains literally only one entity - date and time of the latest update
    of any exchange rate in the DB. Storing separated value that will be called very often is better approach
    than every time find it the main table.

    Attributes:
        datetime (DateTimeField): date and time of the latest update of any exchange rate in the main table.

    """
    class Meta:
        """The nested class for LatestUpdate Model Class for table specifying.

        Attributes:
            db_table (str): the name of the corresponding table in the DB.

        """
        db_table = "latest_update"

    datetime = DateTimeField(default=peewee_datetime.datetime.now, index=True)

    def __str__(self):
        return str(self.datetime)


class ApiLog(_LogModel):
    """The class that describes a model of special logs of calls to external APIs.

    Attributes:
        request_url (CharField): URL for external API request.
        request_data (TextField): request data
        request_method (CharField): request method
        request_headers (TextField): request headers
        response_text (TextField): response text
        created (DateTimeField): date and time when the request was sent, index.
        finished (DateTimeField): date and time when the request was finished.
        error (TextField): error text.

    """
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
    """The class that describes a model of special logs of errors occurred during calls to external APIs.

    Attributes:
        request_url (CharField): URL for external API request.
        request_data (TextField): request data
        request_method (CharField): request method
        created (DateTimeField): date and time when the error occurred, index
        error (TextField): error text.
        traceback (TextField): error traceback.

    """
    class Meta:
        db_table = "error_logs"

    request_data = TextField(null=True)
    request_url = TextField()
    request_method = CharField(max_length=100)
    error = TextField()
    traceback = TextField(null=True)
    created = DateTimeField(default=peewee_datetime.datetime.now, index=True)


def start_db():
    """This function creates DB tables if they not exist and fills them with pre-defined values."""
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
    """This method does first initialization of the DB. Should be called only once."""
    XRate.drop_table()
    LatestUpdate.drop_table()
    ApiLog.drop_table()
    ErrorLog.drop_table()
    start_db()

import time

from django.db.models.fields import AutoField, BigAutoField, SmallAutoField, NOT_PROVIDED, Field


def field_init(self, *args, **kwargs):
    if "xtdb" not in kwargs:
        self.__orig_init__(*args, **kwargs)
        return

    xtdb = kwargs.pop("xtdb")
    self.__orig_init__(*args, **kwargs)

    if xtdb is not True:
        return

    if self.primary_key:
        # XTDB always requires an _id column with the primary key of the row.
        self.db_column = "_id"

    # This is for model inheritance. The parent_link is the field that links
    # back to the parent model. Given that functions as the primary key the
    # field also needs to be called _id.
    if self.remote_field and self.remote_field.parent_link:
        self.db_column = "_id"


class XTDBAutoField(AutoField):
    # XTDB does not support server side IDs and Django AutoField that is
    # used for the primary key field relies on this. Normally you insert
    # a row without the primary key and get the primary key back from
    # PostgreSQL. For XTDB we need to generate the primary key IDs
    # ourself.
    #
    # The number of nanoseconds since the unix epoch gives us a 64-bit
    # number that is increasing and also very unlikely to give
    # collisions. This is also what is used in UUID1 and because we
    # don't care about being globally unique we don't need the host part
    # of UUID1.
    #
    # Some tests in de Django test suite expect that ids are increasing
    # and fail when you use random numbers, so having a number that is
    # increasing makes running the test suite easier.
    db_returning = False

    def __init__(self, default=NOT_PROVIDED, db_column=None, *args, **kwargs):
        if default is NOT_PROVIDED:
            default = time.time_ns

        # XTDB always requires an _id column with the primary key of the row.
        super().__init__(default=default, db_column="_id", *args, **kwargs)


class XTDBBigAutoField(BigAutoField):
    db_returning = False

    def __init__(self, default=NOT_PROVIDED, db_column=None, *args, **kwargs):
        if default is NOT_PROVIDED:
            default = time.time_ns

        # XTDB always requires an _id column with the primary key of the row.
        super().__init__(default=default, db_column="_id", *args, **kwargs)


class XTDBSmallAutoField(SmallAutoField):
    db_returning = False

    def __init__(self, default=NOT_PROVIDED, db_column=None, *args, **kwargs):
        if default is NOT_PROVIDED:
            default = time.time_ns

        # XTDB always requires an _id column with the primary key of the row.
        super().__init__(default=default, db_column="_id", *args, **kwargs)


def monkey_patch():
    Field.__orig_init__ = Field.__init__
    Field.__init__ = field_init

import datetime

TINDERPY_EPOCH = 1420070400000


def snowflake_time(id):
    """Returns the creation date in UTC of a snowflake ID."""
    return datetime.datetime.utcfromtimestamp(((id >> 22) + TINDERPY_EPOCH) / 1000)

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\monolith_converters\time.py
import datetime
from datetimeutils.RFC3339 import EPOCH_AS_FILETIME, HUNDREDS_OF_NANOSECONDS
from google.protobuf.timestamp_pb2 import Timestamp
SECONDS_IN_A_YEAR = int(31557600.0)

def get_timestamp(year, month, day, hour = 0, minute = 0, second = 0, microsecond = 0, ts = None):
    if ts is None:
        ts = Timestamp()
    datetime_to_timestamp(datetime.datetime(year, month, day, hour, minute, second, microsecond), ts)
    return ts


def datetime_to_timestamp(py_datetime_obj, ts):
    ts.FromDatetime(py_datetime_obj)


def blue_to_timestamp(blue_ts, ts):
    seconds_since_epoch, _nanoseconds = divmod(blue_ts - EPOCH_AS_FILETIME, HUNDREDS_OF_NANOSECONDS)
    ts.FromSeconds(seconds_since_epoch)


def timestamp_to_blue(ts):
    return ts.ToSeconds() * HUNDREDS_OF_NANOSECONDS + EPOCH_AS_FILETIME


def rfc3339_to_timestamp(dt_string, ts):
    ts.FromJsonString(dt_string)


def years_to_seconds(years):
    return years * SECONDS_IN_A_YEAR

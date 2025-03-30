#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\monolith_converters\units.py


def split_precision(value):
    units = int(value)
    nanos = int(value * 1000000000) - units * 1000000000
    return (units, nanos)


def get_single_value_from_split_precision_message(message):
    return message.units + message.nanos * 1e-09

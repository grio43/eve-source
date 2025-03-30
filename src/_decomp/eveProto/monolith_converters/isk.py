#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveProto\monolith_converters\isk.py


def split_isk(amt):
    units = int(amt)
    divisor = 1
    if amt < 0:
        divisor = -1
    truncated_precision = amt * 10000
    fraction = truncated_precision % (10000 * divisor)
    nanos = int(fraction) * 100000
    return (units, nanos)

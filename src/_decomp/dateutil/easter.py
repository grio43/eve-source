#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dateutil\easter.py
import datetime
__all__ = ['easter',
 'EASTER_JULIAN',
 'EASTER_ORTHODOX',
 'EASTER_WESTERN']
EASTER_JULIAN = 1
EASTER_ORTHODOX = 2
EASTER_WESTERN = 3

def easter(year, method = EASTER_WESTERN):
    if not 1 <= method <= 3:
        raise ValueError('invalid method')
    y = year
    g = y % 19
    e = 0
    if method < 3:
        i = (19 * g + 15) % 30
        j = (y + y // 4 + i) % 7
        if method == 2:
            e = 10
            if y > 1600:
                e = e + y // 100 - 16 - (y // 100 - 16) // 4
    else:
        c = y // 100
        h = (c - c // 4 - (8 * c + 13) // 25 + 19 * g + 15) % 30
        i = h - h // 28 * (1 - h // 28 * (29 // (h + 1)) * ((21 - g) // 11))
        j = (y + y // 4 + i + 2 - c + c // 4) % 7
    p = i - j + e
    d = 1 + (p + 27 + (p + 6) // 40) % 31
    m = 3 + (p + 26) // 30
    return datetime.date(int(y), int(m), int(d))

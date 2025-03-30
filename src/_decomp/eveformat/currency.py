#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\currency.py
import mathext
from eveformat import localization
from eveformat.number import number, number_readable, number_readable_short
isk_readable_format_label_by_log1k = {1: 'UI/Util/FmtThousandIskLong',
 2: 'UI/Util/FmtMillionIskLong',
 3: 'UI/Util/FmtBillionIskLong'}

def isk(amount, fraction = False, rounded = False):
    if rounded:
        amount = mathext.round_to_significant(amount, 3)
    decimal_places = 2 if fraction else 0
    return _isk_label(number(amount, decimal_places=decimal_places))


def isk_readable(amount):
    return _isk_label(number_readable(amount))


def isk_readable_short(amount):
    return _isk_label(number_readable_short(amount))


def _isk_label(amount):
    return u'{amount} {isk}'.format(amount=amount, isk=localization.get_by_label('UI/Common/ISK'))


def plex(amount):
    return u'{amount} {plex}'.format(amount=number(amount), plex=localization.get_by_label('UI/Common/PLEX'))

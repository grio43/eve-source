#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\number.py
import mathext
from eveformat import localization
unit_prefix_by_log1k = {1: 'UI/Util/UnitPrefixThousand',
 2: 'UI/Util/UnitPrefixMillion',
 3: 'UI/Util/UnitPrefixBillion',
 4: 'UI/Util/UnitPrefixTrillion'}
unit_prefix_short_by_log1k = {1: 'UI/Util/UnitPrefixThousandShort',
 2: 'UI/Util/UnitPrefixMillionShort',
 3: 'UI/Util/UnitPrefixBillionShort',
 4: 'UI/Util/UnitPrefixTrillionShort'}

def number(value, decimal_places = None):
    if decimal_places is None:
        if int(round(abs(value) * 100)) % 10 > 0:
            decimal_places = 2
        elif int(round(abs(value) * 10)) % 10 > 0:
            decimal_places = 1
        else:
            decimal_places = 0
    return localization.format_numeric(value, use_grouping=True, decimal_places=decimal_places)


def number_readable(value, significant_digits = 3):
    formatted_value, log_thousand = _readable_value_and_log1k(value, significant_digits)
    prefix_label = unit_prefix_by_log1k.get(log_thousand, None)
    if not prefix_label:
        return formatted_value
    return u'{value} {prefix}'.format(value=formatted_value, prefix=localization.get_by_label(prefix_label))


def number_readable_short(value, significant_digits = 3):
    formatted_value, log_thousand = _readable_value_and_log1k(value, significant_digits)
    prefix_label = unit_prefix_short_by_log1k.get(log_thousand, None)
    if not prefix_label:
        return formatted_value
    return u'{value}{prefix}'.format(value=formatted_value, prefix=localization.get_by_label(prefix_label))


def number_roman(value, zero_text = None):
    if value == 0:
        if zero_text is None:
            raise ValueError("can't represent zero in roman numerals")
        else:
            return zero_text
    if value > 3999 or value < 0:
        raise ValueError('value out of representable range')
    roman = ''
    for r, v, s in (('M', 1000, (('CM', 900), ('D', 500), ('CD', 400))),
     ('C', 100, (('XC', 90), ('L', 50), ('XL', 40))),
     ('X', 10, (('IX', 9), ('V', 5), ('IV', 4))),
     ('I', 1, ())):
        while value > v - 1:
            roman += r
            value -= v

        for rs, vs in s:
            if value > vs - 1:
                roman += rs
                value -= vs

    return roman


def percent(value, decimal_places = None):
    return u'{}%'.format(number(value * 100.0, decimal_places))


def _readable_value_and_log1k(value, significant_digits, log_min = 0, log_max = 4):
    if significant_digits <= 0:
        raise ValueError('Must have at least one significant digit')
    value = mathext.round_to_significant(value, significant_digits)
    log_thousand = max(log_min, min(log1k(value), log_max))
    value = value / mathext.pow(1000, log_thousand)
    for i in range(significant_digits - 1):
        if int(round(value * mathext.pow(10, significant_digits - 1 - i))) % 10 > 0:
            decimal_places = significant_digits - 1 - i
            break
    else:
        decimal_places = 0

    return (localization.format_numeric(value, use_grouping=True, decimal_places=decimal_places), log_thousand)


def log1k(value):
    if mathext.is_close(value, 0):
        return 0
    return int(mathext.floor(mathext.log(abs(value), 1000)))

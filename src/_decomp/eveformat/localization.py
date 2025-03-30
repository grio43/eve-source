#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\localization.py
from __future__ import absolute_import
try:
    import localization
except ImportError:
    localization = None

def get_by_label(label, **kwargs):
    return localization.GetByLabel(label, **kwargs)


def format_numeric(value, use_grouping = False, decimal_places = None, leading_zeroes = None):
    value = float(value)
    return localization.formatters.FormatNumeric(value, useGrouping=use_grouping, decimalPlaces=decimal_places, leadingZeroes=leading_zeroes)

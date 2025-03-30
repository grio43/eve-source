#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\scale.py
from carbonui.uicore import uicore

def scale_dpi(value):
    return int(round(value * uicore.dpiScaling))


def scale_dpi_f(value):
    return value * uicore.dpiScaling


def reverse_scale_dpi(value):
    if uicore.dpiScaling != 1.0:
        try:
            return int(round(value / uicore.dpiScaling))
        except (ValueError, OverflowError):
            return 0

    else:
        return int(value)

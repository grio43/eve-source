#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\dpi.py
from carbonui.uicore import uicore

def ScaleDpi(value):
    return int(value * uicore.dpiScaling + 0.5)


scale_dpi = ScaleDpi

def ScaleDpiF(value):
    return value * uicore.dpiScaling


scale_dpi_f = ScaleDpiF

def ReverseScaleDpi(value):
    if uicore.dpiScaling != 1.0:
        try:
            return int(value / uicore.dpiScaling + 0.5)
        except (ValueError, OverflowError):
            return 0

    else:
        return int(value)


reverse_scale_dpi = ReverseScaleDpi

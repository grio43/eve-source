#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\formatters\numericFormatters.py
import eveLocalization
import pytelemetry.zoning as telemetry
from localization import internalUtil
from localization import uiutil

@telemetry.ZONE_FUNCTION
def FormatNumeric(value, useGrouping = False, decimalPlaces = None, leadingZeroes = None):
    result = eveLocalization.FormatNumeric(value, internalUtil.GetLanguageID(), useGrouping=useGrouping, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)
    return uiutil.PrepareLocalizationSafeString(result, messageID='numeric')

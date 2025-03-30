#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\propertyHandlers\numericPropertyHandler.py
import carbon.common.script.util.format as fmtutils
import eve.common.script.util.eveFormat as evefmtutils
import eveLocalization
from localization import const as locconst
from localization.propertyHandlers.basePropertyHandler import BasePropertyHandler

class NumericPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ['quantity',
                               'isk',
                               'aur',
                               'distance']}

    def _GetQuantity(self, value, languageID, *args, **kwargs):
        return value

    def _GetIsk(self, value, languageID, *args, **kwargs):
        decimalPlaces = kwargs.get('decimalPlaces', 2)
        showFraction = True if decimalPlaces > 0 else False
        return evefmtutils.FmtISK(value, showFractionsAlways=showFraction)

    def _GetAur(self, value, languageID, *args, **kwargs):
        return evefmtutils.FmtAUR(value)

    def _GetDistance(self, value, languageID, *args, **kwargs):
        return fmtutils.FmtDist(value, maxdemicals=kwargs.get('decimalPlaces', 3))


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.NUMERIC, NumericPropertyHandler())

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\colorInfoWrapperMapFilter.py
import trinity
from carbonui.util import colorblind
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilter import BaseMapFilter
from eve.client.script.ui.shared.mapView.filters.mapFilterConst import STAR_COLORTYPE_PASSIVE, STAR_COLORTYPE_DATA, NEUTRAL_COLOR
from eve.client.script.ui.shared.mapView.mapViewConst import STAR_SIZE_STANDARD
from eve.client.script.ui.shared.mapView.mapViewUtil import PARTICLE_SPRITE_DATA_TEXTURE, PARTICLE_SPRITE_HEAT_TEXTURE
from utillib import KeyVal

class ColorInfoWrapperMapFilter(BaseMapFilter):

    def __init__(self, colorMode, itemID, filterData):
        BaseMapFilter.__init__(self, colorMode, itemID)
        self.filterData = filterData
        self._colorCurve = None
        loadArguments = filterData.loadArguments or ()
        self.colorInfo = self._GetDefaultStarColorInfo()
        if itemID is not None:
            colorMode = (colorMode, itemID)
        filterData.loadFunction(self.colorInfo, colorMode, *loadArguments)

    def GetName(self):
        if self.filterData is None:
            return ''
        elif callable(self.filterData.header):
            return self.filterData.header((self.filterID, self.itemID))
        else:
            return self.filterData.header

    def GetSearchHandler(self):
        return self.filterData.searchHandler

    def _GetDefaultStarColorInfo(self):
        return KeyVal(solarSystemDict={}, colorList=None, legend=set(), colorType=STAR_COLORTYPE_PASSIVE, defaultSize=STAR_SIZE_STANDARD, defaultColor=NEUTRAL_COLOR)

    def GetLineColor(self, solarSystemID):
        return self.GetStarColor(solarSystemID)

    def GetStarColor(self, solarSystemID):
        data = self._GetSolarSystemData(solarSystemID)
        if data:
            uniqueColor = data[3]
            colorPositionNormalized = data[1]
            if uniqueColor:
                col = uniqueColor
            else:
                col = self._GetColorCurveValue(colorPositionNormalized)
            try:
                col = (col.r,
                 col.g,
                 col.b,
                 col.a)
            except:
                pass

        else:
            col = self.colorInfo.defaultColor
        return colorblind.CheckReplaceColor(col)

    def _GetSolarSystemData(self, solarSystemID):
        return self.colorInfo.solarSystemDict.get(solarSystemID, None)

    def _GetTooltipCallback(self, solarSystemID):
        data = self._GetSolarSystemData(solarSystemID)
        if data:
            return data[2]

    def GetSystemHint(self, solarSystemID):
        tooltipCallback = self._GetTooltipCallback(solarSystemID)
        if tooltipCallback:
            func, args = tooltipCallback
            return func(*args)

    def GetStarSize(self, solarSystemID):
        data = self._GetSolarSystemData(solarSystemID)
        if data:
            return mapViewConst.STAR_SIZE_AFFECTED * data[0]
        else:
            return mapViewConst.STAR_SIZE_UNIMPORTANT

    def _GetColorCurveValue(self, time):
        return self._GetColorCurve().GetValueAt(time)

    def _GetDefaultColorList(self):
        return [(1.0, 0.0, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0)]

    def _GetColorCurve(self):
        if not self._colorCurve:
            self._colorCurve = self._ConstructColorCurve()
        return self._colorCurve

    def _ConstructColorCurve(self):
        colorList = self.colorInfo.colorList or self._GetDefaultColorList()
        colorCurve = trinity.Tr2CurveColor()
        colorListDivisor = float(len(colorList) - 1)
        for colorID, colorValue in enumerate(colorList):
            time = float(colorID) / colorListDivisor
            colorCurve.AddKey(time, colorValue, trinity.Tr2CurveInterpolation.LINEAR)

        return colorCurve

    def GetSpriteEffectPath(self):
        if self.colorInfo.colorType == STAR_COLORTYPE_DATA:
            return PARTICLE_SPRITE_DATA_TEXTURE
        else:
            return PARTICLE_SPRITE_HEAT_TEXTURE

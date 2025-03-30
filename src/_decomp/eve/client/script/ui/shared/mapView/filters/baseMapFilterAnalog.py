#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\baseMapFilterAnalog.py
from carbonui.util.color import Color
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilter import BaseMapFilter

class BaseMapFilterAnalog(BaseMapFilter):

    def GetStarSizeAffected(self, solarSystemID):
        return mapViewConst.STAR_SIZE_AFFECTED * self.GetNumInstances(solarSystemID) ** 0.5

    def GetStarSizeUnaffected(self):
        return mapViewConst.STAR_SIZE_UNIMPORTANT

    def GetStarColorAffected(self, solarSystemID):
        x = 0.5 * self.GetNumInstances(solarSystemID)
        x = min(1.0, x)
        return Color(*self.color).SetBrightness(0.5 + 0.5 * x).GetRGBA()

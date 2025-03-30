#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\mapFilterActualColor.py
from eve.client.script.ui.shared.mapView.filters import mapFilterConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilter import BaseMapFilter
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.common.script.sys import idCheckers
from localization import GetByLabel

class MapFilterActualColor(BaseMapFilter):
    name = GetByLabel('UI/Map/MapPallet/cbStarsActual')
    spriteEffectPath = mapFilterConst.PARTICLE_SPRITE_HEAT_TEXTURE

    def _ConstructDataBySolarSystemID(self):
        dataBySolarSystemID = {}
        for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            dataBySolarSystemID[solarSystemID] = solarSystem.star.color

        return dataBySolarSystemID

    def GetStarColor(self, solarSystemID):
        if idCheckers.IsTriglavianSystem(solarSystemID):
            return (0.8, 0.0, 0.0, 1.0)
        else:
            return self.dataBySolarSystemID[solarSystemID]

    def GetLineColor(self, solarSystemID):
        return self.GetStarColor(solarSystemID)

    def GetHintAffected(self, solarSystemID):
        return None

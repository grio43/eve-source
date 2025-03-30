#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\mapFilterEDENCOMMinorVictories.py
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupTriglavianSpace
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilterBinary import BaseMapFilterBinary
from localization import GetByLabel

class MapFilterEDENCOMMinorVictories(BaseMapFilterBinary):
    name = GetByLabel('UI/Map/StarModeHandler/EDENCOMMinorVictories')
    hint = GetByLabel('UI/Map/StarModeHandler/Hints/EDENCOMMinorVictories')
    agencyContentGroupID = contentGroupTriglavianSpace

    def _ConstructDataBySolarSystemID(self):
        solarSystemIDs = sm.GetService('map').GetEdencomMinorVictorySystems()
        return {solarSystemID:None for solarSystemID in solarSystemIDs}

    def GetStarSizeAffected(self, solarSystemID):
        return mapViewConst.STAR_SIZE_AFFECTED * 2

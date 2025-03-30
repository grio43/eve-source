#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\mapFilterSettledByCorp.py
from eve.client.script.ui.shared.mapView.filters.baseMapFilterBinary import BaseMapFilterBinary
from localization import GetByLabel

class MapFilterSettledByCorp(BaseMapFilterBinary):
    name = GetByLabel('UI/InfoWindow/SettledSystems')

    def GetHintAffected(self, solarSystemID):
        corporationName = cfg.eveowners.Get(self.itemID).name
        return GetByLabel('UI/InfoWindow/SystemSettledByCorp', corpName=corporationName)

    def _ConstructDataBySolarSystemID(self):
        solarSystemIDs = sm.RemoteSvc('config').GetStationSolarSystemsByOwner(self.itemID)
        return {solarSystem.solarSystemID:[] for solarSystem in solarSystemIDs}

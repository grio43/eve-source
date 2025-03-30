#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\map.py
from behaviors.tasks import Task
from bluepy import TimedFunction

class GetSolarSystemFactionID(Task):

    @TimedFunction('behaviors::actions::map::GetSolarSystemFactionID::OnEnter')
    def OnEnter(self):
        faction_id = self.GetFactionIdBySolarSystemContextValue()
        if faction_id:
            self.SendBlackboardValue(self.attributes.messageAddress, faction_id)
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def GetFactionIdBySolarSystemContextValue(self):
        solarSystem = cfg.mapSystemCache.get(self.context.solarSystemId, None)
        return getattr(solarSystem, 'factionID', None)

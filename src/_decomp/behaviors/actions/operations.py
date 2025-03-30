#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\operations.py
from behaviors.tasks import Task

class GetOperationSiteSpawn(Task):

    def OnEnter(self):
        character_id = self.GetLastBlackboardValue(self.attributes.characterIdAddress)
        site_id = self.attributes.operationSiteId
        solar_system_id, spawn_id, x, y, z = self.context.keeper.GetOperationSpawnpointPosition(character_id, site_id)
        self.SendBlackboardValue(self.attributes.siteSolarSystemIdAddress, solar_system_id)
        self.SendBlackboardValue(self.attributes.siteSpawnIdAddress, spawn_id)
        self.SendBlackboardValue(self.attributes.siteCoordinatesAddress, (x, y, z))
        self.SetStatusToSuccess()

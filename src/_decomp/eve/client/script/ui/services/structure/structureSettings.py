#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\structure\structureSettings.py
from caching.memoize import Memoize
from carbon.common.script.sys.service import Service

class StructureSettings(Service):
    __guid__ = 'svc.structureSettings'
    __notifyevents__ = ['OnSessionReset']

    def Run(self, *args):
        pass

    @Memoize(2)
    def CharacterHasService(self, structureID, serviceID):
        return sm.RemoteSvc('structureSettings').CharacterHasService(structureID, serviceID)

    @Memoize(2)
    def CharacterHasSetting(self, structureID, settingID):
        return sm.RemoteSvc('structureSettings').CharacterHasSetting(structureID, settingID)

    def OnSessionReset(self):
        self.CharacterHasService.clear_memoized()
        self.CharacterHasSetting.clear_memoized()

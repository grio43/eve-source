#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\publicQaToolsClient.py
import blue
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.moveMeWindow import MoveMeWnd
from eveexceptions import UserError

class PublicQaToolsClient(Service):
    __exportedcalls__ = {}
    __guid__ = 'svc.publicQaToolsClient'
    __servicename__ = 'publicQaToolsClient'
    __displayname__ = 'Public QA Tools Client'
    __dependencies__ = []
    __notifyevents__ = ['OnMoveMeLocations']
    allowedSlashCommands = ['/moveme',
     '/copyskills',
     '/copyships',
     '/boostsov',
     '/booststandings',
     '/giveitem',
     '/shipcloak',
     '/shipuncloak',
     '/mycharid',
     '/giveallskills',
     '/givetesteventskills',
     '/omega',
     '/alpha',
     '/completeextraction']

    def MoveMeTo(self, destination, *args):
        try:
            sm.GetService('sessionMgr').PerformSessionChange('MoveMeTo', sm.RemoteSvc('publicQaToolsServer').MoveMeTo, destination)
        except UserError as e:
            if e.msg == 'SystemCheck_TransferFailed_Loading':
                eve.Message('CustomNotify', {'notify': 'Spooling up system. Please wait.'})
                blue.pyos.synchro.SleepSim(10000)
                sm.GetService('sessionMgr').PerformSessionChange('MoveMeTo', sm.RemoteSvc('publicQaToolsServer').MoveMeTo, destination)
            else:
                raise

    def SlashCmd(self, commandLine):
        sm.RemoteSvc('publicQaToolsServer').SlashCmd(commandLine)

    def CommandAllowed(self, commandLine):
        commandLine = commandLine.lower()
        for command in self.allowedSlashCommands:
            if commandLine.startswith(command):
                return True

        return False

    def CanGiveItemForMultifit(self):
        return sm.RemoteSvc('publicQaToolsServer').CanGiveItemForMultifit()

    def OnMoveMeLocations(self, solarsystems):
        MoveMeWnd.Open(solarSystems=solarsystems)

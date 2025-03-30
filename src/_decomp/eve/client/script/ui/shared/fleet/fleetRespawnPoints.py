#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetRespawnPoints.py
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from inventorycommon.const import typeCombatRespawnBooster
from localization import GetByLabel

class RespawnPanel(Container):
    __notifyevents__ = ['OnSessionChanged', 'OnFleetRespawnPointsUpdate_Local']
    default_clipChildren = True

    def LoadPanel(self):
        if not self.sr.Get('inited', 0):
            self.PostStartup()
            setattr(self.sr, 'inited', 1)
        self.UpdateList()

    def PostStartup(self):
        sm.RegisterNotify(self)
        self.respawnLabel = Label(name='respawnLabel', parent=self, align=uiconst.TOTOP, padding=(0, 0, 0, 8), state=uiconst.UI_NORMAL, color=TextColor.SECONDARY)
        self.respawnScroll = Scroll(name='respawnScroll', parent=self, align=uiconst.TOALL)

    def OnSessionChanged(self, isremote, sess, change):
        if 'solarsystemid2' in change:
            self.UpdateList()

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)
        Container._OnClose(self)

    def UpdateList(self):
        self.respawnLabel.text = GetByLabel('UI/Fleet/Respawn/Summary', requiresBoosterTypeID=typeCombatRespawnBooster)
        scrollList = []
        for respawnPoint in sm.GetService('fleet').GetRespawnPoints():
            character = cfg.eveowners.Get(respawnPoint.extraClientState.characterID).name
            solarsystem = cfg.evelocations.Get(respawnPoint.solarsystemID).name
            jumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, respawnPoint.solarsystemID)
            entry = GetFromClass(Generic, {'label': '%s<t>%s<t>%s' % (character, solarsystem, jumps)})
            scrollList.append(entry)

        scrollHeaders = [GetByLabel('UI/Common/Character'), GetByLabel('UI/Common/LocationTypes/SolarSystem'), GetByLabel('UI/Common/Jumps')]
        self.respawnScroll.Load(contentList=scrollList, headers=scrollHeaders, noContentHint=GetByLabel('UI/Fleet/Respawn/NoRespawnPointsAvailable'))

    def OnFleetRespawnPointsUpdate_Local(self):
        self.UpdateList()

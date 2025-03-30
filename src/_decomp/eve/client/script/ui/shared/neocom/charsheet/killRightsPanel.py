#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\killRightsPanel.py
import blue
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.killRights import KillRightsEntry
from localization import GetByLabel

class KillRightsPanel(Container):
    default_name = 'KillRightsPanel'
    __notifyevents__ = ['OnKillRightSold',
     'OnKillRightExpired',
     'OnKillRightSellCancel',
     'OnKillRightCreated',
     'OnKillRightUsed']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.scroll = Scroll(parent=self, padding=(0, 4, 0, 4))

    def LoadPanel(self, *args):
        scrolllist = []
        killRights = sm.GetService('bountySvc').GetMyKillRights()
        currentTime = blue.os.GetWallclockTime()
        myKillRights = filter(lambda x: x.fromID == session.charid and currentTime < x.expiryTime, killRights)
        otherKillRights = filter(lambda x: x.toID == session.charid and currentTime < x.expiryTime, killRights)
        charIDsToPrime = set()
        for eachKR in myKillRights:
            charIDsToPrime.add(eachKR.toID)

        for eachKR in otherKillRights:
            charIDsToPrime.add(eachKR.fromID)

        cfg.eveowners.Prime(charIDsToPrime)
        if myKillRights:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/CanKill'),
             'hideLines': True}))
            for killRight in myKillRights:
                scrolllist.append(GetFromClass(KillRightsEntry, {'charID': killRight.toID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': True}))

        if otherKillRights:
            scrolllist.append(GetFromClass(Header, {'label': GetByLabel('UI/InfoWindow/CanBeKilledBy'),
             'hideLines': True}))
            for killRight in otherKillRights:
                scrolllist.append(GetFromClass(KillRightsEntry, {'charID': killRight.fromID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': False}))

        self.scroll.sr.id = 'charsheet_killrights'
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillRightsFound'))

    def _ReloadPanel(self):
        if self.display:
            self.LoadPanel()

    def OnKillRightSold(self, killRightID):
        self._ReloadPanel()

    def OnKillRightExpired(self, killRightID):
        self._ReloadPanel()

    def OnKillRightSellCancel(self, killRightID):
        self._ReloadPanel()

    def OnKillRightCreated(self, killRightID, fromID, toID, expiryTime):
        self._ReloadPanel()

    def OnKillRightUsed(self, killRightID, toID):
        self._ReloadPanel()

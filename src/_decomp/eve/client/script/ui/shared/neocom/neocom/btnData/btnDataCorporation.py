#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataCorporation.py
from eve.client.script.ui.shared.neocom.corporation import corpUISignals
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode
from localization import GetByLabel

class BtnDataNodeCorporation(BtnDataNode):

    def __init__(self, parent = None, children = None, iconPath = None, label = None, btnID = None, btnType = None, isRemovable = True, isDraggable = True, isOpen = False, isBlinking = False, labelAbbrev = None, wndCls = None, cmdName = None, **kw):
        BtnDataNode.__init__(self, parent, children, iconPath, label, btnID, btnType, isRemovable, isDraggable, isOpen, isBlinking, labelAbbrev, wndCls, cmdName, **kw)
        corpUISignals.on_corporation_application_changed.connect(self.OnCorpApplicationChanged)

    def OnCorpApplicationChanged(self, *args):
        self.OnBadgeCountChanged()

    def GetItemCount(self):
        return len(sm.GetService('corp').GetMyOpenInvitations())

    def _disconnect_signals(self):
        BtnDataNode._disconnect_signals(self)
        corpUISignals.on_corporation_application_changed.disconnect(self.OnCorpApplicationChanged)

    def GetUnseenItemsHint(self):
        numItems = self.GetItemCount()
        if numItems:
            return GetByLabel('UI/Corporations/Applications/OpenInvitationsHint', numInvitations=numItems)

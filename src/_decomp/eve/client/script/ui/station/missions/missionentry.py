#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\missions\missionentry.py
import localization
import utillib
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
from eveservices.menu import GetMenuService
from menu import MenuLabel
from eve.common.lib import appConst as const

class VirtualBaseMissionEntry(SE_BaseClassCore):
    __guid__ = 'listentry.VirtualBaseMissionEntry'
    OnSelectCallback = None

    def Startup(self, *etc):
        self.sr.label = eveLabel.EveLabelMedium(text='', parent=self, left=5, state=uiconst.UI_DISABLED, color=None, maxLines=1, align=uiconst.CENTERLEFT)
        self.sr.line = Container(name='lineparent', align=uiconst.TOBOTTOM, parent=self, height=1)

    def GetHeight(_self, *args):
        node, width = args
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 4
        return node.height

    def OnSelect(self, *args):
        if getattr(self, 'OnSelectCallback', None):
            apply(self.OnSelectCallback, args)

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)
        self.OnSelect(self)

    def NoEvent(self, *args):
        pass

    @classmethod
    def GetCopyData(cls, node):
        return node.label


class VirtualAgentMissionEntry(VirtualBaseMissionEntry):
    __guid__ = 'listentry.VirtualAgentMissionEntry'
    isDragObject = True

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = node.label
        self.sr.iconList = []
        textOffset = 1
        for iconID, hintText in node.missionIconData:
            self.sr.iconList.append(eveIcon.Icon(icon=iconID, parent=self, pos=(textOffset,
             1,
             16,
             16), align=uiconst.TOPLEFT, idx=0))
            self.sr.iconList[-1].hint = hintText
            textOffset += self.sr.iconList[-1].width

        self.sr.label.left = textOffset + 4
        self.rightClickMenu = []
        self.rightClickMenu.append((MenuLabel('UI/Agents/Commands/ReadDetails'), self.OpenDetails))
        self.rightClickMenu.append((MenuLabel('UI/Agents/Commands/StartConversationWith', {'agentID': self.sr.node.agentID}), self.Convo))
        if node.missionState == const.agentMissionStateOffered:
            self.rightClickMenu.append((MenuLabel('UI/Agents/Commands/RemoveOffer'), self.RemoveOffer))

    def OpenDetails(self):
        sm.GetService('agents').PopupMission(self.sr.node.agentID)

    def RemoveOffer(self):
        sm.StartService('agents').RemoveOfferFromJournal(self.sr.node.agentID)

    def OnDblClick(self, *args):
        self.OpenDetails()

    def Convo(self):
        sm.GetService('agents').OpenDialogueWindow(self.sr.node.agentID)

    def GetMenu(self):
        return self.rightClickMenu

    def GetDragData(self, *args):
        fakeNode = []
        if session.fleetid:
            _fakeNode = utillib.KeyVal()
            _fakeNode.__guid__ = 'listentry.VirtualAgentMissionEntry'
            _fakeNode.agentID = self.sr.node.agentID
            _fakeNode.charID = session.charid
            _fakeNode.label = localization.GetByLabel('UI/Agents/MissionJournal')
            fakeNode = [_fakeNode]
        return fakeNode

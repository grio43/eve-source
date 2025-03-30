#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\officeEntry.py
import carbonui.const as uiconst
import uthread
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveIcon import CorpIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.themeColored import LineThemeColored
from inventorycommon.util import IsNPC
from localization import GetByLabel
ICON_SIZE = 32

class OfficeEntry(SE_BaseClassCore):
    __guid__ = 'listentry.OfficeEntry'

    def Startup(self, *args):
        self.Flush()
        self.ConstructLayout()

    def ConstructLayout(self):
        self.mainCont = ContainerAutoSize(name='mainCont', parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=4)
        self.infoIcon = InfoIcon(name='ShowInfoButton', parent=Container(name='showInfoContainer', parent=self.mainCont, align=uiconst.TORIGHT, width=16, left=5), align=uiconst.TOTOP, top=5, hint=GetByLabel('UI/Station/Lobby/CorpShowInfoButton'))
        self.iconContainer = Container(name='iconCont', parent=self.mainCont, align=uiconst.TOLEFT, width=ICON_SIZE, padding=(0, 0, 8, 0))
        self.corpNameLabel = EveLabelSmall(name='CorpNameLabel', text=GetByLabel('UI/Station/Lobby/CorpName'), parent=self.mainCont, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=4)
        self.corpNameText = EveLabelMedium(name='corpNameText', parent=self.mainCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP)
        self.buttonCnt = Container(name='ButtonContainer', parent=self.mainCont, align=uiconst.TOTOP, height=32, state=uiconst.UI_PICKCHILDREN, padTop=4)

    def Load(self, node):
        self.sr.node = node
        data = node
        self.infoIcon.UpdateInfoLink(const.typeCorporation, data.corpID)
        self.corpNameText.SetText(data.Get('corpName', ''))
        uthread.new(self.SetLogoIcon, data)
        self.buttonCnt.Flush()
        if not IsNPC(node.corpID):
            buttonEntries = []
            if session.corpid != node.corpID:
                if sm.GetService('corp').GetActiveApplication(node.corpID) is not None:
                    applyLabel = GetByLabel('UI/Corporations/CorpApplications/ViewApplication')
                else:
                    applyLabel = GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/ApplyToJoin')
                buttonEntries.append((applyLabel,
                 sm.GetService('corp').ApplyForMembership,
                 (node.corpID,),
                 80))
            if len(buttonEntries) > 0:
                self.buttonsGroup = ButtonGroup(btns=buttonEntries, parent=self.buttonCnt)

    def SetLogoIcon(self, data):
        if not self.destroyed:
            CorpIcon(corpID=data.corpID, parent=self.iconContainer, align=uiconst.CENTERTOP, pos=(0,
             5,
             ICON_SIZE,
             ICON_SIZE))

    def GetHeight(self, *args):
        node, width = args
        lw, lh = EveLabelSmall.MeasureTextSize(text=GetByLabel('UI/Station/Lobby/CorpName'), width=width)
        tw, th = EveLabelMedium.MeasureTextSize(text=node.corpName, width=width)
        multiplier = 1
        height = 2
        height += (lh + th + 15) * multiplier
        height += 8
        if not IsNPC(node.corpID) and session.corpid != node.corpID:
            height += 30
        node.height = height
        return node.height

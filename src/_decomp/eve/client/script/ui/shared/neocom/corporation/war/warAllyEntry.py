#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warAllyEntry.py
import blue
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtDate
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarAssistanceOfferWnd
from eve.common.script.sys.idCheckers import IsCorporation, IsAlliance
from localization import GetByLabel

class AllyEntry(SE_BaseClassCore):
    __guid__ = 'listentry.AllyEntry'

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.iconCont = Container(name='iconCont', parent=self, align=uiconst.TOLEFT, width=110)
        self.textCont = Container(name='textCont', parent=self, align=uiconst.TOALL, padLeft=7, clipChildren=True, width=30)
        self.allyButton = ButtonIcon(name='allyButton', parent=self, align=uiconst.TORIGHT, width=24, iconSize=24, texturePath='res:/UI/Texture/Icons/Mercenary_64.png', left=2, isHoverBGUsed=False)
        self.allyNameLabel = EveLabelMedium(text='', parent=self.textCont, top=2, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)

    def Load(self, node):
        self.sr.node = node
        if node.allyRow is None:
            self.timeStarted = None
            self.timeFinished = None
        else:
            originalWarTimeFinished = node.originalWarTimeFinished
            originalWarTimeStarted = node.originalWarTimeStarted
            allyStart = node.allyRow.timeStarted
            self.timeStarted = max(allyStart, originalWarTimeStarted)
            self.timeFinished = min(node.allyRow.timeFinished, originalWarTimeFinished) if originalWarTimeFinished else node.allyRow.timeFinished
        self.warNegotiation = node.warNegotiation
        self.LoadEntry(node.warID, node.allyID, node.isAlly)

    def LoadEntry(self, warID, allyID, isAlly):
        if hasattr(self, 'allyLogo'):
            self.allyLogo.Close()
        self.allyNameLabel.text = ''
        self.allyID = allyID
        self.isAlly = isAlly
        self.warID = warID
        if IsCorporation(self.allyID):
            allyLinkType = const.typeCorporation
        elif IsAlliance(self.allyID):
            allyLinkType = const.typeAlliance
        else:
            allyLinkType = const.typeFaction
        allyName = cfg.eveowners.Get(self.allyID).name
        self.allyLogo = GetLogoIcon(itemID=self.allyID, parent=self.iconCont, acceptNone=False, align=uiconst.TOPRIGHT, size=32, state=uiconst.UI_NORMAL, top=2)
        self.allyLogo.OnClick = (self.ShowInfo, self.allyID, allyLinkType)
        self.allyLogo.hint = '%s<br>%s' % (allyName, GetByLabel('UI/Corporations/Wars/Ally'))
        allyName = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=allyName, info=('showinfo', allyLinkType, self.allyID))
        self.allyNameLabel.text = allyName
        self.UpdateText()
        if not self.isAlly:
            allyTexturePath = 'res:/UI/Texture/Icons/Mercenary_Attention_64.png'
            allyHint = GetByLabel('UI/Corporations/Wars/OfferedHelp')
            if self.IsDirector():
                self.allyButton.func = self.AllyClick
                self.allyButton.Enable()
        else:
            allyTexturePath = 'res:/UI/Texture/Icons/Mercenary_Ally_64.png'
            allyHint = GetByLabel('UI/Corporations/Wars/HelpAccepted')
            self.allyButton.Disable()
        self.allyButton.texturePath = allyTexturePath
        self.allyButton.UpdateIconState()
        self.allyButton.hint = allyHint
        self.allyLogo.OnMouseEnter = self.OnMouseEnter
        self.allyLogo.OnMouseExit = self.OnMouseExit
        self.allyNameLabel.OnMouseEnter = self.OnMouseEnter
        self.allyNameLabel.OnMouseExit = self.OnMouseExit

    def UpdateText(self):
        if IsCorporation(self.allyID):
            allyLinkType = const.typeCorporation
        elif IsAlliance(self.allyID):
            allyLinkType = const.typeAlliance
        else:
            allyLinkType = const.typeFaction
        currentTime = blue.os.GetWallclockTime()
        allyName = cfg.eveowners.Get(self.allyID).ownerName
        if not self.isAlly:
            self.allyNameLabel.text = GetByLabel('UI/Corporations/Wars/AllyEntryAssistanceOffered', allyID=self.allyID, info=('showinfo', allyLinkType, self.allyID), ally=cfg.eveowners.Get(self.allyID).ownerName)
            self.hint = GetByLabel('UI/Corporations/Wars/AllyEntryAssistanceOfferedHint', ally=cfg.eveowners.Get(self.allyID).ownerName, description=self.warNegotiation.description, iskValue=self.warNegotiation.iskValue)
        if currentTime < self.timeStarted:
            self.allyNameLabel.text = GetByLabel('UI/Corporations/Wars/AllyEntryNotStarted', allyID=self.allyID, info=('showinfo', allyLinkType, self.allyID), ally=cfg.eveowners.Get(self.allyID).ownerName, timeToFight=self.timeStarted - currentTime)
            self.hint = GetByLabel('UI/Corporations/Wars/AllyEntryNotStartedHint', startTime=FmtDate(self.timeStarted, 'sn'), endTime=FmtDate(self.timeFinished, 'sn'))
        elif currentTime < self.timeFinished:
            self.allyNameLabel.text = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=allyName, info=('showinfo', allyLinkType, self.allyID))
            self.hint = GetByLabel('UI/Corporations/Wars/AllyEntryStartedHint', startTime=FmtDate(self.timeStarted, 'sn'), endTime=FmtDate(self.timeFinished, 'sn'))

    def GetHeight(self, *args):
        node, width = args
        node.height = 36
        return node.height

    def OnDblClick(self, *args):
        from eve.client.script.ui.shared.neocom.corporation.war.warReport import WarReportWnd
        wnd = WarReportWnd.GetIfOpen()
        if wnd:
            wnd.LoadInfo(warID=self.warID)
            wnd.Maximize()
        else:
            WarReportWnd.Open(warID=self.warID)

    def AllyClick(self):
        if not self.isAlly:
            self.ShowWarNegotiation()

    def IsDirector(self):
        entityID = session.allianceid or session.corpid
        if session.corprole & const.corpRoleDirector == const.corpRoleDirector:
            return True
        return False

    def ShowWarNegotiation(self):
        WarAssistanceOfferWnd.Open(isRequest=False, warNegotiationID=self.sr.node.warNegotiation.warNegotiationID, requesterID=self.allyID)

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def GetMenu(self, *args):
        menu = []
        if session.role & ROLE_GML == ROLE_GML:
            subMenu = []
            if self.isAlly:
                if self.timeStarted > blue.os.GetWallclockTime():
                    subMenu.append(('Start Defending', sm.GetService('war').GMActivateDefender, (self.warID, self.allyID)))
                else:
                    subMenu.append(('Extend Contract', sm.GetService('war').GMExtendAllyContract, (self.warID, self.allyID, const.WEEK)))
                    subMenu.append(('Finish Defending', sm.GetService('war').GMDeactivateDefender, (self.warID, self.allyID)))
                menu.append(('GM Tools', subMenu))
        return menu


class AllyListEntry(AllyEntry):
    __guid__ = 'listentry.AllyListEntry'

    def ApplyAttributes(self, attributes):
        AllyEntry.ApplyAttributes(self, attributes)
        self.iconCont.width = 36

    def LoadEntry(self, warID, allyID, isAlly):
        AllyEntry.LoadEntry(self, warID, allyID, isAlly)
        self.allyLogo.left = 2

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warEntry.py
from collections import defaultdict
import blue
import eve.common.lib.appConst as appConst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtDate, ParseDateTime
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarAssistanceOfferWnd, WarSurrenderWnd
from eve.client.script.ui.shared.neocom.corporation.war.warContainerForWarEntry import WarContainer
from eve.client.script.ui.shared.neocom.corporation.war.allyWnd import AllyWnd
from eve.client.script.ui.util.utilWindows import NamePopup
from eve.common.script.sys.idCheckers import IsFaction
from evewar import warConst
from localization import GetByLabel
from menu import MenuLabel
from utillib import KeyVal

class WarEntry(SE_BaseClassCore):
    __guid__ = 'listentry.WarEntry'
    __notifyevents__ = ['OnWarEntryChanged']
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.showAllyButton = False
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.buttonCont = Container(name='buttons', parent=self, align=uiconst.TORIGHT, width=30)
        warCont = Container(name='wars', parent=self, align=uiconst.TOALL, clipChildren=True, padRight=4)
        self.warNegotiationID = None
        self.warAllyNegotiationID = None
        self.allies = None
        self.noOfAllies = 0
        utilMenu = UtilMenu(menuAlign=uiconst.TOPRIGHT, parent=self.buttonCont, align=uiconst.CENTERRIGHT, GetUtilMenu=self.WarMenu, texturePath='res:/UI/Texture/Icons/73_16_50.png', left=appConst.defaultPadding)
        self.openForAllies = Icon(parent=self.buttonCont, align=uiconst.CENTERRIGHT, left=27, iconSize=20, size=20)
        self.openForAllies.LoadIcon('res:/UI/Texture/Icons/Mercenary_Add_64.png')
        self.openForAllies.display = False
        self.openForAllies.hint = GetByLabel('UI/Corporations/Wars/DefenderOpenForAllies')
        self.surrenderNegotiation = Icon(parent=self.buttonCont, align=uiconst.CENTERRIGHT, left=52, iconSize=20, size=20)
        self.surrenderNegotiation.LoadIcon('res:/UI/Texture/Icons/Surrender_Attention_64.png')
        self.surrenderNegotiation.display = False
        self.surrenderNegotiation.hint = GetByLabel('UI/Corporations/Wars/SurrenderPending')
        self.expander = GlowSprite(parent=self, pos=(0, 0, 16, 16), name='expander', state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/38_16_228.png', align=uiconst.CENTERLEFT)
        self.expander.display = False
        self.warCont = WarContainer(parent=warCont, top=2)
        sm.RegisterNotify(self)

    def Load(self, node):
        self.sr.node = node
        self.sr.id = node.id
        self.war = war = node.war
        self.myWars = node.myWars
        self.warID = war.warID
        self.attackerID = war.declaredByID
        self.defenderID = war.againstID
        self.warIsOpen = self.IsOpenForAllies()
        self.LoadEntry(war)
        self.expander.display = False
        hasAllyPadding = node.hasAllyPadding
        if self.myWars and hasAllyPadding:
            self.warCont.padLeft = 12
            if node.isExpandable:
                self.expander.display = True
                self.ShowOpenState(node.get('forceOpen', False) or uicore.registry.GetListGroupOpenState(self.sr.id, default=node.Get('openByDefault', False)))
        else:
            self.warCont.padLeft = 0

    def IsDirector(self):
        entityID = session.allianceid or session.corpid
        if session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector:
            return True
        return False

    def IsMyWar(self):
        entityID = session.allianceid or session.corpid
        if entityID in (self.attackerID, self.defenderID):
            return True
        return False

    def IsDefender(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.defenderID:
            return True
        return False

    def IsAttacker(self):
        entityID = session.allianceid or session.corpid
        if entityID == self.attackerID:
            return True
        return False

    def IsNegotiating(self):
        allyNegotiationsByWarID = defaultdict(list)
        myID = session.allianceid or session.corpid
        for row in sm.GetService('war').GetAllyNegotiations():
            allyNegotiationsByWarID[self.warID].append(row)
            if self.warID in allyNegotiationsByWarID:
                for neg in allyNegotiationsByWarID[self.warID]:
                    if neg.negotiationState in (warConst.WAR_NEGOTIATION_STATE_DECLINED, warConst.WAR_NEGOTIATION_STATE_RETRACTED):
                        continue
                    if neg.ownerID1 == myID and neg.warID == self.warID:
                        self.warAllyNegotiationID = neg.warNegotiationID
                        return True

        return False

    def IsRetracted(self):
        warRetracted = self.war.retracted
        if warRetracted is not None:
            return True
        return False

    def IsFinished(self):
        warFinished = self.war.timeFinished
        if warFinished:
            if blue.os.GetWallclockTime() >= warFinished:
                return True
        return False

    def SetOpenForAllies(self, open, *args):
        try:
            self.warIsOpen = open
            sm.GetService('war').SetOpenForAllies(self.war.warID, open)
            sm.ScatterEvent('OnWarEntryChanged', self.war.warID, self.war)
        except Exception:
            raise

    def WarMenu(self, menuParent):
        isMutual = self.war.mutual
        if IsFaction(self.defenderID):
            menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/FactionalWarfare_64.png', text=GetByLabel('UI/Commands/OpenFactionalWarfare'), callback=sm.GetService('cmd').OpenMilitia)
            return
        if not isMutual:
            if self.IsMyWar() and self.IsDirector() and not self.IsFinished():
                if self.IsDefender():
                    if self.warIsOpen:
                        isOpen = True
                    else:
                        isOpen = False
                    menuParent.AddCheckBox(text=GetByLabel('UI/Corporations/Wars/OpenForAllies'), checked=isOpen, callback=(self.SetOpenForAllies, not isOpen))
            if not self.IsMyWar() and self.IsDirector() and not self.IsAlly() and not self.IsFinished():
                if self.IsNegotiating():
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Attention_64.png', text=GetByLabel('UI/Corporations/Wars/ViewAssistanceOffer'), callback=self.ShowWarNegotiation)
                else:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Add_64.png', text=GetByLabel('UI/Corporations/Wars/OfferAssistance'), callback=self.OpenRequestWindow)
            numAllies = self.GetNumAllies()
            if numAllies > 0:
                menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Ally_64.png', text=GetByLabel('UI/Corporations/Wars/ViewNumAllies', num=numAllies), callback=self.OpenAllyWindow)
            else:
                menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Mercenary_Ally_64.png', text=GetByLabel('UI/Corporations/Wars/ViewAllies'))
        if self.IsMyWar() and self.IsDirector() and not self.IsFinished():
            if not self.IsRetracted():
                if self.war.mutual:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_64.png', text=GetByLabel('UI/Corporations/Wars/RetractWar'), callback=self.RetractMutualWarClick)
                elif self.warNegotiationID:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_Attention_64.png', text=GetByLabel('UI/Corporations/Wars/ViewSurrenderOffer'), callback=self.SurrenderClick)
                else:
                    menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/Surrender_64.png', text=GetByLabel('UI/Corporations/Wars/SendSurrenderOffer'), callback=self.SurrenderClick)
        menuParent.AddIconEntry(icon='res:/UI/Texture/Icons/1337_64_2.png', text=GetByLabel('UI/Corporations/Wars/OpenWarReport'), callback=self.OpenWarReport)

    def LoadEntry(self, war):
        if not IsFaction(self.attackerID) and not self.IsFinished():
            self.GetAllies()
            if self.IsOpenForAllies():
                self.buttonCont.width = 50
                self.openForAllies.display = True
            else:
                self.buttonCont.width = 30
                self.openForAllies.display = False
        if not self.war.mutual and not self.IsMyWar() and self.IsInCharge() and self.IsNegotiating() and not self.IsAlly():
            self.openForAllies.LoadIcon('res:/UI/Texture/Icons/Mercenary_Attention_64.png')
            self.openForAllies.display = True
            self.openForAllies.hint = GetByLabel('UI/Corporations/Wars/YouOfferedHelp')
        if self.IsDirector() and self.IsMyWar() and war.retracted is None:
            self.GetSurrenderStatus()
        self.warCont.LoadWarInfo(war)
        self.warCont.corpLabels.OnMouseEnter = self.OnMouseEnter
        self.warCont.attackerLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.defenderLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.corpLabels.OnMouseExit = self.OnMouseExit
        self.warCont.attackerLogo.OnMouseExit = self.OnMouseExit
        self.warCont.defenderLogo.OnMouseExit = self.OnMouseExit

    def OnWarEntryChanged(self, warID, war, *args):
        if warID == self.warID:
            self.war = war
            self.LoadEntry(self.war)

    def GetNumAllies(self):
        return self.noOfAllies

    def IsOpenForAllies(self):
        if self.war.mutual:
            return False
        return self.war.openForAllies

    def IsAlly(self):
        return sm.GetService('war').IsAllyInWar(self.warID)

    def GetSurrenderStatus(self):
        surrenders = sm.GetService('war').GetSurrenderNegotiations(self.war.warID)
        self.surrenderNegotiation.display = False
        if len(surrenders):
            self.surrenderNegotiation.display = True
            if self.IsOpenForAllies():
                self.buttonCont.width = 74
                self.surrenderNegotiation.left = 52
            else:
                self.buttonCont.width = 50
                self.surrenderNegotiation.left = 27
            for surrender in surrenders:
                self.warNegotiationID = surrender.warNegotiationID

    def GetHeight(self, *args):
        node, width = args
        node.height = 40
        return node.height

    def ButtonMouseEnter(self, btn, *args):
        if not btn.enabled:
            return
        uicore.animations.FadeIn(btn.mouseEnterBG, duration=0.2)
        self.OnMouseEnter()

    def ButtonMouseExit(self, btn, *args):
        uicore.animations.FadeOut(btn.mouseEnterBG, duration=0.2)
        self.OnMouseExit()

    def AllyClick(self, *args):
        if self.war.retracted is not None:
            self.OpenAllyWindow()
        elif self.IsNegotiating() and self.IsDirector():
            self.ShowWarNegotiation()
        elif not self.IsDirector() or self.IsMyWar() or self.IsAlly():
            self.OpenAllyWindow()
        else:
            self.OpenRequestWindow()

    def GetAllies(self):
        try:
            allies = self.war.allies
            try:
                allies = allies.values()
            except AttributeError:
                pass

            self.noOfAllies = len([ ally for ally in allies if blue.os.GetWallclockTime() < ally.timeFinished ])
        except AttributeError:
            self.noOfAllies = self.war.noOfAllies

        return self.noOfAllies

    def OpenAllyWindow(self):
        AllyWnd.CloseIfOpen()
        AllyWnd.Open(war=self.war, allies=self.allies)

    def OpenRequestWindow(self):
        WarAssistanceOfferWnd.Open(isRequest=True, warID=self.warID, war=self.war, attackerID=self.attackerID, defenderID=self.defenderID, requesterID=session.allianceid or session.corpid, iskValue=getattr(self.war, 'reward', 0))

    def ShowWarNegotiation(self):
        WarAssistanceOfferWnd.Open(isRequest=False, warNegotiationID=self.warAllyNegotiationID, requesterID=session.allianceid or session.corpid)

    def SurrenderClick(self, *args):
        if self.warNegotiationID:
            WarSurrenderWnd.CloseIfOpen()
            WarSurrenderWnd.Open(warNegotiationID=self.warNegotiationID, isRequest=False)
        else:
            WarSurrenderWnd.CloseIfOpen()
            requesterID = session.corpid if session.allianceid is None else session.allianceid
            WarSurrenderWnd.Open(war=self.war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)

    def RetractMutualWarClick(self, *args):
        headerLabel = GetByLabel('UI/Corporations/Wars/RetractWar')
        bodyLabel = GetByLabel('UI/Corporations/Wars/RetractWarSure')
        ret = eve.Message('CustomQuestion', {'header': headerLabel,
         'question': bodyLabel}, uiconst.YESNO)
        if ret != uiconst.ID_YES:
            return
        warID = self.warID
        sm.GetService('war').RetractMutualWar(warID)

    def OpenWarReport(self):
        OpenWarReport(self.warID)

    def OnDblClick(self, *args):
        if IsFaction(self.attackerID):
            sm.GetService('cmd').OpenMilitia()
        else:
            self.OpenWarReport()

    def GetMenu(self):
        war = self.war
        return GetWarMenu(war)

    def GetDragData(self, *args):
        if IsFaction(self.attackerID):
            return []
        nodes = [self.sr.node]
        return nodes

    def IsInCharge(self):
        if session.allianceid is not None:
            return session.corpid == sm.GetService('alliance').GetAlliance().executorCorpID and session.corprole & appConst.corpRoleDirector == appConst.corpRoleDirector
        else:
            return sm.GetService('corp').UserIsActiveCEO()

    def OnClick(self, *args, **kwargs):
        self.Toggle()

    def Toggle(self, *args):
        node = self.sr.node
        if not node or node.get('toggling', 0) or not node.get('isExpandable', False):
            return
        node.toggling = 1
        w = node.panel
        if not w:
            node.toggling = 0
            return
        node.open = not node.open
        if node.open:
            PlaySound(uiconst.SOUND_EXPAND)
        else:
            PlaySound(uiconst.SOUND_COLLAPSE)
        self.ShowOpenState(node.open)
        uicore.registry.SetListGroupOpenState(node.id, node.open)
        node.scroll.PrepareSubContent(node)
        node.toggling = 0

    def ShowOpenState(self, open_):
        if self.expander:
            if open_:
                self.expander.LoadIcon('res:/UI/Texture/Icons/38_16_229.png')
            else:
                self.expander.LoadIcon('res:/UI/Texture/Icons/38_16_228.png')


class WarEntrySimple(SE_BaseClassCore):
    __guid__ = 'listentry.WarEntry'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.showAllyButton = False
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        warCont = Container(name='wars', parent=self, align=uiconst.TOALL, clipChildren=True, padRight=4)
        self.warCont = WarContainer(parent=warCont, top=2)

    def Load(self, node):
        self.sr.node = node
        self.war = war = node.war
        self.warID = war.warID
        self.attackerID = war.declaredByID
        self.defenderID = war.againstID
        self.LoadEntry(war)

    def LoadEntry(self, war):
        warKeyVal = KeyVal(war)
        warKeyVal.retracted = None
        self.warCont.LoadWarInfo(warKeyVal)
        self.warCont.corpLabels.OnMouseEnter = self.OnMouseEnter
        self.warCont.attackerLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.defenderLogo.OnMouseEnter = self.OnMouseEnter
        self.warCont.corpLabels.OnMouseExit = self.OnMouseExit
        self.warCont.attackerLogo.OnMouseExit = self.OnMouseExit
        self.warCont.defenderLogo.OnMouseExit = self.OnMouseExit

    def GetHeight(self, *args):
        node, width = args
        node.height = 40
        return node.height

    def OnDblClick(self, *args):
        self.OpenWarReport()

    def OpenWarReport(self):
        from eve.client.script.ui.shared.neocom.corporation.war.warReport import WarReportWnd
        wnd = WarReportWnd.GetIfOpen()
        if wnd:
            wnd.LoadInfo(warID=self.warID)
            wnd.Maximize()
        else:
            WarReportWnd.Open(warID=self.warID)

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def GetMenu(self):
        war = self.war
        menu = [(MenuLabel('UI/Corporations/Wars/OpenWarReport'), OpenWarReport, (war.warID,))]
        menu += GetWarMenu(war)
        return menu


def GetWarMenu(war):
    menu = []
    subMenu = []
    hasGMLRole = session.role & ROLE_GML == ROLE_GML
    if hasGMLRole:
        myWarEntityID = session.allianceid or session.corpid
        subMenu.append(('Copy : %s' % war.warID, blue.pyos.SetClipboardData, (str(war.warID),)))
        if myWarEntityID in (war.againstID, war.declaredByID):
            subMenu.extend([('Set Declare Time', GMSetDeclareTime, (war,)), ('Set Finish Time', GMSetFinishTime, (war,)), ('Force Finish War', GMForceFinishWar, (war,))])
        elif hasattr(war, 'allies') and myWarEntityID in war.allies:
            subMenu.append(('Start Defending', GMActivateDefender, (war.warID, myWarEntityID)))
        else:
            subMenu.append(('Join Defender', sm.GetService('war').GMJoinDefender, (war.warID, war.declaredByID)))
    if subMenu:
        menu.append(['GM Tools', subMenu])
    return menu


def OpenWarReport(warID):
    from eve.client.script.ui.shared.neocom.corporation.war.warReport import WarReportWnd
    wnd = WarReportWnd.GetIfOpen()
    if wnd:
        wnd.LoadInfo(warID=warID)
        wnd.Maximize()
    else:
        WarReportWnd.Open(warID=warID)


def GMSetDeclareTime(war):
    ret = NamePopup(caption='Set Declare Time', label='Type in Declare Time', setvalue=FmtDate(war.timeDeclared))
    if ret is None:
        return
    newTime = ParseDateTime(ret)
    sm.GetService('war').GMSetDeclareTime(war.warID, newTime)


def GMSetFinishTime(war):
    ret = NamePopup(caption='Set Finished Time', label='Type in Finished Time', setvalue=FmtDate(war.timeFinished))
    if ret is None:
        return
    newTime = ParseDateTime(ret)
    sm.GetService('war').GMSetWarFinishTime(war.warID, newTime)


def GMForceFinishWar(war):
    sm.GetService('war').GMSetWarFinishTime(war.warID, blue.os.GetTime() - appConst.DAY)


def GMActivateDefender(warID, allyID):
    sm.GetService('war').GMActivateDefender(warID, allyID)

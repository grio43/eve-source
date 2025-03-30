#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warKillEntry.py
import evetypes
from carbon.common.script.util.format import FmtDate
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from crimewatch.util import GetKillReportHashValue
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.killReportUtil import OpenKillReport, CleanKillMail
from eve.client.script.ui.shared.neocom.corporation.war.warReportConst import ATTACKER_COLOR, DEFENDER_COLOR
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.script.util.esiUtils import CopyESIKillmailUrlToClipboard
from eve.common.script.util.eveCommonUtils import CombatLog_CopyText
from localization import GetByLabel
from menu import MenuLabel
import blue

class WarKillEntry(SE_BaseClassCore):
    __guid__ = 'listentry.WarKillEntry'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=40)
        self.shipCont = Container(parent=iconCont, align=uiconst.CENTER, width=32, height=32)
        self.shipFrame = Frame(parent=self.shipCont)
        self.shipIcon = Icon(parent=self.shipCont, align=uiconst.TOALL, size=256, ignoreSize=True)
        self.shipIcon.cursor = uiconst.UICURSOR_MAGNIFIER
        self.shipIcon.OnClick = (self.OnPreviewClick, self.shipIcon)
        self.shipIcon.OnMouseEnter = self.OnControlEnter
        self.shipIcon.OnMouseExit = self.OnControlExit
        self.techIcon = Sprite(name='techIcon', parent=self.shipCont, align=uiconst.RELATIVE, width=16, height=16, idx=0, left=1, top=1)
        self.techIcon.OnMouseEnter = self.OnControlEnter
        self.techIcon.OnMouseExit = self.OnControlExit
        self.timeCont = Container(parent=self, align=uiconst.TORIGHT, width=35, padRight=6)
        self.textCont = Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self.victimLabel = EveLabelMedium(text='', parent=self.textCont, left=5, top=3, state=uiconst.UI_NORMAL, maxLines=1)
        self.killerLabel = EveLabelMedium(text='', parent=self.textCont, left=5, top=20, state=uiconst.UI_NORMAL, maxLines=1)
        self.dateLabel = EveLabelMedium(text='', parent=self.timeCont, align=uiconst.TOPRIGHT, top=20)
        self.victimLabel.OnMouseEnter = self.OnControlEnter
        self.victimLabel.OnMouseExit = self.OnControlExit
        self.killerLabel.OnMouseEnter = self.OnControlEnter
        self.killerLabel.OnMouseExit = self.OnControlExit

    def Load(self, node):
        self.sr.node = node
        self.killID = node.killID
        self.killTime = node.killTime
        self.finalCharacterID = node.finalCharacterID
        self.finalCorporationID = node.finalCorporationID
        self.finalAllianceID = node.finalAllianceID
        self.finalShipTypeID = node.finalShipTypeID
        self.victimCharacterID = node.victimCharacterID
        self.victimCorporationID = node.victimCorporationID
        self.victimAllianceID = node.victimAllianceID
        self.victimShipTypeID = node.victimShipTypeID
        self.attackerKill = node.attackerKill
        self.DisplayInfo()

    def DisplayInfo(self):
        GetTechLevelIcon(self.techIcon, 0, self.victimShipTypeID)
        self.shipIcon.LoadIconByTypeID(typeID=self.victimShipTypeID)
        self.shipIcon.typeID = self.victimShipTypeID
        self.shipIcon.hint = evetypes.GetName(self.victimShipTypeID)
        if self.attackerKill:
            color = ATTACKER_COLOR
        else:
            color = DEFENDER_COLOR
        self.shipFrame.color = color
        try:
            victimName = cfg.eveowners.Get(self.victimCharacterID).name
            victimInfo = ('showinfo', const.typeCharacter, self.victimCharacterID)
        except:
            victimName = evetypes.GetName(self.victimShipTypeID)
            victimInfo = ('showinfo', self.victimShipTypeID)

        victimCorp = cfg.eveowners.Get(self.victimCorporationID).name
        victimCorpInfo = ('showinfo', const.typeCorporation, self.victimCorporationID)
        if self.victimAllianceID:
            victimAlliance = cfg.eveowners.Get(self.victimAllianceID).name
            victimAllianceInfo = ('showinfo', const.typeAlliance, self.victimAllianceID)
            victimLabel = GetByLabel('UI/Corporations/Wars/KillVictimInAlliance', victimName=victimName, victimInfo=victimInfo, victimCorp=victimCorp, victimCorpInfo=victimCorpInfo, victimAlliance=victimAlliance, victimAllianceInfo=victimAllianceInfo)
        else:
            victimLabel = GetByLabel('UI/Corporations/Wars/KillVictim', victimName=victimName, victimInfo=victimInfo, victimCorp=victimCorp, victimCorpInfo=victimCorpInfo)
        self.victimLabel.text = victimLabel
        try:
            killerName = cfg.eveowners.Get(self.finalCharacterID).name
            killerInfo = ('showinfo', const.typeCharacter, self.finalCharacterID)
        except StandardError:
            killerName = evetypes.GetName(self.finalShipTypeID)
            killerInfo = ('showinfo', self.finalShipTypeID)

        killerCorp = cfg.eveowners.Get(self.finalCorporationID).name
        killerCorpInfo = ('showinfo', const.typeCorporation, self.finalCorporationID)
        if self.finalAllianceID:
            killerAlliance = cfg.eveowners.Get(self.finalAllianceID).name
            killerAllianceInfo = ('showinfo', const.typeAlliance, self.finalAllianceID)
            killerLabel = GetByLabel('UI/Corporations/Wars/KillKillerInAlliance', killerName=killerName, killerInfo=killerInfo, killerCorp=killerCorp, killerCorpInfo=killerCorpInfo, killerAlliance=killerAlliance, killerAllianceInfo=killerAllianceInfo)
        else:
            killerLabel = GetByLabel('UI/Corporations/Wars/KillKiller', killerName=killerName, killerInfo=killerInfo, killerCorp=killerCorp, killerCorpInfo=killerCorpInfo)
        self.killerLabel.text = killerLabel
        self.dateLabel.text = FmtDate(self.killTime, 'ns')

    def GetHeight(self, *args):
        node, width = args
        node.height = 41
        return node.height

    def OnPreviewClick(self, obj, *args):
        sm.GetService('preview').PreviewType(getattr(obj, 'typeID'))

    def OnControlEnter(self, *args):
        self.ShowHilite()

    def OnControlExit(self, *args):
        self.HideHilite()

    def GetFullKillReport(self):
        hashValue = GetKillReportHashValue(self.sr.node.mail)
        return sm.RemoteSvc('warStatisticMgr').GetKillMail(self.killID, hashValue)

    def OnDblClick(self, *args):
        kill = self.GetFullKillReport()
        if kill is not None:
            OpenKillReport(kill)

    def GetCombatText(self, *args):
        kill = self.GetFullKillReport()
        ret = CombatLog_CopyText(kill)
        blue.pyos.SetClipboardData(CleanKillMail(ret))

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def GetMenu(self):
        m = []
        if self.sr.node.GetMenu:
            m = self.sr.node.GetMenu()
        return m + [(MenuLabel('UI/Commands/ShowInfo'), self.RedirectToInfo, (1,)),
         None,
         (MenuLabel('UI/Control/Entries/CopyKillInformation'), self.GetCombatText, (1,)),
         (MenuLabel('UI/Control/Entries/CopyExternalKillLink'), CopyESIKillmailUrlToClipboard, (self.sr.node.mail,))]

    def RedirectToInfo(self, *args):
        kill = self.sr.node.mail
        infoSvc = sm.GetService('info')
        if kill.victimCharacterID == session.charid:
            if kill.finalCharacterID is None:
                baddieGuyID = kill.finalCorporationID
            else:
                baddieGuyID = kill.finalCharacterID
            char = cfg.eveowners.Get(baddieGuyID)
            infoSvc.ShowInfo(char.typeID, baddieGuyID)
        elif kill.victimCharacterID is not None:
            char = cfg.eveowners.Get(kill.victimCharacterID)
            infoSvc.ShowInfo(char.typeID, kill.victimCharacterID)
        elif kill.victimCorporationID is not None:
            sm.StartService('info').ShowInfo(const.typeCorporation, kill.victimCorporationID)
        elif kill.allianceID is not None:
            infoSvc.ShowInfo(const.typeAlliance, kill.victimAllianceID)

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\kill_mail.py
import blue
import evetypes
import localization
from carbon.common.script.util.format import FormatTimeAgo
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared import killReportUtil
from eve.client.script.ui.util import uix
from eve.common.lib import appConst as const
from eve.common.script.util.esiUtils import CopyESIKillmailUrlToClipboard
from eve.common.script.util.eveCommonUtils import CombatLog_CopyText
from menu import MenuLabel

class KillMail(SE_BaseClassCore):
    __guid__ = 'listentry.KillMail'
    __params__ = ['mail']
    __nonpersistvars__ = ['selection', 'id']
    ACTION_ICON_SIZE = 16
    isDragObject = True

    def Startup(self, *args):
        sub = Container(name='sub', parent=self, pos=(0, 0, 0, 0))
        self.sr.leftbox = Container(parent=sub, align=uiconst.TOLEFT, width=42, height=42, padding=(0, 2, 4, 2))
        self.sr.middlebox = Container(parent=sub, align=uiconst.TOALL, padding=(0, 2, 0, 0))
        self.sr.techIcon = Sprite(name='techIcon', parent=self.sr.leftbox, left=1, width=16, height=16, idx=0)
        self.sr.icon = Icon(parent=self.sr.leftbox, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        Frame(parent=self.sr.leftbox, color=(0.4, 0.4, 0.4, 0.5))

    def Load(self, node):
        self.sr.node = node
        self.FillTextAndIcons()

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(KillMail, self).UpdateAlignment(*args, **kwargs)
        self.UpdateLabelRightFade()
        return alignment

    def UpdateLabelRightFade(self):
        availableWidth = self.sr.middlebox.displayWidth - const.defaultPadding - self.ACTION_ICON_SIZE
        for label in self.sr.middlebox.children:
            label.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)

    def FillTextAndIcons(self):
        kill = self.sr.node.mail
        if self.height == 64:
            expanded = 1
        else:
            expanded = 0
        topLine = 14
        if eve.session.charid == kill.victimCharacterID or eve.session.corpid == kill.victimCorporationID:
            text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndTime', shipTypeID=kill.victimShipTypeID, killTime=max(blue.os.GetWallclockTime() - kill.killTime, 0L))
            self.AddOrSetTextLine(text, configName='killMailsShipAndTimeLabel')
            text = ''
            if kill.victimShipTypeID is not None:
                self.sr.icon.LoadIconByTypeID(kill.victimShipTypeID, ignoreSize=True)
                techSprite = uix.GetTechLevelIcon(self.sr.techIcon, 1, kill.victimShipTypeID)
            text = self._GetCorpAndOrAllianceText(kill.finalCorporationID, kill.finalAllianceID)
            self.AddOrSetTextLine(text, configName='killerCorpOrAllianceLabel', top=topLine)
            text = ''
            if kill.finalShipTypeID is not None and kill.finalWeaponTypeID is not None:
                text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndWeapon', shipTypeID=kill.finalShipTypeID, weaponTypeID=kill.finalWeaponTypeID)
            elif kill.finalShipTypeID is not None:
                text = evetypes.GetName(kill.finalShipTypeID)
            elif kill.finalWeaponTypeID is not None:
                text = evetypes.GetName(kill.finalWeaponTypeID)
            self.AddOrSetTextLine(text, configName='killerShipOrWeaponLabel', top=topLine * 2)
        elif eve.session.charid == kill.finalCharacterID or eve.session.corpid == kill.finalCorporationID:
            if kill.victimCharacterID is not None or kill.victimCorporationID is not None:
                if kill.victimCharacterID is not None:
                    text = localization.GetByLabel('UI/Control/Entries/KillMailCharacterAndTime', characterID=kill.victimCharacterID, killTime=max(blue.os.GetWallclockTime() - kill.killTime, 0L))
                else:
                    text = FormatTimeAgo(kill.killTime)
                self.AddOrSetTextLine(text, configName='victimNameOrTimeLabel')
                text = ''
                text = self._GetCorpAndOrAllianceText(kill.victimCorporationID, kill.victimAllianceID)
                self.AddOrSetTextLine(text, configName='victimCorpOrAllianceLabel', top=topLine)
                text = ''
                if kill.victimShipTypeID and kill.solarSystemID:
                    mapSvc = sm.GetService('map')
                    regionID = mapSvc.GetParent(mapSvc.GetParent(kill.solarSystemID))
                    text = localization.GetByLabel('UI/Control/Entries/KillMailShipAndSolarSystem', shipTypeID=kill.victimShipTypeID, solarSystemID=kill.solarSystemID, regionID=regionID, security=sm.GetService('map').GetSecurityStatus(kill.solarSystemID))
                elif kill.victimShipTypeID:
                    text = evetypes.GetName(kill.victimShipTypeID)
                elif kill.solarSystemID:
                    mapSvc = sm.GetService('map')
                    regionID = mapSvc.GetParent(mapSvc.GetParent(kill.solarSystemID))
                    text = localization.GetByLabel('UI/Control/Entries/KillMailSolarSystem', solarSystemID=kill.solarSystemID, regionID=regionID, security=sm.GetService('map').GetSecurityStatus(kill.solarSystemID))
                self.AddOrSetTextLine(text, configName='shipNameAndSolarSystemLabel', top=topLine * 2)
            else:
                self.AddOrSetTextLine(localization.GetByLabel('UI/Control/Entries/KillMailUnknown'), configName='unknownLabel')
            if kill.victimShipTypeID is not None:
                self.sr.icon.LoadIconByTypeID(kill.victimShipTypeID, ignoreSize=True)
                techSprite = uix.GetTechLevelIcon(self.sr.techIcon, 1, kill.victimShipTypeID)
        else:
            text = localization.GetByLabel('UI/Control/Entries/KillMailError')
            self.sr.icon.LoadIcon('res:/ui/Texture/WindowIcons/personalstandings.png', ignoreSize=True)
            self.sr.techIcon.display = False
            self.sr.copyicon.state = uiconst.UI_HIDDEN
            self.sr.linkicon.state = uiconst.UI_HIDDEN
            self.GetMenu = None

    def _GetCorpAndOrAllianceText(self, corpID, allianceID):
        corpName = None
        corpTicker = ''
        allianceName = None
        allianceTicker = ''
        text = None
        if corpID is not None:
            corpName = cfg.eveowners.Get(corpID).name
            try:
                corpTicker = cfg.corptickernames.Get(corpID).tickerName
            except KeyError as e:
                pass

        if allianceID is not None:
            allianceName = cfg.eveowners.Get(allianceID).name
            try:
                allianceTicker = cfg.allianceshortnames.Get(allianceID).shortName
            except KeyError as e:
                pass

        if corpName and allianceName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpAndAlliance', corpName=corpName, corpTicker=corpTicker, allianceName=allianceName, allianceTicker=allianceTicker)
        elif corpName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpOrAlliance', name=corpName, ticker=corpTicker)
        elif allianceName:
            text = localization.GetByLabel('UI/Control/Entries/KillMailCorpOrAlliance', name=allianceName, ticker=allianceTicker)
        return text

    def AddOrSetTextLine(self, text, configName = '', top = 0):
        if text:
            label = getattr(self, configName, None)
            if label is not None:
                label.text = text
            else:
                label = EveLabelSmall(text=text, parent=self.sr.middlebox, align=uiconst.TOPLEFT, top=top)
                if configName:
                    setattr(self, configName, label)

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
        if kill.victimCharacterID == session.charid:
            baddieGuyID = None
            if kill.finalCharacterID is None:
                baddieGuyID = kill.finalCorporationID
            else:
                baddieGuyID = kill.finalCharacterID
            char = cfg.eveowners.Get(baddieGuyID)
            sm.StartService('info').ShowInfo(char.typeID, baddieGuyID)
        elif kill.victimCharacterID is not None:
            char = cfg.eveowners.Get(kill.victimCharacterID)
            sm.StartService('info').ShowInfo(char.typeID, kill.victimCharacterID)
        elif kill.victimCorporationID is not None:
            sm.StartService('info').ShowInfo(const.typeCorporation, kill.victimCorporationID)
        elif kill.allianceID is not None:
            sm.StartService('info').ShowInfo(const.typeAlliance, kill.victimAllianceID)

    def GetCombatText(self, isCopy = 0, *args):
        mail = self.sr.node.mail
        ret = CombatLog_CopyText(mail)
        if isCopy:
            blue.pyos.SetClipboardData(killReportUtil.CleanKillMail(ret))
        else:
            return ret

    def CopyCombatText(self):
        text = self.GetCombatText()
        blue.pyos.SetClipboardData(killReportUtil.CleanKillMail(text))

    def _OnClose(self):
        self.timer = None
        SE_BaseClassCore.Close(self)

    def GetHeight(self, *args):
        node, width = args
        node.height = 46
        return node.height

    def OnDblClick(self, *args):
        mail = self.sr.node.mail
        kill = mail
        if kill is not None:
            from eve.client.script.ui.shared.killReportUtil import OpenKillReport
            OpenKillReport(kill)

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes


class KillMailCondensed(Generic):
    __guid__ = 'listentry.KillMailCondensed'
    isDragObject = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

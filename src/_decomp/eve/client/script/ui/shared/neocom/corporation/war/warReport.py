#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warReport.py
import math
from collections import defaultdict
import blue
import carbonui.const as uiconst
import uthread
from appConst import corpRoleDirector
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveLabelMedium, EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.shared.neocom.corporation.war.warKillEntry import WarKillEntry
from eve.client.script.ui.shared.neocom.corporation.war.warReportConst import ATTACKER_COLOR, DEFENDER_COLOR
from eve.client.script.ui.shared.neocom.corporation.war.warReportController import WarReportController
from eve.client.script.ui.shared.neocom.corporation.war.warReportKillGroups import WarReportKillsByGroupParent
from eve.client.script.ui.shared.neocom.corporation.war.warWindows import WarSurrenderWnd
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.sys.idCheckers import IsCorporation
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
from utillib import KeyVal
WAR_HQ_PADDING = 50
KILLS_PARENT_FULL_HEIGHT = 206

class WarReportWnd(Window):
    __guid__ = 'form.WarReportWnd'
    __notifyevents__ = []
    default_windowID = 'WarReportWnd'
    default_width = 600
    default_height = 640
    default_minSize = (default_width, default_height)
    default_iconNum = 'res:/UI/Texture/WindowIcons/warreport.png'
    default_captionLabelPath = 'UI/Corporations/Wars/WarReport'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.warReportController = WarReportController(attributes.Get('warID', None))
        self.graphAndKillsLoaded = False
        self.loading = False
        self.maxKills = 0
        self.killsByShipGroup = defaultdict(lambda : KeyVal(attackerKills=0, defenderKills=0, attackerKillsIsk=0, defenderKillsIsk=0))
        self.ConstructLayout()

    def GetWarStatisticMoniker(self, warID):
        self.warStatisticMoniker = eveMoniker.GetWarStatistic(warID)
        self.warStatisticMoniker.Bind()
        return self.warStatisticMoniker

    def ConstructLayout(self):
        topCont = ContainerAutoSize(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, clipChildren=True, padding=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.loadingCont = Container(name='loadingCont', parent=self.sr.main, align=uiconst.TOALL)
        self.loadingText = EveCaptionMedium(text='', parent=self.loadingCont, align=uiconst.CENTER)
        self.loadingCont.display = True
        self.historyCont = Container(name='historyCont', parent=self.sr.main, align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding * 2,
         const.defaultPadding,
         const.defaultPadding))
        self.historyCont.display = False
        self.ConstructWarInfoUI(topCont)
        showGraph = settings.user.ui.Get('killShowGraph', 0)
        self.killsByGroupParent = WarReportKillsByGroupParent(name='killsByGroupParent', parent=self.historyCont, loadFunc=self.LoadKillsScroll, height=KILLS_PARENT_FULL_HEIGHT if showGraph else 0)
        killsFilterCont = ContainerAutoSize(name='killsFilterCont', parent=self.historyCont, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        self.killsScroll = Scroll(name='killsScroll', parent=self.historyCont)
        killOptions = [(GetByLabel('UI/Corporations/Wars/ShowAllKills'), None), (GetByLabel('UI/Corporations/Wars/ShowAggressorKills'), 'attacker'), (GetByLabel('UI/Corporations/Wars/ShowDefenderKills'), 'defender')]
        comboSetting = settings.user.ui.Get('killComboValue', 0)
        self.killsFilterCombo = Combo(name='killsFilterCombo', parent=killsFilterCont, options=killOptions, adjustWidth=True, select=comboSetting, callback=self.OnKillComboChange)
        showGraphPadLeft = self.killsFilterCombo.left + self.killsFilterCombo.width + 8
        self.showGraph = Checkbox(text=GetByLabel('UI/Corporations/Wars/ShowGraph'), parent=killsFilterCont, left=showGraphPadLeft, checked=showGraph, callback=self.ChangeGraphDisplay, align=uiconst.CENTERLEFT)
        EveLabelSmall(text=GetByLabel('UI/Corporations/CorporationWindow/Wars/DelayedKillboardDetails'), parent=killsFilterCont, align=uiconst.CENTERRIGHT)
        warID = self.warReportController.GetWarID()
        self.LoadInfo(warID, forceLoad=True)

    def ConstructWarInfoUI(self, topCont):
        textCont = ContainerAutoSize(name='textCont', parent=topCont, align=uiconst.TOTOP)
        warDateLabelCont = ContainerAutoSize(name='warDateLabelCont', parent=textCont, align=uiconst.TOTOP, padTop=4, padBottom=6)
        self.warDateLabel = EveLabelMedium(name='warDateLabel', text='', parent=warDateLabelCont, align=uiconst.TOPRIGHT, left=10)
        self.mutualLabelCont = ContainerAutoSize(name='mutualLabelCont', parent=textCont, align=uiconst.TOTOP, padTop=4, padBottom=6)
        self.mutualWarLabel = EveLabelMedium(name='mutualWarLabel', text=GetByLabel('UI/Corporations/Wars/MutualWar'), parent=self.mutualLabelCont, align=uiconst.CENTER)
        self.mutualLabelCont.display = False
        warCont = Container(name='warCont', parent=topCont, align=uiconst.TOTOP, height=70)
        warHQCont = ContainerAutoSize(name='warHQCont', parent=topCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.helpIcon = MoreInfoIcon(parent=warHQCont, align=uiconst.CENTER, hint=GetByLabel('UI/Corporations/Wars/WarHQExtraInfoWarReport'))
        self.arrowLeft = Sprite(parent=warHQCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/war/leftArrow.png', pos=(0, 0, 20, 20), state=uiconst.UI_DISABLED)
        self.arrowLeft.SetRGBA(*ATTACKER_COLOR)
        self.arrowRight = Sprite(parent=warHQCont, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/war/rightArrow.png', pos=(0, 0, 20, 20), state=uiconst.UI_DISABLED)
        self.arrowRight.SetRGBA(*ATTACKER_COLOR)
        self.warHQLabel = EveLabelMedium(name='warHQLabel', text='  ', parent=warHQCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, top=2, padLeft=WAR_HQ_PADDING, padRight=WAR_HQ_PADDING)
        self.warHQLabel.OnSizeChanged = self.OnWarHqLabelChanged
        self.buttonCont = Container(name='buttonCont', parent=topCont, align=uiconst.TOTOP, height=33)
        self.surrenderBtn = Button(name='surrenderBtn', parent=self.buttonCont, align=uiconst.CENTERLEFT, left=4, iconSize=16, texturePath='res:/UI/Texture/Icons/Surrender_64.png', func=self.OpenSurrenderWnd, label=GetByLabel('UI/Corporations/Wars/OfferSurrenderBtn'))
        self.surrenderBtn.display = False
        self.allyBtn = Button(name='allyBtn', parent=self.buttonCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_HIDDEN, left=4, iconSize=16, texturePath='res:/UI/Texture/Icons/Mercenary_64.png', func=self.OpenAllyWnd, label=GetByLabel('UI/Corporations/Wars/ViewAlliesBtn'))
        attackerCont = Container(name='attackerCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.45)
        attackerLogoCont = Container(name='attackerLogoCont', parent=attackerCont, align=uiconst.TORIGHT, width=64)
        self.attackerLogoDetailed = Container(name='attackerLogoDetailed', parent=attackerLogoCont, align=uiconst.TOPRIGHT, width=64, height=64)
        attackerTextCont = Container(name='attackerTextCont', parent=attackerCont, align=uiconst.TOALL, padding=(4, 0, 8, 4))
        self.attackerNameLabel = EveLabelLarge(text='', parent=attackerTextCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, maxLines=1)
        attackerText = '<right>%s</right>' % GetByLabel('UI/Corporations/Wars/WarAttacker')
        self.attackerLabel = EveLabelMedium(text=attackerText, parent=attackerTextCont, align=uiconst.TOTOP)
        self.attackerLabel.SetRGBA(*ATTACKER_COLOR)
        self.attackerISKLostLabel = EveLabelMedium(text='', parent=attackerTextCont, align=uiconst.TOTOP)
        self.attackerShipsLostLabel = EveLabelMedium(text='', parent=attackerTextCont, align=uiconst.TOTOP)
        centerCont = Container(name='centerCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.1)
        self.swordsSprite = Sprite(name='swordsSprite', parent=centerCont, align=uiconst.CENTER, pos=(0, 0, 32, 32), state=uiconst.UI_NORMAL, opacity=0.3, texturePath='res:/UI/Texture/WindowIcons/wars.png', hint=GetByLabel('UI/Corporations/Wars/Vs'))
        self.swordsSprite.GetDragData = self.GetSwordDragData
        defenderCont = Container(name='defenderCont', parent=warCont, align=uiconst.TOLEFT_PROP, width=0.45)
        defenderLogoCont = Container(name='defenderLogoCont', parent=defenderCont, align=uiconst.TOLEFT, width=64)
        self.defenderLogoDetailed = Container(name='defenderLogoDetailed', parent=defenderLogoCont, align=uiconst.TOPLEFT, width=64, height=64)
        defenderTextCont = Container(name='defenderTextCont', parent=defenderCont, align=uiconst.TOALL, padding=(8, 0, 4, 4))
        self.defenderNameLabel = EveLabelLarge(text='', parent=defenderTextCont, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, maxLines=1)
        defenderText = GetByLabel('UI/Corporations/Wars/WarDefender')
        self.defenderLabel = EveLabelMedium(text=defenderText, parent=defenderTextCont, align=uiconst.TOTOP)
        self.defenderLabel.SetRGBA(*DEFENDER_COLOR)
        self.defenderISKKilledLabel = EveLabelMedium(text='', parent=defenderTextCont, align=uiconst.TOTOP, height=16)
        self.defenderShipsKilledLabel = EveLabelMedium(text='', parent=defenderTextCont, align=uiconst.TOTOP)

    def SetAllyBtnIcon(self):
        allies = self.warReportController.GetAllies()
        if len(allies):
            texturePath = 'res:/UI/Texture/Icons/Mercenary_Ally_64.png'
        elif self.warReportController.IsWarOpenForAllies():
            texturePath = 'res:/UI/Texture/Icons/Mercenary_Add_64.png'
        else:
            texturePath = 'res:/UI/Texture/Icons/Mercenary_64.png'
        self.allyBtn.icon = texturePath

    def GetSwordDragData(self, *args):
        fakeNode = KeyVal(__guid__='listentry.WarEntry', war=self.warReportController.GetWar())
        return [fakeNode]

    def _ShowInvContLoadingWheel(self):
        blue.synchro.SleepWallclock(500)
        wheel = LoadingWheel(parent=self.loadingCont, align=uiconst.CENTER)
        while self.loading:
            blue.synchro.Yield()

        wheel.Close()

    def ShowLoading(self):
        self.loading = True
        uthread.new(self._ShowInvContLoadingWheel)
        self.loadingCont.display = True
        self.historyCont.display = False

    def HideLoading(self):
        self.loading = False
        self.loadingCont.display = False
        self.historyCont.display = True

    def LoadInfo(self, warID, forceLoad = False):
        uthread.new(self.LoadInfo_thread, warID, forceLoad=forceLoad)

    def LoadInfo_thread(self, warID, forceLoad = False):
        reloadingTheSameWar = warID == self.warReportController.GetWarID()
        if not forceLoad and reloadingTheSameWar and self.graphAndKillsLoaded:
            return
        self.warStatisticMoniker = self.GetWarStatisticMoniker(warID)
        war, shipsKilled, iskKilled, allies = self.warStatisticMoniker.GetBaseInfo()
        if not reloadingTheSameWar:
            self.warReportController = WarReportController(war.warID)
        self.warReportController.SetWar(war)
        self.warReportController.SetAllies(allies)
        attackerID = self.warReportController.GetAttackerID()
        defenderID = self.warReportController.GetDefenderID()
        if self.warReportController.IsWarMutual():
            self.mutualLabelCont.display = True
        else:
            self.mutualLabelCont.display = False
        if not len(allies):
            self.allyBtn.Disable()
            self.allyBtn.hint = GetByLabel('UI/Corporations/Wars/DefenderHasNoAllies')
        else:
            self.allyBtn.Enable()
            self.allyBtn.hint = GetByLabel('UI/Corporations/Wars/DefenderHasNumAllies', num=len(allies))
        self.SetAllyBtnIcon()
        self.attackerLogoDetailed.Flush()
        self.defenderLogoDetailed.Flush()
        self.killsByShipGroup.clear()
        self.graphAndKillsLoaded = False
        self.surrenderBtn.display = False
        self.allyBtn.display = False
        if self.warReportController.IsWarMutual():
            self.buttonCont.display = False
        else:
            self.buttonCont.display = True
            self.allyBtn.display = True
            requesterID = session.allianceid or session.corpid
            requesterIsInThisWar = requesterID in (attackerID, defenderID)
            warHasBeenRetracted = war.retracted is not None
            if requesterIsInThisWar and not warHasBeenRetracted and corpRoleDirector & session.corprole == corpRoleDirector:
                self.surrenderBtn.display = True
                self.surrenderBtn.hint = GetByLabel('UI/Corporations/Wars/OffereToSurrender')
                surrenders = sm.GetService('war').GetSurrenderNegotiations(warID)
                for surrender in surrenders:
                    iskValue = surrender.iskValue
                    self.warReportController.SetWarNegotiationID(surrender.warNegotiationID)
                    corpName = cfg.eveowners.Get(surrender.ownerID1).name
                    self.surrenderBtn.hint = GetByLabel('UI/Corporations/Wars/OfferedToSurrender', amount=iskValue, corpName=corpName)

        shipsKilledByID = dict(shipsKilled)
        iskKilledByID = dict(iskKilled)
        self.warDateLabel.text = '<right>%s</right>' % self.GetWarDateText()
        self.warDateLabel.width = self.width
        self._LoadAttackerInfo(iskKilledByID, shipsKilledByID)
        warHqText = self._GetWarHqText()
        self.warHQLabel.text = '<center>%s</center>' % warHqText
        self.arrowLeft.display = self.arrowRight.display = self.helpIcon.display = bool(self.warReportController.GetWarHq())
        self.OnWarHqLabelChanged()
        self._LoadDefenderInfo(iskKilledByID, shipsKilledByID)
        self.UpdateSwords()
        self.ShowLoading()
        self.GetMaxKills()
        self.ShowOrHideGraph()
        self.UpdateGraphsAndKillScroll()
        self.graphAndKillsLoaded = True
        self.HideLoading()

    def _GetWarHqText(self):
        warHqText = ''
        warHQ = self.warReportController.GetWarHq()
        if warHQ:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(warHQ)
            if structureInfo:
                warHqLink = GetShowInfoLink(structureInfo.typeID, structureInfo.itemName, itemID=warHQ)
                warHqText = GetByLabel('UI/Corporations/Wars/WarHQTextWithLink', hqLink=warHqLink)
        return warHqText

    def _LoadDefenderInfo(self, iskKilledByID, shipsKilledByID):
        defenderID = self.warReportController.GetDefenderID()
        Frame(parent=self.defenderLogoDetailed, color=DEFENDER_COLOR)
        if IsCorporation(defenderID):
            defenderLinkType = const.typeCorporation
        else:
            defenderLinkType = const.typeAlliance
        defenderLogo = GetLogoIcon(itemID=defenderID, parent=self.defenderLogoDetailed, acceptNone=False, align=uiconst.TOPLEFT, height=64, width=64, state=uiconst.UI_NORMAL, ignoreSize=True)
        defenderLogo.OnClick = (self.ShowInfo, defenderID, defenderLinkType)
        defenderName = cfg.eveowners.Get(defenderID).name
        defenderLogo.hint = '%s:<br>%s' % (GetByLabel('UI/Corporations/Wars/Defender'), defenderName)
        defenderNameLabel = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=defenderName, info=('showinfo', defenderLinkType, defenderID))
        self.defenderNameLabel.text = defenderNameLabel
        shipsAmt = self.GetHighlightedText(FmtAmt(shipsKilledByID.get(defenderID, 0)))
        self.defenderShipsKilledLabel.text = GetByLabel('UI/Corporations/Wars/NumShipsKilled', ships=shipsAmt)
        iskAmt = self.GetHighlightedText(FmtISK(iskKilledByID.get(defenderID, 0), 0))
        self.defenderISKKilledLabel.text = GetByLabel('UI/Corporations/Wars/ISKKilled', iskAmount=iskAmt)
        roleTextDisplay = False if self.warReportController.IsWarMutual() else True
        self.attackerLabel.display = roleTextDisplay
        self.defenderLabel.display = roleTextDisplay

    def _LoadAttackerInfo(self, iskKilledByID, shipsKilledByID):
        attackerID = self.warReportController.GetAttackerID()
        Frame(parent=self.attackerLogoDetailed, color=ATTACKER_COLOR)
        if IsCorporation(attackerID):
            attackerLinkType = const.typeCorporation
        else:
            attackerLinkType = const.typeAlliance
        attackerLogo = GetLogoIcon(itemID=attackerID, parent=self.attackerLogoDetailed, acceptNone=False, align=uiconst.TOPRIGHT, height=64, width=64, state=uiconst.UI_NORMAL, ignoreSize=True)
        attackerLogo.OnClick = (self.ShowInfo, attackerID, attackerLinkType)
        attackerName = cfg.eveowners.Get(attackerID).name
        attackerLogo.hint = '%s:<br>%s' % (GetByLabel('UI/Corporations/Wars/Offender'), attackerName)
        attackerNameLabel = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=attackerName, info=('showinfo', attackerLinkType, attackerID))
        self.attackerNameLabel.text = '<right>%s' % attackerNameLabel
        iskAmt = self.GetHighlightedText(FmtISK(iskKilledByID.get(attackerID, 0), 0))
        self.attackerISKLostLabel.text = '<right>%s' % GetByLabel('UI/Corporations/Wars/ISKKilled', iskAmount=iskAmt)
        shipsAmt = self.GetHighlightedText(FmtAmt(shipsKilledByID.get(attackerID, 0)))
        self.attackerShipsLostLabel.text = '<right>%s' % GetByLabel('UI/Corporations/Wars/NumShipsKilled', ships=shipsAmt)

    def UpdateSwords(self):
        war = self.warReportController.GetWar()
        if blue.os.GetWallclockTime() <= war.timeStarted:
            texturePath = 'res:/UI/Texture/WindowIcons/limitedengagement.png'
        else:
            texturePath = 'res:/UI/Texture/WindowIcons/wars.png'
        self.swordsSprite.texturePath = texturePath

    def GetHighlightedText(self, myText):
        return '<b>%s</b>' % myText

    def ShowInfo(self, itemID, typeID, *args):
        sm.GetService('info').ShowInfo(typeID, itemID)

    def OpenAllyWnd(self, *args):
        from eve.client.script.ui.shared.neocom.corporation.war.allyWnd import AllyWnd
        AllyWnd.CloseIfOpen()
        allies = self.warReportController.GetAllies()
        war = self.warReportController.GetWar()
        AllyWnd.Open(war=war, allies=allies)

    def OpenSurrenderWnd(self, *args):
        warNegotiationID = self.warReportController.GetWarNegotiationID()
        WarSurrenderWnd.CloseIfOpen()
        if warNegotiationID:
            WarSurrenderWnd.Open(warNegotiationID=warNegotiationID, isRequest=False)
        else:
            requesterID = session.corpid if session.allianceid is None else session.allianceid
            war = self.warReportController.GetWar()
            WarSurrenderWnd.Open(war=war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)

    def GetWarDateText(self):
        war = self.warReportController.GetWar()
        declareDate = FmtDate(war.timeDeclared, 'ss') if war.timeDeclared else GetByLabel('UI/Common/Unknown')
        fightDate = FmtDate(war.timeStarted, 'ss') if war.timeStarted else None
        warFinishTime = FmtDate(war.timeFinished, 'ss') if war.timeFinished else None
        warNotStarted = blue.os.GetWallclockTime() <= war.timeStarted
        if warFinishTime:
            warIsStillActve = blue.os.GetWallclockTime() < war.timeFinished
            if warNotStarted:
                timeText = GetByLabel('UI/Corporations/Wars/WarReportFutureWarWithStartAndEndDate', fightDate=fightDate, endDate=warFinishTime)
            elif warIsStillActve:
                timeText = GetByLabel('UI/Corporations/Wars/WarReportActiveWarWithStartAndEndDate', fightDate=fightDate, endDate=warFinishTime)
            else:
                timeText = GetByLabel('UI/Corporations/Wars/WarReportFinishedWarWithStartAndEndDate', fightDate=fightDate, endDate=warFinishTime)
        elif warNotStarted:
            timeText = GetByLabel('UI/Corporations/Wars/WarReportWarDeclaredCanFightDetailed', declareTime=declareDate, endDate=fightDate)
        else:
            timeText = GetByLabel('UI/Corporations/Wars/WarStarted', date=fightDate)
        return timeText

    def UpdateGraphsAndKillScroll(self):
        groupID = None
        isGraphVisible = self.showGraph.checked
        if isGraphVisible:
            groupID = settings.user.ui.Get('killGroupDisplayed', None)
        self.LoadKillsScroll(groupID)
        if isGraphVisible:
            self.DrawKillsByGroup()
        self.graphAndKillsLoaded = True

    def LoadKillsScroll(self, groupID = None):
        killsScrollList = self.GetKillsScrollList(groupID)
        if groupID is None:
            noContentHint = GetByLabel('UI/Corporations/Wars/NoKillsFound')
        else:
            noContentHint = GetByLabel('UI/Corporations/Wars/NoKillsFoundForGroup')
        self.killsScroll.Load(contentList=killsScrollList, noContentHint=noContentHint)

    def GetKillsScrollList(self, shipGroup = None):
        killValue = self.killsFilterCombo.GetValue()
        entityID = {'attacker': self.warReportController.GetAttackerID(),
         'defender': self.warReportController.GetDefenderID()}.get(killValue, None)
        kills = self.warStatisticMoniker.GetKills(entityID, shipGroup)
        return self._GetKillsScrollList(kills, killValue)

    def _GetKillsScrollList(self, kills, killValue):
        myDate = None
        sortedScrolllist = []
        ownerIDsToPrime = set()
        for eachKill in kills:
            ownerIDsToPrime.add(eachKill.finalCharacterID)
            ownerIDsToPrime.add(eachKill.finalCorporationID)
            ownerIDsToPrime.add(eachKill.finalAllianceID)
            ownerIDsToPrime.add(eachKill.victimCharacterID)
            ownerIDsToPrime.add(eachKill.victimCorporationID)
            ownerIDsToPrime.add(eachKill.victimAllianceID)

        ownerIDsToPrime = filter(None, ownerIDsToPrime)
        cfg.eveowners.Prime(ownerIDsToPrime)
        attackerID = self.warReportController.GetAttackerID()
        for kill in kills:
            if attackerID in (kill.finalCorporationID, kill.finalAllianceID):
                attackerKill = True
            else:
                attackerKill = False
            if killValue == 'attacker' and attackerKill == False:
                continue
            elif killValue == 'defender' and attackerKill == True:
                continue
            sortedScrolllist.append((kill.killTime, GetFromClass(WarKillEntry, {'label': '',
              'killID': kill.killID,
              'killTime': kill.killTime,
              'finalCharacterID': kill.finalCharacterID,
              'finalCorporationID': kill.finalCorporationID,
              'finalAllianceID': kill.finalAllianceID,
              'finalShipTypeID': kill.finalShipTypeID,
              'victimCharacterID': kill.victimCharacterID,
              'victimCorporationID': kill.victimCorporationID,
              'victimAllianceID': kill.victimAllianceID,
              'victimShipTypeID': kill.victimShipTypeID,
              'attackerKill': attackerKill,
              'mail': kill})))

        sortedScrolllist = SortListOfTuples(sortedScrolllist, reverse=True)
        scrolllist = []
        for entry in sortedScrolllist:
            if myDate is None or myDate != FmtDate(entry.killTime, 'sn'):
                scrolllist.append(GetFromClass(Header, {'label': FmtDate(entry.killTime, 'sn')}))
                myDate = FmtDate(entry.killTime, 'sn')
            scrolllist.append(entry)

        return scrolllist

    def OnKillComboChange(self, *args):
        comboSetting = settings.user.ui.Get('killComboValue', 0)
        comboValue = self.killsFilterCombo.GetValue()
        if comboValue == comboSetting:
            return
        settings.user.ui.Set('killComboValue', comboValue)
        self.UpdateGraphsAndKillScroll()

    def DrawKillsByGroup(self):
        self.PrimeKillsByGroup()
        maxKills = self.GetMaxKills()
        self.killsByGroupParent.DrawKillsByGroup(self.killsByShipGroup, self.warReportController, maxKills=maxKills)
        self.graphLoaded = True

    def PrimeKillsByGroup(self):
        if self.killsByShipGroup == {}:
            killsByGroup = self.warStatisticMoniker.GetKillsByGroup()
            for groupID, groupInfo in killsByGroup.iteritems():
                classTypeID = cfg.GetShipClassTypeByGroupID(groupID)
                self.killsByShipGroup[classTypeID].attackerKills += groupInfo['defenderShipLoss']
                self.killsByShipGroup[classTypeID].defenderKills += groupInfo['attackerShipLoss']
                self.killsByShipGroup[classTypeID].attackerKillsIsk += groupInfo['defenderIskLoss']
                self.killsByShipGroup[classTypeID].defenderKillsIsk += groupInfo['attackerIskLoss']

    def GetMaxKills(self):
        self.PrimeKillsByGroup()
        killsByGroup = self.killsByShipGroup
        if not killsByGroup:
            return 10
        maxKills = max((max(kills.attackerKillsIsk, kills.defenderKillsIsk) for kills in killsByGroup.itervalues()))
        if maxKills < 10:
            return 10
        exp = math.ceil(math.log(maxKills, 10))
        self.maxKills = 10 ** exp
        if float(maxKills) / self.maxKills < 0.5:
            self.maxKills = self.maxKills * 0.5
        self.maxKills = max(10, self.maxKills)
        return self.maxKills

    def ChangeGraphDisplay(self, *args):
        showGraph = self.showGraph.checked
        settings.user.ui.Set('killShowGraph', showGraph)
        self.ShowOrHideGraph()
        self.UpdateGraphsAndKillScroll()

    def ShowOrHideGraph(self):
        showGraph = self.showGraph.checked
        if showGraph:
            uicore.animations.FadeIn(self.killsByGroupParent, duration=0.5)
            uicore.animations.MorphScalar(self.killsByGroupParent, 'height', self.killsByGroupParent.height, KILLS_PARENT_FULL_HEIGHT, duration=0.3)
            self.killsByGroupParent.Enable()
        else:
            uicore.animations.FadeOut(self.killsByGroupParent, duration=0.1)
            uicore.animations.MorphScalar(self.killsByGroupParent, 'height', self.killsByGroupParent.height, 0, duration=0.3)
            self.killsByGroupParent.Disable()

    def OnWarHqLabelChanged(self):
        numLines = getattr(self.warHQLabel, '_numLines', 1)
        if numLines > 1:
            self.helpIcon.align = uiconst.TOPRIGHT
            iconLeft = WAR_HQ_PADDING - self.arrowLeft.width / 2 - 8
            self.helpIcon.left = iconLeft - self.helpIcon.width
            self.arrowLeft.align = uiconst.TOPLEFT
            self.arrowRight.align = uiconst.TOPRIGHT
            self.arrowLeft.left = iconLeft
            self.arrowRight.left = iconLeft
        else:
            self.helpIcon.align = uiconst.CENTER
            w, h = EveLabelMedium.MeasureTextSize(text=self._GetWarHqText())
            offset = (w + self.arrowLeft.width) / 2 + 4
            self.arrowLeft.align = uiconst.CENTER
            self.arrowRight.align = uiconst.CENTER
            self.arrowLeft.left = -offset
            self.arrowRight.left = offset
            self.helpIcon.left = offset + self.arrowRight.width

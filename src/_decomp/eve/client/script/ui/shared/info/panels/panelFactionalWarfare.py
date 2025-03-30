#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelFactionalWarfare.py
import carbonui
import evelink
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui import const as uiconst, TextColor
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from characterdata.factions import get_faction_name
from eve.client.script.ui.control.eveIcon import OwnerIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.factionalWarfare.fwSystemBenefitIcon import FWSystemBenefitIcon
from eve.common.script.util.facwarCommon import BENEFITS_BY_LEVEL
from evelink.client import owner_link
from factionwarfare.client.text import GetSystemCaptureStatusText, GetSystemCaptureStatusHint
from fwwarzone.client.dashboard.const import ADJACENCY_TO_LABEL_SYSTEM_TEXT
from fwwarzone.client.dashboard.gauges.advantageWidget import AdvantageWidget
from fwwarzone.client.dashboard.gauges.contestedGauge import ContestedFWSystemGauge
from fwwarzone.client.util import GetAttackerDefenderColors, GetSystemCaptureStatusColorFromVp
from localization import GetByLabel
import inventorycommon.const as invConst
iconSize = 48
textPad = 10

class PanelFactionalWarfare(Container):

    def ApplyAttributes(self, attributes):
        super(PanelFactionalWarfare, self).ApplyAttributes(attributes)
        self.solarsystemID = attributes.solarsystemID
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.facWarSvc = sm.GetService('facwar')
        myScrollCont = ScrollContainer(parent=self, padding=const.defaultPadding)
        ownerCont = ContainerAutoSize(name='ownerCont', parent=myScrollCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=iconSize)
        self.ownerCont = Container(name='ownerCont', parent=ownerCont, align=uiconst.TOLEFT, width=iconSize + textPad)
        self.occupierIcon = OwnerIcon(name='occupierIcon', parent=self.ownerCont, align=uiconst.CENTER, pos=(0,
         0,
         iconSize,
         iconSize))
        self.occupierNameLabel = EveLabelMedium(name='occupierNameLabel', parent=ownerCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.originalOwnerLabel = EveLabelMedium(name='originalOwnerLabel', parent=ownerCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        constestedCont = ContainerAutoSize(name='constestedCont', parent=myScrollCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=20, minHeight=iconSize)
        self.gaugeCont = Container(name='gaugeCont', parent=constestedCont, align=uiconst.TOLEFT, width=iconSize + textPad)
        self.controlGauge = ContestedFWSystemGauge(parent=self.gaugeCont, align=uiconst.CENTER, systemId=self.solarsystemID, radius=int(iconSize / 2))
        self.adjacencyLabel = EveLabelMedium(name='adjacencyLabel', parent=constestedCont, align=uiconst.TOTOP)
        self.systemStatusLabel = EveLabelMedium(name='systemStatusLabel', parent=constestedCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        upgradeCont = ContainerAutoSize(name='upgradeCont', parent=myScrollCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=20, minHeight=iconSize)
        self.benefitCont = Container(name='benefitCont', parent=upgradeCont, align=uiconst.TOLEFT, alignMode=uiconst.TOTOP)
        self.systemLevelLabel = EveLabelMedium(name='systemLevelLabel', parent=upgradeCont, align=uiconst.TOTOP)
        advantageCont = ContainerAutoSize(name='advantageCont', parent=myScrollCont, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padTop=10)
        self.advantageLabel = EveLabelMedium(name='advantageLabel', parent=advantageCont, align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel'))
        systemAdvantageWidget = AdvantageWidget(systemId=self.solarsystemID, name='AdvantageWidget', parent=advantageCont, align=uiconst.TOTOP, padRight=10)

    def Load(self, *args):
        self.UpdateOccupier()
        self.UpdateGauge()
        self.UpdateAdjacencyLabel()
        self.UpdateSystemStatusLabel()
        self.UpdateSystemLevel()
        self.UpdateWidth()

    def UpdateAdjacencyLabel(self):
        fwOccupationState = self.fwWarzoneSvc.GetOccupationState(self.solarsystemID)
        adjacencyText = ''
        if fwOccupationState:
            adjacencyText = ADJACENCY_TO_LABEL_SYSTEM_TEXT.get(fwOccupationState.adjacencyState, '')
        self.adjacencyLabel.SetText(adjacencyText)

    def UpdateOccupier(self):
        occupierID = self.fwWarzoneSvc.GetSystemOccupier(self.solarsystemID)
        newText = GetByLabel('UI/Agency/FactionWarfare/systemOccupierLabel', factionID=occupierID, typeID=invConst.typeFaction)
        self.occupierNameLabel.SetText(newText)
        self.occupierIcon.SetOwnerID(occupierID)
        solarSystem = cfg.mapSystemCache.Get(self.solarsystemID)
        ownerLink = owner_link(solarSystem.factionID)
        ownerText = GetByLabel('UI/FactionWarfare/OriginalOwner', factionLink=ownerLink)
        self.originalOwnerLabel.SetText(ownerText)

    def UpdateGauge(self):
        attackerColor, defenderColor = GetAttackerDefenderColors(self.solarsystemID)
        self.controlGauge.SetGaugeColors(attackerColor, defenderColor)
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarsystemID)
        if victoryPointState:
            value = victoryPointState.contestedFraction
        else:
            value = 0.0
        self.controlGauge.UpdateChart(value)
        fwOccupationState = self.fwWarzoneSvc.GetOccupationState(self.solarsystemID)
        adjacencyState = fwOccupationState.adjacencyState if fwOccupationState else None
        self.controlGauge.SetAdjacency(adjacencyState)

    def UpdateSystemStatusLabel(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarsystemID)
        systemStatusText = GetSystemCaptureStatusText(victoryPointState)
        newStatusText = GetByLabel('UI/Agency/FactionWarfare/systemStatusLabel', systemStatusText=systemStatusText, color=Color.RGBtoHex(*GetSystemCaptureStatusColorFromVp(victoryPointState)))
        self.systemStatusLabel.SetText(newStatusText)
        self.systemStatusLabel.SetHint(GetSystemCaptureStatusHint(victoryPointState))

    def UpdateSystemLevel(self):
        upgradeLevel = self.facWarSvc.GetSolarSystemUpgradeLevel(self.solarsystemID)
        self.benefitCont.Flush()
        if upgradeLevel is None:
            factionID = self.facWarSvc.GetSystemOccupier(self.solarsystemID)
            carbonui.TextBody(state=uiconst.UI_NORMAL, parent=self.benefitCont, align=uiconst.TOLEFT, text=GetByLabel('UI/PirateInsurgencies/factionDoesNotGetSystemUpgrades', factionName=owner_link(factionID)), color=TextColor.WARNING)
            return
        self.systemLevelLabel.SetText(GetByLabel('UI/Agency/FactionWarfare/systemUpgradeLevel', level=upgradeLevel))
        width = 0
        currentBenefits = BENEFITS_BY_LEVEL.get(upgradeLevel)
        for i, (benefitType, benefitValue) in enumerate(reversed(currentBenefits)):
            icon = FWSystemBenefitIcon(parent=self.benefitCont, align=uiconst.TOLEFT, left=10 if i else 0, benefitType=benefitType, benefitValue=benefitValue, opacity=1.0, width=26)
            width += icon.left + icon.width

        self.benefitCont.width = width + 10

    def UpdateWidth(self):
        maxWidth = max(self.ownerCont.width, self.gaugeCont.width, self.benefitCont.width)
        self.ownerCont.width = self.gaugeCont.width = self.benefitCont.width = maxWidth

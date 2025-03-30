#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\warzoneStats.py
from itertools import chain
from evePathfinder.core import IsUnreachableJumpCount
from carbonui import TextColor, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.common.script.util import facwarCommon
from factionwarfare.client.text import GetVictoryPointStateText
from fwwarzone.client.dashboard.advantageStatsDataLoader import AdvantageStatsDataLoader
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR, ADJACENCY_TO_LABEL_TEXT
from inventorycommon.const import typeSolarSystem
from localization import GetByLabel

class FWWarzoneStatsPanel(Container):

    def ApplyAttributes(self, attributes):
        super(FWWarzoneStatsPanel, self).ApplyAttributes(attributes)
        self.factionID = attributes.get('factionID')
        self.fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
        self.loaded = False

    def LoadPanel(self, *args, **kwargs):
        if self.loaded:
            return
        fwSvc = sm.GetService('facwar')
        foeIDs = facwarCommon.GetAllFwEnemies()[self.factionID]
        self.occupationEnemyFactionID = facwarCommon.GetOccupationEnemyFaction(self.factionID)
        factionsTuple = tuple(chain((self.factionID,), tuple(foeIDs)))
        self.systemIDs = fwSvc.GetSolarSystemsOccupiedByFactions(factionsTuple)
        self.ConstructLayout()
        asyncDataLoader = AdvantageStatsDataLoader(self.systemIDs.keys())
        asyncDataLoader.onSuccessSignal.connect(self.advantageDataLoaded)
        asyncDataLoader.onErrorSignal.connect(self.advantageDataError)
        asyncDataLoader.AsyncLoadAdvantage()
        self.loaded = True

    def advantageDataError(self):
        self.loadingAdvantageMessageCont.Flush()
        EveLabelSmall(parent=self.loadingAdvantageMessageCont, align=uiconst.TORIGHT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/errorLoadingAdvantageData'))

    def advantageDataLoaded(self, systemAdvantageData):
        self.systemAdvantageData = systemAdvantageData
        self._UpdateSystemsScroll(advantageColumn=True)
        self.loadingAdvantageMessageCont.Hide()

    def ConstructLayout(self):
        mainCont = Container(parent=self, align=uiconst.TOALL, padding=80)
        self.systemsScroll = eveScroll.Scroll(name='systemsScroll', parent=mainCont)
        self.loadingAdvantageMessageCont = ContainerAutoSize(name='loadingAdvantageMessageCont', parent=mainCont, height=32, align=uiconst.TOPLEFT, top=-20, padLeft=8, alignMode=uiconst.TORIGHT, state=uiconst.UI_DISABLED)
        LoadingWheel(width=16, height=16, parent=Container(parent=self.loadingAdvantageMessageCont, align=uiconst.TORIGHT, width=32, height=32, top=-8), align=uiconst.CENTER, left=-16)
        EveLabelSmall(parent=self.loadingAdvantageMessageCont, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/loadingAdvantageData'), align=uiconst.TORIGHT, padRight=16)
        self.systemsScroll.sr.id = 'FWSystemsScroll'
        self._UpdateSystemsScroll(advantageColumn=False)

    def _GetAdvantageText(self, advantageState, factionA, factionB):
        score = advantageState.GetNetAdvantageScore(factionA, factionB)
        if score > 0:
            color = Color.RGBtoHex(*FACTION_ID_TO_COLOR[factionA])
            return '<color=%s>%s</color>' % (color, u'{0:.1%}'.format(score))
        elif score < 0:
            color = Color.RGBtoHex(*FACTION_ID_TO_COLOR[factionB])
            return '<color=%s>%s</color>' % (color, u'{0:.1%}'.format(score * -1))
        else:
            color = Color.RGBtoHex(*TextColor.DISABLED)
            return '<color=%s>%s</color>' % (color, score)

    def _GetAdvantageSortableScore(self, advantageState, factionA, factionB):
        score = advantageState.GetNetAdvantageScore(factionA, factionB)
        return abs(score) * 100.0

    def _UpdateSystemsScroll(self, advantageColumn = False):
        scrolllist = []
        for systemID in self.systemIDs:
            numJumps = self.GetNumJumpsString(systemID)
            victoryPointsState = sm.GetService('fwVictoryPointSvc').GetVictoryPointState(systemID)
            contestedPercentage = u'{0:.1%}'.format(victoryPointsState.contestedFraction)
            captureStatus = GetVictoryPointStateText(victoryPointsState)
            systemName = self.ColorTextBySide(cfg.evelocations.Get(systemID).name, systemID)
            frontlineStatusText = ADJACENCY_TO_LABEL_TEXT[self.fwWarzoneSvc.GetOccupationState(systemID).adjacencyState]
            label = None
            if advantageColumn:
                label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (systemName,
                 contestedPercentage,
                 numJumps,
                 captureStatus,
                 frontlineStatusText,
                 self._GetAdvantageText(self.systemAdvantageData[systemID], self.factionID, self.occupationEnemyFactionID))
            else:
                label = '%s<t>%s<t>%s<t>%s<t>%s' % (systemName,
                 contestedPercentage,
                 numJumps,
                 captureStatus,
                 frontlineStatusText)
            data = {'label': label,
             'itemID': systemID,
             'typeID': typeSolarSystem,
             'selectable': 0}
            data['sort_%s' % GetByLabel('UI/FactionWarfare/frontlines/contested')] = victoryPointsState.contestedFraction
            if advantageColumn:
                data['sort_%s' % GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel')] = self._GetAdvantageSortableScore(self.systemAdvantageData[systemID], self.factionID, self.occupationEnemyFactionID)
            scrolllist.append(GetFromClass(Generic, data))

        headers = [GetByLabel('UI/FactionWarfare/System'),
         GetByLabel('UI/FactionWarfare/frontlines/contested'),
         GetByLabel('UI/FactionWarfare/Jumps'),
         GetByLabel('UI/FactionWarfare/Capture status'),
         GetByLabel('UI/FactionWarfare/adjacency')]
        if advantageColumn:
            headers.append(GetByLabel('UI/FactionWarfare/frontlinesDashboard/advantageTitleLabel'))
        self.systemsScroll.Load(contentList=scrolllist, headers=headers)
        return scrolllist

    def IsFriendSystem(self, systemID):
        friendSystems = sm.GetService('facwar').GetSolarSystemsOccupiedByFactions([self.factionID])
        return systemID in friendSystems

    def GetSystemScrollEntry(self, systemID):
        for node in self.systemsScroll.GetNodes():
            if node.itemID == systemID:
                return node

    def GetNumJumpsString(self, systemID):
        numJumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(systemID)
        if IsUnreachableJumpCount(numJumps):
            return '-'
        else:
            return numJumps

    def ColorTextBySide(self, text, systemID):
        color = Color.RGBtoHex(*FACTION_ID_TO_COLOR[self.fwWarzoneSvc.GetOccupationState(systemID).occupierID])
        return '<color=%s>%s</color>' % (color, text)

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\lpIncursionsPanel.py
import blue
from carbon.common.script.util.format import FmtDate, FmtSimpleDateUTC, ParseDate, ParseSmallDate
import carbonui.const as uiconst
from carbonui.control.button import Button
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.common.lib import appConst
from eve.common.script.mgt import appLogConst
import evetypes
import localization

class LPIncursionsPanel(Container):
    panelID = walletConst.PANEL_LP_INCURSIONS

    def ApplyAttributes(self, attributes):
        self.incursionLPLogData = None
        Container.ApplyAttributes(self, attributes)
        self.ConstructLayout()

    def OnTabSelect(self):
        if self.incursionLPLogData is None:
            self.scroll.Clear()
            self.scroll.ShowHint(localization.GetByLabel('UI/Incursion/Journal/LoadData'))
        else:
            self.UpdateIncursionLPLog(self.incursionLPLogData)

    def ConstructLayout(self):
        self.incursionLPLogFilters = Container(name='incursionLPLogFilters', parent=self, height=Button.default_height, align=uiconst.TOTOP, padTop=16)
        self.incursionLPLoadbutton = Button(parent=self.incursionLPLogFilters, label=localization.GetByLabel('UI/Generic/Load'), align=uiconst.BOTTOMRIGHT, func=self.LoadIncursionLPLog)
        now = FmtDate(blue.os.GetWallclockTime(), 'sn')
        self.incursionLPDate = SingleLineEditText(name='incursionFromdate', parent=self.incursionLPLogFilters, setvalue=now, align=uiconst.TOLEFT, maxLength=16, label=localization.GetByLabel('UI/Common/Date'), padding=(4, 0, 0, 0), width=110)
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        self.incursionTaleIDFilter = Combo(label=localization.GetByLabel('UI/Incursion/Journal/Incursion'), parent=self.incursionLPLogFilters, options=options, name='incursionTaleIDFilter', width=110, align=uiconst.TOLEFT, padding=(4, 0, 0, 0))
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None)]
        self.incursionTypeFilter = Combo(label=localization.GetByLabel('UI/Incursion/Journal/Types'), parent=self.incursionLPLogFilters, options=options, name='incursionTypeFilter', width=110, align=uiconst.TOLEFT, padding=(4, 0, 0, 0))
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_HIDDEN)
        self.scroll = Scroll(parent=self)
        self.scroll.multiSelect = 0
        self.scroll.sr.id = 'walletLoyaltyPointIncursionScroll'

    def LoadIncursionLPLog(self, *args):
        self.incursionLPLoadbutton.disabled = True
        self.incursionTaleIDFilter.Disable()
        self.incursionTypeFilter.Disable()
        self.incursionLPDate.Disable()
        self.loadingWheel.Show()
        self.scroll.Clear()
        self.incursionLPLogData = sm.RemoteSvc('rewardMgr').GetRewardLPLogs()
        self.UpdateIncursionLPLog(self.incursionLPLogData)
        self.loadingWheel.Hide()
        self.incursionLPLoadbutton.disabled = False
        self.incursionTaleIDFilter.Enable()
        self.incursionTypeFilter.Enable()
        self.incursionLPDate.Enable()

    def UpdateIncursionLPLog(self, data, selectedTaleID = None, selectedConstellationID = None):
        mapsvc = sm.GetService('map')
        taleIDFilter = self.incursionTaleIDFilter.selectedValue
        incursionTypeFilter = self.incursionTypeFilter.selectedValue
        try:
            fromDate = ParseSmallDate(self.incursionLPDate.GetValue())
        except (Exception, TypeError):
            dateString = localization.formatters.FormatDateTime(blue.os.GetWallclockTime(), dateFormat='short', timeFormat='none')
            fromDate = ParseDate(dateString)
            self.incursionLPDate.SetValue(dateString)

        fromDate += appConst.DAY
        dungeonTypes = set()
        taleIDs = {}
        filteredData = []
        for d in data:
            dungeonTypes.add(d.rewardMessageKey)
            constellationID = mapsvc.GetParent(d.solarSystemID)
            if constellationID is not None:
                constellation = mapsvc.GetItem(constellationID)
                if constellation is not None:
                    taleIDs[d.taleID] = constellation.itemName
            if selectedTaleID is not None:
                if selectedTaleID != d.taleID:
                    continue
            if taleIDFilter is not None and selectedTaleID is None:
                if taleIDFilter != d.taleID:
                    continue
            if incursionTypeFilter is not None:
                shouldAdd = False
                if incursionTypeFilter == LPTypeFilter.LPPayedOut:
                    if d.eventTypeID == appLogConst.eventRewardLPPoolPayedOut:
                        shouldAdd = True
                elif incursionTypeFilter == LPTypeFilter.LPLost:
                    if d.eventTypeID == appLogConst.eventRewardLPPoolLost:
                        shouldAdd = True
                elif incursionTypeFilter == d.rewardMessageKey:
                    shouldAdd = True
                if not shouldAdd:
                    continue
            if fromDate < d.date:
                continue
            filteredData.append(d)

        if selectedTaleID is not None:
            if selectedTaleID not in taleIDs:
                constellation = mapsvc.GetItem(selectedConstellationID)
                if constellation is not None:
                    taleIDs[selectedTaleID] = constellation.itemName
        scrolllist = []
        for d in filteredData:
            solarSystemType = ''
            if d.eventTypeID == appLogConst.eventRewardLPPoolPayedOut:
                solarSystemType = _FormatLogEntry('CompletedAndPaidOut', d.rewardID)
            elif d.eventTypeID == appLogConst.eventRewardLPPoolLost:
                solarSystemType = _FormatLogEntry('CompletedAndNotPaidOut', d.rewardID)
            elif d.rewardMessageKey is not None and isinstance(d.rewardMessageKey, int):
                solarSystemType = localization.GetByMessageID(d.rewardMessageKey)
            elif d.rewardMessageKey is not None and d.rewardMessageKey != '':
                solarSystemType = localization.GetByLabel(d.rewardMessageKey)
            if d.lpAmountAddedToPool is None:
                d.lpAmountAddedToPool = 0
            if d.lpAmountAddedToPool == 0:
                LPAmountAddedToPool = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountAddedToPool = '<color=0xFFFFFF00>' + localization.formatters.FormatNumeric(d.lpAmountAddedToPool) + '</color>'
            if d.lpAmountPayedOut is None:
                d.lpAmountPayedOut = 0
            if d.lpAmountPayedOut == 0:
                LPAmountPayedOut = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            elif d.eventTypeID == appLogConst.eventRewardLPPoolLost:
                LPAmountPayedOut = '<color=0xFFFF0000>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountPayedOut = '<color=0xFF00FF00>' + localization.formatters.FormatNumeric(d.lpAmountPayedOut) + '</color>'
            if d.numberOfPlayers is None:
                d.numberOfPlayers = 0
            description = ''
            if d.eventTypeID == appLogConst.eventRewardDisqualified:
                if d.disqualifierType == appConst.rewardIneligibleReasonTrialAccount:
                    description = _FormatLogEntry('DisqualifiedTrialAccount', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonInvalidGroup:
                    groupName = evetypes.GetGroupNameByGroup(d.disqualifierData)
                    description = _FormatLogEntry('DisqualifiedInvalidShipGroup2', d.rewardID, groupName=groupName)
                elif d.disqualifierType == appConst.rewardIneligibleReasonShipCloaked:
                    description = _FormatLogEntry('DisqualifiedCloaked', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonNotInFleet:
                    description = _FormatLogEntry('DisqualifiedNoFleet', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonNotBestFleet:
                    description = _FormatLogEntry('DisqualifiedNotBestFleet', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonNotTop5:
                    description = _FormatLogEntry('DisqualifiedNotInTopFive', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonNotTopN:
                    maxWinners = d.disqualifierData
                    description = _FormatLogEntry('DisqualifiedNotInTopN', d.rewardID, n=maxWinners)
                elif d.disqualifierType == appConst.rewardIneligibleReasonNotRightAmountOfPlayers:
                    description = _FormatLogEntry('DisqualifiedNotEnoughParticipants', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonTaleAlreadyEnded:
                    description = _FormatLogEntry('DisqualifiedExpired', d.rewardID)
                elif d.disqualifierType == appConst.rewardIneligibleReasonLowContribution:
                    description = _FormatLogEntry('DisqualifiedLowContribution', d.rewardID)
            elif d.eventTypeID == appLogConst.eventRewardLPStoredInPool:
                description = _FormatLogEntry('LoyaltyPointPilotRewardCount', d.rewardID, rewardedPlayers=d.numberOfPlayers)
            elif d.eventTypeID == appLogConst.eventRewardLPPoolPayedOut:
                description = _FormatLogEntry('LoyaltyPointPoolPaidOut', d.rewardID)
            elif d.eventTypeID == appLogConst.eventRewardLPPoolLost:
                description = _FormatLogEntry('LoyaltyPointPoolLost', d.rewardID)
            elif d.eventTypeID == appLogConst.eventRewardLPPaidDirectly:
                description = _FormatLogEntry('LPPaidDirectly', d.rewardID, rewardedPlayers=d.numberOfPlayers)
            hint = description
            texts = [FmtSimpleDateUTC(d.date),
             solarSystemType,
             d.dungeonName,
             LPAmountAddedToPool,
             LPAmountPayedOut,
             description]
            scrolllist.append(GetFromClass(Generic, {'label': '<t>'.join(texts),
             'sort_' + localization.GetByLabel('UI/Incursion/Journal/StoredLP'): d.lpAmountAddedToPool,
             'sort_' + localization.GetByLabel('UI/Incursion/Journal/PaidLP'): d.lpAmountPayedOut,
             'hint': hint}))

        headers = [localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Incursion/Journal/Type'),
         localization.GetByLabel('UI/Incursion/Journal/EncounterName'),
         localization.GetByLabel('UI/Incursion/Journal/StoredLP'),
         localization.GetByLabel('UI/Incursion/Journal/PaidLP'),
         localization.GetByLabel('UI/Incursion/Journal/Description')]
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        for taleID, constellationName in taleIDs.iteritems():
            options.append((constellationName, taleID))

        self.incursionTaleIDFilter.LoadOptions(options)
        if selectedTaleID is None:
            self.incursionTaleIDFilter.SelectItemByValue(taleIDFilter)
        else:
            self.incursionTaleIDFilter.SelectItemByValue(selectedTaleID)
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None), (localization.GetByLabel('UI/Incursion/Journal/CompletedAndNotPaidOut'), LPTypeFilter.LPLost), (localization.GetByLabel('UI/Incursion/Journal/CompletedAndPaidOut'), LPTypeFilter.LPPayedOut)]
        for dungeonType in dungeonTypes:
            if dungeonType is not None and dungeonType != '':
                if isinstance(dungeonType, int):
                    options.append((localization.GetByMessageID(dungeonType), dungeonType))
                else:
                    options.append((localization.GetByLabel(dungeonType), dungeonType))

        self.incursionTypeFilter.LoadOptions(options)
        self.incursionTypeFilter.SelectItemByValue(incursionTypeFilter)
        if scrolllist:
            sortBy = self.scroll.GetSortBy()
            sortDirection = self.scroll.GetSortDirection()
            self.scroll.LoadContent(contentList=scrolllist, reversesort=1, headers=headers, scrollTo=0.0)
            if sortBy is None:
                self.scroll.Sort(by=localization.GetByLabel('UI/Common/Date'), reversesort=1)
            else:
                self.scroll.Sort(by=sortBy, reversesort=sortDirection)
        else:
            self.scroll.Clear()
            self.scroll.ShowHint(localization.GetByLabel('UI/Incursion/Journal/NoRecordFound'))


def _GetInvasionLogEntry(label, **kwargs):
    label_path = '/'.join(['UI/Invasion/Journal', label])
    return localization.GetByLabel(label_path, **kwargs)


def _GetIncursionLogEntry(label, **kwargs):
    label_path = '/'.join(['UI/Incursion/Journal', label])
    return localization.GetByLabel(label_path, **kwargs)


def _FormatLogEntry(label, rewardID, **kwargs):
    if rewardID == appConst.rewardInvasions:
        return _GetInvasionLogEntry(label, **kwargs)
    return _GetIncursionLogEntry(label, **kwargs)


class LPTypeFilter():
    LPLost = -1
    LPPayedOut = -2

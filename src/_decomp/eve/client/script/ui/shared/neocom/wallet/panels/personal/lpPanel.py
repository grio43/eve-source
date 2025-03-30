#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\lpPanel.py
import blue
import uthread2
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.tabGroup import TabGroup, GetTabData
from carbonui.primitives.container import Container
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.panels.personal.lpIncursionsPanel import LPIncursionsPanel
from eve.client.script.ui.shared.neocom.wallet.panels.personal.personalDonateLPPanel import PersonalDonateLPPanel
from eve.common.lib import appConst
from eve.common.script.sys.idCheckers import IsStation
from localization import GetByLabel
from localization.formatters import FormatNumeric
from menu import MenuLabel
from npcs.npccorporations import get_corporation_faction_id

class PersonalLPPanel(Container):
    panelID = walletConst.PANEL_LP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isInitialized = False
        self.tabGroup = None

    def OnTabSelect(self):
        if not self.isInitialized:
            self.ConstructLayout()
            self.isInitialized = True
        if self.tabGroup:
            self.tabGroup.AutoSelect()

    def ConstructLayout(self):
        self.balancePanel = LPBalancePanel(parent=self, state=uiconst.UI_HIDDEN)
        self.incursionsPanel = LPIncursionsPanel(parent=self, state=uiconst.UI_HIDDEN)
        self.donatePanel = PersonalDonateLPPanel(parent=self, state=uiconst.UI_HIDDEN)
        tabs = (GetTabData(label=GetByLabel('UI/Wallet/WalletWindow/TabOverview'), panel=self.balancePanel, tabID=walletConst.PANEL_LP_BALANCE), GetTabData(label=GetByLabel('UI/Incursion/Journal/LoyaltyPointLog'), panel=self.incursionsPanel, tabID=walletConst.PANEL_LP_INCURSIONS), GetTabData(label=GetByLabel('UI/Wallet/WalletWindow/TabDonate'), panel=self.donatePanel, tabID=walletConst.PANEL_LP_DONATE))
        self.tabGroup = TabGroup(name='WalletPersonalLPTabGroup', parent=self, tabs=tabs, padBottom=16, groupID='WalletPersonalLPTabs', idx=0)


class LPBalancePanel(Container):
    panelID = walletConst.PANEL_LP_BALANCE
    __notifyevents__ = ['OnCharacterLPBalanceChange_Local']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.loyaltyPointsWalletSvc = sm.GetService('loyaltyPointsWalletSvc')
        self.factionSvc = sm.GetService('faction')
        self.ConstructLayout()
        sm.RegisterNotify(self)

    def OnTabSelect(self):
        uthread2.StartTasklet(self.Update)

    def Update(self):
        self.loadingWheel.Show()
        self.PopulateFactionCombo()
        uthread2.StartTasklet(self.PopulateScroll)

    def PopulateFactionCombo(self):
        factionIDs = {get_corporation_faction_id(corpID) for corpID, lpAmount in self.GetMyLoyaltyPointsData() if lpAmount > 0}
        factionIDs = filter(None, factionIDs)
        options = [ (cfg.eveowners.Get(factionID).ownerName, factionID) for factionID in factionIDs ]
        options.sort()
        options.insert(0, (GetByLabel('UI/Wallet/WalletWindow/AllFactions'), 0))
        self.factionCombo.LoadOptions(options)

    def GetMyLoyaltyPointsData(self):
        return self.loyaltyPointsWalletSvc.GetAllCharacterLPBalancesExcludingEvermarks()

    def ConstructLayout(self):
        topCont = Container(parent=self, align=uiconst.TOTOP, height=32, padBottom=6)
        self.factionCombo = Combo(parent=topCont, align=uiconst.TOLEFT, width=200, callback=self.OnFactionCombo)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.ConstructScroll()

    def OnFactionCombo(self, *args):
        return self.PopulateScroll()

    def ConstructScroll(self):
        self.scroll = Scroll(name='loyaltyPointScroll', parent=self)
        self.scroll.sr.id = 'walletLoyaltyPointScroll2'
        self.scroll.sr.defaultColumnWidth = LPEntry.GetDefaultColumnWidth()

    def PopulateScroll(self):
        self.scroll.Clear()
        entries = self.GetScrollEntries()
        self.scroll.Load(contentList=entries, headers=LPEntry.GetHeaders(), noContentHint=GetByLabel('UI/Journal/JournalWindow/Agents/NoLP'))
        self.loadingWheel.Hide()

    def GetScrollEntries(self):
        entries = []
        lpData = self.GetMyLoyaltyPointsData()
        ownersToPrime = set()
        stationToPrime = set()
        locationsToPrime = set()
        lpInfoByCorpID = {}
        lpStoreSvc = sm.GetService('lpstore')
        for corpID, lpAmount in lpData:
            blue.pyos.BeNice()
            if self.IsFilteredOut(corpID):
                continue
            ownersToPrime.add(corpID)
            nearestDockableLocationID = lpStoreSvc.GetNearestDockableWithLPStoreForCorp(corpID)
            if IsStation(nearestDockableLocationID):
                stationToPrime.add(nearestDockableLocationID)
                locationsToPrime.add(nearestDockableLocationID)
            elif nearestDockableLocationID:
                structureInfo = sm.GetService('structureDirectory').GetStructureInfo(nearestDockableLocationID)
                if not structureInfo:
                    continue
                locationsToPrime.add(nearestDockableLocationID)
            lpInfoByCorpID[corpID] = (lpAmount, nearestDockableLocationID)

        if ownersToPrime:
            cfg.eveowners.Prime(ownersToPrime)
        if stationToPrime:
            cfg.stations.Prime(stationToPrime)
        if locationsToPrime:
            cfg.evelocations.Prime(locationsToPrime)
        for corpID, lpInfo in lpInfoByCorpID.iteritems():
            lpAmount, nearestDockableLocationID = lpInfo
            if lpAmount <= 0:
                continue
            entry = self.GetScrollEntry(corpID, lpAmount, nearestDockableLocationID)
            if entry:
                entries.append(entry)

        return entries

    def IsFilteredOut(self, corpID):
        factionID = self.factionCombo.GetValue()
        return factionID and factionID != get_corporation_faction_id(corpID)

    def GetScrollEntry(self, corpID, lpAmount, nearestDockableLocationID):
        return GetFromClass(LPEntry, {'lpAmount': lpAmount,
         'corpID': corpID,
         'sortValues': LPEntry.GetColumnSortValues(corpID, lpAmount),
         'nearestDockableLocationID': nearestDockableLocationID})

    def OnCharacterLPBalanceChange_Local(self, *args, **kwargs):
        self.Update()


class LPEntry(BaseListEntryCustomColumns):

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.lpStoreSvc = sm.GetService('lpstore')
        self.nameColumn = self.AddColumnText()
        self.lpColumn = self.AddColumnText()
        self.stationColumn = self.AddColumnText()
        self.stationColumn.state = uiconst.UI_NORMAL

    def Load(self, node):
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        self.PopulateLabels(node)

    def PopulateLabels(self, node):
        node = node if node else self.sr.node
        corpName = cfg.eveowners.Get(node.corpID).name
        lpFormatted = FormatNumeric(value=node.lpAmount, useGrouping=True)
        nearestDockableLocationID = node.nearestDockableLocationID
        if IsStation(nearestDockableLocationID):
            stationName = self._GetStationName(nearestDockableLocationID)
        elif nearestDockableLocationID:
            stationName = self._GetStrucureName(nearestDockableLocationID)
        else:
            stationName = GetByLabel('UI/Common/None')
        self.nameColumn.text = corpName
        self.lpColumn.text = lpFormatted
        self.stationColumn.text = stationName

    def _GetStationName(self, nearestStationID):
        stationTypeID = cfg.stations.Get(nearestStationID).stationTypeID
        nearestStationName = cfg.evelocations.Get(nearestStationID).name
        return '<url=showinfo:%s//%s>%s</url>' % (stationTypeID, nearestStationID, nearestStationName)

    def _GetStrucureName(self, nearestStructureID):
        structureInfo = sm.GetService('structureDirectory').GetStructureInfo(nearestStructureID)
        return GetShowInfoLink(structureInfo.typeID, structureInfo.itemName, structureInfo.structureID)

    def GetMenu(self, *args):
        m = [(GetByLabel('UI/Commands/ShowInfo'), self.ShowCorpInfo)]
        lpSvc = sm.GetService('lpstore')
        loyaltyPointsWalletSvc = sm.GetService('loyaltyPointsWalletSvc')
        xChangeRate = lpSvc.GetConcordLPExchangeRate(self.sr.node.corpID)
        concordLPs = loyaltyPointsWalletSvc.GetCharacterConcordLPBalance()
        if session.stationid is not None and xChangeRate is not None and xChangeRate > 0.0 and concordLPs > 0:
            m.append((MenuLabel('UI/Journal/JournalWindow/Agents/ConvertConcordLoyaltyPoints'), self.ShowConcordExchangeDialog))
        return m

    def ShowCorpInfo(self):
        sm.GetService('info').ShowInfo(appConst.typeCorporation, self.sr.node.corpID)

    def ShowConcordExchangeDialog(self):
        sm.GetService('lpstore').OpenConcordExchange(self.sr.node.corpID)

    @staticmethod
    def GetHeaders():
        return (GetByLabel('UI/Journal/JournalWindow/Agents/HeaderIssuingCorporation'), GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints'), GetByLabel('UI/Wallet/WalletWindow/ClosestLPStore'))

    @staticmethod
    def GetDynamicHeight(node, width):
        return 24

    @staticmethod
    def GetDefaultColumnWidth():
        return {GetByLabel('UI/Journal/JournalWindow/Agents/HeaderIssuingCorporation'): 160,
         GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints'): 100,
         GetByLabel('UI/Wallet/WalletWindow/ClosestLPStore'): 600}

    @staticmethod
    def GetColumnSortValues(corpID, lpAmount):
        return (cfg.eveowners.Get(corpID).name, lpAmount, None)

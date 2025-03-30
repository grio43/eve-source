#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\standingsPanel\standingsPanel.py
import localization
from carbonui import uiconst
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.button.menu import MenuButtonIcon
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel import standingsFilterSettings, standingsConst
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingCompositionScroll import StandingCompositionScroll
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsHeader import StandingsHeader
from eve.client.script.ui.shared.neocom.charsheet.standingsPanel.standingsHistoryScroll import StandingsHistoryScroll
from eve.client.script.ui.shared.standings.standingsBar import StandingsBar
from eve.client.script.ui.shared.standings.standingsGraph import StandingsGraph
from eve.client.script.ui.shared.standings.standingsUIUtil import GetStandingScrollGroups, STANDING_SETTING_CONFIG_NAME
from eve.common.script.sys import idCheckers
import eveicon

class StandingsPanel(Container):
    default_name = 'StandingsPanel'
    __notifyevents__ = ['OnStandingNotificationClicked', 'OnNPCStandingsClicked', 'OnNPCStandingChange']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.toID = attributes.toID
        self.fromID = None
        self.leftCont = DragResizeCont(parent=self, align=uiconst.TOLEFT_PROP, minSize=0.33, maxSize=0.6, settingsID='StandingsPanelResizeCont')
        filterContainer = ContainerAutoSize(parent=self.leftCont.mainCont, align=uiconst.TOTOP, alignMode=uiconst.TOPRIGHT, padding=(0, 4, 0, 4))
        self.searchBar = QuickFilterEdit(name='searchBar', parent=filterContainer, align=uiconst.TOPRIGHT)
        self.searchBar.ReloadFunction = self.PopulateOwnerScroll
        self.settingMenu = MenuButtonIcon(parent=filterContainer, align=uiconst.CENTERRIGHT, texturePath=eveicon.bars_sort_ascending, iconSize=16, pos=(self.searchBar.width + 8,
         0,
         18,
         18), get_menu_func=standingsFilterSettings.get_menu, hint=localization.GetByLabel('UI/Common/SortBy'))
        self.rightCont = Container(parent=self, padLeft=2)
        self.standingBar = StandingsBar(parent=self, align=uiconst.TOTOP, height=72, padding=(4, 0, 6, 0), idx=0)
        self.ConstructLeftCont()
        self.ConstructRightCont()
        sm.RegisterNotify(self)
        standingsConst.STANDING_SORT_SETTING.on_change.connect(self.OnSortingSettingChanged)

    def ConstructRightCont(self):
        self.standingsHeader = StandingsHeader(parent=self.rightCont, align=uiconst.TOTOP, height=64, padRight=6)
        if idCheckers.IsCorporation(self.toID):
            self.compositionDescription = Label(name='CompositionDescriptionLabel', parent=self.rightCont, align=uiconst.TOTOP, padding=(0, 6, 2, 6), text=localization.GetByLabel('UI/Standings/CompositionWindow/NPCToPlayerCorp'))
            scrollClass = StandingCompositionScroll
        else:
            self.graphResizeCont = DragResizeCont(parent=self.rightCont, align=uiconst.TOTOP, minSize=60, maxSize=250, defaultSize=150, settingsID='StandingsPanelRight')
            self.standingsGraph = StandingsGraph(parent=self.graphResizeCont.mainCont, align=uiconst.TOALL, padTop=3, padBottom=3)
            scrollClass = StandingsHistoryScroll
        self.standingsScroll = scrollClass(parent=self.rightCont, align=uiconst.TOALL, ownerID=self.fromID)

    def ConstructLeftCont(self):
        self.scroll = Scroll(parent=self.leftCont.mainCont, padding=(0, 0, 0, 0), multiSelect=False)
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.sr.id = 'charsheet_standings'

    def OnScrollSelectionChange(self, nodes):
        if not nodes:
            return
        self.standingData = nodes[0].standingData
        if self.standingData.GetOwnerID2() == self.fromID:
            return
        self.fromID = self.standingData.GetOwnerID2()
        self.toID = self.standingData.GetOwnerID1()
        self.UpdateSelectedEntry()

    def UpdateStandingsScroll(self):
        if idCheckers.IsCorporation(self.toID):
            transactions = self.GetStandingsCompositions()
        else:
            transactions = self.GetStandingsTransactions()
            if transactions:
                self.graphResizeCont.Show()
                self.standingsGraph.Update(self.fromID, self.toID, transactions)
            else:
                self.graphResizeCont.Hide()
        self.standingsScroll.Update(transactions, self.fromID)

    def UpdateSelectedEntry(self):
        self.standingsHeader.Update(self.standingData)
        self.UpdateStandingsScroll()
        self.standingBar.Update(self.fromID, self.toID)

    def GetStandingsTransactions(self):
        return sm.GetService('standing').GetStandingTransactions(self.fromID, self.toID)

    def GetStandingsCompositions(self):
        return sm.GetService('standing').GetStandingCompositions(self.fromID, self.toID)

    def Load(self, *args):
        self.LoadPanel()

    def LoadPanel(self, *args):
        self.PopulateOwnerScroll()
        ownerIDFromSettings = settings.char.ui.Get(STANDING_SETTING_CONFIG_NAME, None)
        standingNodes = []
        nodes = self.scroll.GetNodes()
        for node in nodes:
            ownerID = node.standingData and node.standingData.GetOwnerID2()
            if ownerID is None:
                continue
            standingNodes.append(node)
            if ownerID == ownerIDFromSettings:
                self.SelectEntry(ownerID)
                return

        if standingNodes:
            self.scroll.SelectNode(standingNodes[0])

    def PopulateOwnerScroll(self):
        standingSvc = sm.GetService('standing')
        if self.toID == session.charid:
            standings = standingSvc.GetStandingsDataNPCsToMyCharacter()
        else:
            standings = standingSvc.GetStandingsDataNPCsToMyCorp()
        searchText = self.searchBar.GetValue().lower()
        scrolllist = GetStandingScrollGroups(standings, self.toID, searchText=searchText)
        scrolllist = standingsFilterSettings.get_nodes_sorted(scrolllist)
        self.scroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Standings/NoResultsFound'))

    def OnSortingSettingChanged(self, *args):
        self._ApplyScrollSorting()

    def _ApplyScrollSorting(self):
        nodes = standingsFilterSettings.get_nodes_sorted(self.scroll.GetNodes())
        self.scroll.SetNodes(nodes)
        self.scroll.ReloadNodes()

    def SelectEntry(self, ownerID):
        if sm.GetService('standing').AppendZeroStandingIfNeeded(ownerID):
            self.PopulateOwnerScroll()
        for node in self.scroll.GetNodes():
            if node.standingData and node.standingData.GetOwnerID2() == ownerID:
                self.standingData = node.standingData
                self.fromID = ownerID
                self.scroll.SetSelected(node.idx)
                self.scroll.ScrollToSelectedNode()
                self.UpdateSelectedEntry()
                break

    def OnStandingNotificationClicked(self, entryToOpen):
        self.SelectEntry(entryToOpen)

    def OnNPCStandingsClicked(self, ownerID):
        self.SelectEntry(ownerID)

    def OnNPCStandingChange(self, fromID, newStandingsValue, oldStandingsValue):
        if fromID == self.fromID:
            self.PopulateOwnerScroll()
            self.SelectEntry(self.fromID)

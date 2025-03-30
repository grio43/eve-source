#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\browserSkyhooks.py
import threadutils
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.structure.structureBrowser.controllers.filterContController import FilterContControllerSkyhook
from eve.client.script.ui.structure.structureBrowser.entries.skyhookEntry import SkyhookEntry
from eve.client.script.ui.structure.structureBrowser.filterCont import FilterContMySkyhooks
from eve.client.script.ui.structure.structureBrowser.filterContUtil import IsFilteredOutByText
from localization import GetByLabel
OWNER_ANY = 1
OWNER_NPC = 2
OWNER_CORP = 3

class BrowserAllSkyhooks(Container):
    default_name = 'BrowserAllSkyhooks'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.skyhookController
        self.filterContController = FilterContControllerSkyhook()
        self.filterContController.on_filters_changed.connect(self._OnFiltersChanged)
        self.isInitialized = False

    def OnTabSelect(self):
        self.LoadPanel()

    def LoadPanel(self):
        self.display = True
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.comboCont = FilterContMySkyhooks(name='filterCont', parent=self, filterContController=self.filterContController, padBottom=8)
        self.scroll = Scroll(parent=self, id='mySkyhookScroll')
        self.scroll.GetTabStops = self.GetTabStops
        self.UpdateScroll()

    def GetTabStops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, SkyhookEntry, idx=idx)

    @threadutils.throttled(0.5)
    def UpdateScroll(self):
        if not self.isInitialized:
            return
        self.scroll.ShowLoading()
        scrollList, somethingFilteredOut = self.GetScrollList()
        if somethingFilteredOut:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFoundWithFilters')
        else:
            noContentHint = GetByLabel('UI/Structures/Browser/NoStructuresFound')
        self.scroll.LoadContent(contentList=scrollList, headers=SkyhookEntry.GetHeaders(), noContentHint=noContentHint)
        self.scroll.HideLoading()

    def IsFilteredOut(self, skyhookController):
        if self._IsFilteredOutByText(skyhookController):
            return True
        if self._IsFilteredOutByLocation(skyhookController):
            return True
        if self._IsFilteredOutByState(skyhookController):
            return True
        if self._IsFilteredOutByTheftVulnerability(skyhookController):
            return True
        return False

    def _IsFilteredOutByText(self, skyhookController):
        filterText = self.filterContController.GetTextFilter()
        return IsFilteredOutByText(skyhookController, filterText)

    def _IsFilteredOutByLocation(self, skyhookController):
        locationOption = self.filterContController.GetSelectedLocationOption()
        if locationOption is None:
            return False
        if locationOption == 1:
            return skyhookController.GetSolarSystemID() != session.solarsystemid2
        if locationOption == -1:
            regionID = self.filterContController.GetSelectedRegionOption() or session.regionid
            return skyhookController.GetRegionID() != regionID
        return skyhookController.GetNumJumps() > locationOption

    def _IsFilteredOutByState(self, skyhookController):
        stateOption = self.filterContController.GetSelectedStateOption()
        if stateOption is None:
            return False
        isVulnerable = skyhookController.IsVulnerable()
        if stateOption == 'vulnerable':
            return not isVulnerable
        if stateOption == 'reinforced':
            return isVulnerable
        return False

    def _IsFilteredOutByTheftVulnerability(self, skyhookController):
        stateOption = self.filterContController.GetSelectedTheftVulnerabilityOption()
        if stateOption is None:
            return False
        isVulnerable = skyhookController.IsTheftVulnerable()
        if stateOption == 'vulnerable':
            return not isVulnerable
        if stateOption == 'secure':
            return isVulnerable
        return False

    def GetScrollList(self):
        scrollList = []
        skyhookControllers = self.controller.GetMySkyhooks()
        somethingFilteredOut = False
        for controller in skyhookControllers:
            if self.IsFilteredOut(controller):
                somethingFilteredOut = True
                continue
            node = Bunch(controller=controller, decoClass=SkyhookEntry, columnSortValues=SkyhookEntry.GetColumnSortValues(controller), charIndex=controller.GetName(), GetSortValue=SkyhookEntry.GetSortValue)
            scrollList.append(node)

        return (scrollList, somethingFilteredOut)

    def _OnFiltersChanged(self):
        self.UpdateScroll()

    def Close(self):
        if self.filterContController:
            self.filterContController.on_filters_changed.disconnect(self._OnFiltersChanged)
        self.controller = None
        self.filterContController = None
        super(BrowserAllSkyhooks, self).Close()

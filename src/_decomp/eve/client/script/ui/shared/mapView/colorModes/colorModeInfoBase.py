#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\colorModes\colorModeInfoBase.py
import weakref
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.searchinput import SearchInput
from eve.client.script.ui.shared.mapView.mapViewSearch import SearchResultEntry
from eve.client.script.ui.util import searchUtil
from localization import GetByLabel

class ColorModeInfoBase(Container):
    default_align = uiconst.TOLEFT_NOPUSH
    default_width = 220
    default_padLeft = 8
    default_padTop = 8
    searchHandler = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.activeFilter = None
        self.headerLabel = EveLabelLarge(parent=self, align=uiconst.TOTOP, bold=True)
        self.resultLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP)
        showInAgencyCont = ContainerAutoSize(name='showInAgencyCont', parent=self, align=uiconst.TOTOP, padTop=10)
        self.showInAgencyBtn = Button(parent=showInAgencyCont, align=uiconst.TOPLEFT, label=GetByLabel('UI/Agency/ShowInAgency'), hint=GetByLabel('UI/Agency/ShowInAgencyHint'), texturePath='res:/UI/Texture/WindowIcons/theAgency.png', state=uiconst.UI_HIDDEN, func=self.OnShowInAgencyBtn)
        self.mapView = weakref.proxy(attributes.mapView)

    def LoadColorModeInfo(self, filter):
        if not self.mapView:
            return
        self.activeFilter = filter
        self.headerLabel.text = filter.GetName()
        self.resultLabel.text = filter.GetHint()
        if filter.GetAgencyContentGroupID():
            self.showInAgencyBtn.Show()
        else:
            self.showInAgencyBtn.Hide()

    def OnShowInAgencyBtn(self, *args):
        if self.activeFilter:
            from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
            AgencyWndNew.OpenAndShowContentGroup(self.activeFilter.GetAgencyContentGroupID())


class ColorModeInfoSearchBase(Container):
    default_align = uiconst.TOTOP
    default_height = 32
    settingsKey = None
    searchFor = None
    searchString = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapView = weakref.ref(attributes.mapView)
        searchInput = SearchInput(name=self.settingsKey, parent=self, align=uiconst.TOTOP, width=0, maxLength=64, GetSearchEntries=self.GetSearchData, OnSearchEntrySelected=self.OnSearchEntrySelected, OnReturn=self.OnSearchInputConfirm, hintText=GetByLabel('UI/Common/Buttons/Search'))
        searchInput.searchResultVisibleEntries = 10
        searchInput.SetHistoryVisibility(False)
        searchInput.ShowClearButton()
        searchInput.SetValue(settings.char.ui.Get('%s_searchString' % self.settingsKey, None))
        self.searchInput = searchInput

    def GetSearchData(self, searchString):
        searchString = searchString.lstrip()
        settings.char.ui.Set('%s_searchString' % self.settingsKey, searchString)
        if searchString == self.searchString:
            return self.scrollListResult
        self.searchString = searchString
        if len(searchString) >= 3:
            self.searchInput.SetValue(searchString, docallback=False)
            scrollList = searchUtil.GetResultsScrollList(searchString, self.searchFor)
            self.scrollListResult = self.PrepareResultScrollEntries(scrollList, searchString)
        else:
            self.scrollListResult = []
            self.OnSearchCleared()
        return self.scrollListResult

    def PrepareResultScrollEntries(self, results, searchString, *args):
        scrollList = []
        if not results:
            scrollList.append(ScrollEntryNode(label=GetByLabel('UI/Search/UniversalSearch/NoResultsReturned', searchStr=searchString)))
        else:
            for groupEntry in results:
                entryType, typeList = groupEntry['groupItems']
                for entryData in typeList:
                    scrollList.append(ScrollEntryNode(decoClass=SearchResultEntry, **entryData))

        return scrollList

    def OnSearchInputConfirm(self, *args, **kwds):
        if self.scrollListResult and len(self.scrollListResult) == 1:
            self.OnSearchEntrySelected(self.scrollListResult)

    def OnSearchEntrySelected(self, *args, **kwds):
        pass

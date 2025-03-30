#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewSearch.py
import eveformat
import localization
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import ScrollEntryNode, SE_BaseClassCore
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.searchinput import SearchInput
import weakref
import evetypes
import uthread
from eve.client.script.ui.util import searchUtil
from eve.common.script.search import const as search_const
from eveexceptions import UserError
from localization import GetByLabel
from carbonui.uicore import uicore
from eveservices.menu import StartMenuService

class MapViewSearchControl(Container):
    default_align = uiconst.TOPLEFT
    default_width = 160
    default_height = 20
    searchInput = None
    searchResult = None
    searchFor = None
    mapView = None
    scrollListResult = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        if attributes.mapView:
            self.mapView = weakref.ref(attributes.mapView)
        self.icon = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/searchMagnifyingGlass.png', pos=(0, 0, 24, 24), state=uiconst.UI_NORMAL, iconSize=24)
        self.icon.OnClick = self.ClickIcon
        self.searchFor = [search_const.ResultType.constellation,
         search_const.ResultType.solar_system,
         search_const.ResultType.region,
         search_const.ResultType.station]
        searchInput = SearchInput(name='MapViewSearchEdit', parent=self, align=uiconst.TOPRIGHT, width=0, maxLength=64, GetSearchEntries=self.GetSearchData, OnSearchEntrySelected=self.OnSearchEntrySelected, OnReturn=self.OnSearchInputConfirm, OnResultMenuClosed=self.OnResultMenuClosed, hintText=GetByLabel('UI/Common/Buttons/Search'), opacity=0.0, setvalue=settings.char.ui.Get('mapView_searchString', None))
        searchInput.searchResultVisibleEntries = 10
        searchInput.SetHistoryVisibility(False)
        searchInput.OnFocusLost = self.OnSearchFocusLost
        self.searchInput = searchInput

    def ClickIcon(self, *args):
        self.ShowInput()

    def OnSearchFocusLost(self, *args):
        if not self.searchInput.HasResultMenu():
            self.HideInput()

    def OnResultMenuClosed(self, *args):
        if uicore.registry.GetFocus() is not self.searchInput:
            self.HideInput()

    def ShowInput(self):
        uicore.registry.SetFocus(self.searchInput)
        duration = 0.2
        uicore.animations.FadeTo(self.searchInput, startVal=self.searchInput.opacity, endVal=1.0, duration=duration)
        uicore.animations.FadeTo(self.icon, startVal=self.icon.opacity, endVal=0.0, callback=self.icon.Hide, duration=duration)
        uicore.animations.MorphScalar(self.searchInput, 'width', startVal=self.searchInput.width, endVal=self.width, duration=duration, callback=self.OnInputScaleDone)

    def HideInput(self):
        duration = 0.4
        uicore.animations.FadeTo(self.searchInput, startVal=self.searchInput.opacity, endVal=0.0, duration=duration)
        self.icon.Show()
        uicore.animations.FadeTo(self.icon, startVal=self.icon.opacity, endVal=1.0, duration=duration)
        uicore.animations.MorphScalar(self.searchInput, 'width', startVal=self.searchInput.width, endVal=0, duration=duration)

    def OnInputScaleDone(self, *args):
        resultMenu = self.searchInput.GetResultMenu()
        if resultMenu:
            l, t, w, h = self.GetAbsolute()
            resultMenu.left = l
        uthread.new(self.searchInput.SearchForData)

    def GetSearchData(self, searchString):
        self.scrollListResult = []
        searchString = eveformat.simple_html_unescape(searchString)
        searchString = searchString.lstrip()
        settings.char.ui.Set('mapView_searchString', searchString)
        if len(searchString) >= 64:
            self.scrollListResult.append(ScrollEntryNode(label=GetByLabel('UI/Common/SearchStringTooLong')))
        elif len(searchString) >= search_const.min_wildcard_length or localization.util.IsTextInConciseLanguage(session.languageID, searchString):
            self.searchInput.SetValue(searchString, docallback=False)
            try:
                results = searchUtil.GetResultsScrollList(searchString, self.searchFor)
            except UserError:
                results = []

            self.scrollListResult = self.PrepareResultScrollEntries(results, searchString)
        return self.scrollListResult

    def PrepareResultScrollEntries(self, results, searchString, *args):
        scrollList = []
        if not results:
            label = GetByLabel('UI/Search/UniversalSearch/NoResultsReturned', searchStr=searchString)
            scrollList.append(ScrollEntryNode(label=label))
        else:
            for groupEntry in results:
                entryType, typeList = groupEntry['groupItems']
                for entryData in typeList:
                    scrollList.append(ScrollEntryNode(decoClass=SearchResultEntry, **entryData))

        return scrollList

    def OnSearchInputConfirm(self, *args, **kwds):
        if self.scrollListResult:
            self.OnSearchEntrySelected(self.scrollListResult[0])

    def OnSearchEntrySelected(self, entry, *args, **kwds):
        self.delaySelectionTimer = AutoTimer(100, self._OnSearchEntrySelectedDelayed, entry)

    def _OnSearchEntrySelectedDelayed(self, entry, *args, **kwds):
        if not entry or not getattr(entry, 'itemID', None):
            return
        self.delaySelectionTimer = None
        if self.mapView:
            mapView = self.mapView()
            if mapView:
                mapView.SetActiveItemID(entry.itemID, zoomToItem=True)


class SearchResultEntry(SE_BaseClassCore):

    def Startup(self, *args):
        self.icon = Sprite(parent=self, pos=(2, 1, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED)
        self.label = EveLabelSmall(parent=self, padding=(20, 3, 4, 0), state=uiconst.UI_DISABLED, align=uiconst.TOTOP)

    def Load(self, node):
        data = node
        self.typeID = data.Get('typeID', None)
        self.itemID = data.Get('itemID', None)
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        self.label.text = data.label
        bracketIconPath = sm.GetService('bracket').GetBracketIcon(self.typeID)
        if bracketIconPath:
            self.icon.texturePath = bracketIconPath
        else:
            groupID = evetypes.GetGroupID(self.typeID)
            if groupID == const.groupRegion:
                self.icon.texturePath = 'res:/UI/Texture/Shared/Brackets/region.png'
            if groupID == const.groupConstellation:
                self.icon.texturePath = 'res:/UI/Texture/Shared/Brackets/constellation.png'
            if groupID == const.groupSolarSystem:
                self.icon.texturePath = 'res:/UI/Texture/Shared/Brackets/solarSystem.png'

    def GetHeight(self, *args):
        node, width = args
        return max(20, EveLabelSmall.MeasureTextSize(text=node.label, width=164)[1] + 5)

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        if self.sr.node:
            uicore.Message('ListEntryEnter')

    def OnClick(self, *args):
        if self.sr.node.Get('selectable', 1):
            self.sr.node.scroll.SelectNode(self.sr.node)
        uicore.Message('ListEntryClick')
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def OnMouseDown(self, *args):
        SE_BaseClassCore.OnMouseDown(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseDown', None):
            self.sr.node.OnMouseDown(self)

    def OnMouseUp(self, *args):
        SE_BaseClassCore.OnMouseUp(self, *args)
        if self.sr.node and self.sr.node.Get('OnMouseUp', None):
            self.sr.node.OnMouseUp(self)

    def GetMenu(self):
        return StartMenuService().CelestialMenu(self.sr.node.itemID)

    @classmethod
    def GetCopyData(cls, node):
        return node.label

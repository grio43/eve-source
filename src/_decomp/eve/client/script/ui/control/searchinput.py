#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\searchinput.py
import random
import weakref
from eve.client.script.ui.shared.userentry import User
import carbonui.const as uiconst
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import IsUnder, GetWindowAbove
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.decorative.menuUnderlay import MenuUnderlay
from eve.client.script.ui.shared.userentry import User

class SearchInput(SingleLineEditText):
    default_name = 'SearchInput'
    scrollPosition = None
    searchString = None
    searchResultMenu = None
    searchResultVisibleEntries = 5
    OnSearchEntrySelected = None
    blockSelection = False
    selectedNode = None

    def ApplyAttributes(self, attributes):
        SingleLineEditText.ApplyAttributes(self, attributes)
        self.OnChange = self.OnSearchInputChange
        self.GetSearchEntries = attributes.GetSearchEntries
        self.OnSearchEntrySelected = attributes.OnSearchEntrySelected
        self.CloseMenuCallback = attributes.OnResultMenuClosed
        self.allowBrowsing = attributes.Get('allowBrowsing', False)
        uicore.uilib.RegisterForTriuiEvents([uiconst.UI_MOUSEDOWN], self.OnGlobalMouseDown)

    def Close(self):
        self.OnSearchEntrySelected = None
        self.GetSearchEntries = None
        self.CloseMenuCallback = None
        self.OnInsert = None
        self.searchThread = None
        self.CloseResultMenu()
        super(SearchInput, self).Close()

    def HasResultMenu(self):
        if self.searchResultMenu:
            searchResultMenu = self.searchResultMenu()
            if searchResultMenu and not searchResultMenu.destroyed:
                return True
        return False

    def CloseResultMenu(self):
        if self.searchResultMenu:
            searchResultMenu = self.searchResultMenu()
            if searchResultMenu and not searchResultMenu.destroyed:
                self.scrollPosition = (self.searchString, searchResultMenu.searchScroll.GetScrollProportion())
                searchResultMenu.Close()
            self.searchResultMenu = None
            if self.CloseMenuCallback:
                self.CloseMenuCallback()

    def OnSearchInputChange(self, *args, **kwds):
        if not self.GetValue():
            self.searchThread = None
            self.SearchForData()
        else:
            self.searchThread = AutoTimer(280, self.SearchForData)

    def SearchForData(self):
        self.searchThread = None
        if self.GetSearchEntries:
            searchString = self.GetValue()
            self.searchString = searchString
            if self.isCharacterField and not self.ValidateSearchString(searchString):
                return
            valid = self.GetSearchEntries(searchString)
            self.ShowSearchResult(valid)

    def ValidateSearchString(self, searchString):
        splitString = searchString.split()
        if any((len(i) >= 3 for i in splitString)):
            return True
        return False

    def ShowSearchResult(self, result):
        searchResultMenu = None
        if self.searchResultMenu:
            searchResultMenu = self.searchResultMenu()
            if searchResultMenu and searchResultMenu.destroyed:
                searchResultMenu = None
        if not result:
            self.CloseResultMenu()
            return
        if not searchResultMenu:
            l, t, w, h = self.GetAbsolute()
            searchResultMenu = Container(name='resultMenuParent', parent=uicore.layer.utilmenu, pos=(l,
             t + h + 1,
             max(w, 200),
             300), align=uiconst.TOPLEFT, opacity=0.0)
            searchResultMenu.searchScroll = Scroll(parent=searchResultMenu, align=uiconst.TOALL, padding=1, multiSelect=0 if self.allowBrowsing else 0)
            if self.OnSearchEntrySelected:
                searchResultMenu.searchScroll.OnSelectionChange = self.OnSelectionChanged
            MenuUnderlay(bgParent=searchResultMenu)
            self.searchResultMenu = weakref.ref(searchResultMenu)
            self.updateThread = AutoTimer(1, self.UpdateDropdownState)
            startHeight = 0
        else:
            startHeight = searchResultMenu.height
        if self.scrollPosition and self.searchString == self.scrollPosition[0]:
            scrollTo = self.scrollPosition[1]
        else:
            scrollTo = 0.0
        self.scrollTo = scrollTo
        searchResultMenu.searchScroll.LoadContent(contentList=result, scrollTo=scrollTo)
        for node in searchResultMenu.searchScroll.sr.nodes:
            node['OnClick'] = self.OnSearchEntrySelected

        visibleEntriesHeight = sum([ node.height for node in searchResultMenu.searchScroll.sr.nodes[:self.searchResultVisibleEntries] ])
        endHeight = min(searchResultMenu.searchScroll.GetContentHeight(), visibleEntriesHeight) + 4
        uicore.animations.MorphScalar(searchResultMenu, 'height', startVal=startHeight, endVal=endHeight, duration=0.25, callback=self.SetScrollPosition)
        uicore.animations.FadeTo(searchResultMenu, startVal=searchResultMenu.opacity, endVal=1.0, duration=0.5)

    def SetScrollPosition(self, *args, **kwds):
        if self.searchResultMenu:
            searchResultMenu = self.searchResultMenu()
            if searchResultMenu and not searchResultMenu.destroyed:
                uthread.new(searchResultMenu.searchScroll.ScrollToProportion, self.scrollTo)

    def GetResultMenu(self):
        if self.searchResultMenu:
            searchResultMenu = self.searchResultMenu()
            if searchResultMenu and not searchResultMenu.destroyed:
                return searchResultMenu

    def UpdateDropdownState(self):
        if self.destroyed:
            self.updateThread = None
            return
        if not (self.searchResultMenu and self.searchResultMenu()):
            self.updateThread = None
            return
        wnd = GetWindowAbove(self)
        activeWindow = uicore.registry.GetActive()
        if wnd and wnd is not activeWindow and activeWindow is not uicore.desktop:
            self.CloseResultMenu()
            return

    def GetSearchEntriesDemo(self, searchString):
        if not searchString:
            return []
        entries = []
        for i in xrange(random.choice([0,
         2,
         4,
         8,
         16])):
            entries.append(GetFromClass(User, {'charID': session.charid}))

        return entries

    def OnSelectionChanged(self, *args, **kwds):
        if self.allowBrowsing:
            self.selectedNode = args[0]
        elif not self.blockSelection and self.OnSearchEntrySelected:
            self.OnSearchEntrySelected(*args, **kwds)

    def OnMouseDown(self, *args, **kwds):
        SingleLineEditText.OnMouseDown(self, *args, **kwds)
        self.selectedNode = None
        uthread.new(self.SearchForData)

    def OnGlobalMouseDown(self, *args):
        if self.destroyed:
            return False
        self.blockSelection = False
        searchResultMenu = self.searchResultMenu
        if searchResultMenu and searchResultMenu():
            for layer in (uicore.layer.utilmenu, uicore.layer.menu):
                if IsUnder(uicore.uilib.mouseOver, layer):
                    if uicore.uilib.rightbtn:
                        self.blockSelection = True
                    return True

            self.CloseResultMenu()
        return True

    def OnKeyDown(self, vkey, flag):
        if vkey in (uiconst.VK_DOWN, uiconst.VK_UP):
            if self.searchResultMenu:
                searchResultMenu = self.searchResultMenu()
                if searchResultMenu and not searchResultMenu.destroyed:
                    if vkey == uiconst.VK_UP:
                        searchResultMenu.searchScroll.OnUp()
                    else:
                        searchResultMenu.searchScroll.OnDown()
        if vkey == uiconst.VK_RETURN:
            if not self.selectedNode:
                return
            self.OnSearchEntrySelected(self.selectedNode)
        SingleLineEditText.OnKeyDown(self, vkey, flag)

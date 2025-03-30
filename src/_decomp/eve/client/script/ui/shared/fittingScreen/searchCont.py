#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\searchCont.py
from carbonui.primitives.container import Container
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.fittingScreen import BROWSER_SEARCH_CHARGE, BROWSER_SEARCH_FITTINGS, BROWSER_SEARCH_MODULES
from localization import GetByLabel
import carbonui.const as uiconst
FITTING_MODE = 0
HARDWARE_MODE = 1
CHARGE_MODE = 2

class SearchCont(Container):
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.searchFunc = attributes.searchFunc
        self.collapseFunc = attributes.collapseFunc
        self.searchMode = None
        self.configValue = ''
        ButtonIcon(name='collapse', parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 24, 24), iconSize=12, texturePath='res:/UI/Texture/classes/Scroll/Collapse.png', func=self.CollapseAll, hint=GetByLabel('UI/Common/Buttons/CollapseAll'))
        self.searchInput = QuickFilterEdit(name='searchField', parent=self, setvalue='', hintText=GetByLabel('UI/Common/Search'), pos=(0, 0, 18, 0), padLeft=28, padRight=0, maxLength=64, align=uiconst.TOTOP, OnClearFilter=self.Search, isTypeField=True)
        self.searchInput.OnReturn = self.Search
        self.searchInput.ReloadFunction = self.Search

    def ChangeSearchMode(self, searchMode):
        if self.searchMode == searchMode:
            return
        self.searchMode = searchMode
        if searchMode == HARDWARE_MODE:
            self.configValue = BROWSER_SEARCH_MODULES
        elif searchMode == CHARGE_MODE:
            self.configValue = BROWSER_SEARCH_CHARGE
        else:
            self.configValue = BROWSER_SEARCH_FITTINGS
        searchString = settings.user.ui.Get(self.configValue, '')
        self.searchInput.SetValue(searchString, docallback=False)

    def Search(self):
        searchString = self.searchInput.GetValue()
        settingConfig = self.configValue
        self.searchFunc(settingConfig, searchString)

    def CollapseAll(self, *args):
        if self.collapseFunc:
            self.collapseFunc(self.configValue)

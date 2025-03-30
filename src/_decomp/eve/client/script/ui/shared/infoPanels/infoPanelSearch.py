#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelSearch.py
from carbonui import uiconst
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_SEARCH_INFO_PANEL
from eve.client.script.ui.util import searchUtil
from eve.common.script.search import const as search_const
from localization import GetByLabel
from uihider import UiHiderMixin

class InfoPanelSearch(UiHiderMixin, InfoPanelBase):
    default_name = 'InfoPanelSearch'
    uniqueUiName = UNIQUE_NAME_SEARCH_INFO_PANEL
    panelTypeID = infoPanelConst.PANEL_SEARCH
    label = 'UI/Search/SearchNewEden'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/search.png'
    default_isModeFixed = True
    hasSettings = False
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnSetSearchBarFocus']

    def ApplyAttributes(self, attributes):
        super(InfoPanelSearch, self).ApplyAttributes(attributes)
        self.loadingWheel = LoadingWheel(parent=self.headerBtnCont, align=uiconst.CENTERRIGHT, pos=(6, 0, 16, 16), state=uiconst.UI_DISABLED, opacity=0.0)
        self.searchEdit = SingleLineEditText(name='searchEdit', parent=self.headerCont, align=uiconst.TOALL, OnSetFocus=self.OnEditSetFocus, OnFocusLost=self.OnEditFocusLost, OnReturn=self.Search, width=0, padding=(0, 2, 0, 2), hintText=GetByLabel('UI/Search/SearchForAnything'))
        self.headerButton.Enable()
        self.headerButton.OnClick = self.Search

    def ConstructHeaderButton(self):
        return self.ConstructSimpleHeaderButton()

    def Search(self, *args):
        text = self.searchEdit.text
        if not text:
            return
        self.searchEdit.RegisterHistory()
        duration = 0.15
        animations.FadeIn(self.loadingWheel, duration=duration)
        animations.FadeOut(self.headerButton, duration=duration)
        try:
            searchUtil.GetResultsInNewWindow(self.searchEdit.GetText(), search_const.all_result_types, includeUiElements=True)
        finally:
            self.searchEdit.Clear()
            animations.FadeOut(self.loadingWheel, duration=duration)
            animations.FadeIn(self.headerButton, duration=duration)

    def OnEditFocusLost(self, *args):
        if not self.searchEdit.text:
            self.searchEdit.Clear()

    def OnEditSetFocus(self, *args):
        self.searchEdit.Clear()

    def OnSetSearchBarFocus(self):
        uicore.registry.SetFocus(self.searchEdit)

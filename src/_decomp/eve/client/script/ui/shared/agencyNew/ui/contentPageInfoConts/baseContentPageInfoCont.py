#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPageInfoConts\baseContentPageInfoCont.py
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.systemInfoContainer import SystemInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.controls.agencyScrollContEntry import AgencyScrollContEntry
from carbonui.control.section import Section
from localization import GetByLabel

class BaseContentPageInfoContainer(Section):
    default_name = 'BaseContentPageInfoContainer'
    default_padLeft = 10
    default_padRight = 10
    default_align = uiconst.TOLEFT
    default_scroll_container_height = 150
    default_width = 400

    def ApplyAttributes(self, attributes):
        super(BaseContentPageInfoContainer, self).ApplyAttributes(attributes)
        self.contentPiece = attributes.contentPiece
        self.clickedEntry = None
        self.primaryActionButton = None
        self.bottomCont = None
        self.buttonRowCont = None
        self.scrollEntries = []
        self.isEmpty = True
        if not self.contentPiece:
            self.ConstructEmptyState()
        else:
            self.Initialize()

    def Initialize(self):
        self.Flush()
        self.ConstructBaseLayout()
        self.ConstructLayout()
        self.isEmpty = False

    def ConstructBaseLayout(self):
        self.ConstructSystemInfoContainer()
        self.ConstructButtonContainer()

    def ConstructLayout(self):
        self.ConstructScroll()

    def UpdateContentPiece(self, contentPiece):
        if not contentPiece:
            self.Empty()
            return
        if self.isEmpty:
            self.Initialize()
        self.contentPiece = contentPiece
        self._UpdateContentPiece(contentPiece)

    def Empty(self):
        self.Flush()
        self.isEmpty = True
        self.ConstructEmptyState()

    def _UpdateContentPiece(self, contentPiece):
        if not self.systemInfoContainer:
            return
        self.systemInfoContainer.UpdateContentPiece(contentPiece)
        if not self.primaryActionButton:
            return
        self.primaryActionButton.SetController(contentPiece)
        self.UpdateScroll()

    def ConstructEmptyState(self):
        pass

    def ConstructButtonContainer(self):
        self.buttonRowCont = Container(name='buttonRowContainer', parent=self, align=uiconst.TOBOTTOM, padTop=10, height=30, idx=0)
        self.primaryActionButton = StatefulButton(parent=self.buttonRowCont, align=uiconst.CENTERRIGHT, iconAlign=uiconst.TORIGHT)

    def ConstructSystemInfoContainer(self):
        self.systemInfoContainer = SystemInfoContainer(name='systemInfoContainer', parent=self, align=uiconst.TOTOP, height=22, padBottom=10)
        self.systemInfoContainer.Hide()

    def ConstructScroll(self):
        self.scrollParent = Container(name='scrollParent', parent=self, align=uiconst.TOTOP, height=self.default_scroll_container_height)
        self.scrollCont = ScrollContainer(name='scrollCont', parent=self.scrollParent, align=uiconst.TOALL, showUnderlay=True)
        self.scrollLoadingWheel = LoadingWheel(name='infoContLoadingWheel', parent=self.scrollParent, align=uiconst.CENTER)
        self.HideLoadingWheel()

    def ShowLoadingWheel(self):
        self.scrollLoadingWheel.Show()

    def HideLoadingWheel(self):
        self.scrollLoadingWheel.Hide()

    def ConstructScrollEntries(self, contentPieces):
        contentPieces = sorted(contentPieces, key=lambda contentPiece: contentPiece.GetCardSortValue())
        for contentPiece in contentPieces:
            self.ConstructScrollEntry(contentPiece)

    def ConstructScrollEntry(self, contentPiece):
        entry = self._GetScrollEntryClass()(name=contentPiece.GetName(), parent=self.scrollCont, contentPiece=contentPiece)
        self.scrollEntries.append(entry)
        entry.on_clicked.connect(self.OnScrollEntryClicked)
        return entry

    def _GetScrollEntryClass(self):
        return AgencyScrollContEntry

    def GetEntryContentPieces(self):
        raise NotImplementedError

    def AnimEnterScrollEntries(self):
        for i, entry in enumerate(self.scrollCont.mainCont.children):
            entry.AnimEnter(i)

    def UpdateScroll(self):
        self.scrollCont.Flush()
        self.scrollCont.ScrollToVertical(0)
        self.scrollLoadingWheel.Show()
        self.scrollEntries = []
        contentPieces = self.GetEntryContentPieces()
        if contentPieces:
            self.ConstructScrollEntries(contentPieces)
        if self.scrollEntries:
            self.scrollEntries[0].OnClick()
        else:
            self.scrollCont.ShowNoContentHint(self.GetNoContentHint())
        self.scrollLoadingWheel.Hide()
        self.AnimEnterScrollEntries()

    def GetNoContentHint(self):
        return GetByLabel('UI/Common/NothingFound')

    def OnScrollEntryClicked(self, clickedEntry):
        self.clickedEntry = clickedEntry
        for entry in self.scrollEntries:
            if entry == clickedEntry:
                entry.OnSelect()
            else:
                entry.OnDeselect()

        if self.primaryActionButton:
            self.primaryActionButton.SetController(clickedEntry.contentPiece)
        if self.bottomCont:
            self.bottomCont.Show()
            animations.FadeTo(self.bottomCont, 0.0, 1.0, duration=0.3)
        animations.FadeTo(self.buttonRowCont, 0.0, 1.0, duration=0.3)
        if self.buttonRowCont:
            animations.FadeTo(self.buttonRowCont, 0.0, 1.0, duration=0.3)

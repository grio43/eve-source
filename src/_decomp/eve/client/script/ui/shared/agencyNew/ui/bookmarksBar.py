#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\bookmarksBar.py
import eveicon
import uthread2
from carbonui import ButtonVariant, TextColor, uiconst
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.agencyNew import agencyBookmarks, agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupProvider
from localization import GetByLabel

class BookmarksBar(Container):
    default_name = 'BookmarksBar'
    default_height = 32

    def ApplyAttributes(self, attributes):
        super(BookmarksBar, self).ApplyAttributes(attributes)
        self.currContentGroup = None
        self.bookmarkEntries = []
        self.ConstructLeftCont()
        self.bookmarksContainer = ContainerAutoSize(name='bookmarksContainer', parent=self, left=24, align=uiconst.TOLEFT)
        self.ReconstructBookmarkEntries()
        agencySignals.on_bookmarks_changed.connect(self.OnBookmarksChanged)
        agencySignals.on_content_group_selected.connect(self.OnContentGroupSelected)
        agencySignals.on_content_pieces_invalidated.connect(self.OnContentPiecesInvalidated)

    def OnContentPiecesInvalidated(self, contentGroupID = None):
        self.UpdateBookmarkEntryStates()

    def OnContentGroupSelected(self, contentGroupID, itemID = None, *args, **kwargs):
        self.currContentGroup = contentGroupProvider.GetContentGroup(contentGroupID, itemID)
        self.CheckEnableAddBookmarkButton()

    def CheckEnableAddBookmarkButton(self):
        numBookmarks = len(agencyBookmarks.GetBookmarks())
        if not self.currContentGroup.IsBookmarkable():
            self.addBookmarkBtn.Disable()
            self.addBookmarkBtn.SetHint(GetByLabel('UI/Agency/pageNotBookmarkable'))
        elif numBookmarks >= agencyBookmarks.MAX_NUM_BOOKMARKS:
            self.addBookmarkBtn.Disable()
            self.addBookmarkBtn.SetHint(GetByLabel('UI/Agency/maxBookmarksReached'))
        else:
            self.addBookmarkBtn.SetHint(None)
            self.addBookmarkBtn.Enable()

    def OnBookmarksChanged(self, *args):
        self.ReconstructBookmarkEntries()
        self.CheckEnableAddBookmarkButton()

    def ConstructLeftCont(self):
        self.leftCont = ContainerAutoSize(name='leftCont', parent=self, align=uiconst.TOLEFT)
        self.addBookmarkBtn = Button(parent=ContainerAutoSize(parent=self.leftCont, align=uiconst.TOLEFT), align=uiconst.CENTERLEFT, texturePath=eveicon.add, label=GetByLabel('UI/Agency/AddBookmark'), func=agencySignals.on_add_bookmark_button, args=(), variant=ButtonVariant.GHOST)

    def ReconstructBookmarkEntries(self):
        self.bookmarksContainer.Flush()
        self.bookmarkEntries = []
        contentGroupIDs = self.GetContentGroupIDsSorted()
        numBookmarks = len(contentGroupIDs)
        for i, contentGroupID in enumerate(contentGroupIDs):
            self.ConstructBookmarkEntry(contentGroupID, i, numBookmarks)

    def GetContentGroupIDsSorted(self):
        contentGroupIDs = agencyBookmarks.GetBookmarks()
        return sorted(contentGroupIDs, key=self._GetSortKey)

    def _GetSortKey(self, contentGroupID):
        return contentGroupProvider.GetContentGroup(contentGroupID).GetName()

    def ConstructBookmarkEntry(self, contentGroupID, i, numBookmarks):
        bookmarkEntry = BookmarkEntry(parent=self.bookmarksContainer, align=uiconst.TOLEFT, padRight=24, contentGroupID=contentGroupID)
        self.bookmarkEntries.append(bookmarkEntry)
        bookmarkEntry.SetSizeAutomatically()

    def Close(self):
        super(BookmarksBar, self).Close()
        agencySignals.on_bookmarks_changed.disconnect(self.OnBookmarksChanged)

    def UpdateBookmarkEntryStates(self):
        for bookmarkEntry in self.bookmarkEntries:
            bookmarkEntry.UpdateState()


class BookmarkEntry(ContainerAutoSize):
    default_name = 'BookmarkEntry'
    default_state = uiconst.UI_NORMAL
    default_maxWidth = 115

    def ApplyAttributes(self, attributes):
        super(BookmarkEntry, self).ApplyAttributes(attributes)
        contentGroupID = attributes.contentGroupID
        self.contentGroup = contentGroupProvider.GetContentGroup(contentGroupID)
        self.label = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, text=self.contentGroup.GetName(), autoFadeSides=10)
        self.UpdateState()

    def UpdateState(self):
        if self.IsEnabled():
            self.Enable()
        else:
            self.Disable()

    def IsEnabled(self):
        return self.contentGroup.IsEnabled()

    def OnClick(self, *args):
        if not self.IsEnabled():
            return
        from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=self.contentGroup.GetID())

    def Remove(self, *args):
        agencyBookmarks.RemoveBookmark(self.contentGroup.GetID())

    def GetMenu(self):
        return [(GetByLabel('UI/Commands/Remove'), self.Remove)]

    def OnMouseEnter(self, *args):
        uthread2.StartTasklet(self._OnMouseEnter)

    def _OnMouseEnter(self):
        if not uicore.uilib.mouseOver.IsUnder(self) and uicore.uilib.mouseOver is not self:
            return
        if self.IsEnabled():
            self.label.SetTextColor(TextColor.NORMAL)

    def OnMouseExit(self, *args):
        self.label.SetTextColor(TextColor.SECONDARY)

    def Disable(self, *args):
        self.label.opacity = 0.5

    def Enable(self, *args):
        self.label.opacity = 0.75


class AddBookmarkButton(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(AddBookmarkButton, self).ApplyAttributes(attributes)
        self.isEnabled = True
        bookmarkButtonContainer = Container(name='bookmarkButtonContainer', parent=self, align=uiconst.TOLEFT, width=32)
        Sprite(name='buttonBrackets', parent=bookmarkButtonContainer, align=uiconst.CENTER, width=24, height=24, texturePath='res:/UI/Texture/Shared/DarkStyle/buttonBracket.png', state=uiconst.UI_DISABLED)
        self.button = ButtonIcon(name='addBookmarkButton', parent=bookmarkButtonContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=16, height=16, iconSize=16, texturePath='res:/UI/Texture/classes/CharacterSelection/plus.png', iconColor=ButtonIcon.default_iconColor)
        self.label = EveLabelMedium(name='bookmarkButtonLabel', parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, left=5), align=uiconst.CENTERLEFT, text=GetByLabel('UI/Agency/AddBookmark'))

    def Disable(self, *args):
        self.isEnabled = False
        self.opacity = 0.5

    def Enable(self, *args):
        self.isEnabled = True
        self.opacity = 1.0

    def OnClick(self, *args):
        if not self.isEnabled:
            return
        self.button.OnClick()
        agencySignals.on_add_bookmark_button()

    def OnMouseEnter(self, *args):
        if not self.isEnabled:
            return
        self.button.SetSelected()
        animations.FadeTo(self.label, self.label.opacity, 1.5, duration=0.2)

    def OnMouseExit(self, *args):
        if not self.isEnabled:
            return
        self.button.SetDeselected()
        animations.FadeTo(self.label, self.label.opacity, 1.0, duration=0.2)

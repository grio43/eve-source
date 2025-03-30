#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\locations\window.py
import eveicon
import localization
from carbonui import AxisAlignment, ButtonVariant, Density, uiconst
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.util.various_unsorted import GetWindowAbove
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from carbonui.window.segment.bottom import WindowSegmentBottom
from eve.client.script.ui.shared.bookmarks.bookmarkContainerWindow import BookmarkContainerWindow
from eve.client.script.ui.shared.bookmarks.bookmarkSubfolderWindow import BookmarkSubfolderWindow
from eve.client.script.ui.shared.neocom.addressBook.bookmarksPanel import BookmarksPanel
from eve.client.script.ui.shared.neocom.locations.search import LocationSearchPanel
from uihighlighting.uniqueNameConst import UNIQUE_NAME_BOOKMARKS_TAB

class LocationsWindow(Window):
    default_windowID = 'locations'
    default_captionLabelPath = 'UI/PeopleAndPlaces/Locations'
    default_descriptionLabelPath = 'Tooltips/Neocom/Locations_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/locations.png'
    default_width = 450
    default_height = 450
    default_minSize = (250, 210)
    default_isCompactable = True

    def ApplyAttributes(self, attributes):
        super(LocationsWindow, self).ApplyAttributes(attributes)
        self._locations_panel = LocationsPanel(parent=self.content, align=uiconst.TOALL, compact=self.compact)
        self._search_panel = LocationSearchPanel(parent=self.content, align=uiconst.TOALL)
        self.header.tab_group.AddTab(label=localization.GetByLabel('UI/PeopleAndPlaces/Locations'), panel=self._locations_panel, uniqueName=UNIQUE_NAME_BOOKMARKS_TAB)
        self.header.tab_group.AddTab(label=localization.GetByLabel('UI/Common/Search'), panel=self._search_panel)
        self.header.tab_group.AutoSelect()
        self.on_compact_mode_changed.connect(self._on_window_compact_mode_changed)

    def _on_window_compact_mode_changed(self, window):
        self._locations_panel.compact = self.compact

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()


class LocationsPanel(Container):
    __notifyevents__ = ('OnRefreshBookmarks', 'OnSessionChanged')

    def __init__(self, parent, align, compact = False):
        self._compact = compact
        self._selected = False
        self._bottom_panel = None
        super(LocationsPanel, self).__init__(parent=parent, align=align)
        self._bookmarks_panel = BookmarksPanel(parent=self, align=uiconst.TOALL)
        sm.RegisterNotify(self)

    @property
    def compact(self):
        return self._compact

    @compact.setter
    def compact(self, value):
        if self._compact != value:
            self._compact = value
            self._on_compact_changed()

    def OnRefreshBookmarks(self):
        if self._selected:
            self.update_content()

    def OnSessionChanged(self, isRemote, session, change):
        if session.solarsystemid2 and 'solarsystemid2' in change:
            if self._selected:
                self.update_content()

    def OnTabSelect(self):
        self._selected = True
        self.update_content()

    def OnTabDeselect(self):
        self._selected = False
        self.update_content()

    def update_content(self):
        if not self._selected:
            self._close_bottom_panel()
        else:
            if self._bottom_panel is None:
                self._create_bottom_panel()
            self._bookmarks_panel.RefreshScroll()

    def _create_bottom_panel(self):
        self._bottom_panel = WindowSegmentBottom(window=GetWindowAbove(self))
        button_cont = FlowContainer(parent=self._bottom_panel.content, align=uiconst.TOTOP, autoHeight=True, contentAlignment=AxisAlignment.END, contentSpacing=(8, 8))
        self._create_icon_or_label_button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/PeopleAndPlaces/AddBookmark'), icon=eveicon.location, func=_bookmark_current_location)
        self._create_icon_or_label_button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/PeopleAndPlaces/CreateFolder'), icon=eveicon.add_folder, func=_create_acl_folder)
        self._create_icon_or_label_button(parent=button_cont, align=uiconst.NOALIGN, label=localization.GetByLabel('UI/AclBookmarks/CreateSubfolder'), icon=eveicon.subfolder, func=_create_sub_folder)

    def _close_bottom_panel(self):
        if self._bottom_panel is not None:
            self._bottom_panel.Close()
            self._bottom_panel = None

    def _recreate_bottom_panel(self):
        self._close_bottom_panel()
        self._create_bottom_panel()

    def _create_icon_or_label_button(self, parent, align, label, icon, func):
        if self.compact:
            return ButtonIcon(parent=parent, align=align, width=24, height=24, texturePath=icon, hint=label, func=func, args=())
        else:
            return Button(parent=parent, align=align, label=label, texturePath=icon, func=func, args=(), density=Density.COMPACT, variant=ButtonVariant.GHOST)

    def _on_compact_changed(self):
        if self._selected:
            self._recreate_bottom_panel()


def _bookmark_current_location():
    sm.GetService('addressbook').BookmarkCurrentLocation()


def _create_acl_folder():
    window = BookmarkContainerWindow.Open()
    window.Maximize()


def _create_sub_folder():
    validFolders = sm.GetService('bookmarkSvc').GetFilteredFolders()
    if len(validFolders) == 0:
        if eve.Message('CreateBookmarkFolderAsNoneValid', {}, uiconst.YESNO, uiconst.ID_YES) == uiconst.ID_YES:
            wnd = BookmarkContainerWindow.Open()
            wnd.Maximize()
        return
    wnd = BookmarkSubfolderWindow.Open()
    wnd.Maximize()


def __reload_update__(module):
    try:
        window_class = LocationsWindow
        window = window_class.GetIfOpen()
        if window is not None:
            window.Close()
        window_class.Open()
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Failed to reload window')

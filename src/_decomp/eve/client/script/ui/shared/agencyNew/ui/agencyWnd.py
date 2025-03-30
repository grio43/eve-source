#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\agencyWnd.py
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.agencyNew import agencySignals, agencyBookmarks
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst, contentGroupProvider
from eve.client.script.ui.shared.agencyNew.ui.bookmarksBar import BookmarksBar
from eve.client.script.ui.shared.agencyNew.ui.contentGroupBrowser import ContentGroupBrowser
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from localization import GetByLabel
lastActiveContentGroupIDItemID = None

class AgencyWndNew(Window):
    __guid__ = 'AgencyWndNew'
    default_name = 'AgencyWndNew'
    default_windowID = 'AgencyWndNew'
    uniqueUiName = pConst.UNIQUE_NAME_AGENCY
    default_fixedHeight = 694
    default_height = default_fixedHeight
    default_fixedWidth = 1188
    default_width = default_fixedWidth
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False
    default_isCollapseable = False
    default_captionLabelPath = 'UI/Agency/Caption'
    default_descriptionLabelPath = 'UI/Agency/Description'
    default_iconNum = 'res:/UI/Texture/WindowIcons/theAgency.png'

    def ApplyAttributes(self, attributes):
        super(AgencyWndNew, self).ApplyAttributes(attributes)
        if attributes.contentGroupID:
            contentGroupID = attributes.contentGroupID
            itemID = attributes.itemID
        else:
            contentGroupID, itemID = self._GetLastActiveContentGroupIDItemID()
        videoID = attributes.get('videoID', None)
        self.contentGroup = None
        BookmarksBar(parent=self.sr.main, align=uiconst.TOBOTTOM)
        self.contentGroupBrowser = ContentGroupBrowser(parent=self.sr.main)
        if self.closing:
            return
        agencySignals.on_add_bookmark_button.connect(self.OnAddBookmarkButton)
        agencySignals.on_content_group_selected.connect(self.OnContentGroupSelected)
        if contentGroupProvider.IsContentGroupValid(contentGroupID):
            selectedGroup = contentGroupID
            agencySignals.on_content_group_selected(selectedGroup, itemID=itemID, videoID=videoID)
        else:
            selectedGroup = contentGroupConst.contentGroupHome
            agencySignals.on_content_group_selected(selectedGroup)
        if self.closing:
            return
        rootContentGroup = contentGroupProvider.GetRootContentGroup()
        self.header.tab_group.AddTab(label=GetByLabel(self.default_captionLabelPath), tabID=contentGroupConst.contentGroupHome)
        children = self._GetSortedChildren(rootContentGroup)
        for g in children:
            if not g.IsTabGroup():
                continue
            tab = self.header.tab_group.AddTab(label=g.GetName(), tabID=g.GetID())
            tab.uniqueUiName = pConst.GetUniqueAgencyTabName(g.GetID())

        if selectedGroup == contentGroupConst.contentGroupHome:
            self.header.tab_group.SelectByID(selectedGroup, silent=True, useCallback=False)
        else:
            self.header.tab_group.AutoSelect(silently=True, useCallback=False)

    def _GetLastActiveContentGroupIDItemID(self):
        global lastActiveContentGroupIDItemID
        if lastActiveContentGroupIDItemID:
            try:
                contentGroup = contentGroupProvider.GetContentGroup(lastActiveContentGroupIDItemID)
                if contentGroup.IsEnabled() and contentGroup.CanLoadAsLastActive():
                    return lastActiveContentGroupIDItemID
            except RuntimeError:
                pass

        return (contentGroupConst.contentGroupHome, None)

    def OnAddBookmarkButton(self):
        if self.destroyed:
            return
        if self.contentGroup.IsBookmarkable():
            agencyBookmarks.AddBookmark(self.contentGroup.GetID())

    def OnContentGroupSelected(self, contentGroupID, itemID = None, *args, **kwargs):
        if self.destroyed:
            return
        self.contentGroup = contentGroupProvider.GetContentGroup(contentGroupID, itemID)
        self._NotifyOperationsContentExpanded()
        self._NotifyOperationsContentGroupExpanded()
        self._UpdateTabgroup()
        self.UpdateLastActiveContentGroupIDItemID(contentGroupID, itemID)

    def UpdateLastActiveContentGroupIDItemID(self, contentGroupID, itemID):
        global lastActiveContentGroupIDItemID
        lastActiveContentGroupIDItemID = (contentGroupID, itemID)

    def _UpdateTabgroup(self):
        contentGroup = self.contentGroup.GetLevel1Ancestor()
        self.header.tab_group.SelectByID(panelID=contentGroup.GetID(), silent=True, useCallback=False)

    @staticmethod
    def _GetSortedChildren(rootContentGroup):
        children = sorted([ child for child in rootContentGroup.children ], key=lambda x: x.contentGroupID)
        return children

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader(on_tab_selected=self.OnMainTabGroup)

    def OnMainTabGroup(self, contentGroupID, oldTabID):
        agencySignals.on_content_group_selected(contentGroupID)

    def OnBack(self):
        self.contentGroupBrowser.OnBack()

    def OnForward(self):
        self.contentGroupBrowser.OnForward()

    @classmethod
    def OpenAndShowContentGroup(cls, contentGroupID, itemID = None, *args, **kwargs):
        contentGroup = contentGroupProvider.GetContentGroup(contentGroupID)
        if contentGroup and contentGroup.IsExternalGroup():
            contentGroup.CallExternalFunc()
            return
        if not contentGroup:
            contentGroupID = contentGroupConst.contentGroupHome
        wnd = cls.GetIfOpen()
        if not wnd:
            cls.Open(contentGroupID=contentGroupID, itemID=itemID, *args, **kwargs)
        else:
            wnd.Maximize()
            agencySignals.on_content_group_selected(contentGroupID, itemID=itemID, *args, **kwargs)

    def GetMenu(self):
        m = super(AgencyWndNew, self).GetMenu()
        if bool(session.role & ROLE_PROGRAMMER):
            m += [('GM: Refresh all content', sm.GetService('agencyNew').RefreshAllContent)]
        return m

    def GetSelectedContentType(self):
        return self.contentGroup.GetContentType()

    def OnEndMaximize_(self, *args):
        self._NotifyOperationsContentExpanded()
        self._NotifyOperationsContentGroupExpanded()

    def _NotifyOperationsContentExpanded(self):
        if not self.contentGroup:
            return
        contentPieces = self.contentGroup.GetContentPieces()
        if contentPieces:
            sm.ScatterEvent('OnClientEvent_AgencyContentExpanded', contentPieces[0])

    def _NotifyOperationsContentGroupExpanded(self):
        sm.ScatterEvent('OnClientEvent_AgencyContentGroupExpanded', self.contentGroup.contentGroupID)

    def Close(self, *args, **kwargs):
        agencySignals.on_content_group_selected.disconnect(self.OnContentGroupSelected)
        agencySignals.on_add_bookmark_button.disconnect(self.OnAddBookmarkButton)
        super(AgencyWndNew, self).Close(*args, **kwargs)

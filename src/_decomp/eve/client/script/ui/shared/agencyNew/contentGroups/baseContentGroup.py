#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\baseContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupNameByID, contentGroupDescriptionByID, contentGroupsEnabledInWormholes
from eve.client.script.ui.shared.agencyNew.ui.contentGroupPages.baseContentGroupPage import BaseContentGroupPage
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
import evelink
from localization import GetByLabel

class BaseContentGroup(object):
    contentGroupID = None
    childrenGroups = []
    parent = None

    def __init__(self, contentGroupID = None, itemID = None, parent = None):
        self.itemID = itemID
        self.parent = parent
        if self.contentGroupID is None:
            self.contentGroupID = contentGroupID
        self._children = []
        self.lastSelectedID = None
        self._ConstructChildrenGroups()

    def _ConstructChildrenGroups(self):
        if not self.childrenGroups:
            return
        for contentGroupID, contentGroupCls in self.childrenGroups:
            newGroup = contentGroupCls(contentGroupID=contentGroupID, parent=self)
            self._children.append(newGroup)

    @property
    def children(self):
        return self._children

    def GetChild(self, contentGroupID):
        for child in self.children:
            if child.contentGroupID == contentGroupID:
                return child

    def GetName(self):
        name = contentGroupNameByID.get(self.GetNameKey(), None)
        if name:
            return GetByLabel(name)

    def GetInternalName(self):
        name = contentGroupNameByID.get(self.GetNameKey(), None)
        if name:
            return GetByLabel(name, languageID='en')
        return self.__class__.__name__

    def GetNameKey(self):
        return self.contentGroupID

    def GetDescription(self):
        description = contentGroupDescriptionByID.get(self.GetDescriptionKey(), None)
        if description:
            return GetByLabel(description)

    def GetDescriptionKey(self):
        return self.contentGroupID

    def GetNameWithLink(self, *args, **kwargs):
        return evelink.local_service_link(method='AgencyOpenAndShow', text=self.GetName(), contentGroupID=self.contentGroupID, itemID=self.itemID, **kwargs)

    def GetAncestorList(self):
        ret = []
        self.parent._GetAncestorList(ret)
        return ret

    def _GetAncestorList(self, breadcrumbs):
        if self.parent:
            self.parent._GetAncestorList(breadcrumbs)
        breadcrumbs.append(self)

    def GetID(self):
        return self.contentGroupID

    def GetParentID(self):
        if self.parent:
            return self.parent.contentGroupID

    def GetContentGroup(self, contentGroupID, itemID = None):
        if self.contentGroupID == contentGroupID and self.itemID == itemID:
            return self
        for child in self.children:
            contentGroup = child.GetContentGroup(contentGroupID, itemID)
            if contentGroup:
                return contentGroup

    def GetDepthLevel(self):
        if not self.parent:
            return 0
        else:
            return self.parent.GetDepthLevel() + 1

    def GetLevel1Ancestor(self):
        if self.GetDepthLevel() <= 1:
            return self
        if self.parent:
            return self.parent.GetLevel1Ancestor()

    def IsNewContentAvailable(self):
        for child in self.children:
            if child.IsNewContentAvailable():
                return True

        return False

    def GetContentType(self):
        return contentGroupConst.contentTypeByContentGroup.get(self.contentGroupID, None)

    def GetContentGroupHint(self):
        return GetByLabel(contentGroupConst.contentGroupHintByContentGroup.get(self.contentGroupID, None))

    def IsGroupContent(self):
        return self.contentGroupID in contentGroupConst.groupActivityContentGroups

    def GetContentPieces(self):
        contentProvider = self.GetContentProvider()
        if not contentProvider:
            return []
        return contentProvider.GetContentPieces()

    def GetContentProvider(self):
        return sm.GetService('agencyNew').GetContentProvider(self.contentGroupID)

    def ApplyDefaultFilters(self):
        contentProvider = self.GetContentProvider()
        if contentProvider:
            contentProvider.ApplyDefaultFilters()

    def GetChatChannelID(self):
        return contentGroupConst.chatChannelIDsByContentGroups.get(self.GetID(), None)

    def RemoveChild(self, child):
        if child in self.children:
            self.children.remove(child)

    def Close(self):
        if not self.parent:
            return
        self.parent.RemoveChild(self)

    def Flush(self):
        for child in self.children:
            child.Close()

        self._children = []

    def IsEnabled(self):
        if not IsKnownSpaceSystem(session.solarsystemid2):
            if self.GetID() not in contentGroupsEnabledInWormholes:
                return False
        return True

    def IsVisible(self):
        return True

    def GetDisabledHint(self):
        return None

    def GetTimeRemaining(self):
        return None

    def IsBookmarkable(self):
        return self.contentGroupID not in contentGroupConst.contentGroupBookmarkableBlacklist

    def IsChildNewContentAvailable(self):
        for child in self.children:
            if child.IsNewContentAvailable() or child.IsChildNewContentAvailable():
                return True

        return False

    def GetBackgroundTexture(self):
        return contentGroupConst.cardBackgroundByContentGroup.get(self.contentGroupID, '')

    @staticmethod
    def IsContentAvailable():
        return True

    @staticmethod
    def IsExternalGroup():
        return False

    @staticmethod
    def CanLoadAsLastActive():
        return True

    @staticmethod
    def CanLoadFromHistory():
        return True

    @staticmethod
    def GetContentPageClass():
        return BaseContentGroupPage

    @staticmethod
    def IsTabGroup():
        return False

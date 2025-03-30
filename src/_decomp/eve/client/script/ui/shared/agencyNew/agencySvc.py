#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\agencySvc.py
import eveexceptions
import log
from carbon.common.script.sys.service import Service
from eve.client.script.ui.shared.agencyNew import agencySignals, agencyBookmarks
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupProvider
from eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst import contentGroupHome, contentGroupMissionAgentsHeraldry, get_content_group_name
from eve.client.script.ui.shared.agencyNew.contentProviders import contentProviders
from eve.client.script.ui.shared.agencyNew.message_bus.agencyMessenger import AgencyMessenger
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew

class AgencySvc(Service):
    __guid__ = 'svc.agencyNew'
    __startupdependencies__ = ['agents', 'publicGatewaySvc']
    __notifyevents__ = ['OnSessionChanged', 'OnHeraldryAvailabilityChanged']

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)
        self._ResetVariables()

    def _ResetVariables(self):
        self.contentProviders = []
        self.contentProvidersByContentGroup = {}

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change:
            contentGroupProvider.ResetData()
            agencyBookmarks.ClearBookmarksVariable()
            self._ConstructContentProviders()
        agencySignals.on_content_pieces_invalidated()

    def OnHeraldryAvailabilityChanged(self):
        self.RefreshAllContent()
        if self.IsContentGroupOpened(contentGroupID=contentGroupMissionAgentsHeraldry):
            self.OpenWindow(contentGroupID=contentGroupHome)

    def _ConstructContentProviders(self):
        for contentProviderCls in contentProviders:
            log.LogInfo('Class::cls name = ' + str(contentProviderCls.__name__) + ', group = ' + str(contentProviderCls.contentGroup))
            self._ConstructContentProvider(contentProviderCls)

    def _ConstructContentProvider(self, cls):
        try:
            contentProvider = cls()
        except Exception as e:
            log.LogInfo('Class::exception = ' + str(e))

        log.LogInfo('Class::contentProviders len before = ' + str(len(self.contentProviders)))
        self.contentProviders.append(contentProvider)
        self.contentProvidersByContentGroup[contentProvider.contentGroup] = contentProvider
        log.LogInfo('Class::contentProviders len after = ' + str(len(self.contentProviders)))
        log.LogInfo('Class::cls = ' + str(cls.__name__) + ', contentProvider.contentGroup = ' + str(contentProvider.contentGroup))
        return contentProvider

    def GetContentProvider(self, contentGroupID):
        return self.contentProvidersByContentGroup.get(contentGroupID, None)

    def RefreshAllContent(self):
        self.InvalidateAllContentProviderData()
        contentGroupProvider.ResetData()
        self._ResetVariables()
        self._ConstructContentProviders()
        agencySignals.on_content_pieces_invalidated()

    def InvalidateAllContentProviderData(self):
        for contentProvider in self.contentProviders:
            contentProvider.InvalidateContentPieces()

    def ClearNewMarkerForContent(self, contentPiece):
        contentProviders = self.GetContentProvidersByContentType(contentPiece.contentType)
        for contentProvider in contentProviders:
            contentProvider.ClearNewContent(contentPiece)

    def GetContentProvidersByContentType(self, contentType):
        contentProviders = []
        for contentProvider in self.contentProviders:
            if contentType == contentProvider.contentType:
                contentProviders.append(contentProvider)

        return contentProviders

    def IsCardSelected(self, contentType):
        agencyWindow = AgencyWndNew.GetIfOpen()
        if agencyWindow is None:
            return False
        if agencyWindow.IsMinimized():
            return False
        return agencyWindow.GetSelectedContentType() == contentType

    def OpenWindow(self, contentGroupID = None, itemID = None, *args, **kwargs):
        if contentGroupID is not None:
            AgencyWndNew.OpenAndShowContentGroup(contentGroupID=contentGroupID, itemID=itemID, *args, **kwargs)
        else:
            AgencyWndNew.Open()

    def IsContentGroupOpened(self, contentGroupID):
        agencyWindow = AgencyWndNew.GetIfOpen()
        if agencyWindow:
            contentGroup = getattr(agencyWindow, 'contentGroup', None)
            if contentGroup:
                currentContentGroupID = getattr(contentGroup, 'contentGroupID', None)
                return currentContentGroupID == contentGroupID
        return False

    def IsContentGroupOpenedByName(self, contentGroupName):
        agencyWindow = AgencyWndNew.GetIfOpen()
        if agencyWindow:
            contentGroup = getattr(agencyWindow, 'contentGroup', None)
            if contentGroup:
                currentContentGroupID = getattr(contentGroup, 'contentGroupID', None)
                if currentContentGroupID:
                    currentContentGroupName = get_content_group_name(currentContentGroupID)
                    if currentContentGroupName:
                        return currentContentGroupName == contentGroupName
        return False

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogHelpVideoLinkCreated(self, video_path):
        message_bus = AgencyMessenger(self.publicGatewaySvc)
        message_bus.help_video_link_created(video_path)

    @eveexceptions.EatsExceptions('protoClientLogs')
    def LogHelpVideoLinkClicked(self, video_path):
        message_bus = AgencyMessenger(self.publicGatewaySvc)
        message_bus.help_video_link_clicked(video_path)

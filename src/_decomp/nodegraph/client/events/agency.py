#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\events\agency.py
from .base import Event

class AgencyContentExpanded(Event):
    atom_id = 38
    __notifyevents__ = ['OnClientEvent_AgencyContentExpanded']

    def OnClientEvent_AgencyContentExpanded(self, content_piece):
        self.invoke(content_type_id=content_piece.GetContentTypeID() or 0, content_piece_type=content_piece.contentType or 0)


class AgencyContentGroupExpanded(Event):
    atom_id = 39
    __notifyevents__ = ['OnClientEvent_AgencyContentGroupExpanded']

    def OnClientEvent_AgencyContentGroupExpanded(self, content_group_id):
        self.invoke(content_group_id=content_group_id)


class AgencyContentCardClicked(Event):
    atom_id = 555
    __notifyevents__ = ['OnAgencyContentCardClicked']

    def OnAgencyContentCardClicked(self, contentGroupID, contentItemID, contentTypeID):
        self.invoke(content_group_id=contentGroupID, content_item_id=contentItemID, content_type_id=contentTypeID)

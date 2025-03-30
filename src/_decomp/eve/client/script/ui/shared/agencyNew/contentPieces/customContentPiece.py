#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\customContentPiece.py
import logging
from agency.client.custom_content import get_remote_agency_provider_service
from agency.common.contentdata import CustomContentData
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from localization import GetByMessageID
logger = logging.getLogger(__name__)

class CustomContentPiece(BaseContentPiece):

    def __init__(self, content_data, is_new = False):
        self._content_data = content_data
        self.contentType = content_data.content_type
        super(CustomContentPiece, self).__init__(solarSystemID=content_data.solar_system_id, locationID=content_data.location_id, itemID=content_data.item_id, typeID=content_data.type_id, ownerID=content_data.owner_id, enemyOwnerID=content_data.enemy_owner_id, isNew=is_new)

    def GetCardID(self):
        return (self.contentType, self._GetUniqueID())

    def _GetButtonState(self):
        if self._content_data.primary_action_id:
            return self._content_data.primary_action_id
        return super(CustomContentPiece, self)._GetButtonState()

    def _ExecutePrimaryFunction(self, actionID):
        if actionID == agencyUIConst.ACTION_WARPTO and self.locationID is None:
            self._WarpToCustomContent()
        else:
            super(CustomContentPiece, self)._ExecutePrimaryFunction(actionID)

    def GetMarkerID(self):
        return '%s_%s_%s' % (self.solarSystemID, self._GetUniqueID(), self.contentType)

    def _GetUniqueID(self):
        return (self._content_data.source_id, self._content_data.source_content_id)

    def _WarpToCustomContent(self):
        get_remote_agency_provider_service().warp_to_content(self._content_data.agency_content_id)

    def GetSubSolarSystemPosition(self):
        return self._content_data.solar_system_coordinates

    def GetName(self):
        if self._content_data.subtitle_text_id:
            return GetByMessageID(self._content_data.subtitle_text_id)
        return super(CustomContentPiece, self).GetSubtitle()

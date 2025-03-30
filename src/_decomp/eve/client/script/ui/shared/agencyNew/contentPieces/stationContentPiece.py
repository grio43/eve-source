#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\stationContentPiece.py
from eve.client.script.ui.const import buttonConst
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.common.script.sys.eveCfg import IsDocked, IsControllingStructure

class StationContentPiece(BaseContentPiece):

    def __init__(self, stationID, *args, **kwargs):
        super(StationContentPiece, self).__init__(*args, **kwargs)
        self.stationID = stationID

    def GetStationID(self):
        return self.stationID

    def _GetButtonState(self):
        if IsControllingStructure() or IsDocked() and session.stationid == self.stationID:
            return buttonConst.STATE_NONE
        return super(StationContentPiece, self)._GetButtonState()

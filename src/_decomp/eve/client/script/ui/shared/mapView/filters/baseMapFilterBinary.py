#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\filters\baseMapFilterBinary.py
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.filters.baseMapFilter import BaseMapFilter

class BaseMapFilterBinary(BaseMapFilter):

    def GetStarSizeAffected(self, solarSystemID):
        return mapViewConst.STAR_SIZE_AFFECTED

    def GetStarSizeUnaffected(self):
        return mapViewConst.STAR_SIZE_UNIMPORTANT

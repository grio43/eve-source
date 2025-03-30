#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerMyHome.py
import homestation.client
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from localization import GetByLabel
from eveservices.menu import GetMenuService

class MarkerMyHome(MarkerIconBase):
    distanceFadeAlphaNearFar = None
    texturePath = homestation.texture.icon_home_station_16
    backgroundColor = homestation.Color.home_station

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.stationInfo = kwds['stationInfo']
        self.typeID = self.stationInfo.stationTypeID
        self.itemID = self.stationInfo.stationID
        self.backgroundGlow = None

    def Load(self):
        super(MarkerMyHome, self).Load()
        self.backgroundGlow = Sprite(parent=self.markerContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/MapView/icon_location_glow.png', color=self.backgroundColor, blendMode=trinity.TR2_SBM_ADDX2, width=102, height=111)

    def SetOverlappedState(self, overlapState):
        super(MarkerMyHome, self).SetOverlappedState(overlapState)
        if overlapState:
            self.backgroundGlow.opacity = 0.0
        else:
            self.backgroundGlow.opacity = 1.0

    def GetMenu(self):
        if self.stationInfo:
            return GetMenuService().GetMenuFromItemIDTypeID(self.stationInfo.stationID, self.stationInfo.stationTypeID, noTrace=1)

    def GetLabelText(self):
        return GetByLabel('UI/Map/HomeStationLabel')

    def GetDragText(self):
        return cfg.evelocations.Get(self.stationInfo.stationID).name

    def GetOverlapSortValue(self, reset = False):
        return None

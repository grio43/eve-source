#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerMyLocation.py
import blue
import uthread
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from localization import GetByLabel
import carbonui.const as uiconst

class MarkerMyLocation(MarkerIconBase):
    solarSystemID = None
    distanceFadeAlphaNearFar = None
    texturePath = 'res:/UI/Texture/classes/MapView/focusIcon.png'

    def __init__(self, animate = True, *args, **kwds):
        super(MarkerMyLocation, self).__init__(*args, **kwds)
        self.bgCircles = []

    def GetMenu(self):
        pass

    def GetLabelText(self):
        return GetByLabel('UI/Map/StarMap/lblYouAreHere')

    def ShowDscanHilite(self):
        pass

    def _CreateRenderObject(self):
        MarkerIconBase._CreateRenderObject(self)
        self.CheckConstructCircles()

    def CheckConstructCircles(self):
        if self.markerContainer and not self.markerContainer.destroyed:
            self.ConstructCircles()
            uthread.new(self.AnimateBGCircles)

    def AnimateBGCircles(self):
        duration = 3.0
        radius = 300
        kOffset = 0.6
        while not self.destroyed:
            blue.pyos.synchro.SleepWallclock((3 * kOffset + duration) * 1000)
            if not self.IsThisWindowActive():
                continue
            for i, circle in enumerate(self.bgCircles):
                timeOffset = i * kOffset
                animations.MorphScalar(circle, 'width', 0, radius, duration=duration, timeOffset=timeOffset)
                animations.MorphScalar(circle, 'height', 0, radius, duration=duration, timeOffset=timeOffset)
                animations.FadeTo(circle, 0.0, 0.02, duration=duration, timeOffset=timeOffset, curveType=uiconst.ANIM_WAVE)

    def IsThisWindowActive(self):
        if not self.markerContainer:
            return False
        wnd = GetWindowAbove(self.markerContainer)
        return uicore.registry.GetActive() == wnd

    def ConstructCircles(self):
        for i in xrange(3):
            circle = SpriteThemeColored(name='circle', parent=self.markerContainer, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/hexMap/circleFilled256.png', colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
            self.bgCircles.append(circle)

    def GetMarkerOpacity(self, bracketCameraDistance, cameraZoomDistance):
        return 1.0

    def GetOverlapSortValue(self, reset = False):
        return None

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerVulnerableSkyhook.py
import blue
import eveicon
import uthread
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from localization import GetByLabel
import carbonui.const as uiconst
from carbonui.primitives.base import ScaleDpi
from math import pi
import logging
log = logging.getLogger(__name__)

class MarkerVulnerableSkyhook(MarkerIconBase):
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE)
    texturePath = eveicon.skyhook

    def __init__(self, animate = True, *args, **kwds):
        super(MarkerVulnerableSkyhook, self).__init__(*args, **kwds)
        self.bgCircles = []
        self.projectBracket.offsetY = ScaleDpi(30)
        self.lock_label = ''

    def Load(self):
        super(MarkerVulnerableSkyhook, self).Load()
        self.backgroundSprite.rotation = pi
        self.backgroundSprite.pos = ((self.width - 64) / 2,
         (self.height - 64) / 2 - 12,
         64,
         64)
        self.backgroundSprite.color = eveColor.CHERRY_RED

    def Close(self):
        uicore.animations.StopAllAnimations(self)
        super(MarkerVulnerableSkyhook, self).Close()

    def GetMenu(self):
        pass

    def GetLabelText(self):
        return GetByLabel('UI/OrbitalSkyhook/SkyhookMap/SkyhookVulnerableToTheft')

    def ShowDscanHilite(self):
        pass

    def _CreateRenderObject(self):
        super(MarkerVulnerableSkyhook, self)._CreateRenderObject()
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

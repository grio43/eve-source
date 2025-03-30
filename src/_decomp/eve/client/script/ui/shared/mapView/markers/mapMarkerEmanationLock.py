#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerEmanationLock.py
import blue
import evetypes
import uthread
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.agencyNew.ui.contentPages.contentPageZarzakh import Topics
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
import eve.client.script.ui.shared.agencyNew.contentGroups.contentGroupConst as agencyContentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.agencyWnd import AgencyWndNew
from localization import GetByLabel
import carbonui.const as uiconst
from carbonui.primitives.base import ScaleDpi
from math import pi
import logging
log = logging.getLogger(__name__)

class MarkerEmanationLock(MarkerIconBase):
    solarSystemID = None
    distanceFadeAlphaNearFar = None
    texturePath = 'res:/UI/Texture/eveicon/system_icons/link_16px.png'

    def __init__(self, animate = True, *args, **kwds):
        super(MarkerEmanationLock, self).__init__(*args, **kwds)
        self.bgCircles = []
        self.projectBracket.offsetY = ScaleDpi(30)
        self.lock_label = ''

    def Load(self):
        super(MarkerEmanationLock, self).Load()
        self.backgroundSprite.rotation = pi
        self.backgroundSprite.pos = ((self.width - 64) / 2,
         (self.height - 64) / 2 - 12,
         64,
         64)
        self.backgroundSprite.color = eveColor.CHERRY_RED

    def Close(self):
        uicore.animations.StopAllAnimations(self)
        super(MarkerEmanationLock, self).Close()

    def GetMenu(self):
        pass

    def OnDblClick(self, *args):
        log.info('MarkerEmanationLock.OnDblClick')
        AgencyWndNew.OpenAndShowContentGroup(contentGroupID=agencyContentGroupConst.contentGroupZarzakh)
        wnd = AgencyWndNew.GetIfOpen()
        if wnd is None:
            return
        wnd.contentGroupBrowser.contentPage.select_topic(Topics.JOVIAN)

    def SetLabelTextFromItem(self, itemID, typeID):
        text = self.GetLabelTextFromItem(itemID, typeID)
        self.lock_label = GetByLabel('UI/Map/StarMap/EmanationLockMarkerTooltip', gate_name=text)

    def GetLabelTextFromItem(self, itemID, typeID):
        displayName = ''
        locationName = cfg.evelocations.Get(itemID).name
        if locationName:
            displayName = locationName
        elif typeID:
            displayName = evetypes.GetName(typeID)
        return displayName

    def GetLabelText(self):
        return self.lock_label

    def ShowDscanHilite(self):
        pass

    def _CreateRenderObject(self):
        super(MarkerEmanationLock, self)._CreateRenderObject()
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

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\markers\mapMarkerSolarSystem.py
from evePathfinder.core import IsUnreachableJumpCount
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerSolarSystemBased
import carbonui.const as uiconst
import math
from carbonui.uianimations import animations
from eve.common.script.sys import idCheckers
from localization import GetByLabel
CIRCLESIZE = 14
LABEL_LEFT_MARGIN = 8
LABEL_LEFT = CIRCLESIZE + LABEL_LEFT_MARGIN

class MarkerLabelSolarSystem(MarkerSolarSystemBased):
    distanceFadeAlphaNearFar = (0.0, 25000)
    hilightContainer = None
    positionPickable = True
    extraInfo = None
    _cachedLabel = None

    def __init__(self, *args, **kwds):
        MarkerSolarSystemBased.__init__(self, *args, **kwds)
        self.typeID = const.typeSolarSystem
        self.itemID = self.markerID
        self.solarSystemID = self.markerID

    def Load(self):
        self.isLoaded = True
        self.textLabel = EveLabelSmall(parent=self.markerContainer, text=self.GetLabelText(), bold=True, state=uiconst.UI_NORMAL, left=LABEL_LEFT)
        self.textLabel.GetMenu = self.markerContainer.GetMenu
        self.markerContainer.width = LABEL_LEFT + self.textLabel.textwidth
        self.markerContainer.height = self.textLabel.textheight
        Fill(bgParent=self.markerContainer, padding=(LABEL_LEFT - 2,
         0,
         -2,
         0), color=(0, 0, 0, 0.5))
        self.projectBracket.offsetX = ScaleDpi(self.markerContainer.width * 0.5 - CIRCLESIZE / 2)
        self.UpdateActiveAndHilightState()

    def DestroyRenderObject(self):
        MarkerSolarSystemBased.DestroyRenderObject(self)
        self.hilightContainer = None

    def _HideRenderObject(self):
        if self.IsActive():
            self.markerContainer.Hide()
        else:
            self.DestroyRenderObject()

    def UpdateSolarSystemPosition(self, solarSystemPosition):
        self.mapPositionSolarSystem = solarSystemPosition
        self.SetPosition(solarSystemPosition)

    def GetLabelText(self):
        if self._cachedLabel is None:
            securityStatus, color = sm.GetService('map').GetSecurityStatus(self.markerID, True)
            securityModifierIconText = sm.GetService('securitySvc').get_security_modifier_icon_text(self.solarSystemID)
            self._cachedLabel = '%s <color=%s>%s</color>%s' % (cfg.evelocations.Get(self.markerID).name,
             Color.RGBtoHex(color[0], color[1], color[2]),
             securityStatus,
             securityModifierIconText)
        return self._cachedLabel

    def UpdateLabelText(self):
        self._cachedLabel = None
        self.textLabel.text = self.GetLabelText()

    def GetDragText(self):
        return cfg.evelocations.Get(self.markerID).name

    def UpdateActiveAndHilightState(self):
        if self.hilightState or self.activeState:
            self.projectBracket.maxDispRange = 1e+32
            if self.markerContainer:
                if self.hilightState:
                    self.CheckConstructHilightContainer()
                elif self.hilightContainer:
                    self.hilightContainer.Close()
                    self.hilightContainer = None
                if self.activeState == mapViewConst.MARKER_SELECTED:
                    self.textLabel.opacity = 1.3
                else:
                    self.textLabel.opacity = 1.0
                self.UpdateExtraInfo()
        else:
            if self.distanceFadeAlphaNearFar:
                self.projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]
            if self.hilightContainer:
                self.hilightContainer.Close()
                self.hilightContainer = None
            if self.extraContainer:
                self.extraContainer.Close()
                self.extraContainer = None
        self.lastUpdateCameraValues = None

    def CheckConstructHilightContainer(self):
        if not self.hilightContainer:
            hilightContainer = Container(parent=self.markerContainer, align=uiconst.CENTERLEFT, pos=(0,
             0,
             CIRCLESIZE,
             CIRCLESIZE), state=uiconst.UI_DISABLED)
            DashedCircle(parent=hilightContainer, dashCount=4, lineWidth=0.8, radius=CIRCLESIZE / 2, range=math.pi * 2)
            self.hilightContainer = hilightContainer

    def UpdateExtraInfo(self):
        if self.IsHilighted() or self.IsSelected():
            extraInfoText = self.GetExtraMouseOverInfo() or ''
            lines = extraInfoText.split('<br>')
            if len(lines) > 1 and not self.hilightState:
                extraInfoText = GetByLabel('UI/Map/ColorModeHandler/NumRecordsFound', count=len(lines))
            if self.IsHilighted() and self.solarSystemID != session.solarsystemid2 and idCheckers.IsKnownSpaceSystem(session.solarsystemid2):
                numJumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(self.solarSystemID)
                if not IsUnreachableJumpCount(numJumps):
                    if extraInfoText:
                        extraInfoText += '<br>'
                    extraInfoText += GetByLabel('UI/Fleet/FleetRegistry/NumberOfJumps', numJumps=numJumps)
            if not self.extraContainer:
                self.extraContainer = ExtraInfoContainer(parent=self.markerContainer, text=extraInfoText, top=self.textLabel.textheight, left=LABEL_LEFT, markerObject=self, idx=0)
            else:
                self.extraContainer.SetText(extraInfoText)
        elif self.extraContainer:
            self.extraContainer.Close()
            self.extraContainer = None

    def GetMarkerOpacity(self, bracketCameraDistance, zoomDistance):
        if self.IsSelected() or self.IsHilighted():
            return mapViewConst.OPACITY_MARKER_ACTIVE
        if self.IsActive():
            nearFadeDist, farFadeDist = self._distanceFadeAlphaNearFar
            return self.GetMarkerBaseOpacity(bracketCameraDistance, nearFadeDist, farFadeDist)

    def SetBracketMaxDispRange(self):
        self.projectBracket.maxDispRange = 0

    def OnClick(self, *args, **kwds):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            clearOtherWaypoints = not uicore.uilib.Key(uiconst.VK_SHIFT)
            sm.GetService('starmap').SetWaypoint(self.solarSystemID, clearOtherWaypoints=clearOtherWaypoints)
        else:
            MarkerSolarSystemBased.OnClick(self, *args, **kwds)


class ExtraInfoLabel(EveLabelSmall):

    def OnMouseEnter(self, *args):
        if self.destroyed:
            return
        EveLabelSmall.OnMouseEnter(self, *args)
        self.parent.markerObject.markerHandler.HilightMarkers([self.parent.markerObject.markerID], add=True)


class ExtraInfoContainer(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_clipChildren = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.markerObject = attributes.markerObject
        self.label = ExtraInfoLabel(parent=self, text=attributes.text, bold=True, state=uiconst.UI_NORMAL, opacity=0.8, cursor=uiconst.UICURSOR_DEFAULT)
        self.UpdateSize()
        Fill(bgParent=self, padding=(-3, 0, -2, 0), color=(0, 0, 0, 0.4))
        animations.FadeTo(self, startVal=0.0, endVal=1.0, duration=0.1)
        animations.MorphScalar(self, 'displayWidth', 0, self.label.actualTextWidth, duration=0.2)

    def UpdateSize(self):
        self.height = self.label.textheight
        self.width = self.label.textwidth

    def Close(self, *args):
        Container.Close(self, *args)
        self.markerObject = None

    def SetText(self, text):
        self.label.text = text
        self.UpdateSize()

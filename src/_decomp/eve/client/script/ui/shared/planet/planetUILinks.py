#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetUILinks.py
import geo2
import localization
import trinity
from carbonui import uiconst
from carbonui.primitives.bracket import Bracket
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared.planet.planetCommon import PLANET_COLOR_LINKEDITMODE
from eve.client.script.ui.shared.planet.planetConst import LINK_COLOR_BASE, LINK_COLOR_DEFAULT, LINK_COLOR_INACTIVE, LINK_COLOR_HOVER, LINK_COLOR_ROUTED
from eve.common.script.planet.surfacePoint import SurfacePoint
from utillib import KeyVal
LINK_WIDTH = 6.0
LINK_OFFSET = 0.0006
LINK_FLOWSPEED = 0.002
LINK_SEGMENTRATIO = 25.0

class LinkBase:

    def __init__(self, lsName, surfacePoint1, surfacePoint2, color = LINK_COLOR_DEFAULT):
        self.destroyed = False
        self.state = KeyVal(mouseHover=False, link1AsRoute=False, link2AsRoute=False, selected=False, link1Active=False, link2Active=False)
        self.lsName = lsName
        self.clDrawer = sm.GetService('planetUI').curveLineDrawer
        self.length = surfacePoint1.GetDistanceToOther(surfacePoint2)
        self.flowSpeed = LINK_FLOWSPEED / self.length
        self.texWidth = 1200.0 * self.length
        self.linkGraphicID = self.clDrawer.DrawArc(lsName, surfacePoint2, surfacePoint1, LINK_WIDTH * 0.5, LINK_COLOR_BASE, LINK_COLOR_BASE)
        numSegments = max(1, int(self.length * LINK_SEGMENTRATIO))
        self.clDrawer.SetLineSetNumSegments(lsName, self.linkGraphicID, numSegments)
        self.SetAnimation(color=color, isActive=True)

    def SetAnimation(self, color, isActive, speed = 1.0):
        self.clDrawer.ChangeLineAnimation(self.lsName, self.linkGraphicID, color, speed * self.flowSpeed, self.texWidth)
        self.clDrawer.SubmitLineset(self.lsName)

    def Remove(self):
        self.destroyed = True
        self.clDrawer.RemoveLine(self.lsName, self.linkGraphicID)


class Link:

    def __init__(self, surfacePoint1, surfacePoint2, parentID, childID, typeID, link = None):
        self.destroyed = False
        self.link = link
        self.state = KeyVal(mouseHover=False, link1AsRoute=False, link2AsRoute=False, selected=False, link1Active=False, link2Active=False)
        self.clDrawer = sm.GetService('planetUI').curveLineDrawer
        self.sp1A, self.sp1B, self.sp2A, self.sp2B, self.surfacePoint = self._GetLinkEndPoints(surfacePoint1, surfacePoint2)
        self.length = surfacePoint1.GetDistanceToOther(surfacePoint2)
        self.IDTuple = (childID, parentID)
        self.typeID = typeID
        self.flowSpeed = LINK_FLOWSPEED / self.length
        self.texWidth = 600.0 * self.length
        self.currentRouteVolume = None
        self.linkGraphicID1 = self.clDrawer.DrawArc('links', self.sp1A, self.sp1B, LINK_WIDTH, LINK_COLOR_BASE, LINK_COLOR_BASE)
        self.linkGraphicID2 = self.clDrawer.DrawArc('links', self.sp2B, self.sp2A, LINK_WIDTH, LINK_COLOR_BASE, LINK_COLOR_BASE)
        numSegments = max(1, int(self.length * LINK_SEGMENTRATIO))
        self.clDrawer.SetLineSetNumSegments('links', self.linkGraphicID1, numSegments)
        self.clDrawer.SetLineSetNumSegments('links', self.linkGraphicID2, numSegments)
        self.clDrawer.SubmitLineset('links')
        self.graphicIDbyID = {(childID, parentID): self.linkGraphicID1,
         (parentID, childID): self.linkGraphicID2}
        self._InitInfoBracket()
        self.state.link1Active, self.state.link2Active = self._GetLinksActiveState()
        self.RenderAccordingToState()

    def _InitInfoBracket(self):
        self.infoBracket = Bracket()
        self.infoBracket.name = '__inflightbracket'
        self.infoBracket.align = uiconst.ABSOLUTE
        self.infoBracket.state = uiconst.UI_DISABLED
        self.infoBracket.dock = False
        self.infoBracket.display = False
        pad = 2
        self.infoBracket.padding = (pad,
         pad,
         pad,
         pad)
        self.infoBracket.trackTransform = trinity.EveTransform()
        self.infoBracket.trackTransform.name = 'LinkInfoBracket'
        t = self.surfacePoint.GetAsXYZTuple()
        scale = 1.01
        self.infoBracket.trackTransform.translation = (t[0] * scale, t[1] * scale, t[2] * scale)
        self.bracketCurveSet = sm.GetService('planetUI').myPinManager.bracketCurveSet
        self.bracketCurveSet.curves.append(self.infoBracket.projectBracket)
        sm.GetService('planetUI').planetTransform.children.append(self.infoBracket.trackTransform)
        sm.GetService('planetUI').pinInfoParent.children.insert(0, self.infoBracket)
        self.infoText = EveLabelSmall(text='', parent=self.infoBracket, align=uiconst.TOPLEFT, width=self.infoBracket.width, left=pad, top=pad, color=Color.WHITE, state=uiconst.UI_NORMAL)
        self._UpdateInfoBracket()
        self._ResizeInfoBracket()
        Fill(parent=self.infoBracket, color=(0.0, 0.0, 0.0, 0.5))
        self.infoBracket.state = uiconst.UI_HIDDEN

    def _ResizeInfoBracket(self):
        pad = 2
        l, t, w, h = self.infoText.GetAbsolute()
        if self.infoBracket:
            self.infoBracket.width = w + pad * 2
            self.infoBracket.height = h + pad * 2 - 2

    def _UpdateInfoBracket(self):
        linkBandwidthUsage = self.link.GetBandwidthUsage()
        if self.currentRouteVolume is not None:
            addedPercentage = self.currentRouteVolume / self.link.GetTotalBandwidth() * 100.0
            if self.currentRouteVolume + linkBandwidthUsage > self.link.GetTotalBandwidth():
                addedText = localization.GetByLabel('UI/PI/Common/LinkCapacityAddedInvalid', addedPercentage=addedPercentage)
            else:
                addedText = localization.GetByLabel('UI/PI/Common/LinkCapacityAddedOK', addedPercentage=addedPercentage)
        else:
            addedText = ''
        usedPercentage = linkBandwidthUsage / self.link.GetTotalBandwidth() * 100.0
        bandwidthUsage = localization.GetByLabel('UI/PI/Common/LinkCapacityUsed', usedPercentage=usedPercentage, addedText=addedText)
        self.infoText.text = bandwidthUsage
        self._ResizeInfoBracket()

    def _GetLinkEndPoints(self, sp1, sp2):
        p1 = geo2.Vector(*sp1.GetAsXYZTuple())
        p2 = geo2.Vector(*sp2.GetAsXYZTuple())
        vecDiff = p2 - p1
        pOffset = geo2.Vec3Cross(p1, vecDiff)
        pOffset = geo2.Vec3Normalize(pOffset)
        pOffset = geo2.Vec3Scale(pOffset, LINK_OFFSET)
        link1Start = geo2.Vec3Normalize(p1 + pOffset)
        link1End = geo2.Vec3Normalize(p2 + pOffset)
        link2Start = geo2.Vec3Normalize(p1 - pOffset)
        link2End = geo2.Vec3Normalize(p2 - pOffset)
        centerPoint = geo2.Vec3Normalize(p1 + vecDiff * 0.5)
        sp = SurfacePoint
        return (sp(*link1Start),
         sp(*link1End),
         sp(*link2Start),
         sp(*link2End),
         sp(*centerPoint))

    def RenderAccordingToState(self):
        if self.destroyed:
            return
        state = self.state
        if state.mouseHover or state.selected:
            self.SetLinkAppearance(LINK_COLOR_HOVER)
            self._UpdateInfoBracket()
            self.infoBracket.state = uiconst.UI_DISABLED
        elif state.link1AsRoute or state.link2AsRoute:
            if state.link1AsRoute:
                self.SetLinkAppearance(LINK_COLOR_ROUTED, self.linkGraphicID1, speed=3.0)
            if state.link2AsRoute:
                self.SetLinkAppearance(LINK_COLOR_ROUTED, self.linkGraphicID2, speed=3.0)
            self._UpdateInfoBracket()
            self.infoBracket.state = uiconst.UI_DISABLED
        else:
            if self.link.IsEditModeLink():
                color = PLANET_COLOR_LINKEDITMODE
            else:
                color = LINK_COLOR_DEFAULT
            self.SetLinkAppearance(color)
            self.infoBracket.state = uiconst.UI_HIDDEN

    def SetLinkAppearance(self, color, graphicID = None, speed = 1.0):
        link1Active, link2Active = self._GetLinksActiveState()
        if graphicID is None:
            self.clDrawer.ChangeLineAnimation('links', self.linkGraphicID1, color, link1Active * speed * self.flowSpeed, self.texWidth)
            self.clDrawer.ChangeLineAnimation('links', self.linkGraphicID2, color, link2Active * speed * self.flowSpeed, self.texWidth)
        else:
            self.clDrawer.ChangeLineAnimation('links', graphicID, color, speed * self.flowSpeed, self.texWidth)
            self.clDrawer.ChangeLineAnimation('links', graphicID, color, speed * self.flowSpeed, self.texWidth)
        if link1Active or self.link.IsEditModeLink():
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID1, LINK_COLOR_BASE)
        else:
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID1, LINK_COLOR_INACTIVE)
        if link2Active or self.link.IsEditModeLink():
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID2, LINK_COLOR_BASE)
        else:
            self.clDrawer.ChangeLineColor('links', self.linkGraphicID2, LINK_COLOR_INACTIVE)
        self.clDrawer.SubmitLineset('links')

    def _GetLinksActiveState(self):
        link1Active = link2Active = False
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        if planet is None:
            return (False, False)
        colony = planet.GetColonyByPinID(self.IDTuple[0])
        if colony is None:
            return (False, False)
        for routeID in self.link.routesTransiting:
            route = colony.GetRoute(routeID)
            if route is None:
                continue
            route = route.path
            prevId = route[0]
            for currId in route[1:]:
                if prevId == self.IDTuple[0] and currId == self.IDTuple[1]:
                    link1Active = True
                if prevId == self.IDTuple[1] and currId == self.IDTuple[0]:
                    link2Active = True
                prevId = currId
                if link1Active and link2Active:
                    break

        return (link1Active, link2Active)

    def RemoveAsRoute(self, id):
        graphicID = self.graphicIDbyID[id]
        if graphicID == self.linkGraphicID1:
            self.state.link1AsRoute = False
        else:
            self.state.link2AsRoute = False
        self.RenderAccordingToState()
        self.currentRouteVolume = None

    def ShowAsRoute(self, id, numRoute, numTotal, volume = None):
        self.currentRouteVolume = volume
        graphicID = self.graphicIDbyID[id]
        if graphicID == self.linkGraphicID1:
            self.state.link1AsRoute = True
        else:
            self.state.link2AsRoute = True
        self.RenderAccordingToState()

    def HighlightLink(self):
        self.state.mouseHover = True
        self.RenderAccordingToState()

    def RemoveHighlightLink(self):
        self.state.mouseHover = False
        self.RenderAccordingToState()

    def OnRefreshPins(self):
        self.RenderAccordingToState()

    def SetSelected(self):
        self.state.selected = True
        self.RenderAccordingToState()

    def SetDeselected(self):
        self.state.selected = False
        self.RenderAccordingToState()

    def OnMouseEnter(self):
        self.state.mouseHover = True
        self.RenderAccordingToState()
        sm.GetService('audio').SendUIEvent('msg_pi_pininteraction_mouseover_play')

    def OnMouseExit(self):
        self.state.mouseHover = False
        self.RenderAccordingToState()

    def GetGraphicIDs(self):
        return (self.linkGraphicID1, self.linkGraphicID2)

    def GetIDTuple(self):
        return self.IDTuple

    def GetMenu(self):
        return []

    def Remove(self):
        self.destroyed = True
        if self.infoBracket and self.bracketCurveSet:
            self.bracketCurveSet.curves.fremove(self.infoBracket.projectBracket)
            self.bracketCurveSet = None
        planetTransform = sm.GetService('planetUI').planetTransform
        if self.infoBracket.trackTransform in planetTransform.children:
            planetTransform.children.remove(self.infoBracket.trackTransform)
        pinInfoParent = sm.GetService('planetUI').pinInfoParent
        if self.infoBracket in pinInfoParent.children:
            pinInfoParent.children.remove(self.infoBracket)
        self.infoBracket = None

    def SetCurrentRouteVolume(self, volume):
        self.currentRouteVolume = volume
        self.RenderAccordingToState()

    def IsStorage(self):
        return False

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\planetNavigation.py
import math
import carbonui.const as uiconst
import blue
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.control.layer import LayerCore
from eve.client.script.ui.camera.planetCameraController import PlanetCameraController
from eve.client.script.ui.shared.planet import planetConst, planetCommon
import uthread
import log
import geo2
from carbonui.uicore import uicore
from eve.client.script.ui.shared.planet.templateSavingUtil import ConfirmExportWnd
from inventorycommon.const import groupExtractionControlUnitPins, groupSpaceportPins
from menu import MenuLabel
TYPE_PLANET = 1
TYPE_LINK = 2
TYPE_PIN = 3
TYPE_OTHERPLAYERSPIN = 4
TYPE_EXTRACTIONHEAD = 6
TYPE_TILE = 7
TYPE_DEPLETIONPIN = 8

class PlanetLayer(LayerCore):

    def OnCloseView(self, *args):
        self.cameraController.camera.SetCallback(None)
        ConfirmExportWnd.CloseIfOpen()

    def ApplyAttributes(self, attributes):
        LayerCore.ApplyAttributes(self, attributes)
        self.align = uiconst.TOALL
        self.orbitOnMouseMove = False
        self.planetWasRotated = False
        self.isTabStop = True
        self.pickLast = None
        self.mouseDownID = None

    def Startup(self):
        self.eventManager = sm.GetService('planetUI').eventManager
        self.myPinManager = sm.GetService('planetUI').myPinManager
        self.otherPinManager = sm.GetService('planetUI').otherPinManager
        self.cameraController = PlanetCameraController()
        self.cameraController.camera.SetCallback(self.OnCameraUpdated)
        uthread.new(self.InitCamera)

    def InitCamera(self):
        return self.OrbitToPointOfInterest(initStartPos=True)

    def OnCameraUpdated(self):
        self.UpdateSunDirection()
        sm.GetService('planetUI').OnPlanetZoomChanged(self.cameraController.camera.GetZoomLinear())
        if uicore.uilib.mouseOver == self:
            uicore.UpdateCursor(self)

    def UpdateSunDirection(self):
        camera = self.cameraController.camera
        rightMat = geo2.MatrixRotationAxis(camera.GetXAxis(), math.radians(-225))
        upMat = geo2.MatrixRotationAxis(camera.upDirection, math.radians(-45))
        scene = self.GetScene()
        scene.sunDirection = geo2.Vec3Normalize(geo2.Vec3TransformNormal(geo2.Vec3TransformNormal(camera.GetLookAtDirection(), rightMat), upMat))

    def OnSetFocus(self, *args):
        pass

    def OnKillFocus(self, *args):
        self.eventManager.OnPlanetNavFocusLost()

    def OnMouseMove(self, *args):
        if self.orbitOnMouseMove:
            self.cameraController.OnMouseMove()
            self.planetWasRotated = True
        typeID, ID, isTemplatePin = self.GetPick()
        if not self.orbitOnMouseMove and isTemplatePin:
            return self.eventManager.MoveTemplate()
        if not self.pickLast:
            self.pickLast = typeID
            self.areaIDLast = ID
            return
        if not typeID:
            return
        if (typeID, ID) == (self.pickLast, self.areaIDLast):
            self._ScatterMouseMoveEvent(typeID, ID)
            return
        if self.pickLast:
            self._ScatterMouseExitEvent(self.pickLast, self.areaIDLast)
        self._ScatterMouseEnterEvent(typeID, ID)
        self.pickLast = typeID
        self.areaIDLast = ID

    def OnMouseExit(self, *args):
        if self.pickLast:
            self._ScatterMouseExitEvent(self.pickLast, self.areaIDLast)
            self.pickLast = self.areaIDLast = None

    def OnMouseEnter(self, *args):
        if sm.GetService('ui').IsUiVisible():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def _ScatterMouseMoveEvent(self, typeID, ID):
        state = self.eventManager.state
        if typeID != TYPE_PIN or state in (planetConst.STATE_BUILDPIN, planetConst.STATE_SURVEY):
            surfacePoint = planetCommon.GetPickIntersectionPoint()
            if surfacePoint:
                self.eventManager.OnPlanetSurfaceMouseMoved(surfacePoint)

    def _ScatterMouseEnterEvent(self, typeID, ID):
        if typeID == TYPE_PIN:
            self.eventManager.OnPlanetPinMouseEnter(ID)
        elif typeID == TYPE_OTHERPLAYERSPIN:
            self.eventManager.OnPlanetOtherPinMouseEnter(ID)
        elif typeID == TYPE_LINK:
            self.eventManager.OnPlanetLinkMouseEnter(ID)
        elif typeID == TYPE_EXTRACTIONHEAD:
            self.eventManager.OnExtractionHeadMouseEnter(*ID)

    def _ScatterMouseExitEvent(self, typeID, ID):
        if typeID == TYPE_PIN:
            self.eventManager.OnPlanetPinMouseExit(ID)
        elif typeID == TYPE_OTHERPLAYERSPIN:
            self.eventManager.OnPlanetOtherPinMouseExit(ID)
        elif typeID == TYPE_LINK:
            self.eventManager.OnPlanetLinkMouseExit(ID)
        elif typeID == TYPE_EXTRACTIONHEAD:
            self.eventManager.OnExtractionHeadMouseExit(*ID)

    def OnClick(self, *args):
        typeID, ID, isTemplatePin = self.GetPick()
        if self.planetWasRotated or self.eventManager.state == planetConst.STATE_BUILDPIN:
            self.eventManager.OnPlanetNavClicked(self.planetWasRotated)
        elif isTemplatePin:
            self.eventManager.OnPlanetNavClicked(self.planetWasRotated)
        elif ID == self.mouseDownID:
            if typeID == TYPE_PIN:
                self.eventManager.OnPlanetPinClicked(ID)
            elif typeID == TYPE_LINK:
                self.eventManager.OnPlanetLinkClicked(ID)
            elif typeID == TYPE_OTHERPLAYERSPIN:
                self.eventManager.OnOtherCharactersCommandPinClicked(ID)
            elif typeID == TYPE_DEPLETIONPIN:
                self.eventManager.OnDepletionPinClicked(ID)
            elif typeID == TYPE_EXTRACTIONHEAD:
                self.eventManager.OnExtractionHeadClicked(*ID)
            else:
                self.eventManager.OnPlanetNavClicked(self.planetWasRotated)
        self.planetWasRotated = False
        self.mouseDownID = None
        self.cameraAuto = False

    def OnMouseDown(self, *args):
        if not uicore.uilib.leftbtn:
            return
        typeID, self.mouseDownID, isTemplatePin = self.GetPick()
        if typeID == TYPE_EXTRACTIONHEAD:
            self.eventManager.OnExtractionHeadMouseDown(*self.mouseDownID)
        elif typeID not in (TYPE_PIN, TYPE_LINK):
            self.orbitOnMouseMove = True

    def OnMouseUp(self, btnNum):
        self.eventManager.OnPlanetNavMouseUp()
        if btnNum == 0:
            self.orbitOnMouseMove = False
        elif btnNum == 1:
            self.rightMbtnUsedForCameraControl = False

    def OnDblClick(self, *args):
        surfacePoint = planetCommon.GetPickIntersectionPoint()
        typeID, ID, isTemplatePin = self.GetPick()
        if typeID == TYPE_PIN:
            self.eventManager.OnPlanetPinDblClicked(ID)
        elif typeID == TYPE_LINK:
            self.eventManager.OnPlanetLinkDblClicked(ID)
        elif typeID == TYPE_OTHERPLAYERSPIN:
            pass
        elif surfacePoint is not None:
            self.OrbitToCommandCenter()

    def OrbitToCommandCenter(self, initStartPos = False):
        pin = sm.GetService('planetUI').myPinManager.GetCommandCenterPin()
        if pin:
            self.cameraController.camera.OrbitToSurfacePoint(pin.surfacePoint, newZoom=0.15, initStartPos=initStartPos)
        else:
            self.cameraController.camera.SetZoomLinear(0.9)

    def OrbitToPointOfInterest(self, initStartPos = False):
        planetUISvc = sm.GetService('planetUI')
        pinsByTypeID = planetUISvc.myPinManager.GetPinsByGroupTypeIDs()
        extractionControlUnitPins = pinsByTypeID.get(groupExtractionControlUnitPins, [])
        spaceportPins = pinsByTypeID.get(groupSpaceportPins, [])
        if len(extractionControlUnitPins) > 0:
            pin = extractionControlUnitPins[0]
            self.cameraController.camera.OrbitToSurfacePoint(pin.surfacePoint, newZoom=0.15, initStartPos=initStartPos)
        elif len(spaceportPins) > 0:
            pin = spaceportPins[0]
            self.cameraController.camera.OrbitToSurfacePoint(pin.surfacePoint, newZoom=0.15, initStartPos=initStartPos)
        else:
            self.OrbitToCommandCenter(initStartPos=initStartPos)

    def OnMouseWheel(self, *args):
        self.cameraController.OnMouseWheel(*args)

    def ZoomBy(self, amount):
        self.cameraController.ZoomBy(amount)

    def DebugMenu(self):
        menu = []
        planetUISvc = sm.GetService('planetUI')
        planetID = sm.GetService('planetUI').planetID
        surfacePoint = planetCommon.GetPickIntersectionPoint()
        menuItems = [('ID: %d' % planetID, blue.pyos.SetClipboardData, [str(planetID)]),
         None,
         ('Verify Simulation', planetUISvc.VerifySimulation, []),
         ('Draw cartesian axis', planetUISvc.curveLineDrawer.DrawCartesianAxis, [])]
        if surfacePoint is not None:
            menuItems.append(('Get Local Resource Report', planetUISvc.GetLocalDistributionReport, [surfacePoint]))
            menuItems.append(('Add depletion point', planetUISvc.AddDepletionPoint, [surfacePoint]))
            menuItems.append(('Theta: {0} Phi: {1}'.format(surfacePoint.theta, surfacePoint.phi), blue.pyos.SetClipboardData, ['']))
        menu.extend(menuItems)
        return menu

    def GetMenu(self):
        typeID, ID, isTemplatePin = self.GetPick()
        if self.eventManager.OnPlanetNavRightClicked():
            return
        if typeID == TYPE_PIN:
            return self.myPinManager.GetPinMenu(ID)
        if typeID == TYPE_OTHERPLAYERSPIN:
            return self.otherPinManager.GetPinMenuOther(ID)
        if typeID == TYPE_LINK:
            m = self.myPinManager.GetLinkMenu(ID)
            if m:
                return m
        if getattr(self, 'rightMbtnUsedForCameraControl', None):
            self.rightMbtnUsedForCameraControl = False
            return
        m = []
        if session.role & ROLE_GML == ROLE_GML:
            m.append(['GM/Debug Menu...', self.DebugMenu()])
            m.append(None)
        if sm.GetService('planetUI').otherPinManager is not None:
            showOtherPins = settings.user.ui.Get('planetShowOtherCharactersPins', True)
            if showOtherPins:
                showOtherPinsTxt = MenuLabel('UI/PI/Common/HideOtherNetworks')
            else:
                showOtherPinsTxt = MenuLabel('UI/PI/Common/ShowOtherNetworks')
            m.append((showOtherPinsTxt, sm.GetService('planetUI').otherPinManager.ShowOrHideOtherCharactersPins, [not showOtherPins]))
        m.append((MenuLabel('UI/PI/Common/ExitPlanetMode'), sm.GetService('viewState').CloseSecondaryView, ('planet',)))
        return m

    def GetPick(self):
        scene = self.GetScene()
        x, y = uicore.uilib.x, uicore.uilib.y
        pickType = TYPE_PLANET
        id = None
        isTemplatePin = False
        if scene:
            areaID, pick = self.cameraController.GetPick(x, y, scene)
            if pick:
                if pick.__bluetype__ == 'trinity.EveSpherePin' and pick.name:
                    try:
                        pickType, id, isTemplatePin = self.GetPinTypeAndIDFromPickName(pick.name)
                    except Exception:
                        log.LogException('A pin with no ID was picked... this should not be possible:')
                        return (None, None, False)

                elif pick == sm.GetService('planetUI').curveLineDrawer.GetLineSet('links'):
                    pickType = TYPE_LINK
                    id = areaID
            else:
                pickType = TYPE_PLANET
                id = None
        else:
            pickType = None
        return (pickType, id, isTemplatePin)

    def GetScene(self):
        return sm.GetService('sceneManager').GetRegisteredScene('planet')

    def GetPinTypeAndIDFromPickName(self, pickName):
        ids = pickName.split(',')
        pinType = int(ids[0])
        isTemplatePin = False
        if pickName.endswith('temp'):
            isTemplatePin = True
        if pinType == planetCommon.PINTYPE_NORMAL:
            pickID = int(ids[1])
            pickType = TYPE_PIN
        elif pinType == planetCommon.PINTYPE_NORMALEDIT:
            pickID = (int(ids[1]), int(ids[2]))
            pickType = TYPE_PIN
        elif pinType == planetCommon.PINTYPE_EXTRACTIONHEAD:
            pickID = (int(ids[1]), int(ids[2]))
            pickType = TYPE_EXTRACTIONHEAD
        elif pinType == planetCommon.PINTYPE_OTHERS:
            pickID = int(ids[1])
            pickType = TYPE_OTHERPLAYERSPIN
        elif pinType == planetCommon.PINTYPE_DEPLETION:
            pickID = int(ids[1])
            pickType = TYPE_DEPLETIONPIN
        else:
            return (None, None, False)
        return (pickType, pickID, isTemplatePin)

    def GetCursor(self):
        state = self.eventManager.state
        if state in (planetConst.STATE_CREATELINKSTART, planetConst.STATE_CREATELINKEND):
            return 'res:/UI/Texture/Planet/Cursors/cursorCreateLink.png'
        elif state == planetConst.STATE_BUILDPIN:
            return 'res:/UI/Texture/Planet/Cursors/cursorPlacePin.png'
        elif state == planetConst.STATE_DECOMMISSION:
            return 'res:/UI/Texture/Planet/Cursors/cursorDecommission.png'
        elif state == planetConst.STATE_CREATEROUTE:
            return 'res:/UI/Texture/Planet/Cursors/cursorCreateRoute.png'
        elif state == planetConst.STATE_SURVEY and uicore.uilib.Key(uiconst.VK_CONTROL):
            return 'res:/UI/Texture/Planet/Cursors/cursorPlacePin.png'
        else:
            return uiconst.UICURSOR_DRAGGABLE

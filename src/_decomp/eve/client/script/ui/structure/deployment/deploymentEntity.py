#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\deploymentEntity.py
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
from evegraphics.utils import BuildSOFDNAFromTypeID
from carbonui.uicore import uicore
import evetypes
from moonmining.const import MOONMINING_NEVER_AVAILABLE, MOONMINING_NOT_POSSIBLE
from signals import Signal
import structures
import trinity
import blue
import geo2
from eve.client.script.environment.sofService import GetSofService
from structures.deployment import DEPLOY_DIST_MAX, IsDrillingPlatform
import fsdBuiltData.common.graphicIDs as fsdGraphicIDs

class StructurePlacementEntity(object):

    def __init__(self, typeID):
        self.typeID = typeID
        self.radius = evetypes.GetRadius(typeID)
        self.movingOffset = None
        self.cameraMatrixes = None
        self._opacity = 0.0
        self.blueprintColor = None
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.model_refinary_invalid = None
        self.model_valid = self._LoadModel(':variant?placement', display=True)
        self.model_invalid = self._LoadModel(':variant?forbiddenplacement', display=False)
        self.model_placement = self._LoadPlacementModel()
        self.on_location_updated = Signal(signalName='on_location_updated')
        self.UpdateModel()

    @property
    def model(self):
        if self.model_valid and self.model_valid.display:
            return self.model_valid
        if self.model_invalid and self.model_invalid.display:
            return self.model_invalid
        if self.model_refinary_invalid and self.model_refinary_invalid.display:
            return self.model_refinary_invalid

    def GetRefineryInvalidModel(self):
        if not getattr(self, 'model_refinary_invalid', None):
            self.model_refinary_invalid = self._LoadModel(':variant?refineryplacementunoptimal', display=False)
        return self.model_refinary_invalid

    def FindDeploymentConflict(self):
        ballsAndItems, position = self._GetPositionAndBalls()
        return structures.GetDeploymentConflictForBalls(self.ballpark, ballsAndItems, self.typeID, position)

    def GetMoonminingAvailabilityValue(self):
        if not IsDrillingPlatform(self.typeID):
            return MOONMINING_NEVER_AVAILABLE
        ballsAndItems, position = self._GetPositionAndBalls()
        return structures.GetMoonminingAvailabilityValueForBalls(ballsAndItems, self.typeID, position)

    def _GetPositionAndBalls(self):
        ship = self.ballpark.GetBall(session.shipid)
        position = geo2.Vec3AddD((ship.x, ship.y, ship.z), self.GetPosition())
        ballsAndItems = self.ballpark.GetBallsAndItems()
        return (ballsAndItems, position)

    def UpdateModel(self):
        conflict = self.FindDeploymentConflict()
        canMoonMine = self.GetMoonminingAvailabilityValue()
        isValidLocation = conflict is None
        changedModel = None
        if isValidLocation:
            if canMoonMine == MOONMINING_NOT_POSSIBLE:
                modelToShow = self.GetRefineryInvalidModel()
                modelToHide = self.model_valid
            else:
                modelToShow = self.model_valid
                modelToHide = self.model_refinary_invalid
            if not modelToShow.display:
                self.TryHideModel(modelToHide)
                self.model_invalid.display = False
                modelToShow.display = True
                modelToShow.translationCurve.value = self.model_invalid.translationCurve.value
                modelToShow.modelRotationCurve.value = self.model_invalid.modelRotationCurve.value
            changedModel = self.model
        elif not self.model_invalid.display:
            self.TryHideModel(self.model_refinary_invalid)
            currentModel = self.model_valid if self.model_valid.display else self.model_refinary_invalid
            self.model_valid.display = False
            self.model_invalid.display = True
            self.model_invalid.translationCurve.value = currentModel.translationCurve.value
            self.model_invalid.modelRotationCurve.value = currentModel.modelRotationCurve.value
            changedModel = self.model_invalid
        if changedModel and self.model_placement:
            self.model_placement.translationCurve = changedModel.translationCurve
            self.model_placement.modelRotationCurve = changedModel.modelRotationCurve
        self.on_location_updated(conflict, canMoonMine)

    def TryHideModel(self, modelToHide):
        if not modelToHide:
            return
        modelToHide.display = False

    def GetCurrShipPosition(self):
        ball = self.ballpark.GetBall(session.shipid)
        pos = ball.GetVectorAt(blue.os.GetSimTime())
        pos = (pos.x, 0, pos.z)
        camOffset = self.GetCamera().eyePosition
        camOffset = (camOffset[0], 0.0, camOffset[2])
        camDist = geo2.Vec3Length(camOffset)
        return geo2.Vec3Subtract(pos, geo2.Vec3Scale(camOffset, (structures.GetDeploymentDistance(const.typeCapsule) + self.radius) / camDist))

    def _LoadModel(self, variant, display):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None:
            return
        sof = GetSofService().spaceObjectFactory
        model = sof.BuildFromDNA(BuildSOFDNAFromTypeID(self.typeID) + variant)
        model.modelRotationCurve = trinity.Tr2RotationAdapter()
        model.translationCurve = trinity.Tr2TranslationAdapter()
        model.name = 'StructurePlacement'
        model.translationCurve.value = self.GetCurrShipPosition()
        model.display = display
        scene.objects.append(model)
        return model

    def _LoadPlacementModel(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None:
            return
        graphicID = evetypes.GetGraphicID(self.typeID)
        states = fsdGraphicIDs.GetAnimationStateObjects(graphicID, {})
        dna = states.get('placement', '')
        if not dna:
            return
        sof = GetSofService().spaceObjectFactory
        model = sof.BuildFromDNA(dna)
        model.name = 'StructurePlacementBlinkies'
        model.display = True
        scene.objects.append(model)
        return model

    def Close(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene:
            if self.model_valid:
                scene.objects.fremove(self.model_valid)
            if self.model_invalid:
                scene.objects.fremove(self.model_invalid)
            if self.model_placement:
                scene.objects.fremove(self.model_placement)
            if self.model_refinary_invalid:
                scene.objects.fremove(self.model_refinary_invalid)

    def UpdateModelPosition(self, pos):
        self.UpdateModel()
        if self.model:
            pos = geo2.Vec3Add(pos, self.movingOffset)
            pos = self.EnforcePositionRestrictions(pos)
            if pos:
                self.model.translationCurve.value = pos

    def GetPosition(self):
        return self.model.translationCurve.value

    def GetRotation(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self.model.modelRotationCurve.value)

    def EnforcePositionRestrictions(self, pos):
        vecLen = geo2.Vec3Length(pos)
        if vecLen > DEPLOY_DIST_MAX:
            return geo2.Vec3Scale(pos, DEPLOY_DIST_MAX / vecLen)
        else:
            return pos

    def UpdateModelRotation(self, dx):
        if self.model:
            rotation = geo2.QuaternionRotationAxis((0, 1.0, 0), dx)
            self.model.modelRotationCurve.value = geo2.QuaternionMultiply(self.model.modelRotationCurve.value, rotation)

    def SetModelRotation(self, yaw, pitch, roll):
        if self.model:
            rotation = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            self.model.modelRotationCurve.value = rotation

    def MoveDragObject(self):
        pYPlane, sign = self.GetMousePosToYPlaneIntersection()
        if sign > 0:
            self.UpdateModelPosition(pYPlane)

    def GetMousePosToYPlaneIntersection(self):
        ray, p0 = self.GetRayAndPointFromScreen()
        pYPlane, sign = self.GetIntersectionToYPlane(p0, ray)
        return (pYPlane, sign)

    def RotateDragObject(self):
        dx = float(uicore.uilib.dx * 0.01)
        self.UpdateModelRotation(dx)

    def GetRayAndPointFromScreen(self):
        x = float(uicore.uilib.x)
        y = float(uicore.uilib.y)
        data = self.GetCameraMatrixes()
        start = geo2.Vec3Unproject((x, y, 0.0), *data)
        end = geo2.Vec3Unproject((x, y, 100000.0), *data)
        ray = geo2.Vec3SubtractD(end, start)
        ray = geo2.Vector(*ray)
        start = geo2.Vector(*start)
        return (ray, start)

    def GetCameraMatrixes(self):
        if self.cameraMatrixes:
            return self.cameraMatrixes
        camera = self.GetCamera()
        viewPort = (0.0,
         0.0,
         float(uicore.desktop.width),
         float(uicore.desktop.height),
         0,
         100000.0)
        self.cameraMatrixes = (viewPort,
         camera.projectionMatrix.transform,
         camera.viewMatrix.transform,
         geo2.MatrixIdentity())
        return self.cameraMatrixes

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveCamera()

    def GetIntersectionToYPlane(self, p0, ray):
        intersection, sign = RayToPlaneIntersection(p0, ray, (0, 0, 0), (0, 1.0, 0), returnSign=True)
        return (intersection, sign)

    def StartMoving(self):
        structPos = self.model.translationCurve.value
        structPos = (structPos[0], 0, structPos[2])
        mousePos, sign = self.GetMousePosToYPlaneIntersection()
        if sign > 0:
            self.movingOffset = geo2.Vec3Subtract(structPos, mousePos)

    def EndMoving(self):
        self.cameraMatrixes = None
        self.movingOffset = None

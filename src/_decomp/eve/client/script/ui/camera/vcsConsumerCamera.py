#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\vcsConsumerCamera.py
import geo2
import trinity
import weakref
import logging
from carbon.common.script.util.mathCommon import FloatCloseEnough
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
from util.egoChangeSmoother import EgoChangeSmoother
logger = logging.getLogger(__name__)

def _ItemIDsToModels(itemIDs):
    ballpark = sm.GetService('michelle').GetBallpark()
    if ballpark is None:
        return
    found = []
    for itemID in itemIDs:
        ball = ballpark.GetBall(itemID)
        if hasattr(ball, 'model') and ball.model:
            found.append(ball.model)
        else:
            logger.warning('A trinity model could not be found for item ID: {}'.format(itemID))

    return found


def _LoadCameraFromFile(resFilePath):
    camera = trinity.Load(resFilePath)
    if not camera or not isinstance(camera, trinity.EveVirtualCamera):
        camera = None
    return camera


class _LinkedVirtualCamera(object):

    def __init__(self, virtualCameraInterface):
        self.vcsInterface = weakref.ref(virtualCameraInterface)
        self._sourceCamera = None
        self._egoChangeSmoother = EgoChangeSmoother(10.0)

    @property
    def externalCamera(self):
        vcsi = self.vcsInterface()
        if vcsi:
            return vcsi.externalCamera
        else:
            return None

    def Activate(self, lastCamera):
        self._sourceCamera = lastCamera

    def Deactivate(self):
        self._sourceCamera = None

    def Update(self):
        if self.externalCamera and self._sourceCamera:
            self.externalCamera.UpdateExternal(geo2.Vec3Add(self._sourceCamera.eyePosition, self._egoChangeSmoother.GetTotalOffset(8.0)), geo2.Vec3Add(self._sourceCamera.atPosition, self._egoChangeSmoother.GetTotalOffset(7.0)), self._sourceCamera.fov, self._sourceCamera.GetRoll())


class VirtualCameraSystemInterface(object):

    def __init__(self):
        self._vcs = None
        self._scene = None
        self._eveCameraLink = None

    @property
    def vcs(self):
        if not self._vcs:
            self._vcs = trinity.EveVirtualCameraSystem()
        return self._vcs

    @property
    def externalCamera(self):
        return self.vcs.externalCamera

    def FindCameraByName(self, name):
        return self.vcs.GetCameraByName(name)

    def Update(self, parentEveCamera):
        if self._eveCameraLink:
            self._eveCameraLink.Update()
        camera = self.vcs.GetCurrentCamera()
        if camera and not FloatCloseEnough(a=geo2.Vec3Distance(camera.pointOfInterest, camera.position), b=0.0, epsilon=0.01):
            parentEveCamera.eyePosition = camera.position
            parentEveCamera.atPosition = camera.pointOfInterest
            parentEveCamera.fov = camera.fov
            parentEveCamera.upDirection = camera.up

    def _CreateVirtualCamera(self):
        camera = trinity.EveVirtualCamera()
        self.vcs.cameras.append(camera)
        return camera

    def LoadVirtualCameraSystem(self, resFilePath):
        vcs = trinity.Load(resFilePath)
        if vcs and isinstance(vcs, trinity.EveVirtualCameraSystem):
            self._vcs = vcs
        else:
            vcs = None
        return vcs

    def AddCameraFromFile(self, resFilePath):
        logger.debug('Adding camera from file %s', resFilePath)
        camera = _LoadCameraFromFile(resFilePath)
        if camera:
            logger.debug("Adding camera '%s'", camera.name)
            self.vcs.cameras.append(camera)
        else:
            raise RuntimeError('Failed to load camera from {}'.format(resFilePath))
        return camera

    def SetAnchorsFromItemIDs(self, camera, positionAnchorIDs = None, pointOfInterestAnchorIDs = None):
        logger.debug("Adding anchors for camera '%s' posAnchorIDs=%s pointOfInterestAnchorIDs=%s", camera.name, positionAnchorIDs, pointOfInterestAnchorIDs)
        del camera.positionAnchors[:]
        del camera.pointOfInterestAnchors[:]
        if positionAnchorIDs is not None:
            camera.positionAnchors.extend(_ItemIDsToModels(positionAnchorIDs))
        if pointOfInterestAnchorIDs is not None:
            camera.pointOfInterestAnchors.extend(_ItemIDsToModels(pointOfInterestAnchorIDs))

    def CutToCamera(self, camera):
        logger.debug("Cut to camera '%s'", camera.name)
        self.vcs.CutToCamera(camera)

    def LerpToCamera(self, camera, transitionTime):
        currentCamera = self.vcs.GetCurrentCamera()
        logger.debug("Lerp to camera '%s'. Current camera is '%s'", camera.name, currentCamera.name if currentCamera else None)
        if not self.vcs.GetCurrentCamera():
            self.vcs.CutToCamera(camera)
        else:
            self.vcs.LerpToCamera(camera, transitionTime)

    def _CleanUpScene(self):
        if self._scene and self._scene.virtualCameraSystem is self.vcs:
            self._scene.virtualCameraSystem = None

    def _CleanUpVCS(self):
        self._CleanUpScene()
        self._eveCameraLink = None
        self._vcs = None

    def SetScene(self, scene):
        self._scene = scene

    def Activate(self, lastCamera):
        logger.debug('Activate camera. Last camera was %s', lastCamera.name if lastCamera else None)
        self._CleanUpScene()
        if not self._scene:
            self._scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if self._scene:
            self._scene.virtualCameraSystem = self.vcs
        if not self._eveCameraLink:
            self._eveCameraLink = _LinkedVirtualCamera(self)
        self._eveCameraLink.Activate(lastCamera)

    def Deactivate(self):
        logger.debug('Deactivate camera')
        if self._eveCameraLink:
            self._eveCameraLink.Deactivate()
        self._CleanUpVCS()
        self._scene = None

    def __del__(self):
        self.Deactivate()


class VCSConsumerCamera(BaseSpaceCamera):
    name = 'VirtualCamera'
    cameraID = evecamera.CAM_VCS_CONSUMER
    default_fov = 1.0

    def __init__(self):
        self._vcsInterface = VirtualCameraSystemInterface()
        super(VCSConsumerCamera, self).__init__()

    @property
    def vcsInterface(self):
        return self._vcsInterface

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        self.vcsInterface.Activate(lastCamera)
        super(VCSConsumerCamera, self).OnActivated(**kwargs)

    def OnDeactivated(self):
        self._vcsInterface.Deactivate()

    def GetItemID(self):
        return self.ego

    def IsLocked(self):
        return True

    def Track(self, itemID, **kwargs):
        pass

    def LookAt(self, itemID, radius = None, **kwargs):
        pass

    def Update(self):
        self._vcsInterface.Update(self)
        super(VCSConsumerCamera, self).Update()

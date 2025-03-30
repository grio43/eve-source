#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\camera\starmapCamera.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP
import evecamera

class StarmapCamera(CameraOld):
    cameraID = evecamera.CAM_STARMAP
    __notifyevents__ = []

    def _GetMinMaxTranslationFromParent(self):
        return (ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP)

    def LookAt(self, *args, **kwds):
        print 'LOOOOOOOOOOOOOOOOOK'

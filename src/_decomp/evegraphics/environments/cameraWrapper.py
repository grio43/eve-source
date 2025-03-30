#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\environments\cameraWrapper.py


def CreateCameraWrapper(cameraObject):
    if hasattr(cameraObject, 'view'):
        return CameraWrapper(cameraObject.view)
    if hasattr(cameraObject, 'viewMatrix'):
        return CameraWrapper(cameraObject.viewMatrix)


class CameraWrapper(object):

    def __init__(self, viewMatrix):
        self.viewMatrix = viewMatrix

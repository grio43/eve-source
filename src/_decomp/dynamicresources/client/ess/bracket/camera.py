#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\client\ess\bracket\camera.py
import geo2

class CameraReference(object):

    def get_camera(self):
        raise NotImplementedError()

    @property
    def is_valid(self):
        return self.get_camera() is not None

    @property
    def world_position(self):
        if not self.is_valid:
            return (0, 0, 0)
        return self.get_camera().GetEyePosition()

    @property
    def up(self):
        if not self.is_valid:
            return (0, 1.0, 0)
        return geo2.Vec3Normalize(self.get_camera().GetYAxis())

    @property
    def forward(self):
        if not self.is_valid:
            return (0, 0, 1.0)
        return self.get_camera().GetLookAtDirection()

    @property
    def left(self):
        return geo2.Vec3Cross(self.up, geo2.Vec3Scale(self.forward, -1.0))

    @property
    def right(self):
        return geo2.Vec3Cross(self.up, self.forward)

    def distance_from(self, position):
        return geo2.Vec3Length(geo2.Vec3Subtract(position, self.world_position))

    def distance_from_transform(self, transform):
        _, _, position = geo2.MatrixDecompose(transform.worldTransform)
        return self.distance_from(position)


class InFlightCameraReference(CameraReference):

    def __init__(self, scene_manager):
        self._scene_manager = scene_manager

    def get_camera(self):
        return self._scene_manager.GetActiveSpaceCamera()

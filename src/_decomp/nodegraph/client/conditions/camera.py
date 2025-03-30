#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\conditions\camera.py
from .base import Condition
from .parameters import SlimItemParameters

class CameraLookAtObject(SlimItemParameters):
    atom_id = 100

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        item_id = camera.GetLookAtItemID()
        if not item_id or item_id == camera.ego:
            return False
        return super(CameraLookAtObject, self).validate(item_id=item_id)


class CameraLookAtSelf(Condition):
    atom_id = 99

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        item_id = camera.GetLookAtItemID()
        return item_id is None or item_id == camera.ego


class CameraIsTracking(Condition):
    atom_id = 103

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        if not hasattr(camera, 'IsTracking'):
            return False
        return camera.IsTracking()


class CameraIsTrackingObject(SlimItemParameters):
    atom_id = 104

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        if not hasattr(camera, 'IsTracking') or not camera.IsTracking():
            return False
        track_ball = getattr(camera, 'trackBall', None)
        if not track_ball:
            return False
        return super(CameraIsTrackingObject, self).validate(item_id=track_ball.id)


class CameraIsInView(Condition):
    atom_id = 212

    def __init__(self, item_id = None, **kwargs):
        super(CameraIsInView, self).__init__(**kwargs)
        self.item_id = item_id

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        if not hasattr(camera, 'IsWithinViewFrustum'):
            return False
        return camera.IsWithinViewFrustum(self.item_id)


class CameraIsInViewAngle(Condition):
    atom_id = 213

    def __init__(self, item_id = None, angle = None, **kwargs):
        super(CameraIsInViewAngle, self).__init__(**kwargs)
        self.item_id = item_id
        self.angle = angle

    def validate(self, **kwargs):
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not camera:
            return False
        if not hasattr(camera, 'IsWithinViewAngle'):
            return False
        return camera.IsWithinViewAngle(self.item_id, self.angle)

    @classmethod
    def get_subtitle(cls, angle = None, **kwargs):
        if angle:
            return '{angle} degrees'.format(angle=angle)
        return ''


class ViewStateActive(Condition):
    atom_id = 438

    def __init__(self, view_state = None, **kwargs):
        super(ViewStateActive, self).__init__(**kwargs)
        self.view_state = self.get_atom_parameter_value('view_state', view_state)

    def validate(self, **kwargs):
        try:
            return sm.GetService('viewState').IsViewActive(self.view_state)
        except AttributeError:
            return False

    @classmethod
    def get_subtitle(cls, view_state = None, **kwargs):
        return cls.get_atom_parameter_value('view_state', view_state)

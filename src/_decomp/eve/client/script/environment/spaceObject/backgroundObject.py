#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\backgroundObject.py
import math
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from gametime import GetSecondsSinceSimTime
import geo2
import trinity

class BackgroundObject(SpaceObject):

    def LoadModel(self):
        graphicURL = self.typeData.get('graphicFile')
        if graphicURL is None:
            self.logger.error('BackgroundObject graphicURL is None, cannot load model. TypeID is %s', self.typeID)
            return
        obj = trinity.Load(graphicURL)
        self.backgroundObject = obj
        slimItem = self.typeData.get('slimItem', None)
        if slimItem:
            position = slimItem.dunPosition
            if position:
                try:
                    self.backgroundObject.translation = position
                except AttributeError:
                    pass

            if hasattr(obj, 'SetControllerVariable'):
                timeAddedToSpace = slimItem.timeAddedToSpace or -1
                lifetime = GetSecondsSinceSimTime(timeAddedToSpace)
                removalAge = slimItem.duration or lifetime + 90000.0
                obj.SetControllerVariable('lifeTime', lifetime)
                obj.SetControllerVariable('removeTime', removalAge)
        rot = self.typeData.get('dunRotation', None)
        if rot:
            yaw, pitch, roll = map(math.radians, rot)
            quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            try:
                self.backgroundObject.rotation = quat
            except AttributeError:
                pass

        scene = self.spaceMgr.GetScene()
        scene.backgroundObjects.append(obj)
        self.SetupAmbientAudio(model=obj)
        try:
            obj.StartControllers()
        except AttributeError:
            pass

    def Release(self):
        if self.released or not hasattr(self, 'backgroundObject'):
            return
        scene = self.spaceMgr.GetScene()
        if scene:
            scene.backgroundObjects.fremove(self.backgroundObject)
        self.backgroundObject = None
        SpaceObject.Release(self, 'BackgroundObject')

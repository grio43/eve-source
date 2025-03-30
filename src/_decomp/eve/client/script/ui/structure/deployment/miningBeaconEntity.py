#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\miningBeaconEntity.py
import trinity
from moonmining.const import MAXIMUM_MINING_BEACON_DISTANCE

class MiningBeaconEntity(object):

    def __init__(self, beaconPosition):
        self.clientBall = None
        self.sphereModel = None
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None:
            return
        self._Setup(scene, beaconPosition)

    def _Setup(self, scene, beaconPosition):
        ballpark = sm.GetService('michelle').GetBallpark()
        self.clientBall = ballpark.AddClientSideBall(beaconPosition)
        self.sphereModel = trinity.Load('res:/ui/inflight/tactical/rangeSphereBlue.red')
        self.sphereModel.scaling = (2 * MAXIMUM_MINING_BEACON_DISTANCE, 2 * MAXIMUM_MINING_BEACON_DISTANCE, 2 * MAXIMUM_MINING_BEACON_DISTANCE)
        self.sphereModel.translationCurve = self.clientBall
        self.sphereModel.display = True
        scene.objects.append(self.sphereModel)

    def Close(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene:
            if self.sphereModel:
                scene.objects.fremove(self.sphereModel)
                self.sphereModel = None
        if self.clientBall:
            ballpark = sm.GetService('michelle').GetBallpark()
            ballpark.RemoveBall(self.clientBall.id)

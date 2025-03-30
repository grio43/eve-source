#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\structureDrillingPlatform.py
import blue
from eve.client.script.environment.model.turretSet import StructureMoonMiningTurretSet
from eve.client.script.environment.spaceObject.structure import Structure
import inventorycommon.const as invConst
import uthread

class StructureDrillingPlatform(Structure):

    def __init__(self):
        super(StructureDrillingPlatform, self).__init__()
        self.closestMoon = None
        self.closestMoonID = None
        self.moonMiningTurret = None

    def _OnSlimItemUpdated(self, item, taskletSpawner):
        self.closestMoonID = item.closestMoonID
        super(StructureDrillingPlatform, self)._OnSlimItemUpdated(item, taskletSpawner)

    def FitHardpoints(self, blocking = False):
        super(StructureDrillingPlatform, self).FitHardpoints(blocking)
        for turret in self.turrets:
            if isinstance(turret, StructureMoonMiningTurretSet):
                self.moonMiningTurret = turret
                if self.closestMoonID is not None:
                    ball = sm.GetService('michelle').GetBall(self.closestMoonID)
                    if ball.GetModel() is None:
                        ball.RegisterForModelLoad(self.SetMoonDrillTarget)
                    else:
                        self.SetMoonDrillTarget()

    def SetMoonDrillTarget(self):
        self.moonMiningTurret.SetMoonID(self.closestMoonID)

    def UnfitHardpoints(self):
        super(StructureDrillingPlatform, self).UnfitHardpoints()
        self.moonMiningTurret = None

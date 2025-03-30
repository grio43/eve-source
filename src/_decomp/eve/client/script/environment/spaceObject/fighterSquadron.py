#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\fighterSquadron.py
import trinity
import Drone
import evegraphics.settings as gfxsettings
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from fighters.client import GetSquadronSizeFromSlimItem
from fighters import GetTurretGraphicIDsForFighter
import eve.client.script.environment.model.turretSet as turretSet
from tacticalNavigation.ballparkFunctions import ConvertPositionToGlobalSpace

class FighterSquadronError(Exception):
    pass


class FighterSquadron(Drone.Drone):

    def __init__(self):
        Drone.Drone.__init__(self)
        self.squadronSize = 0

    def GetDNA(self):
        dna = super(FighterSquadron, self).GetDNA()
        return dna.replace(':class?ship', '')

    def Assemble(self):
        if not self._usingDroneModel:
            return
        self.FitBoosters(alwaysOn=False)
        self.SetupAmbientAudio()
        self.model.EnableSwarming(True)
        self.squadronSize = GetSquadronSizeFromSlimItem(self.typeData['slimItem'])
        if self.squadronSize is None:
            self.squadronSize = 1
        self.model.SetCount(self.squadronSize)

    def FitHardpoints(self, blocking = False):
        if self.fitted or self.squadronSize == 0:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.fitted = True
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        self._PopulateTurretSets()

    def _AddTurretModules(self, slotID, graphicID, count):
        index = len(self.modules[slotID])
        for i in range(count):
            ts = turretSet.TurretSet.AddTurretToModel(self.model, graphicID, swarmID=index + i)
            ts.turretIndex = index + i
            if ts is not None:
                self.modules[slotID].append(ts)

    def _PopulateModuleSlot(self, slotID, graphicID):
        if self.modules is None:
            return
        if slotID not in self.modules:
            self.modules[slotID] = []
            self._AddTurretModules(slotID, graphicID, self.squadronSize)
        elif self.squadronSize > len(self.modules[slotID]):
            self._AddTurretModules(slotID, graphicID, self.squadronSize - len(self.modules[slotID]))
        else:
            removeTurrets = self.modules[slotID][self.squadronSize:]
            self.modules[slotID] = self.modules[slotID][:self.squadronSize]
            for turret in removeTurrets:
                turret.RemoveTurretFromModel(self.model)

    def _PopulateTurretSets(self):
        slotIDtoGraphicID = GetTurretGraphicIDsForFighter(self.GetTypeID())
        for slotID, graphicID in slotIDtoGraphicID.iteritems():
            self._PopulateModuleSlot(slotID, graphicID)

    def DestroyClientBall(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None and ball.ballpark is not None:
            bp.RemoveBall(ball.id)

    def _ClearExplosion(self, model):
        if model is None:
            return
        if model.translationCurve is not None:
            self.DestroyClientBall(model.translationCurve)
            model.translationCurve = None
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene.objects.fremove(model)

    def SpawnExplosion(self, position):
        if gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            SpaceObjectExplosionManager.PlayExplosionAtPosition(self.explosionBucketID, 'default', ConvertPositionToGlobalSpace(position), scene)

    def DestroyFighter(self):
        if self.model is None:
            return
        if not self._usingDroneModel:
            return
        try:
            position = self.model.RemoveSwarmer()
            self.SpawnExplosion(position)
        except:
            self._RaiseFighterException('DestroyFighter failed!')

    def OnSlimItemUpdated(self, slimItem):
        if self.model is None:
            return
        if not self._usingDroneModel:
            return
        oldSize = self.squadronSize
        self.squadronSize = GetSquadronSizeFromSlimItem(slimItem)
        if self.squadronSize > oldSize:
            self.model.SetCount(self.squadronSize)
            self._PopulateTurretSets()
        else:
            for i in range(oldSize - self.squadronSize):
                self.DestroyFighter()

            self._PopulateTurretSets()

    def Explode(self):
        if not self._usingDroneModel or not gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            return False
        if self.exploded:
            return
        while self.squadronSize > 0:
            self.DestroyFighter()
            self.squadronSize -= 1

        self.exploded = True
        return False

    def _RaiseFighterException(self, header = ''):
        message = header + '\n'
        message += 'typeID: ' + str(self.typeData.get('typeID', 'None')) + '\n'
        message += 'bluetype: ' + getattr(self.model, '__bluetype__', 'None')
        raise FighterSquadronError(message)

    def PrepareForFiring(self):
        if self.model is None:
            return
        if not self._usingDroneModel:
            return
        try:
            self.model.PickFiringOrigin()
        except:
            self._RaiseFighterException('PickFiringOrigin failed!')

    def GetPositionCurve(self):
        if self.model is None:
            return self
        curve = trinity.EveLocalPositionCurve()
        curve.parent = self.model
        curve.behavior = trinity.EveLocalPositionBehavior.centerBounds
        return curve

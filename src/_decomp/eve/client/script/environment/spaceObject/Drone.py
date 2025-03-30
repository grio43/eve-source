#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\Drone.py
import blue
import trinity
import eve.client.script.environment.spaceObject.ship as ship
import evegraphics.settings as gfxsettings
import eveSpaceObject
import eve.client.script.environment.model.turretSet as turretSet

class Drone(ship.Ship):

    def __init__(self):
        ship.Ship.__init__(self)
        self._usingDroneModel = True

    def GetDNA(self):
        dna = super(Drone, self).GetDNA()
        if dna and ':class?' not in dna:
            dna += ':class?ship'
        return dna

    def LoadModel(self, fileName = None, loadedModel = None):
        droneModel = None
        if not self.IsDroneModelEnabled():
            droneModel = trinity.EveShip2()
            loc = trinity.EveLocator2()
            loc.name = 'locator_turret_1a'
            droneModel.locators.append(loc)
            self._usingDroneModel = False
        ship.Ship.LoadModel(self, fileName, droneModel)

    def Assemble(self):
        if not self.IsDroneModelEnabled():
            return
        self.FitBoosters(alwaysOn=True, enableTrails=False)
        self.SetupAmbientAudio()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.fitted = True
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        groupID = self.typeData.get('groupID', None)
        raceName = self.typeData.get('sofRaceName', None)
        typeID = self.typeData.get('typeID', None)
        droneGroup = eveSpaceObject.droneGroupFromTypeGroup.get(groupID, None)
        if droneGroup is None:
            self.logger.error('FitHardpoints - no gfx drone group for groupID %s', str(groupID))
            return
        turretGfxIDs = eveSpaceObject.droneTurretGfxID.get(droneGroup, None)
        if turretGfxIDs is None:
            self.logger.error('FitHardpoints - no turret gfxID info for drone group %s', str(droneGroup))
            return
        turretGraphicID = turretGfxIDs[1]
        if typeID in eveSpaceObject.droneTypeGroup:
            turretGraphicID = eveSpaceObject.droneTypeGroup.get(typeID, None)
        elif turretGfxIDs[0] is not None:
            if raceName is not None:
                turretGraphicID = turretGfxIDs[0].get(raceName, turretGfxIDs[1])
        if turretGraphicID is not None:
            ts = turretSet.TurretSet.AddTurretToModel(self.model, turretGraphicID)
            if ts is not None and self.modules is not None:
                self.modules[self.id] = ts

    def Explode(self):
        if not self.IsDroneModelEnabled():
            return False
        return super(Drone, self).Explode()

    def IsDroneModelEnabled(self):
        groupID = self.typeData.get('groupID', None)
        droneGroup = eveSpaceObject.droneGroupFromTypeGroup.get(groupID, None)
        if droneGroup == eveSpaceObject.gfxDroneGroupNpc:
            return True
        return gfxsettings.Get(gfxsettings.UI_DRONE_MODELS_ENABLED)

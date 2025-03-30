#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\structureSentryGun.py
import eve.client.script.environment.model.turretSet as turretSet
from eve.client.script.environment.spaceObject.playerOwnedStructure import PlayerOwnedStructure
import evegraphics.settings as gfxsettings

class StructureSentryGun(PlayerOwnedStructure):

    def __init__(self):
        PlayerOwnedStructure.__init__(self)
        self.modules = {}
        self.fitted = False
        self.turretTypeID = None
        self.typeID = None

    def Assemble(self):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        godmaStateManager = sm.StartService('godma').GetStateManager()
        godmaType = godmaStateManager.GetType(slimItem.typeID)
        self.turretTypeID = godmaType.gfxTurretID
        self.typeID = slimItem.typeID
        if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED) and self.IsAnchored():
            self.FitHardpoints()

    def FitHardpoints(self, blocking = False):
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        if self.fitted:
            return
        if self.typeID is None:
            self.logger.warning('FitHardpoints - No typeID')
            return
        newTurretSet = turretSet.TurretSet.FitTurret(self.model, self.turretTypeID, 1, self.typeData.get('sofFactionName', None))
        if newTurretSet is None:
            return
        self.fitted = True
        self.modules[self.id] = newTurretSet

    def StartBuildingEffect(self, state, dogmaBuildingLength, elapsedTime):
        PlayerOwnedStructure.StartBuildingEffect(self, state, dogmaBuildingLength, elapsedTime)
        if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            self.FitHardpoints()

    def Release(self):
        PlayerOwnedStructure.Release(self, 'spaceObject.StructureSentryGun')

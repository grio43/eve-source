#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\entityShip.py
import blue
import destiny
from caching import Memoize
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.spaceObject.ship import Ship
from eve.client.script.environment.model.turretSet import TurretSet
import eve.common.lib.appConst as const
import evetypes
import mathext

@Memoize
def _GetTypesWithThreeTurretHardPoints():
    return evetypes.GetTypeIDsByListID(evetypes.TYPE_LIST_MAX_THREE_TURRET_HARD_POINTS)


class EntityShip(Ship):
    launcherTypeCache = {}

    def __init__(self):
        Ship.__init__(self)
        self.gfxTurretID = None
        self.fitted = False
        self.typeID = None
        self.modules = {}
        self.model = None
        self.launcherTypeID = None

    def GetDNA(self):
        dna = Ship.GetDNA(self)
        if dna and ':class?' not in dna:
            dna += ':class?ship'
        return dna

    def LoadModel(self, fileName = None, loadedModel = None):
        godma = self.sm.GetService('godma')
        godmaStateManager = godma.GetStateManager()
        godmaType = godmaStateManager.GetType(self.typeID)
        self.turretTypeID = godmaType.gfxTurretID
        missileTypeID = godmaType.entityMissileTypeID
        self.launcherTypeID = self.DetermineLauncherTypeFromMissileID(self.typeID, missileTypeID)
        SpaceObject.LoadModel(self)

    def Assemble(self):
        Ship.Assemble(self)
        self.FitBoosters(isNPC=True)
        self.SetupSharedAmbientAudio()

    def DetermineLauncherTypeFromMissileID(self, typeID, missileTypeID):
        launcherType = self.launcherTypeCache.get(missileTypeID, None)
        if launcherType:
            return launcherType
        clientDogma = self.sm.GetService('clientDogmaStaticSvc')
        usesMissiles = clientDogma.TypeHasEffect(typeID, const.effectMissileLaunchingForEntity)
        if not usesMissiles:
            return
        godma = self.sm.GetService('godma')
        group = int(godma.GetTypeAttribute2(missileTypeID, const.attributeLauncherGroup))
        for typeID in evetypes.GetTypeIDsByGroup(group):
            if evetypes.GetVariationChildren(typeID):
                launcherType = typeID
                self.launcherTypeCache[missileTypeID] = launcherType
                break

        return launcherType

    def LookAtMe(self):
        if self.model is None:
            return
        if not self.fitted:
            self.FitHardpoints()

    def FitHardpoints(self, blocking = False):
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        if self.fitted:
            return
        self.fitted = True
        turretLocatorCount = int(self.model.GetTurretLocatorCount())
        if self.typeID in _GetTypesWithThreeTurretHardPoints():
            turretLocatorCount = mathext.clamp(turretLocatorCount, 1, 3)
        if self.launcherTypeID:
            launcherSet = TurretSet.FitTurret(self.model, self.launcherTypeID, turretLocatorCount, count=1)
            self.modules[0] = launcherSet
            turretLocatorCount = max(turretLocatorCount - 1, 1)
        if evetypes.GetGroupID(self.turretTypeID) in (const.groupPrecursorTurret, const.groupChainLightningTurret):
            turretLocatorCount = 1
        newTurretSet = TurretSet.FitTurret(self.model, self.turretTypeID, -1, count=turretLocatorCount)
        if newTurretSet is not None:
            self.modules[self.id] = newTurretSet

    def Release(self):
        if self.released:
            return
        for turretPair in self.modules.itervalues():
            if turretPair is not None:
                turretPair.Release()
                turretPair.owner = None

        self.modules = {}
        Ship.Release(self)


class EntitySleeper(EntityShip):

    def FitHardpoints(self, blocking = False):
        if self.launcherTypeID:
            self.launcherTypeID = 0
        EntityShip.FitHardpoints(self)

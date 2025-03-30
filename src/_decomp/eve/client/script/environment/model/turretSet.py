#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\model\turretSet.py
import remotefilecache
import inventorycommon.typeHelpers
import trinity
import blue
import log
import evetypes
import evegraphics.settings as gfxsettings
from eve.common.script.sys import eveCfg
from stacklesslib.util import block_trap
from fsdBuiltData.common.graphicIDs import GetGraphic, GetGraphicFile, GetAmmoColor
import inventorycommon.const as const
from eve.client.script.environment.sofService import GetSofService
LOCATOR_MOONHARVESTER = 'locator_moonharvester_'
LOCATOR_TURRET = 'locator_turret_'

def GetTurretSetCount(model, turretTypeID):
    try:
        graphicId = evetypes.GetGraphicID(turretTypeID)
    except evetypes.TypeNotFoundException:
        return 0

    if not graphicId:
        return 0
    turret = trinity.Load(GetGraphicFile(graphicId))
    if turret is None or not isinstance(turret, trinity.EveTurretSet):
        return 0
    locators = [ loc for loc in model.locators if loc.name.startswith(turret.locatorName) ]
    if len(locators) == 0:
        locators = [ loc for loc in model.locators if loc.name.startswith(LOCATOR_TURRET) ]
    locatorSets = {filter(str.isdigit, loc.name) for loc in locators}
    return len(locatorSets)


class TurretSet(object):
    turretsEnabled = [False]

    def Initialize(self, graphics, locator, overrideBeamGraphicID = None, count = 1, swarmID = 0):
        self.inWarp = False
        self.isShooting = False
        self.targetsAvailable = False
        self.online = True
        self.targetID = None
        self.turretTypeID = 0
        self.turretGroupID = 0
        self.turretSets = []
        if not hasattr(graphics, 'graphicFile'):
            log.LogError('No turret redfile defined for: ' + str(graphics))
            return self.turretSets
        turretPath = graphics.graphicFile
        for i in range(count):
            tSet = trinity.Load(turretPath)
            if tSet is None:
                continue
            if len(tSet.locatorName) == 0:
                tSet.locatorName = LOCATOR_TURRET
            elif tSet.locatorName[-1].isdigit():
                tSet.locatorName = tSet.locatorName[:-1]
            if locator < 0:
                tSet.slotNumber = i + 1
            elif tSet.locatorName == LOCATOR_MOONHARVESTER:
                tSet.slotNumber = 1
            else:
                tSet.slotNumber = locator
            tSet.swarmID = swarmID
            self.turretSets.append(tSet)

        for turretSet in self.turretSets:
            turretFxPath = turretSet.firingEffectResPath
            try:
                effect = blue.recycler.RecycleOrLoad(turretFxPath)
            except RuntimeError:
                log.LogError('Could not load firing effect ' + turretFxPath + ' for turret: ' + turretPath)
                effect = None

            turretSet.firingEffect = effect

        return self.turretSets

    def __del__(self):
        for turretSet in self.turretSets:
            for stretch in turretSet.firingEffect.stretch:
                if hasattr(stretch, 'sourceSpaceObject'):
                    stretch.sourceSpaceObject = None
                if hasattr(stretch, 'destSpaceObject'):
                    stretch.destSpaceObject = None

    def RemoveTurretFromModel(self, model):
        for tSet in self.turretSets:
            model.turretSets.remove(tSet)

    def GetTurretSet(self, index = 0):
        return self.turretSets[index]

    def GetTurretSets(self):
        return self.turretSets

    def Release(self):
        pass

    def SetTargetsAvailable(self, available):
        if self.targetsAvailable and not available:
            self.Rest()
        self.targetsAvailable = available

    def SetTarget(self, targetID):
        self.targetID = targetID
        targetBall = sm.GetService('michelle').GetBall(targetID)
        if targetBall is not None:
            targetModel = getattr(targetBall, 'model', None)
            if targetModel is not None:
                for turretSet in self.turretSets:
                    turretSet.targetObject = targetBall.model

            else:
                self.targetID = None

    def SetAmmoColorByTypeID(self, ammoTypeID):
        gfxid = evetypes.GetGraphicID(ammoTypeID)
        ammoColor = GetAmmoColor(gfxid)
        if ammoColor is not None:
            color = tuple(ammoColor)
            self.SetAmmoColor(color)

    def SetDestSpaceObject(self, targetModel):
        for turretSet in self.turretSets:
            for stretch in turretSet.firingEffect.stretch:
                if hasattr(stretch, 'destSpaceObject'):
                    stretch.destSpaceObject = targetModel

    def SetSourceSpaceObject(self, sourceModel):
        for turretSet in self.turretSets:
            for stretch in turretSet.firingEffect.stretch:
                if hasattr(stretch, 'sourceSpaceObject'):
                    stretch.sourceSpaceObject = sourceModel

    def SetAmmoColor(self, color):
        if color is None:
            return
        for curve in self.GetCurveConstants('Ammo'):
            curve.value = color

    def StartControllers(self):
        for turretSet in self.turretSets:
            turretSet.StartControllers()

    def SetControllerVariable(self, name, value):
        for turretSet in self.turretSets:
            turretSet.SetControllerVariable(name, value)

    def SetIntensity(self, intensity):
        for curve in self.GetCurveConstants('py_intensity'):
            curve.value = (intensity,
             curve.value[1],
             curve.value[2],
             curve.value[3])

    def GetCurveConstants(self, name):
        curves = []
        for turretSet in self.turretSets:
            if turretSet.firingEffect is not None:
                for curve in turretSet.firingEffect.Find('trinity.Tr2CurveConstant'):
                    if curve.name == name:
                        curves.append(curve)

        return curves

    def IsShooting(self):
        return self.isShooting

    def StartShooting(self, ignoreTarget = False):
        if self.inWarp:
            return
        if self.targetID is None and ignoreTarget is not True:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateFiring()

        self.isShooting = True

    def StopShooting(self):
        for turretSet in self.turretSets:
            if self.inWarp:
                turretSet.EnterStateDeactive()
            elif self.targetsAvailable:
                turretSet.EnterStateTargeting()
            else:
                turretSet.EnterStateIdle()

        self.isShooting = False

    def Rest(self):
        if self.inWarp or not self.online:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateIdle()

    def Offline(self):
        if self.online == False:
            return
        self.online = False
        for turretSet in self.turretSets:
            turretSet.isOnline = False
            turretSet.EnterStateDeactive()

    def Online(self):
        if self.online:
            return
        self.online = True
        for turretSet in self.turretSets:
            turretSet.isOnline = True
            turretSet.EnterStateIdle()

    def Reload(self):
        for turretSet in self.turretSets:
            turretSet.EnterStateReloading()

    def EnterWarp(self):
        self.inWarp = True
        for turretSet in self.turretSets:
            turretSet.EnterStateDeactive()

    def ExitWarp(self):
        self.inWarp = False
        if self.online:
            for turretSet in self.turretSets:
                turretSet.EnterStateIdle()

    def TakeAim(self, targetID):
        if self.targetID != targetID:
            return
        if not self.online:
            return
        for turretSet in self.turretSets:
            turretSet.EnterStateTargeting()

    @staticmethod
    def _isFittableTurret(type, group):
        if group in const.turretModuleGroups:
            return True
        if type in (const.typeTriglavianArmorRepairModule1,
         const.typeTriglavianArmorRepairModule2,
         const.typeTriglavianArmorRepairModule3,
         const.typeTriglavianArmorRepairModule4,
         const.typeTriglavianArmorRepairModule5):
            return True
        return False

    @staticmethod
    def AddTurretToModel(model, turretGraphicsID, turretFaction = None, locatorID = 1, count = 1, swarmID = 0, turretTypeID = None):
        if not hasattr(model, 'turretSets'):
            log.LogError('Wrong object is trying to get turret attached due to wrong authored content! model:' + model.name + ' bluetype:' + model.__bluetype__)
            return
        graphics = GetGraphic(turretGraphicsID)
        if turretTypeID is not None and evetypes.GetGroupID(turretTypeID) == const.groupStructureMoonDrillingServiceModule:
            newTurretSet = StructureMoonMiningTurretSet()
        else:
            newTurretSet = TurretSet()
        eveTurretSets = newTurretSet.Initialize(graphics, locatorID, None, count=count, swarmID=swarmID)
        spaceObjectFactory = GetSofService().spaceObjectFactory
        for tSet in eveTurretSets:
            if model.dna:
                spaceObjectFactory.SetupTurretMaterialFromDNA(tSet, model.dna)
            elif turretFaction is not None:
                spaceObjectFactory.SetupTurretMaterialFromFaction(tSet, turretFaction)
            model.turretSets.append(tSet)

        return newTurretSet

    @staticmethod
    def FitTurret(model, turretTypeID, locatorID, turretFaction = None, count = 1, online = True, checkSettings = True):
        if not evetypes.Exists(turretTypeID):
            return
        if checkSettings and not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        groupID = evetypes.GetGroupID(turretTypeID)
        if model is None:
            log.LogError('FitTurret() called with NoneType, so there is no model to fit the turret to!')
            return
        if not TurretSet._isFittableTurret(turretTypeID, groupID):
            return
        newTurretSet = None
        graphicID = evetypes.GetGraphicID(turretTypeID)
        if graphicID is not None:
            newTurretSet = TurretSet.AddTurretToModel(model, graphicID, turretFaction, locatorID, count, turretTypeID=turretTypeID)
            if newTurretSet is None:
                return
            if not online:
                newTurretSet.Offline()
            newTurretSet.turretTypeID = turretTypeID
            newTurretSet.turretGroupID = groupID
        return newTurretSet

    @staticmethod
    def PrefetchGraphicsForModules(modules):
        prefetch_set = set()
        for moduleID, typeID, slot, isOnline, count in modules:
            if not evetypes.Exists(typeID):
                continue
            if evetypes.Exists(typeID) and evetypes.GetGroupID(typeID) not in const.turretModuleGroups:
                continue
            turretPath = inventorycommon.typeHelpers.GetGraphicFile(typeID)
            if turretPath:
                prefetch_set.add(turretPath)

        remotefilecache.prefetch_files(prefetch_set)

    @staticmethod
    def GetSlotFromModuleFlagID(flagID):
        if flagID in const.hiSlotFlags:
            return flagID - const.flagHiSlot0 + 1
        elif flagID in const.medSlotFlags:
            return flagID - const.flagMedSlot0 + 1
        else:
            return -1

    @staticmethod
    def FitTurrets(shipID, model, shipFaction = None):
        if not hasattr(model, 'turretSets'):
            return {}
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return {}
        turretsFitted = {}
        modules = []
        if shipID == eveCfg.GetActiveShip():
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            if not dogmaLocation.IsItemLoaded(shipID):
                return {}
            dogmaLocation.LoadItem(shipID)
            ship = dogmaLocation.GetDogmaItem(shipID)
            modules = []
            for module in ship.GetFittedItems().itervalues():
                slot = TurretSet.GetSlotFromModuleFlagID(module.flagID)
                if module.groupID in const.turretModuleGroups:
                    modules.append([module.itemID,
                     module.typeID,
                     slot,
                     module.IsOnline(),
                     1])

        else:
            bp = sm.StartService('michelle').GetBallpark()
            slimItem = bp.GetInvItem(shipID) if bp else None
            if slimItem is not None:
                for itemID, typeID, flagID in slimItem.modules:
                    slot = TurretSet.GetSlotFromModuleFlagID(flagID)
                    modules.append([itemID,
                     typeID,
                     slot,
                     True,
                     1])

                if len(modules) == 0:
                    godma = sm.GetService('godma')
                    godmaStateManager = godma.GetStateManager()
                    godmaType = godmaStateManager.GetType(slimItem.typeID)
                    if godmaType.gfxTurretID > 0:
                        turretCount = GetTurretSetCount(model, godmaType.gfxTurretID)
                        if turretCount != 0:
                            modules.append([shipID,
                             godmaType.gfxTurretID,
                             -1,
                             True,
                             turretCount])
        TurretSet.PrefetchGraphicsForModules(modules)
        with block_trap():
            del model.turretSets[:]
            modules = sorted(modules, key=lambda x: x[2])
            locatorCounter = 1
            for moduleID, typeID, slot, isOnline, count in modules:
                slot = slot or locatorCounter
                ts = TurretSet.FitTurret(model, typeID, slot, shipFaction, online=isOnline, count=count)
                if ts is not None:
                    turretsFitted[moduleID] = ts
                    locatorCounter += count

            return turretsFitted


class StructureMoonMiningTurretSet(TurretSet):

    def __init__(self):
        self.moonID = None

    def Initialize(self, graphics, locator, overrideBeamGraphicID = None, count = 1, swarmID = 0):
        turretSets = super(StructureMoonMiningTurretSet, self).Initialize(graphics, locator, overrideBeamGraphicID, count, swarmID)
        self.Display(False)
        return turretSets

    def SetMoonID(self, moonID):
        if moonID == self.moonID:
            return
        self.moonID = moonID
        self.SetTarget(moonID)
        self.TakeAim(moonID)
        self.Display()

    def Display(self, display = True):
        for ts in self.turretSets:
            ts.display = display

    def Rest(self):
        self.TakeAim(self.moonID)

    def Offline(self):
        pass

    def Online(self):
        super(StructureMoonMiningTurretSet, self).Online()
        self.TakeAim(self.moonID)

    def SetTarget(self, targetID):
        alreadyTargetted = any([ ts.targetObject is not None for ts in self.turretSets ])
        if targetID == self.moonID and not alreadyTargetted:
            super(StructureMoonMiningTurretSet, self).SetTarget(targetID)

    def TakeAim(self, targetID):
        if self.targetID != targetID:
            return
        if not self.online:
            return
        for turretSet in self.turretSets:
            turretSet.ForceStateTargeting()

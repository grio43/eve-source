#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\godma.py
import cPickle
import itertools
import math
import numbers
import random
import sys
from collections import defaultdict
from operator import itemgetter
import blue
import dogma.data
import evetypes
import log
import telemetry
import uthread
import utillib
from caching import Memoize
from carbon.common.script.sys.crowset import CRowset
from carbon.common.script.sys.row import Row
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_ANY, ROLE_CONTENT, ROLE_GML, ROLE_PROGRAMMER, ROLE_QA
from carbon.common.script.util.timerstuff import ClockThis
from carbonui import uiconst
from dogma.const import attributeDataTypeInstanceBoolean, attributeDataTypeInstanceInteger, attributeDataTypeTypeAttributeId, attributeDataTypeTypeBoolean, attributeDataTypeTypeDamage, attributeDataTypeTypeGroupId, attributeDataTypeTypeInteger, attributeDataTypeTypeMirror, attributeDataTypeTypeTypeId
from eve.client.script.dogma.clientDogmaUtilFunc import WasLaunchingDroneOrFighter
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.inflight.drones.droneSettings import drones_aggressive_setting, drones_focus_fire_setting
from eve.client.script.util import godmarowset
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eve.common.script.util.inventoryFlagsCommon import GetCapacityAttributeForFlag
from eve.common.script.sys import idCheckers
from eve.common.script.sys.dbrow import ConstValueExists, LookupConstValue
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.common.script.sys.rowset import FilterRowset
from eve.common.script.util import eveCommonUtils, inventoryFlagsCommon
from eveexceptions import ExceptionEater, UserError
from gametime import GetDurationInClient
from inventorycommon.util import GetItemVolume, IsShipFittingFlag, IsFittingModule
from localization import GetByLabel
MODULE_NOT_OVERLOADED = 0
MODULE_OVERLOADED = 1
MODULE_PENDING_OVERLOADING = 2
MODULE_PENDING_STOPOVERLOADING = 3
FLAGS_TO_IGNORE_ITEM_CHANGES = list(eveCommonUtils.Flatten((inventoryFlagsCommon.inventoryFlagData,
 const.flagCorpSAGs,
 const.flagDroneBay,
 const.flagCargo,
 const.flagHangar,
 const.flagStructureFuel,
 const.flagStructureDeed)))

def remDups(x, y):
    if x[-1] != y:
        x.append(y)
    return x


class Godma(Service):
    __guid__ = 'svc.godma'
    __exportedcalls__ = {'GetItem': {'role': ROLE_ANY,
                 'fastcall': 1},
     'GetType': {'role': ROLE_ANY,
                 'fastcall': 1},
     'GetStateManager': [ROLE_ANY],
     'LogAttributeViaGodma': [ROLE_ANY],
     'GetDogmaLM': [ROLE_ANY],
     'GetAttributeValueByID': [ROLE_ANY],
     'GetFlagsWithValidCapacity': [ROLE_ANY]}
    __notifyevents__ = ['OnModuleAttributeChange',
     'OnModuleAttributeChanges',
     'OnGodmaShipEffect',
     'OnEffectMessage',
     'OnDamageMessage',
     'OnDamageMessages',
     'OnJamStart',
     'OnJamEnd',
     'OnMultiEvent',
     'ProcessGodmaPrimeLocation',
     'OnGodmaPrimeItem',
     'OnLocationAttributeChange',
     'OnGodmaEffectInfo',
     'OnGodmaFlushLocation',
     'OnGodmaFlushLocationProfile',
     'OnJumpCloneTransitionCompleted',
     'OnSystemEffectStarted',
     'OnDroneControlLost',
     'OnDroneStateChange2',
     'OnFighterRemovedFromControllerClient',
     'DoSimClockRebase',
     'OnSessionReset']
    __dependencies__ = ['invCache']
    __startupdependencies__ = ['settings']

    def __init__(self):
        super(Godma, self).__init__()
        self.__itemrd = None
        self.__sublocrd = None
        self.__subloc_internalrd = None
        self.Initialize()

    def Run(self, ms):
        if ms:
            ms.Seek(0)
            dump = ms.Read()
            if len(dump):
                number = cPickle.loads(str(dump))
                if number == 1:
                    self.GetStateManager().ProcessSessionChange(0, eve.session, {})
        sm.FavourMe(self.OnModuleAttributeChange)
        sm.FavourMe(self.OnModuleAttributeChanges)

    def Initialize(self):
        self.stateManager = None
        self.activeJams = set()
        self.michelle = None

    @property
    def itemrd(self):
        if self.__itemrd is None:
            self.__itemrd = sm.GetService('invCache').GetItemHeader()
        return self.__itemrd

    @property
    def sublocrd(self):
        if not self.__sublocrd:
            columns = []
            for key, dbtype, size in list(self.itemrd):
                if dbtype == 0 and size == 0:
                    continue
                if key == 'itemID':
                    columns.append(('itemID', const.DBTYPE_STR))
                else:
                    columns.append((key, dbtype))

            self.__sublocrd = blue.DBRowDescriptor(tuple(columns))
            self.__sublocrd.virtual = self.itemrd.virtual
        return self.__sublocrd

    @property
    def subloc_internalrd(self):
        if not self.__subloc_internalrd:
            columns = []
            for key, dbtype, size in list(self.itemrd):
                if dbtype == 0 and size == 0:
                    continue
                if key in ('quantity', 'customInfo'):
                    continue
                if key == 'itemID':
                    columns.append(('itemID', const.DBTYPE_STR))
                else:
                    columns.append((key, dbtype))

            self.__subloc_internalrd = blue.DBRowDescriptor(tuple(columns))
        return self.__subloc_internalrd

    def OnSessionReset(self):
        self.ReleaseStateManager()
        self.Initialize()

    def GetType(self, typeID):
        return self.GetStateManager().GetType(typeID)

    def TypeHasEffect(self, typeID, effectID):
        return self.GetStateManager().TypeHasEffect(typeID, effectID)

    def LogAttributeViaGodma(self, itemID, attributeID, reason = None):
        mask = ROLE_CONTENT | ROLE_QA | ROLE_PROGRAMMER | ROLE_GML
        if eve.session.role & mask == 0:
            return
        return self.GetStateManager().LogAttributeViaStateManager(itemID, attributeID, reason)

    def Stop(self, ms):
        if ms is not None:
            ms.Write(cPickle.dumps(1))

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        jamTuple = (sourceBallID,
         moduleID,
         targetBallID,
         jammingType)
        self.activeJams.add(jamTuple)
        uthread.new(self.StopJam, GetDurationInClient(startTime, duration), jamTuple)

    def StopJam(self, duration, jamTuple):
        blue.pyos.synchro.SleepSim(duration)
        if jamTuple in self.activeJams:
            self.activeJams.remove(jamTuple)
            sm.ScatterEvent('OnJamEnd', *jamTuple)

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        try:
            self.activeJams.remove((sourceBallID,
             moduleID,
             targetBallID,
             jammingType))
        except KeyError:
            pass

    def OnMultiEvent(self, events):
        for _, eventBucket in itertools.groupby(sorted(events, key=itemgetter(-1)), key=itemgetter(-1)):
            self.OnMultiEvent_([ e[0] for e in eventBucket ])

    def OnMultiEvent_(self, events):
        if not events:
            return
        dmg = []
        attr = []
        target = []
        gsf = []
        gfl = []
        dastatedict = {'OnDamageMessage': dmg,
         'OnModuleAttributeChange': attr,
         'OnTarget': target,
         'OnGodmaShipEffect': gsf,
         'OnGodmaFlushLocation': gfl,
         'OnGodmaFlushLocationProfile': gfl,
         'OnJamStart': gfl,
         'OnJamStop': gfl}
        other = []
        for ev in events:
            dastatedict.get(ev[0], other).append(ev)

        laters = []
        for ev in other:
            if ev[0].startswith('Process'):
                laters.append(ev)
            else:
                sm.ScatterEvent(*ev)

        if len(gsf):
            self.BroadcastFilteredGSF(gsf)
        if dmg:
            sm.ScatterEvent(*('OnDamageMessages', dmg))
        if target:
            target = reduce(remDups, target, [target[0]])
            sm.ScatterEvent(*('OnTargets', target))
        if attr:
            self.BroadcastFilteredMAC(attr)
        for ev in gfl:
            sm.ScatterEvent(*ev)

        for ev in laters:
            sm.ChainEvent(*ev)

    def BroadcastFilteredGSF(self, gsf):
        gsf.sort(lambda x, y: cmp(x[3], y[3]))
        eventsByID = {}
        for line in gsf:
            k = (line[1], line[2])
            if k not in eventsByID:
                eventsByID[k] = []
            eventsByID[k].append(line)

        skipCount = 0
        sendCount = 0
        for k, lines in eventsByID.iteritems():
            skipCount += len(lines) - 1
            sm.ScatterEvent(*lines[-1])
            sendCount += 1

        self.LogInfo('BroadcastFilteredGSF', 'OnGodmaShipEffect - skips', skipCount, 'sends', sendCount)

    def BroadcastFilteredMAC(self, mac):
        mac.sort(key=lambda x: x[4])
        eventsByID = defaultdict(list)
        for line in mac:
            eventsByID[line[1], line[2], line[3]].append(line)

        skipCount = 0
        result = []
        for k, lines in eventsByID.iteritems():
            skipCount += len(lines) - 1
            result.append(lines[-1])

        result.sort(key=lambda x: x[4])
        self.LogInfo('BroadcastFilteredMAC', 'OnModuleAttributeChanges - skips', skipCount, 'sends', len(result))
        sm.ScatterEvent(*('OnModuleAttributeChanges', result))

    def GetStateManager(self):
        if self.stateManager == None:
            self.stateManager = StateManager(self)
        return self.stateManager

    def ReleaseStateManager(self):
        if self.stateManager:
            self.stateManager.Release()
        self.stateManager = None

    def GetDogmaLM(self):
        return self.GetStateManager().GetDogmaLM()

    def GetItem(self, itemID):
        return self.GetStateManager().GetItem(itemID)

    def IsItemReady(self, itemID):
        return self.GetStateManager().IsItemReady(itemID)

    def GetAttributeValueByID(self, itemID, attributeID):
        return self.GetStateManager().GetAttributeValueByID(itemID, attributeID)

    @Memoize
    def GetFlagsWithValidCapacity(self, itemID, typeID, useOnlyCargo = False):
        categoryID = evetypes.GetCategoryID(typeID)
        if not idCheckers.IsShip(categoryID):
            self.LogError('Cannot get flags with valid capacity for {typeName} ({itemID}), as it is not a Ship but a {categoryName}'.format(typeName=evetypes.GetName(typeID), itemID=itemID, categoryName=evetypes.GetCategoryName(categoryID)))
            return set()
        flagsWithValidCapacity = {const.flagCargo}
        if not useOnlyCargo:
            flagsToCheck = [const.flagDroneBay,
             const.flagGeneralMiningHold,
             const.flagSpecializedGasHold,
             const.flagSpecializedIceHold,
             const.flagSpecializedAmmoHold]
            dogmaIM = sm.GetService('clientDogmaIM')
            groupID = evetypes.GetGroupID(typeID)
            for flagID in flagsToCheck:
                try:
                    capacityAttributeID = GetCapacityAttributeForFlag(flagID)
                    if capacityAttributeID is None:
                        actualCapacity = None
                        if flagID == const.flagCargo:
                            actualCapacity = dogmaIM.GetCapacityForItem(itemID, const.attributeCapacity)
                        if actualCapacity is None:
                            actualCapacity = evetypes.GetCapacity(typeID)
                    else:
                        actualCapacity = dogmaIM.GetCapacityForItem(itemID, capacityAttributeID)
                        if actualCapacity is None:
                            typeAttributes = dogma.data.get_type_attributes(typeID)
                            capacityAttributes = [ x for x in typeAttributes if x.attributeID == capacityAttributeID ]
                            if groupID == const.groupSilo and categoryID == const.categoryStarbase:
                                actualCapacity = self.GetSiloCapacityByItemID(itemID)
                            if actualCapacity is None and len(capacityAttributes):
                                actualCapacity = capacityAttributes[0].value
                            if actualCapacity is None:
                                actualCapacity = dogma.data.get_attribute_default_value(capacityAttributeID)
                    if actualCapacity:
                        flagsWithValidCapacity.add(flagID)
                except Exception as exc:
                    self.LogException('Failed to get capacity for {typeName} ({itemID}) and flag {flag}: {exc}'.format(typeName=evetypes.GetName(typeID), itemID=itemID, flag=flagID, exc=exc))

        return flagsWithValidCapacity

    def OnModuleAttributeChange(self, *args):
        self.GetStateManager().OnModuleAttributeChange(*args)

    def OnModuleAttributeChanges(self, changes):
        self.GetStateManager().OnModuleAttributeChanges(changes)

    def OnGodmaShipEffect(self, *args, **kwargs):
        self.GetStateManager().OnGodmaShipEffect(*args, **kwargs)

    def ProcessGodmaPrimeLocation(self, locationID, data):
        self.GetStateManager().ProcessGodmaPrimeLocation(locationID, data)

    def OnLocationAttributeChange(self, ownerID, locationID, itemKey, attributeID, t, value, oldValue):
        self.GetStateManager().OnLocationAttributeChange(ownerID, locationID, itemKey, attributeID, t, value, oldValue)

    def OnGodmaEffectInfo(self, *args, **kwargs):
        self.GetStateManager().OnGodmaEffectInfo(*args, **kwargs)

    def OnGodmaPrimeItem(self, locationID, row):
        stateMgr = self.GetStateManager()
        stateMgr.OnGodmaPrimeItem(locationID, row)
        if stateMgr.IsSubLocation(row.itemID):
            rd = self.sublocrd
            locationID, flag, typeID = row.itemID
            quantity = row.attributes[const.attributeQuantity]
            self.LogInfo('Godma:OnGodmaPrimeItem - QUANTITY', quantity)
            ownerID = None
            change = {const.ixLocationID: None,
             const.ixFlag: None}
        else:
            rd = self.itemrd
            flag = row.invItem.flagID
            typeID = row.invItem.typeID
            quantity = row.invItem.quantity
            ownerID = row.invItem.ownerID
            change = {}
        stackSize = max(1, quantity)
        location = None
        groupID = evetypes.GetGroupID(typeID)
        categoryID = evetypes.GetCategoryID(typeID)
        item = blue.DBRow(rd, [row.itemID,
         typeID,
         ownerID,
         locationID,
         flag,
         quantity,
         groupID,
         categoryID,
         stackSize])
        sm.ScatterEvent('OnItemChange', item, change, location)

    def OnGodmaFlushLocation(self, locationID):
        self.GetStateManager().OnGodmaFlushLocation(locationID)

    def OnGodmaFlushLocationProfile(self, locationID, profileID):
        self.GetStateManager().OnGodmaFlushLocationProfile(locationID, profileID)

    @telemetry.ZONE_METHOD
    def DamageMessageGrouped(self, turretSets, hitQuality):
        if hitQuality <= 0:
            for t in turretSets:
                t.SetShotMissed(True)

        elif hitQuality >= 3:
            for t in turretSets:
                t.SetShotMissed(False)

        else:
            missPct = [0.5, 0.25][hitQuality - 1]
            for t in turretSets:
                t.SetShotMissed(random.random() < missPct)

    @telemetry.ZONE_METHOD
    def DamageMessageTurretPropogation(self, shipID, ship, hitQuality, args, banked):
        weaponID = args.get('weapon', 0)
        canGetBanks = banked and shipID == session.shipid
        if getattr(ship, 'modules', None):
            minQueue = None
            minTime = None
            minTimeID = None
            minTimeTurrets = []
            shotTimeVariance = 0.0
            for modID, module in ship.modules.iteritems():
                if hasattr(module, 'GetTurretSets'):
                    turretSets = module.GetTurretSets()
                    if not turretSets:
                        continue
                    shooting = module.isShooting
                    targetMatch = shooting
                    shotTimeVariance = max(shotTimeVariance, turretSets[0].GetShotTimeVariance())
                    if shooting and 'target' in args:
                        targetMatch = module.targetID == args['target']
                    typeMatch = shooting
                    if shooting and weaponID is not 0:
                        typeMatch = module.turretTypeID == weaponID
                    if shooting and targetMatch and typeMatch:
                        queueSize = turretSets[0].MissQueueSize()
                        shotTime = turretSets[0].GetLastShotTime()
                        turretID = modID
                        if canGetBanks:
                            turretID = self.GetStateManager().dogmaLocation.IsInWeaponBank(shipID, modID) or modID
                            if turretID == minTimeID:
                                minTimeTurrets.append(module)
                            elif minQueue is None or queueSize < minQueue:
                                minQueue = queueSize
                                minTime = shotTime
                                minTimeID = turretID
                                minTimeTurrets = [module]
                            elif queueSize == minQueue and (minTime is None or shotTime < minTime):
                                minTime = shotTime
                                minTimeID = turretID
                                minTimeTurrets = [module]
                        elif banked:
                            if minTime is None or shotTime < minTime + shotTimeVariance:
                                if minTime is None:
                                    minTime = shotTime
                                else:
                                    minTime = min(shotTime, minTime)
                                minTimeID = turretID
                                minTimeTurrets.append(module)
                        elif minQueue is None or queueSize < minQueue:
                            minQueue = queueSize
                            minTime = shotTime
                            minTimeTurrets = [module]
                        elif queueSize == minQueue and (minTime is None or shotTime < minTime):
                            minTime = shotTime
                            minTimeTurrets = [module]

            allTurretSets = []
            for turret in minTimeTurrets:
                for turretSet in turret.GetTurretSets():
                    if canGetBanks or minTime + shotTimeVariance >= turretSet.GetLastShotTime():
                        allTurretSets.append(turretSet)

            self.DamageMessageGrouped(allTurretSets, hitQuality)

    @telemetry.ZONE_METHOD
    def OnDamageMessage(self, damageMessagesArgs):
        if self.michelle is None:
            self.michelle = sm.GetService('michelle')
        try:
            hitQuality = damageMessagesArgs.get('hitQuality', 5)
            banked = damageMessagesArgs.get('isBanked', False)
            if 'observed' in damageMessagesArgs:
                sourceID = damageMessagesArgs['source']
                ship = self.michelle.GetBall(sourceID)
                if sourceID and ship:
                    self.DamageMessageTurretPropogation(sourceID, ship, hitQuality, damageMessagesArgs, banked)
            elif 'target' in damageMessagesArgs:
                ship = self.michelle.GetBall(session.shipid)
                if ship and hasattr(ship, 'turrets'):
                    self.DamageMessageTurretPropogation(session.shipid, ship, hitQuality, damageMessagesArgs, banked)
            elif 'owner' in damageMessagesArgs:
                ownerData, ownerID = damageMessagesArgs['owner']
                if ownerData == const.UE_OWNERID:
                    targetSvc = sm.GetService('target')
                    ship = None
                    shipID = targetSvc.ownerToShipIDCache.get(ownerID, None)
                    if shipID is not None:
                        ship = self.michelle.GetBall(shipID)
                    if shipID and ship:
                        self.DamageMessageTurretPropogation(shipID, ship, hitQuality, damageMessagesArgs, banked)
            elif 'source' in damageMessagesArgs:
                shipID = damageMessagesArgs['source']
                ship = self.michelle.GetBall(shipID)
                if hasattr(ship, 'turrets'):
                    self.DamageMessageTurretPropogation(shipID, ship, hitQuality, damageMessagesArgs, banked)
                elif hasattr(ship, 'model') and hasattr(ship.model, 'turretSets'):
                    self.DamageMessageGrouped(ship.model.turretSets, hitQuality)
        except:
            log.LogException('Error setting hit/miss state on a turret')

        if not settings.user.ui.Get('damageMessages', 1):
            return
        if 'damage' in damageMessagesArgs and damageMessagesArgs['damage'] == 0.0 and not settings.user.ui.Get('damageMessagesNoDamage', 1):
            return
        if 'owner' in damageMessagesArgs or 'source' in damageMessagesArgs:
            sm.ScatterEvent('OnShipDamage', damageMessagesArgs.get('damageTypes', {}))
            if not settings.user.ui.Get('damageMessagesEnemy', 1):
                return
        elif not settings.user.ui.Get('damageMessagesMine', 1):
            return
        sm.GetService('logger').AddCombatMessageFromDict(damageMessagesArgs)

    @telemetry.ZONE_METHOD
    def OnDamageMessages(self, dmgmsgs):
        if not settings.user.ui.Get('damageMessages', 1):
            return
        for msg in dmgmsgs:
            self.OnDamageMessage(*msg[1:])

    def OnEffectMessage(self, msgkey, args):
        msg = cfg.GetMessage(msgkey, args)
        ShowQuickMessage(msg.text)

    def ProcessSessionChange(self, isRemote, session, change):
        self.GetStateManager().ProcessSessionChange(isRemote, session, change)

    def OnItemChange(self, *args):
        try:
            self.GetStateManager().OnItemChange(*args)
        finally:
            sm.GetService('clientDogmaIM').GodmaItemChanged(*args)

    def OnDroneControlLost(self, droneID):
        if self.stateManager:
            self.stateManager.OnDroneControlLost(droneID)

    def OnDroneStateChange2(self, droneID, oldState, newState):
        if self.stateManager:
            self.stateManager.OnDroneStateChange2(droneID, oldState, newState)

    def OnFighterRemovedFromControllerClient(self, fighterID):
        if self.stateManager:
            self.stateManager.OnFighterRemovedFromControllerClient(fighterID)

    def OverloadRack(self, moduleID):
        if moduleID is None:
            return
        if self.stateManager:
            self.stateManager.OverloadRack(moduleID)

    def StopOverloadRack(self, moduleID):
        if self.stateManager:
            self.stateManager.StopOverloadRack(moduleID)

    def OnJumpCloneTransitionCompleted(self):
        if self.stateManager:
            self.stateManager.OnJumpCloneTransitionCompleted()

    def GetTypeAttribute(self, typeID, attributeID, defaultValue = None):
        for typeAttribute in dogma.data.get_type_attributes(typeID):
            if typeAttribute.attributeID == attributeID:
                return typeAttribute.value

        return defaultValue

    def GetTypeAttribute2(self, typeID, attributeID):
        val = self.GetTypeAttribute(typeID, attributeID)
        if val is None and dogma.data.is_attribute(attributeID):
            val = dogma.data.get_attribute_default_value(attributeID)
        return val

    def CheckSkillRequirementsForType(self, typeID):
        skillSvc = sm.StartService('skills')
        requiredSkills = skillSvc.GetRequiredSkills(typeID)
        for skillTypeID, level in requiredSkills.iteritems():
            skillInfo = skillSvc.GetSkill(skillTypeID)
            if skillInfo and skillInfo.effectiveSkillLevel >= level:
                continue
            return False

        return True

    def GetFlagsCompatibleWithChargeType(self, chargeTypeID):
        chargeGroupID = self.GetType(chargeTypeID).groupID
        chargeChargeSize = self.GetTypeAttribute(chargeTypeID, const.attributeChargeSize)
        if not hasattr(self, 'chargeGroupAttrs'):
            self.chargeGroupAttrs = []
            for attribute in dogma.data.get_charge_group_attributes():
                self.chargeGroupAttrs.append(attribute.name)

        shipItem = self.GetStateManager().GetItem(session.shipid)
        flags = []
        for module in shipItem.modules:
            groupCompatible = False
            for cgaID in self.chargeGroupAttrs:
                if cgaID in self.stateManager.attributesByItemAttribute.get(module.itemID, {}):
                    if self.stateManager.GetAttribute(module.itemID, cgaID) == chargeGroupID:
                        groupCompatible = True
                        continue

            if groupCompatible is False:
                continue
            if 'chargeSize' in self.stateManager.attributesByItemAttribute.get(module.itemID, {}):
                if self.stateManager.GetAttribute(module.itemID, 'chargeSize') == chargeChargeSize:
                    flags.append(module.flagID)
            else:
                flags.append(module.flagID)

        return flags

    def OnSkillPointsRemovedDueToShipLoss(self, skillTypeID, skillPoints, shipTypeID):
        entry = utillib.KeyVal(skillTypeID=skillTypeID, skillPoints=skillPoints, shipTypeID=shipTypeID)
        settings.char.generic.Set('skillLossNotification', entry)

    def OnSystemEffectStarted(self, typeIDs):
        body = ''
        for typeID in typeIDs:
            if len(body) > 0:
                body += '<br><br>'
            body += evetypes.GetDescription(typeID)

        eve.Message('CustomNotify', {'notify': body})

    def DoSimClockRebase(self, times):
        if self.stateManager:
            self.stateManager.DoSimClockRebase(times)

    def GetPowerEffectForType(self, typeID):
        powerEffects = [const.effectHiPower,
         const.effectMedPower,
         const.effectLoPower,
         const.effectRigSlot,
         const.effectSubSystem,
         const.effectServiceSlot]
        for effect in dogma.data.get_type_effects(typeID):
            if effect.effectID in powerEffects:
                return effect.effectID

    def ShipOnlineModules(self):
        self.GetDogmaLM().ShipOnlineModules()


class TypeWrapper(object):

    def __init__(self, statemanager, typeID):
        self.statemanager = statemanager
        self.typeID = typeID
        self.categoryID = evetypes.GetCategoryID(typeID)

    def __getattr__(self, attributeName):
        result = self.__InnerGetattr(attributeName)
        setattr(self, attributeName, result)
        return result

    def __InnerGetattr(self, attributeName):
        if attributeName == 'itemID':
            return
        typeID = self.typeID
        if attributeName == 'displayAttributes':
            rowDescriptor = blue.DBRowDescriptor((('displayName', const.DBTYPE_STR),
             ('value', const.DBTYPE_R5),
             ('unitID', const.DBTYPE_UI1),
             ('iconID', const.DBTYPE_I4),
             ('attributeID', const.DBTYPE_I2)))
            rowset = CRowset(rowDescriptor, [])
            for typeAttribute in dogma.data.get_type_attributes(typeID):
                attrib = self.statemanager.attributesByID[typeAttribute.attributeID]
                name = dogma.data.get_attribute_display_name(typeAttribute.attributeID) or attrib.name
                if attrib.dataType == attributeDataTypeTypeMirror:
                    val = evetypes.GetAttributeForType(typeID, attrib.name)
                elif typeAttribute.value is not None:
                    val = typeAttribute.value
                else:
                    val = attrib.defaultValue
                rowset.InsertNew([name,
                 val,
                 getattr(attrib, 'unitID', None),
                 getattr(attrib, 'iconID', None),
                 typeAttribute.attributeID])

            return rowset
        if attributeName == 'effects':
            self.statemanager.CacheTypeEffects(typeID)
            return self.statemanager.effectsByType[typeID]
        if attributeName in self.statemanager.attributesByName:
            value = None
            attribute = self.statemanager.attributesByName[attributeName]
            if attribute.dataType == attributeDataTypeTypeMirror:
                value = evetypes.GetAttributeForType(typeID, attributeName)
            attributeID = attribute.attributeID
            for typeAttribute in dogma.data.get_type_attributes(typeID):
                if typeAttribute.attributeID == attributeID:
                    value = typeAttribute.value
                    break

            if value is None:
                value = self.statemanager.attributesByName[attributeName].defaultValue
            if dogma.data.get_attribute_data_type(attributeID) in (attributeDataTypeInstanceBoolean,
             attributeDataTypeInstanceInteger,
             attributeDataTypeTypeBoolean,
             attributeDataTypeTypeInteger,
             attributeDataTypeTypeAttributeId,
             attributeDataTypeTypeTypeId,
             attributeDataTypeTypeGroupId):
                return int(value)
            return value
        if attributeName == 'name':
            return evetypes.GetName(typeID)
        return evetypes.GetAttributeForType(typeID, attributeName)

    def AttributeExists(self, attributeName):
        attributeID = self.statemanager.attributesByName[attributeName].attributeID
        for typeAttribute in dogma.data.get_type_attributes(self.typeID):
            if typeAttribute.attributeID == attributeID:
                return 1

        return 0

    def __str__(self):
        return self.typeName

    def __repr__(self):
        return '<godma-type typeID="%d">' % self.typeID


class ItemWrapper():
    __guid__ = 'godma.ItemWrapper'

    def __init__(self, statemanager, header, dbrow):
        self.statemanager = statemanager
        self.dbrow = dbrow
        self.header = header
        self.defaultEffectName = None

    def __str__(self):
        try:
            tname = self.name
        except:
            sys.exc_clear()
            tname = '<Unknown type name>'

        try:
            name = self.name
            if tname != name:
                name = tname + ':' + name
        except:
            sys.exc_clear()
            name = ''

        name += ' (row data: %s)' % str(self.dbrow)
        return name

    def __getattr__(self, attribute):
        d = self.__dict__
        if attribute == 'defaultEffect':
            if d['defaultEffectName'] is None:
                for effect in d['statemanager'].effectsByItemEffect.get(self.itemID, {}).itervalues():
                    if effect.isDefault:
                        d['defaultEffectName'] = effect.effectName
                        break

            effectName = d['defaultEffectName']
            return d['statemanager'].effectsByItemEffect[self.itemID].get(effectName, None)
        if attribute == 'line':
            return list(d['dbrow'])
        if attribute in d['dbrow'].__columns__:
            return d['dbrow'][attribute]
        if d['dbrow'].__class__.__dict__.has_key(attribute):
            return getattr(d['dbrow'], attribute)
        if self.__class__.__dict__.has_key(attribute):
            return self.__class__.__dict__[attribute]
        if attribute.startswith('__') and attribute.endswith('__'):
            raise AttributeError('ItemWrapper has no %s' % attribute)
        else:
            if attribute == 'inventory':
                return d['statemanager'].invByID.get(self.itemID, None)
            return d['statemanager'].GetAttribute(self.itemID, attribute)

    def __nonzero__(self):
        return True

    def GetChargeEffect(self, typeID):
        eff = self.statemanager.GetDefaultEffect(typeID)
        if eff is None:
            return
        eff = eff.__class__(self.statemanager, eff.header, eff.dbrow)
        idx = eff.header.Index('itemID')
        eff[idx] = self.itemID
        return eff

    def IsFitted(self):
        return IsShipFittingFlag(self.flagID)

    def GetSlotOccupants(self, flag):
        return [ item for item in self.statemanager.invitems.itervalues() if item.locationID == self.itemID and item.flagID == flag ]

    def GetCapacity(self, flag = None):
        used = None
        capacity = 0
        contents = []
        if self.categoryID in (const.categoryShip, const.categoryStructure):
            if IsShipFittingFlag(flag):
                occupants = self.GetSlotOccupants(flag)
                modules = filter(lambda x: IsFittingModule(x.categoryID), occupants)
                if len(modules):
                    capacity = self.statemanager.GetItem(modules[0].itemID).capacity
                else:
                    capacity = 0
                sublocation = self.statemanager.GetSubLocation(self.itemID, flag)
                if sublocation is not None:
                    contents = [sublocation]
                else:
                    occupants = self.GetSlotOccupants(flag)
                    contents = filter(lambda x: x.categoryID == const.categoryCharge, occupants)
            elif flag == const.flagDroneBay:
                contents = self.statemanager.invByID[self.itemID].ListDroneBay()
                capacity = self.droneCapacity
            elif flag is None or flag == const.flagCargo:
                contents = self.statemanager.invByID[self.itemID].ListCargo()
                capacity = self.capacity
            elif flag == const.flagShipHangar:
                if self.itemID in self.statemanager.invByID:
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = inv.List(flag)
                capacity = self.shipMaintenanceBayCapacity
            elif flag in const.flagCorpSAGsAndHangar:
                if self.itemID in self.statemanager.invByID:
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = [ item for item in inv.List() if item.flagID in const.flagCorpSAGsAndHangar ]
                capacity = self.corporateHangarCapacity
            elif flag in inventoryFlagsCommon.inventoryFlagData:
                capacity = self.statemanager.GetAttributeValueByID(self.itemID, inventoryFlagsCommon.inventoryFlagData[flag]['attribute'])
                if self.itemID in self.statemanager.invByID:
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = [ item for item in inv.List() if item.flagID == flag ]
            else:
                raise RuntimeError('BadSlotForCapacity', flag)
        elif self.categoryID == const.categoryStarbase:
            capacity = self.capacity
            if self.groupID in (const.groupMobileMissileSentry, const.groupMobileProjectileSentry, const.groupMobileHybridSentry):
                contents = self.sublocations
            else:
                contents = sm.GetService('invCache').GetInventoryFromId(self.itemID).List(flag)
        if used is None:
            used = 0
            for item in contents:
                if flag and item.flagID != flag:
                    continue
                vol = GetItemVolume(item)
                if vol > 0:
                    used = used + vol

        return Row(['capacity', 'used'], [capacity, used])


class EffectWrapper():
    __guid__ = 'godma.EffectWrapper'

    def __init__(self, statemanager, header, dbrow):
        d = self.__dict__
        d['statemanager'] = statemanager
        d['dbrow'] = dbrow
        d['header'] = header
        d['defaultEffectName'] = None

    def __getattr__(self, attribute):
        d = self.__dict__
        if attribute in d:
            return d[attribute]
        try:
            return d['dbrow'][attribute]
        except:
            sys.exc_clear()
            ret = d['statemanager'].GetEffectAttributeEx(self, d['dbrow'].itemID, attribute)
            if ret is None:
                raise AttributeError, attribute
            return ret

    def __setattr__(self, attr, value):
        d = self.__dict__
        if attr in d['header'].Keys():
            d['dbrow'][attr] = value
        else:
            d[attr] = value

    def __setitem__(self, idx, value):
        self.dbrow[idx] = value

    def Activate(self, target = None, repeat = 0):
        if self.isActive and self.duration <= 0:
            self.statemanager.godma.LogError('Module effect already active', self.effectName, self.itemID)
            return
        elif not eve.session.IsItSafe():
            return
        elif self.effectCategory == const.dgmEffOverload:
            return self.statemanager.Overload(self.itemID, self.effectID)
        else:
            return self.statemanager.Activate(self.itemID, self.effectName, target, repeat)

    def Deactivate(self):
        if not self.isActive:
            self.statemanager.godma.LogError('Module effect not active', self.effectName, self.itemID)
            return
        elif self.effectCategory == const.dgmEffOverload:
            return self.statemanager.StopOverload(self.itemID, self.effectID)
        else:
            return self.statemanager.Deactivate(self.itemID, self.effectName)

    def Toggle(self):
        if self.isActive:
            return self.Deactivate()
        else:
            return self.Activate()


ENV_IDX_SELF = 0
ENV_IDX_CHAR = 1
ENV_IDX_SHIP = 2
ENV_IDX_TARGET = 3
ENV_IDX_OTHER = 4
ENV_IDX_AREA = 5
ENV_IDX_EFFECT = 6
ENV_IDX_LINE = 7

class StateManager():
    __guid__ = 'godma.StateManager'
    __effectheader__ = blue.DBRowDescriptor((('itemID', const.DBTYPE_STR),
     ('effectID', const.DBTYPE_I4),
     ('effectName', const.DBTYPE_STR),
     ('effectCategory', const.DBTYPE_I2),
     ('isDefault', const.DBTYPE_BOOL),
     ('isActive', const.DBTYPE_BOOL),
     ('isOffensive', const.DBTYPE_BOOL),
     ('isAssistance', const.DBTYPE_BOOL),
     ('description', const.DBTYPE_STR),
     ('trackingSpeedAttributeID', const.DBTYPE_I2),
     ('rangeAttributeID', const.DBTYPE_I2),
     ('falloffAttributeID', const.DBTYPE_I4),
     ('dischargeAttributeID', const.DBTYPE_I2),
     ('durationAttributeID', const.DBTYPE_I2),
     ('iconID', const.DBTYPE_I4),
     ('targetID', const.DBTYPE_I8),
     ('startTime', const.DBTYPE_FILETIME),
     ('duration', const.DBTYPE_I4),
     ('repeat', const.DBTYPE_I4),
     ('isDeactivating', const.DBTYPE_BOOL)))

    def __init__(self, godma):
        self.godma = godma
        self.activatedLocation = {}
        self.invitems = godmarowset.GodmaIndexedRowset(godma.itemrd, 'itemID', rowClass=self.GetItemWrapper)
        self.sublocationsByKey = godmarowset.GodmaIndexedRowset(self.godma.subloc_internalrd, 'itemID', rowClass=self.GetSubLocationWrapper)
        self.sublocationsByLocationFlag = godmarowset.GodmaRowset(self.godma.subloc_internalrd, [], rowClass=self.GetSubLocationWrapper).Filter('locationID', 'flagID')
        self.itemsByLocationID = {}
        self.inited = False
        self.priming = False
        self.primingChannel = None
        self.attributesByName = None
        self.attributesByID = None
        self.effectsByType = {}
        self.defaultEffectsByType = {}
        self.chargedAttributeTauCaps = {}
        self.droneSettingAttributes = {}
        self.lastAttributeChange = {}
        self.attributesByItemAttribute = {}
        self.effectsByItemEffect = {}
        self.chargedAttributesByItemAttribute = {}
        self.modulesBeingRepaired = {}
        self.slaveModulesByMasterModule = {}
        self.activatingEffects = set()
        self.chargeTypeByModule = {}
        self.lastStopTimesByItemID = {}
        self.invByID = {}
        self.dogmaLM = None
        self.pending = {}
        self.pendingOverloading = set()
        self.pendingStopOverloading = set()
        self.itemKeyChannels = {}
        self.requiredEffects = {const.effectOnline: True,
         const.effectHiPower: True,
         const.effectMedPower: True,
         const.effectLoPower: True,
         const.effectRigSlot: True}
        self.electronicAttributes = {const.attributeScanGravimetricStrengthBonus: const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrengthBonus: const.attributeScanLadarStrength,
         const.attributeScanMagnetometricStrengthBonus: const.attributeScanMagnetometricStrength,
         const.attributeScanRadarStrengthBonus: const.attributeScanRadarStrength}
        self.propulsionAttributes = {const.attributePropulsionFusionStrengthBonus: const.attributePropulsionFusionStrength,
         const.attributePropulsionIonStrengthBonus: const.attributePropulsionIonStrength,
         const.attributePropulsionMagpulseStrengthBonus: const.attributePropulsionMagpulseStrength,
         const.attributePropulsionPlasmaStrengthBonus: const.attributePropulsionPlasmaStrength}
        self.dogmaLocation = None

    def Release(self):
        self.dogmaLM = None
        self.invitems = None
        self.sublocationsByLocationFlag = None
        self.sublocationsByKey = None
        self.itemsByLocationID = None
        self.godma = None
        self.effectsByItemEffect = None
        self.defaultEffectsByType = None
        self.attributesByItemAttribute = None

    def IsLocationLoaded(self, locationID):
        return locationID in self.itemsByLocationID

    def IsItemLoaded(self, itemKey):
        return itemKey in self.invitems or itemKey in self.sublocationsByKey

    def GetDogmaLM(self):
        if not self.dogmaLM:
            self.dogmaLM = eveMoniker.CharGetDogmaLocation()
        return self.dogmaLM

    def LogAttributeViaStateManager(self, itemID, attributeID, reason = None):
        if reason is None:
            reason = ''
        else:
            reason += '  '
        val = None
        try:
            val = self.GetAttribute(itemID, dogma.data.get_attribute_name(attributeID))
        except:
            sys.exc_clear()
            val = 'screwed'

        if isinstance(itemID, basestring):
            dogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        else:
            dogmaLocation = self.GetDogmaLM()
        logStuff = dogmaLocation.FullyDescribeAttribute(itemID, attributeID, reason + 'Value on client was %s.' % val)
        for line in logStuff:
            self.godma.LogError(line)

    def ProcessSessionChange(self, isRemote, session, change):
        if session.charid:
            if 'stationid' in change or 'solarsystemid' in change or 'shipid' in change or 'charid' in change or 'structureid' in change:
                self.priming = True
                keepList = [session.charid, session.shipid]
                if 'solarsystemid' not in change:
                    keepList.append(session.solarsystemid)
                    for invItem in self.invitems.itervalues():
                        if invItem.locationID == session.solarsystemid and invItem.categoryID == const.categoryStarbase:
                            keepList.append(invItem.itemID)

                self.PurgeInventories(keepList, skipCapacityEvent=True)
                self.dogmaLM = None
                self.godma.LogInfo('ProcessSessionChange: Prime (pre)')
                self.lastAttributeChange = {}
                if session.shipid is None:
                    self.Prime()
                else:
                    oldAttribs = {}
                    try:
                        del self.invByID[session.shipid]
                        oldAttribs = self.attributesByItemAttribute[session.shipid].copy()
                    except KeyError:
                        pass

                    self.Prime()
                    if session.shipid in self.attributesByItemAttribute and self.attributesByItemAttribute[session.shipid]:
                        newAttribs = self.attributesByItemAttribute[session.shipid]
                        attribChanges = []
                        shipItem = self.invitems[session.shipid]
                        for introducedAttribute in set(newAttribs).difference(set(oldAttribs)):
                            attribChanges.append((introducedAttribute, shipItem, newAttribs[introducedAttribute]))

                        for commonAttribute in set(newAttribs).intersection(set(oldAttribs)):
                            if oldAttribs[commonAttribute] != newAttribs[commonAttribute]:
                                attribChanges.append((commonAttribute, shipItem, newAttribs[commonAttribute]))

                        if attribChanges:
                            sm.ScatterEvent('OnAttributes', attribChanges)
                    self.ClearPendingOverloadingFlags()
                self.godma.LogInfo('ProcessSessionChange: Prime (post)')
                self.priming = False
            if session.stationid or session.solarsystemid:
                dogmaLM = self.GetDogmaLM()
                dogmaLM.Bind()
            for moduleID in self.modulesBeingRepaired.keys():
                self.StopRepairModule(moduleID)

            if 'shipid' in change:
                self.chargeTypeByModule = {}
        else:
            self.dogmaLM = None

    def OnItemChange(self, item, change, location):
        if self.IsSubLocation(item.itemID):
            return
        if item.locationID == session.structureid and not IsControllingStructure():
            if not (const.ixLocationID in change and change[const.ixLocationID] == session.shipid):
                return
        if item.itemID in self.chargeTypeByModule and const.ixFlag in change:
            del self.chargeTypeByModule[item.itemID]
        self.godma.LogInfo('OnItemChange', item, change)
        if const.ixLocationID in change or const.ixStackSize in change and item.stacksize == 0:
            flag = item.flagID
            oFlagOk = IsShipFittingFlag(flag) or flag == const.flagPilot
            wasLaunchingDronesOrFighters = False
            if const.ixFlag in change:
                cFlag = change[const.ixFlag]
                wasLaunchingDronesOrFighters = self.WasLaunchingDroneOrFighter(item, change)
                cFlagOk = IsShipFittingFlag(cFlag) or cFlag == const.flagPilot or wasLaunchingDronesOrFighters
                if not (oFlagOk or cFlagOk or wasLaunchingDronesOrFighters):
                    return
            elif not oFlagOk:
                return
            if item.locationID in self.invByID and not (const.ixStackSize in change and item.stacksize == 0):
                self.UpdateItem(item)
                if item.itemID in self.invitems:
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
            elif wasLaunchingDronesOrFighters:
                self.UpdateItem(item)
            elif item.itemID in self.invitems:
                oldLocationID = change.get(const.ixLocationID, item.locationID)
                if item.itemID not in self.invByID:
                    self.invitems[item.itemID].locationID = item.locationID
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
                    del self.invitems[item.itemID]
                else:
                    self.invitems[item.itemID].locationID = item.locationID
                    self.invitems[item.itemID].flagID = item.flagID
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
                if oldLocationID != item.locationID:
                    if oldLocationID in self.itemsByLocationID:
                        self.itemsByLocationID[oldLocationID].discard(item.itemID)
                    if item.locationID in self.itemsByLocationID:
                        self.itemsByLocationID[item.locationID].add(item.itemID)
        elif item.locationID in self.invByID:
            if item.itemID in self.invitems:
                if const.ixFlag in change and not (IsShipFittingFlag(item.flagID) or item.flagID in (const.flagSkill, const.flagSkillInTraining, const.flagBooster)):
                    sm.ScatterEvent('OnGodmaItemChange', item, change)
                    del self.invitems[item.itemID]
                    if item.locationID in self.itemsByLocationID:
                        self.itemsByLocationID[item.locationID].remove(item.itemID)
                    return
            if item.flagID in FLAGS_TO_IGNORE_ITEM_CHANGES:
                return
            if item.groupID == const.groupCapsule and item.ownerID == session.charid:
                if item.locationID == session.locationid and item.flagID == const.flagNone or item.locationID == session.shipid and item.flagID == const.flagCapsule:
                    return
            if len(change) == 1 and const.ixStackSize in change and not (item.singleton and change[const.ixStackSize] > 0):
                self.UpdateItem(item, dontGetInfo=1)
            else:
                self.UpdateItem(item)
            if item.itemID in self.invitems:
                sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)

    def WasLaunchingDroneOrFighter(self, item, change):
        return WasLaunchingDroneOrFighter(item, change, session.solarsystemid)

    def ProcessGodmaPrimeLocation(self, locationID, data):
        self.godma.LogInfo('ProcessGodmaPrimeLocation', locationID, 'rows:', len(data))
        self.itemsByLocationID[locationID] = set()
        if locationID in data:
            row = data[locationID]
            self.UpdateItem(row.invItem, row)
        for itemKey in data.iterkeys():
            if itemKey == locationID:
                continue
            row = data[itemKey]
            self.UpdateItem(row.invItem, row)

        sm.ChainEvent('ProcessGodmaLocationPrimed', locationID)

    def OnGodmaPrimeItem(self, locationID, row):
        if locationID not in self.itemsByLocationID:
            log.LogError('OnGodmaPrimeItem received row %s for locationID %s, location primed!' % (row, locationID))
            self.itemsByLocationID[locationID] = set()
        self.UpdateItem(row.invItem, row)

    def OnGodmaFlushLocation(self, locationID):
        self.godma.LogInfo('OnGodmaFlushLocation', locationID)
        self.PurgeEntries(locationID)

    def OnGodmaFlushLocationProfile(self, locationID, profileID):
        self.godma.LogInfo('OnGodmaFlushLocationProfile', locationID, profileID)
        if profileID[0] == 'effect' and profileID[1] != locationID:
            self.PurgeEntry(profileID[1], locationID)

    def OnModuleAttributeChange(self, ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr = True):
        if self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnModuleAttributeChange - Discarded due to response from receive', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
                return
            self.godma.LogWarn('OnModuleAttributeChange - Stalled, but now in action', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
        self.OnModuleAttributeChange_(ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr, useTasket=True)

    def OnModuleAttributeChange_(self, ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr = True, useTasket = False):
        if not self._IsAttributeChangeRelevant(itemKey, attributeID, wallclockTime):
            self.godma.LogInfo('Ignoring attribute change to attribute', attributeID, 'on', itemKey, 'as it is too old', (oldValue, newValue))
            return
        if wallclockTime:
            self.lastAttributeChange[itemKey, attributeID] = wallclockTime
        if not (itemKey == eve.session.charid or ownerID == eve.session.charid):
            if eve.session.charid is None:
                return
            log.LogTraceback('Got moduleattributechange for object I do not own!!!!!!!! Yayz0r - ownerID = %s, itemKey = %s, attributeID = %s, session.charid = %s' % (ownerID,
             itemKey,
             attributeID,
             eve.session.charid), channel='svc.godma')
            self.godma.LogError('OnModuleAttributeChange', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
            return
        if useTasket:
            uthread.pool('godma::ApplyAttributeChange::OnModuleAttributeChange', self.ApplyAttributeChange, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
        else:
            self.ApplyAttributeChange(ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)

    def OnLocationAttributeChange(self, ownerID, locationID, itemKey, attributeID, time, newValue, oldValue):
        if locationID not in self.itemsByLocationID:
            log.LogInfo('Got attribute change event for unknown location: %s ' % [ownerID,
             locationID,
             itemKey,
             attributeID,
             time,
             newValue,
             oldValue])
            return
        ClockThis('godma::ApplyAttributeChange::OnLocationAttributeChange', self.ApplyAttributeChange, ownerID, itemKey, attributeID, time, newValue, oldValue)

    def OnModuleAttributeChanges(self, changes):
        if self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnModuleAttributeChanges - Discarded due to response from receive', changes)
                return
            self.godma.LogWarn('OnModuleAttributeChanges - Stalled, but now in action', changes)
        qtyChanges = set()
        itemKeyIdx, attributeIdx, newValueIdx = (2, 3, 5)
        for each in changes:
            if type(each[itemKeyIdx]) is tuple and each[attributeIdx] == const.attributeQuantity and each[newValueIdx] == 0.0:
                qtyChanges.add(each[itemKeyIdx])

        for each in changes:
            if each[itemKeyIdx] in qtyChanges and each[attributeIdx] != const.attributeQuantity:
                continue
            with ExceptionEater('Actioning on an attribute change in Godma'):
                self.OnModuleAttributeChange_(*(each[1:] + (0,)))

        ch = []
        for change in changes:
            entry = None
            itemKey = change[2]
            if itemKey in self.invitems:
                entry = self.invitems[itemKey]
            elif itemKey in self.sublocationsByKey:
                entry = self.sublocationsByKey[itemKey]
            if entry:
                ch.append((dogma.data.get_attribute_name(change[3]), entry, change[5]))

        sm.ScatterEvent('OnAttributes', ch)

    def GetActiveModulesOnTargetID(self, targetID):
        activeModulesOnTargetID = []
        for module in self._IterActiveModules():
            try:
                effect = module.defaultEffect
                if effect is not None and effect.targetID == targetID:
                    activeModulesOnTargetID.append(module)
            except KeyError:
                continue

        return activeModulesOnTargetID

    def GetActiveModules(self):
        active_modules = []
        for module in self._IterActiveModules():
            effect = module.defaultEffect
            if effect is not None and not self.effectsByItemEffect[module.itemID][effect.effectName].isDeactivating:
                active_modules.append(module)

        return active_modules

    def GetActiveModuleTypes(self):
        active_module_type_ids = []
        for module in self._IterActiveModules():
            effect = module.defaultEffect
            if effect is not None and not self.effectsByItemEffect[module.itemID][effect.effectName].isDeactivating:
                active_module_type_ids.append(module.typeID)

        return active_module_type_ids

    def GetActiveModuleGroups(self):
        active_module_group_ids = []
        for module in self._IterActiveModules():
            effect = module.defaultEffect
            if effect is not None and not self.effectsByItemEffect[module.itemID][effect.effectName].isDeactivating:
                active_module_group_ids.append(module.groupID)

        return active_module_group_ids

    def _IterActiveModules(self):
        if session.shipid is None:
            return
        for module in self.GetItem(session.shipid).modules:
            try:
                effect = module.defaultEffect
                if effect is not None and effect.isActive:
                    yield module
            except KeyError:
                continue

    def OnGodmaShipEffect(self, itemID, effectID, t, start, active, environment, startTime, duration, repeat, error, actualStopTime = None, stall = True):
        if stall and self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnGodmaShipEffect - Discarded due to response from receive', itemID, effectID, t, start, active, environment, startTime, duration, repeat, error)
                return
            self.godma.LogWarn('OnGodmaShipEffect - Stalled, but now in action', itemID, effectID, t, start, active, environment, startTime, duration, repeat, error)
        effect = dogma.data.get_effect(effectID)
        effectName = effect.effectName
        if itemID in self.effectsByItemEffect and effectName in self.effectsByItemEffect[itemID]:
            self.godma.LogInfo('OnGodmaShipEffect.effectsByItemEffect', itemID, effectName, active, duration, repeat)
            self.effectsByItemEffect[itemID][effectName].isDeactivating = False
            self.effectsByItemEffect[itemID][effectName].isActive = active
            self.effectsByItemEffect[itemID][effectName].startTime = startTime
            self.effectsByItemEffect[itemID][effectName].duration = duration
            self.effectsByItemEffect[itemID][effectName].repeat = repeat
            self.effectsByItemEffect[itemID][effectName].targetID = environment[ENV_IDX_TARGET]
            if active:
                self._NotifyOfEffectActivation(itemID, effectID)
            if environment[ENV_IDX_SHIP] == session.shipid or environment[ENV_IDX_SELF] and sm.GetService('pwn').GetCurrentControl(environment[ENV_IDX_SELF]):
                effectState = utillib.KeyVal(itemID=itemID, effectName=effectName, time=t, start=start, active=active, environment=environment, duration=duration, repeat=repeat, error=error)
                uthread.new(self.ActualStopEffect, itemID, effect, actualStopTime, effectState)
        if effect.effectCategory == const.dgmEffOverload:
            if start and itemID in self.pendingOverloading:
                self.StopPendingOverloadModule(itemID)
            elif not start and itemID in self.pendingStopOverloading:
                self.StopPendingStopOverloadModule(itemID)

    def _NotifyOfEffectActivation(self, itemID, effectID):
        sm.ScatterEvent('OnModuleActivated', itemID, effectID)

    def ActualStopEffect(self, itemID, effect, stopTime, effectState):
        if not effectState.start and stopTime is not None:
            timeDiffInMs = (stopTime - blue.os.GetSimTime()) / const.MSEC
            if timeDiffInMs > 0:
                self.godma.LogInfo('ActualStopEffect::Sleeping for', timeDiffInMs)
                blue.pyos.synchro.SleepSim(timeDiffInMs)
        self.TryRecordLastStopTime(itemID, effectState, effect, time=blue.os.GetSimTime())
        self.ClearPendingOverloadingFlags()
        sm.ChainEvent('ProcessShipEffect', self, effectState)

    def TryRecordLastStopTime(self, itemID, effectState, effect, time):
        if effectState.start or effect.effectID in (const.effectOnline, const.effectOverloadRofBonus):
            return
        if effect.effectCategory == const.dgmEffPassive:
            return
        self.RecordLastStopTime(itemID, time)

    def RecordLastStopTime(self, itemID, time):
        delayTime = self.dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeModuleReactivationDelay)
        if not delayTime:
            return
        self.RemoveOldCooldownTimers()
        self.lastStopTimesByItemID[itemID] = (time, delayTime)

    def OnGodmaEffectInfo(self, itemID, itemTypeID, effectInfo, snapshotTime):
        info = utillib.KeyVal(activeEffects=effectInfo, time=snapshotTime)
        self.RefreshItemEffects(itemID, itemTypeID, info=info, doUpdate=True)

    def DoSimClockRebase(self, rebaseTimes):
        oldSimTime, newSimTime = rebaseTimes
        delta = newSimTime - oldSimTime
        for moduleID, times in self.lastStopTimesByItemID.items():
            time, delayTime = times
            time += delta
            self.lastStopTimesByItemID[moduleID] = (time, delayTime)

    def InitializeData(self):
        if not self.inited:
            self.attributesByName = dogma.data.get_all_attributes_by_name()
            self.attributesByID = dogma.data.get_all_attributes_by_id()
            chargedAttributes = dogma.data.get_attribute_list_by_charge_recharge_time_id()
            chargedAttributeTauCaps = {}
            chargedAttributeTauCapsByMax = {}
            chargedAttributesByTau = {}
            for tauID, attributes in chargedAttributes.iteritems():
                if not tauID:
                    continue
                tauName = self.attributesByID[tauID].name
                for attribute in attributes:
                    if attribute.dataType != attributeDataTypeTypeDamage:
                        attName = attribute.name
                        capName = self.attributesByID[attribute.maxAttributeID].name
                        chargedAttributeTauCaps[attName] = (tauName, capName)
                        if capName not in chargedAttributeTauCapsByMax:
                            chargedAttributeTauCapsByMax[capName] = []
                        chargedAttributeTauCapsByMax[capName].append(attName)
                        if tauName not in chargedAttributesByTau:
                            chargedAttributesByTau[tauName] = []
                        chargedAttributesByTau[tauName].append(attName)

            self.chargedAttributeTauCaps = chargedAttributeTauCaps
            self.chargedAttributeTauCapsByMax = chargedAttributeTauCapsByMax
            self.chargedAttributesByTau = chargedAttributesByTau
            self.typeWrappers = {}
            self.inited = True

    def IsSubLocation(self, itemKey):
        return type(itemKey) is tuple

    def UpdateItem(self, item, infoz = None, dontGetInfo = 0):
        self.godma.LogInfo('UpdateItem:', item, infoz, dontGetInfo)
        isSubLocation = item is not None and self.IsSubLocation(item.itemID) or infoz is not None and self.IsSubLocation(infoz.itemID)
        if isSubLocation:
            itemKey = infoz.itemID
            itemLocationID, itemFlag, itemTypeID = itemKey
            itemGroupID = evetypes.GetGroupID(itemTypeID)
            itemCategoryID = evetypes.GetCategoryID(itemTypeID)
        else:
            itemKey = item.itemID
            itemLocationID = item.locationID
            itemTypeID, itemGroupID, itemCategoryID, itemFlag = (item.typeID,
             item.groupID,
             item.categoryID,
             item.flagID)
        if itemCategoryID not in (const.categoryEntity,
         const.categoryStarbase,
         const.categorySovereigntyStructure,
         const.categoryShip,
         const.categoryModule,
         const.categoryCharge,
         const.categoryDrone,
         const.categorySubSystem,
         const.categoryFighter,
         const.categoryStructure,
         const.categoryStructureModule) and itemGroupID != const.groupCharacter:
            self.godma.LogTraceback('Godma location received unexpected and unwanted item')
            return
        if itemFlag in (const.flagCargo, const.flagDroneBay) or itemFlag in const.fighterTubeFlags:
            return
        doUpdate = False
        if isSubLocation:
            if itemLocationID not in self.invitems:
                self.godma.LogWarn('Godma:UpdateItem - could not find location object', itemLocationID, ', skipping update of', itemKey)
                return
            locationItem = self.invitems[itemLocationID]
            l = blue.DBRow(self.godma.subloc_internalrd, [itemKey,
             itemTypeID,
             locationItem.ownerID,
             itemLocationID,
             itemFlag,
             itemGroupID,
             itemCategoryID])
            if itemFlag not in self.sublocationsByKey:
                self.godma.LogInfo('Godma:UpdateItem - Inserting sublocation', itemKey)
                if const.attributeQuantity not in infoz.attributes:
                    log.LogTraceback('Godma:UpdateItem - QUANTITY MISSING', channel='svc.godma')
                    self.godma.LogError('Godma:UpdateItem - QUANTITY MISSING')
                else:
                    quantity = infoz.attributes[const.attributeQuantity]
                    item = blue.DBRow(self.godma.sublocrd, [itemKey,
                     itemTypeID,
                     locationItem.ownerID,
                     itemLocationID,
                     itemFlag,
                     quantity,
                     itemGroupID,
                     itemCategoryID,
                     None])
                    if self.godma.invCache.IsInventoryPrimedAndListed(itemLocationID):
                        self.godma.LogInfo('Godma:UpdateItem - QUANTITY', infoz.attributes[const.attributeQuantity])
                        change = {const.ixLocationID: None,
                         const.ixFlag: None}
                        location = None
                        sm.ScatterEvent('OnItemChange', item, change, location)
            self.sublocationsByKey[itemKey] = l
            if itemLocationID not in self.sublocationsByLocationFlag:
                self.sublocationsByLocationFlag[itemLocationID] = godmarowset.GodmaIndexedRowset(self.godma.subloc_internalrd, 'flagID', rowClass=self.GetSubLocationWrapper)
            elif itemFlag in self.sublocationsByLocationFlag[itemLocationID]:
                doUpdate = True
            self.sublocationsByLocationFlag[itemLocationID][itemFlag] = l
        else:
            if itemKey not in self.invitems:
                self.godma.LogInfo('Godma:UpdateItem - Inserting item', itemKey)
            else:
                doUpdate = True
            self.invitems[itemKey] = item
            if itemCategoryID in (const.categoryShip, const.categoryStarbase, const.categoryStructure) or itemGroupID == const.groupCharacter:
                self.itemsByLocationID[itemKey] = set()
            if not (idCheckers.IsSolarSystem(itemLocationID) or idCheckers.IsStation(itemLocationID)):
                self.itemsByLocationID[itemLocationID].add(itemKey)
        if IsShipFittingFlag(itemFlag) and not isSubLocation and itemCategoryID not in (const.categoryModule,
         const.categoryStructureModule,
         const.categoryCharge,
         const.categorySubSystem):
            self.godma.LogError('Godma:UpdateItem.skip2', itemKey)
            return
        if (isSubLocation or not item.singleton) and (itemCategoryID != const.categoryCharge or itemGroupID == const.groupMine):
            if itemFlag != const.flagCapsule:
                self.godma.LogError('Godma:UpdateItem.skip3', itemKey)
            return
        if dontGetInfo:
            self.godma.LogError('Godma:UpdateItem.skip4', itemKey)
            return
        if infoz is None:
            infoz = self.GetDogmaLM().ItemGetInfo(itemKey)
        if infoz is None:
            return
        self.RefreshItemAttributes(itemKey, infoz, doUpdate)
        self.RefreshItemEffects(itemKey, itemTypeID, infoz, doUpdate)
        if isSubLocation:
            regKey = (itemLocationID, itemFlag, None)
        else:
            regKey = itemKey
        if regKey in self.itemKeyChannels:
            while self.itemKeyChannels[regKey].queue:
                self.godma.LogInfo('GetWithWait-END', regKey)
                self.itemKeyChannels[regKey].send(ret)

            del self.itemKeyChannels[regKey]

    def RefreshItemEffects(self, itemID, itemTypeID, info = None, doUpdate = False):
        if info is None:
            info = self.GetDogmaLM().ItemGetInfo(itemID)
            if info is None:
                return
        effLines = []
        eventLines = []
        activeDict = info.activeEffects
        typeEffects = dogma.data.get_type_effects(itemTypeID)
        for row in typeEffects:
            effectID = row.effectID
            eff = dogma.data.get_effect(effectID)
            if row.isDefault and effectID != const.effectSkillEffect or effectID in self.requiredEffects or eff.effectCategory in (const.dgmEffActivation,
             const.dgmEffTarget,
             const.dgmEffArea,
             const.dgmEffOverload) or eff.fittingUsageChanceAttributeID is not None:
                line = blue.DBRow(self.__effectheader__, [itemID,
                 eff.effectID,
                 eff.effectName,
                 eff.effectCategory,
                 row.isDefault,
                 effectID in activeDict,
                 eff.isOffensive,
                 eff.isAssistance,
                 dogma.data.get_effect_description(eff.effectID),
                 eff.trackingSpeedAttributeID,
                 eff.rangeAttributeID,
                 eff.falloffAttributeID,
                 eff.dischargeAttributeID,
                 eff.durationAttributeID,
                 eff.iconID,
                 None,
                 None,
                 None,
                 None,
                 False])
                effLines.append(line)
                self.godma.LogInfo('RefreshItemEffects.effectsByItemEffect', itemID, effectID, effLines[-1])
                if effectID in activeDict and eff.effectCategory in (const.dgmEffActivation,
                 const.dgmEffTarget,
                 const.dgmEffArea,
                 const.dgmEffOverload) and effectID not in self.requiredEffects:
                    d = activeDict[effectID]
                    env = d[:ENV_IDX_LINE]
                    startTime, duration, repeat = d[7], d[8], d[9]
                    eventLines.append((itemID,
                     effectID,
                     info.time,
                     True,
                     True,
                     env,
                     startTime,
                     duration,
                     repeat,
                     None))

        if doUpdate and itemID in self.effectsByItemEffect:
            ind = self.effectsByItemEffect[itemID].header.Index('effectName')
            for i in effLines:
                self.effectsByItemEffect[itemID][i[ind]] = i

        else:
            self.effectsByItemEffect[itemID] = godmarowset.GodmaRowset(self.__effectheader__, effLines, rowClass=self.GetEffectWrapper).Index('effectName')
        kwArgs = {'stall': False}
        for line in eventLines:
            apply(self.OnGodmaShipEffect, line, kwArgs)

    def RefreshItemAttributes(self, itemID, info = None, doUpdate = False):
        if info is None:
            info = self.GetDogmaLM().ItemGetInfo(itemID)
            if info is None:
                return
        if doUpdate:
            atts = self.attributesByItemAttribute.get(itemID, {})
        else:
            atts = {}
        time = info.time
        wallclockTime = info.wallclockTime
        for attributeID, val in info.attributes.iteritems():
            if not self._IsAttributeChangeRelevant(itemID, attributeID, wallclockTime):
                continue
            attributeName = dogma.data.get_attribute_name(attributeID)
            self.godma.LogInfo('UpdateAttributeIDs', itemID, attributeID, attributeName, val)
            atts[attributeName] = val

        return self.UpdateAttribute(itemID, atts, time)

    def _IsAttributeChangeRelevant(self, itemID, attributeID, wallclockTime):
        if not wallclockTime:
            return True
        if (itemID, attributeID) not in self.lastAttributeChange:
            return True
        if self.lastAttributeChange[itemID, attributeID] <= wallclockTime:
            return True
        return False

    def UpdateAttribute(self, itemID, attributes, time):
        self.attributesByItemAttribute[itemID] = attributes
        if time is None:
            time = blue.os.GetSimTime()
        for k in attributes.iterkeys():
            if k in self.chargedAttributeTauCaps:
                if itemID not in self.chargedAttributesByItemAttribute:
                    self.chargedAttributesByItemAttribute[itemID] = {}
                if self.attributesByItemAttribute[itemID].get(self.chargedAttributeTauCaps[k][0]) and self.attributesByItemAttribute[itemID].get(self.chargedAttributeTauCaps[k][1]):
                    self.CreateChargedAttribute(itemID, k, attributes[k], time, self.chargedAttributeTauCaps[k])

    def CreateChargedAttribute(self, itemID, attribute, value, time, taucap):
        tau, cap = taucap
        tauValue = self.GetAttribute(itemID, tau) / 5.0
        capValue = self.GetAttribute(itemID, cap)
        self.chargedAttributesByItemAttribute[itemID][attribute] = [value,
         time,
         tauValue,
         capValue]
        self.godma.LogInfo('CreateChargedAttribute', itemID, attribute, time, self.chargedAttributesByItemAttribute[itemID][attribute])

    def NameToGroup(self, name):
        k = 'group' + name[0].capitalize() + name[1:]
        if ConstValueExists(k):
            return LookupConstValue(k, None)

    def NameToType(self, name):
        k = 'type' + name[0].capitalize() + name[1:]
        if ConstValueExists(k):
            return LookupConstValue(k, None)

    def LocateItem(self, id, name):
        typeID = self.NameToType(name)
        if typeID is not None:
            loc = FilterRowset(self.invitems.header, self.invitems.items.values(), 'locationID', self.GetItemWrapper)
            for item in loc[id]:
                if item.flagID in [const.flagSkill, const.flagSkillInTraining] and item.typeID == typeID:
                    return item

    def GetDisplayAttributes(self, id):
        rowDescriptor = blue.DBRowDescriptor((('displayName', const.DBTYPE_STR),
         ('value', const.DBTYPE_R5),
         ('unitID', const.DBTYPE_UI1),
         ('iconID', const.DBTYPE_I4),
         ('attributeID', const.DBTYPE_I2)))
        rowset = CRowset(rowDescriptor, [])
        for k, v in self.GetAttributes(id).iteritems():
            attribute = self.attributesByName[k]
            realK = dogma.data.get_attribute_display_name(attribute.attributeID)
            if not len(realK):
                realK = k
            if attribute.published:
                rowset.InsertNew([realK,
                 v,
                 getattr(attribute, 'unitID', None),
                 getattr(attribute, 'iconID', None),
                 attribute.attributeID])

        return rowset

    def GetItemWrapper(self, header, dbrow):
        return ItemWrapper(self, header, dbrow)

    def GetSubLocationWrapper(self, header, dbrow):
        return ItemWrapper(self, header, dbrow)

    def GetItem(self, itemID, waitForPrime = False):
        if type(itemID) is tuple:
            return self.GetSubLocation(itemID[0], itemID[1], waitForPrime)
        while self.priming:
            blue.pyos.synchro.SleepWallclock(1000)

        try:
            return self.invitems[itemID]
        except KeyError:
            pass

        if waitForPrime:
            self.godma.LogInfo('GetItem.GetWithWait', itemID)
            return self.GetWithWait(itemID)

    def IsItemReady(self, itemID):
        return itemID in self.invitems

    def GetSubLocation(self, locationID, flag, waitForPrime = False):
        while self.priming:
            blue.pyos.synchro.SleepWallclock(1000)

        try:
            return self.sublocationsByLocationFlag[locationID][flag]
        except KeyError:
            if waitForPrime:
                self.godma.LogInfo('GetSubLocation.GetWithWait', locationID, flag)
                return self.GetWithWait((locationID, flag, None))

    def GetWithWait(self, itemKey):
        try:
            channel = self.itemKeyChannels[itemKey]
        except KeyError:
            channel = uthread.Channel(('godma::GetItem', itemKey))
            self.itemKeyChannels[itemKey] = channel

        ret = channel.receive()
        self.godma.LogInfo('GetWithWait', itemKey, 'DONE', ret)
        return ret

    def GetAttributes(self, id):
        try:
            return self.attributesByItemAttribute[id]
        except KeyError:
            return {}

    def GetAttribute(self, itemKey, attrKey):
        if self.IsSubLocation(itemKey):
            if attrKey == 'singleton':
                return 0
            if attrKey == 'stacksize':
                attrKey = 'quantity'
        if itemKey in self.chargedAttributesByItemAttribute and attrKey in self.chargedAttributesByItemAttribute[itemKey]:
            chargedAttribute = self.chargedAttributesByItemAttribute[itemKey][attrKey]
            try:
                return self.GetChargeValue(*chargedAttribute)
            except ZeroDivisionError:
                typeID = self.invitems[itemKey].typeID if not isinstance(itemKey, tuple) else itemKey[2]
                log.LogException('GetChargeValue got a ZeroDivisionError for item %s of type %s' % (itemKey, evetypes.GetName(typeID)))
                raise

        try:
            return self.attributesByItemAttribute[itemKey][attrKey]
        except KeyError:
            pass

        if itemKey in self.sublocationsByKey:
            typeID = itemKey[2]
            locationID = itemKey[0]
        else:
            typeID = self.invitems[itemKey].typeID
            locationID = self.invitems[itemKey].locationID
        categoryID = evetypes.GetCategoryID(typeID)
        if categoryID == const.categorySkill:
            raise RuntimeError('StateManager::GetAttribute called for skill item! Skill items should not exist!')
        try:
            return self.attributesByName[attrKey].defaultValue
        except KeyError:
            pass

        if attrKey == 'invItem':
            if itemKey in self.sublocationsByKey:
                rd = self.godma.sublocrd
                item = self.GetSubLocation(locationID, itemKey[1])
            else:
                rd = self.godma.itemrd
                item = self.Item(itemKey)
            return blue.DBRow(rd, [itemKey,
             typeID,
             item.ownerID,
             locationID,
             item.flagID,
             item.quantity,
             evetypes.GetGroupID(typeID),
             categoryID,
             None])
        if attrKey == 'displayAttributes':
            return self.GetDisplayAttributes(itemKey)
        if attrKey == 'attributes':
            return self.GetAttributes(itemKey)
        if attrKey == 'typeID':
            return typeID
        if attrKey == 'type':
            log.LogTraceback("Someone is asking for 'type' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'description':
            return evetypes.GetDescription(typeID)
        if attrKey == 'group':
            log.LogTraceback("Someone is asking for 'group' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'category':
            log.LogTraceback("Someone is asking for 'category' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'parent':
            return self.invitems[locationID]
        if attrKey == 'name':
            return evetypes.GetName(typeID)
        if attrKey == 'graphicID':
            return evetypes.GetGraphicID(typeID)
        if attrKey == 'iconID':
            return evetypes.GetIconID(typeID)
        if attrKey == 'effects':
            return self.effectsByItemEffect.get(itemKey, {})
        if attrKey == 'skills':
            raise RuntimeError("Godma::GetAttribute called for 'skills'")
        else:
            if attrKey == 'implants':
                return [ implant for implant in sm.StartService('skills').GetImplants().itervalues() ]
            if attrKey == 'boosters':
                boosters = [ booster for booster in sm.StartService('skills').GetBoosters().itervalues() ]
                for booster in boosters:
                    setattr(booster, 'typeID', booster.boosterTypeID)

                return boosters
            if attrKey == 'modules':
                li = []
                if itemKey in self.itemsByLocationID:
                    for itemKey2 in self.itemsByLocationID[itemKey]:
                        if itemKey2 in self.invitems:
                            module = self.invitems[itemKey2]
                            if IsShipFittingFlag(module.flagID):
                                li.append(self.invitems[itemKey2].dbrow)

                return godmarowset.GodmaRowset(self.invitems.header, li, self.GetItemWrapper)
            if attrKey == 'sublocations':
                li = []
                if itemKey in self.sublocationsByLocationFlag:
                    li = [ i.dbrow for i in self.sublocationsByLocationFlag[itemKey].values() if IsShipFittingFlag(i[0][1]) ]
                return godmarowset.GodmaRowset(self.sublocationsByLocationFlag.header, li, self.GetItemWrapper)
        if itemKey not in self.invitems:
            raise RuntimeError('Item (or its parent) has not been primed', itemKey)
        loc = self.LocateItem(itemKey, attrKey)
        if loc is not None:
            return loc
        eff = self.GetEffect(itemKey, attrKey)
        if eff:
            return eff
        raise AttributeError, attrKey

    def GetEffectAttributeEx(self, eff, itemID, attribute):
        if attribute == 'item' or attribute == 'module':
            return self.GetItem(itemID)
        if attribute == 'trackingSpeed':
            trackingSpeedAttributeName = dogma.data.get_attribute_name(eff.trackingSpeedAttributeID)
            return self.GetAttribute(itemID, trackingSpeedAttributeName)
        if attribute == 'falloff':
            falloffAttributeName = dogma.data.get_attribute_name(eff.falloffAttributeID)
            return self.GetAttribute(itemID, falloffAttributeName)
        if attribute == 'range':
            rangeAttributeName = dogma.data.get_attribute_name(eff.rangeAttributeID)
            return self.GetAttribute(itemID, rangeAttributeName)

    def GetEffectWrapper(self, header, line):
        return EffectWrapper(self, header, line)

    def GetEffect(self, id, effect):
        try:
            return self.effectsByItemEffect[id][effect]
        except KeyError:
            return None

    def GetDefaultEffect(self, typeID):
        if typeID not in self.defaultEffectsByType:
            possibleEffects = dogma.data.get_type_effects(typeID)
            eff = None
            for typeEffect in possibleEffects:
                if typeEffect.isDefault:
                    eff = dogma.data.get_effect(typeEffect.effectID)

            if eff is None:
                return
            line = [None,
             eff.effectID,
             eff.effectName,
             eff.effectCategory,
             1,
             0,
             eff.isOffensive,
             eff.isAssistance,
             dogma.data.get_effect_description(eff.effectID),
             eff.trackingSpeedAttributeID,
             eff.rangeAttributeID,
             eff.falloffAttributeID,
             eff.dischargeAttributeID,
             eff.durationAttributeID,
             eff.iconID,
             None,
             None,
             None,
             None,
             0]
            self.defaultEffectsByType[typeID] = EffectWrapper(self, self.__effectheader__, blue.DBRow(self.__effectheader__, line))
        return self.defaultEffectsByType[typeID]

    def TypeHasEffect(self, typeID, effectID):
        self.CacheTypeEffects(typeID)
        return effectID in self.effectsByType[typeID]

    def GetEffectsByTypeID(self, typeID):
        self.CacheTypeEffects(typeID)
        return self.effectsByType[typeID]

    def CacheTypeEffects(self, typeID):
        if typeID not in self.effectsByType:
            self.effectsByType[typeID] = {typeEffect.effectID:dogma.data.get_effect(typeEffect.effectID) for typeEffect in dogma.data.get_type_effects(typeID)}

    def GetShipType(self, shipTypeID):
        return self.GetType(shipTypeID)

    def GetType(self, genericTypeID):
        self.InitializeData()
        if genericTypeID in self.typeWrappers:
            return self.typeWrappers[genericTypeID]
        result = TypeWrapper(self, genericTypeID)
        self.typeWrappers[genericTypeID] = result
        return result

    def GetChargeValue(self, oldVal, oldTime, tau, Ec, newTime = None):
        if Ec == 0:
            return 0
        if newTime is None:
            newTime = blue.os.GetSimTime()
        sq = math.sqrt(max(oldVal / Ec, 0))
        timePassed = min(oldTime - newTime, 0) / float(const.dgmTauConstant)
        exp = math.exp(timePassed / tau)
        ret = (1.0 + (sq - 1.0) * exp) ** 2 * Ec
        return ret

    def Activate(self, itemID, effectName, target, repeat):
        ret = None
        activateKey = (itemID, effectName)
        if activateKey in self.activatingEffects:
            self.godma.LogWarn('Trying to activate effect twice', effectName, itemID)
            return
        self.activatingEffects.add(activateKey)
        try:
            if target is not None and not isinstance(target, numbers.Integral):
                raise RuntimeError('InvalidTargetType', type(target))
            sm.GetService('invCache').TryLockItem(itemID, 'lockItemGodmaActivate', {}, 1)
            try:
                ret = self.GetDogmaLM().Activate(itemID, effectName, target, repeat)
                if effectName != 'online':
                    self.activatedLocation[itemID, effectName] = eve.session.locationid
                return ret
            finally:
                sm.GetService('invCache').UnlockItem(itemID)

        finally:
            self.activatingEffects.remove(activateKey)

    def Overload(self, itemID, effectID):
        self.GetDogmaLM().Overload(itemID, effectID)
        self.pendingOverloading.add(itemID)
        self.StopPendingStopOverloadModule(itemID)
        self.dogmaLocation.Overload(itemID, effectID)
        return itemID

    def OverloadRack(self, itemID):
        moduleIDs = self.GetDogmaLM().OverloadRack(itemID)
        for moduleID in moduleIDs:
            if not self.IsModuleOverloaded(moduleID):
                self.pendingOverloading.add(moduleID)

        self.dogmaLocation.OverloadRack(moduleIDs)
        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)
        return moduleIDs

    def Deactivate(self, itemID, effectName):
        sm.GetService('invCache').TryLockItem(itemID, 'lockItemGodmaDeactivate', {}, 1)
        try:
            if (itemID, effectName) in self.activatedLocation and self.activatedLocation[itemID, effectName] != eve.session.locationid:
                return
            if itemID in self.effectsByItemEffect and effectName in self.effectsByItemEffect[itemID]:
                self.effectsByItemEffect[itemID][effectName].isDeactivating = True
            return self.GetDogmaLM().Deactivate(itemID, effectName)
        except UserError:
            self.effectsByItemEffect[itemID][effectName].isDeactivating = False
            raise
        finally:
            sm.GetService('invCache').UnlockItem(itemID)

    def IsModuleActivating(self, itemID, effectName):
        activateKey = (itemID, effectName)
        if activateKey in self.activatingEffects:
            return True
        return False

    def StopOverload(self, itemID, effectID):
        self.GetDogmaLM().StopOverload(itemID, effectID)
        self.pendingStopOverloading.add(itemID)
        self.StopPendingOverloadModule(itemID)
        self.dogmaLocation.StopOverloading(itemID, effectID)
        return itemID

    def StopOverloadRack(self, itemID):
        moduleIDs = self.GetDogmaLM().StopOverloadRack(itemID)
        self.pendingStopOverloading.update(moduleIDs)
        self.dogmaLocation.StopOverloadingRack(moduleIDs)
        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)

    def StopPendingOverloadModule(self, itemID):
        try:
            self.pendingOverloading.remove(itemID)
        except KeyError:
            pass

        sm.ChainEvent('ProcessPendingOverloadUpdate', [itemID])

    def StopPendingStopOverloadModule(self, itemID):
        try:
            self.pendingStopOverloading.remove(itemID)
        except KeyError:
            pass

        sm.ChainEvent('ProcessPendingOverloadUpdate', [itemID])

    def IsModuleOverloaded(self, itemID):
        for effect in self.GetItem(itemID).effects.itervalues():
            if effect.effectCategory == const.dgmEffOverload and effect.isActive:
                return True

        return False

    def GetOverloadState(self, itemID):
        item = self.GetItem(itemID)
        for effectName, effect in item.effects.iteritems():
            if effect.effectCategory == const.dgmEffOverload and effect.isActive:
                if itemID in self.pendingStopOverloading:
                    return MODULE_PENDING_STOPOVERLOADING
                return MODULE_OVERLOADED
                break
        else:
            if itemID in self.pendingOverloading:
                return MODULE_PENDING_OVERLOADING
            return MODULE_NOT_OVERLOADED

    def ClearPendingOverloadingFlags(self):
        moduleIDs = self.pendingOverloading.copy()
        moduleIDs.update(self.pendingStopOverloading.copy())
        self.pendingOverloading.clear()
        self.pendingStopOverloading.clear()
        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)

    def GetMaxDamagedModuleInGroup(self, shipID, itemID):
        moduleIDs = self.dogmaLocation.GetModulesInBank(shipID, itemID)
        if moduleIDs is None:
            item = self.GetItem(itemID)
            damage = item.damage if item else 0
            return (itemID, damage)
        maxDamage = 0
        for moduleID in moduleIDs:
            item = self.GetItem(moduleID)
            if not item:
                continue
            if item.damage > maxDamage:
                maxDamage = item.damage

        masterID = self.dogmaLocation.GetMasterModuleID(shipID, itemID)
        masterID = masterID if masterID is not None else itemID
        return (masterID, maxDamage)

    def RepairManyModules(self, itemIDs):
        timeStamp = blue.os.GetSimTime()
        success, missingCharges, failed = self.GetDogmaLM().InitiateModuleRepairMany(itemIDs)
        textList = []
        if success:
            textList.append(GetByLabel('UI/Inflight/SuccessfullyStartedRepairing', numModules=len(success)))
        if missingCharges:
            textList.append(GetByLabel('UI/Inflight/NotEnoughNaniteToRepairAll', typeName=evetypes.GetName(const.typeNaniteRepairPaste), numModules=len(missingCharges)))
        if failed:
            textList.append(GetByLabel('UI/Inflight/FailedToStartRepair', numModules=len(failed)))
        if textList:
            text = '<br><br>'.join(textList)
            eve.Message('CustomNotify', {'notify': text})
        for itemID in success:
            self.modulesBeingRepaired[itemID] = timeStamp
            uthread.pool('godma::RepairManyModules::RepairModule_thread', self.RepairModule_thread, itemID, timeStamp)

        if success:
            sm.ScatterEvent('OnMultiModuleRepairStarted', success)

    def RepairModule(self, itemID):
        timeStamp = blue.os.GetSimTime()
        res = self.GetDogmaLM().InitiateModuleRepair(itemID)
        if res == False:
            return False
        self.modulesBeingRepaired[itemID] = timeStamp
        uthread.pool('godma::RepairModule::RepairModule_thread', self.RepairModule_thread, itemID, timeStamp)
        return True

    def IsBeingRepaired(self, itemID):
        if itemID in self.modulesBeingRepaired:
            return True
        slaves = self.GetSlaveModules(itemID)
        for slave in slaves:
            if slave in self.modulesBeingRepaired:
                return True

        return False

    def GetSlaveModules(self, itemID):
        return self.dogmaLocation.GetSlaveModules(itemID, session.shipid) or []

    def RepairModule_thread(self, itemID, timeStamp):
        dmg = self.GetAttribute(itemID, 'damage')
        owner = session.charid
        rateOfRepair = self.GetAttribute(owner, 'moduleRepairRate')
        timeToSleep = dmg / rateOfRepair
        timeToSleepMs = int(timeToSleep * 60 * 1000)
        blue.pyos.synchro.SleepSim(timeToSleepMs + 1000)
        if itemID in self.modulesBeingRepaired and self.modulesBeingRepaired[itemID] == timeStamp:
            self.StopRepairModule(itemID)

    def StopRepairModule(self, itemID):
        if itemID in self.modulesBeingRepaired:
            try:
                self.GetDogmaLM().StopModuleRepair(itemID)
            finally:
                sm.ScatterEvent('OnModuleRepaired', itemID)
                del self.modulesBeingRepaired[itemID]

    def StopRepairModuleManyModules(self, itemIDs):
        for itemID in itemIDs:
            self.StopRepairModule(itemID)

    def GetRepairTimeStamp(self, itemID):
        return self.modulesBeingRepaired.get(itemID, None)

    def OnDroneControlLost(self, droneID):
        self.invitems.pop(droneID, None)

    def OnDroneStateChange2(self, droneID, oldState, newState):
        if newState == -1:
            return
        if droneID in self.invitems:
            return
        slimItem = sm.GetService('michelle').GetItem(droneID)
        if slimItem and slimItem.ownerID == session.charid:
            typeID = slimItem.typeID
            item = blue.DBRow(self.godma.itemrd, [slimItem.itemID,
             typeID,
             slimItem.ownerID,
             session.solarsystemid,
             0,
             1,
             evetypes.GetGroupID(typeID),
             evetypes.GetCategoryID(typeID),
             1])
            self.UpdateItem(item)

    def OnFighterRemovedFromControllerClient(self, fighterID):
        self.invitems.pop(fighterID, None)

    def IsModuleReloading(self, moduleID):
        return self.GetReloadTimes(moduleID) is not None

    def GetReloadTimes(self, moduleID):
        nextCycle = self.GetAttributeValueByID(moduleID, const.attributeNextActivationTime)
        if nextCycle is None or nextCycle < blue.os.GetSimTime():
            return
        duration = self.GetAttributeValueByID(moduleID, const.attributeReloadTime)
        startTime = nextCycle - duration * const.MSEC
        return (startTime, duration)

    def GetCooldownTimes(self, moduleID):
        return self.lastStopTimesByItemID.get(moduleID, None)

    def GetDurationTimeLeft(self, moduleID, typeID):
        defaultEffect = self.GetDefaultEffect(typeID)
        if defaultEffect:
            effectsForItem = self.effectsByItemEffect.get(moduleID, None)
            if not effectsForItem:
                return
            effectInfo = effectsForItem.get(defaultEffect.effectName, None)
            if effectInfo and effectInfo.isActive and effectInfo.startTime and effectInfo.duration:
                now = blue.os.GetSimTime()
                portionDone = blue.os.TimeDiffInMs(effectInfo.startTime, now) / effectInfo.duration
                if portionDone < 1:
                    return (effectInfo.startTime, effectInfo.duration)
                newStart = effectInfo.startTime + int(portionDone) * effectInfo.duration * const.MSEC
                return (newStart, effectInfo.duration)

    def RemoveOldCooldownTimers(self):
        now = blue.os.GetSimTime()
        for moduleID, times in self.lastStopTimesByItemID.items():
            time, delayTime = times
            if time + delayTime + 5 * const.SEC < now:
                del self.lastStopTimesByItemID[moduleID]

    def SendDroneSettings(self):
        droneSettingChanges = {const.attributeDroneIsAggressive: drones_aggressive_setting.is_enabled(),
         const.attributeDroneFocusFire: drones_focus_fire_setting.is_enabled()}
        self.GetDogmaLM().ChangeDroneSettings(droneSettingChanges)

    def ChangeDroneSettings(self, droneSettingChanges):
        validDroneSettingAttribs = [const.attributeDroneIsAggressive, const.attributeDroneFocusFire]
        for key in droneSettingChanges:
            if key in validDroneSettingAttribs:
                self.droneSettingAttributes[key] = droneSettingChanges[key]
                continue
            else:
                return

        self.GetDogmaLM().ChangeDroneSettings(droneSettingChanges)

    def GetDroneSettingAttributes(self):
        return self.droneSettingAttributes

    def RefreshTargets(self):
        for objectID in self.GetDogmaLM().GetTargets():
            sm.ScatterEvent('OnTarget', 'add', objectID)

        for objectID in self.GetDogmaLM().GetTargeters():
            sm.ScatterEvent('OnTarget', 'otheradd', objectID)

    def ForcePrimeLocation(self, locationIDs):
        keepLocationIDs = {session.charid, session.shipid, session.structureid}.difference(locationIDs)
        self.PurgeInventories(keepLocationIDs)
        primeCharacter = session.charid not in keepLocationIDs
        primeShip = session.shipid not in keepLocationIDs
        primeStructure = session.structureid not in keepLocationIDs
        if primeCharacter or primeShip or primeStructure:
            self.ProcessAllInfo(self.GetDogmaLM().GetAllInfo(primeCharacter, primeShip, primeStructure))

    def PrimeLocation(self, itemID, contents, locationID, priority = None, force = False):
        if itemID not in self.invByID or force:
            keys = contents.keys()
            for priorityID in reversed(priority or []):
                try:
                    keys.remove(priorityID)
                    keys.insert(0, priorityID)
                except ValueError:
                    pass

            for key in keys:
                row = contents[key]
                self.UpdateItem(row.invItem, row)

            self.invByID[itemID] = sm.GetService('invCache').GetInventoryFromId(itemID, 1)
        else:
            self.invByID[itemID].locationID = locationID

    def Prime(self):
        self.godma.LogInfo('Godma Prime:', session.shipid)
        self.priming = True
        try:
            self.primingChannel = uthread.Channel(('godma::Prime', session.shipid))
            self.InitializeData()
            primeCharacter = session.charid and session.charid not in self.invByID
            primeShip = session.shipid and session.shipid not in self.invByID
            primeStructure = session.structureid and session.structureid not in self.invByID
            if primeCharacter or primeShip or primeStructure:
                allInfo = self.GetDogmaLM().GetAllInfo(primeCharacter, primeShip, primeStructure)
                self.ProcessAllInfo(allInfo)
            else:
                allInfo = None
        finally:
            self.priming = False

        while self.primingChannel.queue:
            self.primingChannel.send(True)

        self.primingChannel = None
        char = self.GetItem(session.charid)
        for att in ['memory',
         'perception',
         'willpower',
         'charisma',
         'intelligence']:
            sm.ScatterEvent('OnAttribute', att, char, getattr(char, att))

        sm.ScatterEvent('OnCapacityChange', session.shipid)
        if session.charid:
            if allInfo and allInfo.charInfo:
                _, charBrain = allInfo.charInfo
            else:
                charBrain = ()
            self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation(charBrain=charBrain)
            if allInfo is not None:
                self.dogmaLocation.MakeShipActive(session.shipid, allInfo.shipState)

    def ProcessAllInfo(self, allInfo):
        if allInfo.structureInfo:
            self.PrimeLocation(session.structureid, allInfo.structureInfo, session.solarsystemid, [session.structureid, session.shipid, session.charid])
        if allInfo.shipInfo:
            forcePriming = bool(session.shipid == session.structureid and bool(allInfo.shipInfo))
            self.PrimeLocation(session.shipid, allInfo.shipInfo, session.solarsystemid or session.stationid, [session.shipid, session.charid], force=forcePriming)
        if allInfo.charInfo:
            self.PrimeLocation(session.charid, allInfo.charInfo[0], session.shipid, [session.charid])
        if allInfo.shipModifiedCharAttribs:
            self.RefreshItemAttributes(session.charid, info=allInfo.shipModifiedCharAttribs, doUpdate=True)
        if allInfo.systemWideEffectsOnShip:
            sm.ScatterEvent('OnUpdateSystemWideEffectsInfo', allInfo.systemWideEffectsOnShip)

    def PurgeInventories(self, keepList, skipCapacityEvent = False):
        self.godma.LogInfo('PurgeInventories: 1, Inventories.')
        for itemID in self.invByID.keys():
            if itemID not in keepList:
                self.PurgeEntries(itemID, skipCapacityEvent)
            else:
                for itemID2 in self.invitems.iterkeys():
                    if self.invitems[itemID2].locationID == itemID and itemID2 not in self.invByID:
                        if itemID2 in self.effectsByItemEffect:
                            for effect in self.effectsByItemEffect[itemID2].itervalues():
                                if effect.isActive and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget) and effect.effectName != 'online':
                                    effect.isActive = 0
                                    effect.isDeactivating = False

        self.godma.LogInfo('PurgeInventories: 2, Locations.')
        for locationID in self.itemsByLocationID.keys():
            if locationID not in keepList:
                self.PurgeEntries(locationID, skipCapacityEvent)

    def PurgeEntries(self, locationID, skipCapacityEvent = False):
        self.godma.LogInfo('PurgeEntries', locationID, 'with pending', self.pending)
        if locationID in self.pending:
            self.godma.LogError('PurgeEntries: failed,', locationID, 'is marked as pending.')
            return
        if not (locationID in self.invByID or locationID in self.itemsByLocationID):
            self.godma.LogError('PurgeEntries: failed,', locationID, 'is not primed.')
            return
        self.godma.LogInfo('PurgeEntries: Proceeding with', locationID)
        for itemID in self.invitems.keys():
            if self.invitems[itemID].locationID == locationID and itemID not in self.invByID:
                self.PurgeEntry(itemID)
                del self.invitems[itemID]

        for itemKey in self.sublocationsByKey.keys():
            if itemKey[0] == locationID:
                self.PurgeEntry(itemKey)
                try:
                    del self.sublocationsByKey[itemKey]
                    del self.sublocationsByLocationFlag[locationID][itemKey[1]]
                except KeyError:
                    self.godma.LogError("Failed to delete key because it wasn't there", locationID, self.sublocationsByKey, self.sublocationsByLocationFlag, itemKey)

        self.PurgeEntry(locationID)
        for container in (self.invitems, self.invByID, self.itemsByLocationID):
            try:
                del container[locationID]
            except KeyError:
                pass

        if not skipCapacityEvent:
            sm.ScatterEvent('OnCapacityChange', locationID)
        self.godma.LogInfo('PurgeEntries: Done with', locationID)

    def PurgeEntry(self, itemKey, locationID = None):
        if locationID is not None:
            self.godma.LogInfo('PurgeEntry', itemKey, locationID)
            if self.IsSubLocation(itemKey):
                if itemKey[0] == locationID:
                    del self.sublocationsByKey[itemKey]
                    del self.sublocationsByLocationFlag[locationID][itemKey[1]]
            elif itemKey in self.invitems:
                del self.invitems[itemKey]
                if itemKey in self.itemsByLocationID[locationID]:
                    self.itemsByLocationID[locationID].remove(itemKey)
        for container in (self.effectsByItemEffect, self.attributesByItemAttribute, self.chargedAttributesByItemAttribute):
            try:
                del container[itemKey]
            except KeyError:
                pass

    def ApplyAttributeChange(self, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr = True):
        item = None
        if itemKey in self.invitems:
            item = self.invitems[itemKey]
        elif itemKey in self.sublocationsByKey:
            item = self.sublocationsByKey[itemKey]
        if item is None or itemKey not in self.attributesByItemAttribute:
            if itemKey not in self.attributesByItemAttribute:
                self.godma.LogInfo('ApplyAttributeChange - item not found', item, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
            return
        attributeName = dogma.data.get_attribute_name(attributeID)
        att = getattr(item, attributeName, 'not there')
        argumentOldValue = oldValue
        oldValue = self.GetAttribute(itemKey, attributeName)
        if oldValue == newValue:
            self.godma.LogInfo('Reduntant update of attribute %s. Values are %s' % (attributeName, newValue))
            return
        self.godma.LogInfo('Processing attribute %s changing from %s (server sent oldVal as %s) to %s' % (attributeName,
         oldValue,
         argumentOldValue,
         newValue))
        self.attributesByItemAttribute[itemKey][attributeName] = newValue
        if attributeName in self.chargedAttributeTauCaps:
            if itemKey not in self.chargedAttributesByItemAttribute:
                self.chargedAttributesByItemAttribute[itemKey] = {}
            self.godma.LogInfo('Charge Attribute %s created with value %s' % (attributeName, newValue))
            self.CreateChargedAttribute(itemKey, attributeName, newValue, time, self.chargedAttributeTauCaps[attributeName])
        elif attributeName in self.chargedAttributeTauCapsByMax:
            for chargeAttName in self.chargedAttributeTauCapsByMax[attributeName]:
                self.godma.LogInfo('Processing chargedAttributeTauCapsByMax attribute %s for attribute %s' % (chargeAttName, attributeName))
                if itemKey in self.chargedAttributesByItemAttribute:
                    if chargeAttName in self.chargedAttributesByItemAttribute[itemKey]:
                        charge = self.GetAttribute(itemKey, chargeAttName)
                        if oldValue != newValue:
                            maxChangeRatio = float(newValue) / oldValue
                            if charge == oldValue:
                                charge = charge * maxChangeRatio
                            if charge > newValue:
                                charge = newValue
                            self.godma.LogInfo('ChargedAttributeTauCapsByMax Attribute %s re-created with value %s' % (chargeAttName, charge))
                            self.CreateChargedAttribute(itemKey, chargeAttName, charge, time, self.chargedAttributeTauCaps[chargeAttName])
                        break
                    elif self.attributesByItemAttribute[itemKey].get(self.chargedAttributeTauCaps[chargeAttName][0]) and self.attributesByItemAttribute[itemKey].get(self.chargedAttributeTauCaps[chargeAttName][1]):
                        self.godma.LogInfo('ChargedAttributeTauCapsByMax Attribute %s initialized with value %s' % (chargeAttName, self.attributesByItemAttribute[itemKey][chargeAttName]))
                        self.CreateChargedAttribute(itemKey, chargeAttName, self.attributesByItemAttribute[itemKey][chargeAttName], time, self.chargedAttributeTauCaps[chargeAttName])
                        break

        elif attributeName in self.chargedAttributesByTau:
            for attName in self.chargedAttributesByTau[attributeName]:
                self.godma.LogInfo('Processing chargedAttributesByTau attribute %s for attribute %s' % (attName, attributeName))
                if itemKey in self.chargedAttributesByItemAttribute and attName in self.chargedAttributesByItemAttribute[itemKey]:
                    charge = self.GetAttribute(itemKey, attName)
                    self.godma.LogInfo('ChargedAttributesByTau %s created with value %s' % (attName, charge))
                    self.CreateChargedAttribute(itemKey, attName, charge, time, self.chargedAttributeTauCaps[attName])
                    break

        self.godma.LogInfo('Attribute', attributeName, 'of module', itemKey, 'changed from', oldValue, 'to', newValue, 'value I had was', att)
        if attributeID in (const.attributeCapacity,
         const.attributeDroneCapacity,
         const.attributeShipMaintenanceBayCapacity,
         const.attributeFleetHangarCapacity):
            sm.ScatterEvent('OnCapacityChange', itemKey)
        elif attributeID == const.attributeQuantity:
            self.godma.LogInfo('Changing quantity from', att, 'to', newValue)
            if newValue == att:
                return
            locationID, flag, typeID = itemKey
            currSubLocation = self.GetSubLocation(locationID, flag)
            if currSubLocation and currSubLocation.typeID != typeID:
                self.godma.LogWarn("Trying to modify quantity of sublocation that isn't loaded with my type", currSubLocation, itemKey)
                return
            if newValue == 0:
                self.godma.LogInfo('SubLoc.quantityExpelled', itemKey, (oldValue, newValue))
                locationID, flag = itemKey[0], itemKey[1]
                if locationID in self.sublocationsByLocationFlag and flag in self.sublocationsByLocationFlag[locationID]:
                    del self.sublocationsByLocationFlag[locationID][flag]
                del self.sublocationsByKey[itemKey]
            item = blue.DBRow(self.godma.sublocrd, [itemKey,
             typeID,
             None,
             locationID,
             flag,
             newValue,
             evetypes.GetGroupID(typeID),
             evetypes.GetCategoryID(typeID),
             None])
            change = {const.ixStackSize: oldValue}
            location = None
            sm.ScatterEvent('OnItemChange', item, change, location)
        if attributeID == const.attributeIsOnline:
            sm.ScatterEvent('OnModuleOnlineChange', item, oldValue, newValue)
            if newValue == 0 and oldValue == 1:
                if item.online.isActive:
                    self.godma.LogWarn('Module put offline silently, faking event', itemKey)
                    self.OnGodmaShipEffect(itemKey, const.effectOnline, blue.os.GetSimTime(), 0, 0, [itemKey,
                     item.ownerID,
                     item.locationID,
                     None,
                     None,
                     [],
                     const.effectOnline], None, -1, -1, None, None)
        if scatterAttr:
            sm.ScatterEvent('OnAttribute', attributeName, item, newValue)

    def OnJumpCloneTransitionCompleted(self):
        self.priming = True
        self.PurgeInventories([], skipCapacityEvent=True)
        self.dogmaLM = None
        self.godma.LogInfo('OnJumpCloneTransitionCompleted: Prime (pre)')
        self.Prime()
        self.godma.LogInfo('OnJumpCloneTransitionCompleted: Prime (post)')
        self.priming = False
        if session.stationid or session.solarsystemid:
            dogmaLM = self.GetDogmaLM()
            dogmaLM.Bind()
        sm.StartService('skills').OnJumpCloneTransitionCompleted()

    def CheckFutileSubSystemSwitch(self, typeID, itemID):
        flag = self.godma.GetTypeAttribute(typeID, const.attributeSubSystemSlot)
        if flag is None:
            return False
        ship = self.GetItem(session.shipid)
        slotOccupants = ship.GetSlotOccupants(flag)
        if len(slotOccupants) > 0:
            if slotOccupants[0].itemID == itemID:
                return True
            if slotOccupants[0].typeID == typeID:
                if eve.Message('SubSystemTypeAlreadyFitted', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return True
        return False

    def DelayedOnlineAttempt(self, shipID, moduleID, delay = 500):
        blue.pyos.synchro.SleepSim(delay)
        if shipID != session.shipid:
            return
        module = self.GetItem(moduleID)
        if module is None:
            return
        if 'online' not in module.effects:
            return
        effect = module.effects['online']
        if effect.isActive:
            return
        effect.Activate()

    def GetSensorStrengthAttribute(self, shipID):
        ret = None
        max = -1
        ship = self.GetItem(shipID)
        for attribute in ['scanGravimetricStrength',
         'scanLadarStrength',
         'scanMagnetometricStrength',
         'scanRadarStrength']:
            val = getattr(ship, attribute, None)
            if val > max:
                max = val
                ret = (attribute, val)

        return (self.attributesByName[ret[0]].attributeID, ret[1])

    def GetAttributeValueByID(self, itemID, attributeID):
        attribute = self.attributesByID.get(attributeID, None)
        if attribute is None:
            return
        return self.GetAttribute(itemID, attribute.name)

    def ChangeAmmoTypeForModule(self, moduleID, typeID):
        self.chargeTypeByModule[moduleID] = typeID

    def GetAmmoTypeForModule(self, moduleID):
        return self.chargeTypeByModule.get(moduleID, None)


exports = {'godma.MODULE_NOT_OVERLOADED': MODULE_NOT_OVERLOADED,
 'godma.MODULE_OVERLOADED': MODULE_OVERLOADED,
 'godma.MODULE_PENDING_OVERLOADING': MODULE_PENDING_OVERLOADING,
 'godma.MODULE_PENDING_STOPOVERLOADING': MODULE_PENDING_STOPOVERLOADING}

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\playerOwned.py
import sys
import blue
import carbonui.const as uiconst
import dogma.data
import eve.common.script.mgt.posConst as pos
import evetypes
import localization
import log
import telemetry
import uthread
from carbon.common.script.sys.service import Service
from eve.client.script.ui.util import uix
from eve.client.script.ui.util import utilWindows
from eve.common.lib import appConst as const
from eve.common.script.net import eveMoniker
from eveexceptions import UserError
ONLINE_STATES = (pos.STRUCTURE_ONLINING,
 pos.STRUCTURE_REINFORCED,
 pos.STRUCTURE_ONLINE,
 pos.STRUCTURE_OPERATING,
 pos.STRUCTURE_VULNERABLE,
 pos.STRUCTURE_SHIELD_REINFORCE,
 pos.STRUCTURE_ARMOR_REINFORCE,
 pos.STRUCTURE_INVULNERABLE)
UNANCHORABLE_STATES = (pos.STRUCTURE_ONLINING,
 pos.STRUCTURE_REINFORCED,
 pos.STRUCTURE_ONLINE,
 pos.STRUCTURE_OPERATING,
 pos.STRUCTURE_UNANCHORED,
 pos.STRUCTURE_VULNERABLE,
 pos.STRUCTURE_SHIELD_REINFORCE,
 pos.STRUCTURE_ARMOR_REINFORCE,
 pos.STRUCTURE_INVULNERABLE)

class PlayerOwned(Service):
    __guid__ = 'svc.pwn'
    __exportedcalls__ = {'CanAnchorStructure': [],
     'CanUnanchorStructure': [],
     'CanOnlineStructure': [],
     'CanOfflineStructure': [],
     'CanAssumeControlStructure': [],
     'GetStructureState': [],
     'CompareShipStructureHarmonic': [],
     'CheckAnchoringPosition': [],
     'Anchor': [],
     'EnterTowerPassword': [],
     'EnterShipPassword': [],
     'AssumeStructureControl': [],
     'RelinquishStructureControl': [],
     'UnlockStructureTarget': [],
     'GetCurrentTarget': [],
     'ClrCurrentTarget': [],
     'GetCurrentControl': []}
    __notifyevents__ = ['OnSlimItemChange',
     'OnTargetOBO',
     'DoSessionChanging',
     'DoBallsAdded',
     'DoBallRemove',
     'DoBallsRemove']
    __dependencies__ = ['godma', 'michelle']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        sm.FavourMe(self.DoBallsAdded)
        self.currenttargets = {}
        self.currentcontrol = {}
        self.currentlyAssuming = {}

    def Stop(self, stream):
        Service.Stop(self)

    def OnSlimItemChange(self, oldItem, newItem):
        if newItem.categoryID != const.categoryStarbase:
            return
        if newItem.posState == oldItem.posState and newItem.posTimestamp == oldItem.posTimestamp and newItem.controllerID == oldItem.controllerID and newItem.incapacitated == oldItem.incapacitated:
            return
        if oldItem.controllerID is not None and newItem.controllerID == None:
            uthread.new(self.RelinquishStructureControl, oldItem, silent=True, force=True)
        stateName, stateTimestamp, stateDelay = self.GetStructureState(newItem)
        if stateName == 'onlining':
            uthread.pool('pwn::StalledOnlineEvent', self.StalledOnlineEvent, newItem.itemID, newItem.posState, stateTimestamp, stateDelay)

    def StalledOnlineEvent(self, itemID, posState, stateTimestamp, stateDelay):
        item = self.michelle.GetItem(itemID)
        if item is None or item.posState != posState or item.posTimestamp != stateTimestamp:
            return
        x1, x2, stateDelay = self.GetStructureState(item)
        blue.pyos.synchro.SleepWallclock(stateDelay)
        item = self.michelle.GetItem(itemID)
        if item is None:
            return
        if item.posState != posState or item.posTimestamp != stateTimestamp:
            if item.posState != pos.STRUCTURE_ONLINE:
                return
        sm.ScatterEvent('OnStructureFullyOnline', itemID)
        if item.controlTowerID is not None:
            sm.ScatterEvent('OnSpecialFX', item.controlTowerID, itemID, item.typeID, None, None, 'effects.StructureOnlined', 0, 1, 0)

    def CompareShipStructureHarmonic(self, shipID, itemID):
        item = self.michelle.GetItem(itemID)
        if not item:
            return False
        if item.groupID == const.groupControlTower:
            controlTowerID = itemID
            towerItem = item
        else:
            controlTowerID = item.controlTowerID
            if controlTowerID is None:
                return False
            towerItem = self.michelle.GetItem(controlTowerID)
            if towerItem is None:
                return False
        forceFieldID = towerItem.forceFieldID
        if forceFieldID is None:
            return False
        fieldBall = self.michelle.GetBall(forceFieldID)
        shipBall = self.michelle.GetBall(shipID)
        if not shipBall or not fieldBall:
            return False
        if fieldBall.harmonic != -1 and fieldBall.harmonic == shipBall.harmonic:
            return True
        return False

    def GetStructureState(self, slimItem):
        stateName = 'Unknown_State_%s' % slimItem.posState
        stateTimestamp = None
        stateDelay = None
        godmaSM = self.godma.GetStateManager()
        if slimItem.posState == pos.STRUCTURE_ANCHORED:
            stateName = const.pwnStructureStateAnchored
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
                if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = const.pwnStructureStateAnchoring
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_ONLINING:
            stateName = const.pwnStructureStateOnline
            if slimItem.posState == pos.STRUCTURE_ONLINING and slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).onliningDelay
                if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = const.pwnStructureStateOnlining
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_UNANCHORED:
            stateName = const.pwnStructureStateUnanchored
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).unanchoringDelay
                if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                    stateName = const.pwnStructureStateUnanchoring
                    stateTimestamp = slimItem.posTimestamp
                    stateDelay = delayMs
        elif slimItem.posState == pos.STRUCTURE_VULNERABLE:
            stateName = const.pwnStructureStateVulnerable
        elif slimItem.posState == pos.STRUCTURE_INVULNERABLE:
            stateName = const.pwnStructureStateInvulnerable
        elif slimItem.posState == pos.STRUCTURE_REINFORCED:
            delayMs = (blue.os.GetWallclockTime() - slimItem.posTimestamp) / 10000
            if delayMs < 0:
                stateName = const.pwnStructureStateReinforced
                stateDelay = -delayMs
                stateTimestamp = blue.os.GetWallclockTime() + delayMs
        elif slimItem.posState in (pos.STRUCTURE_SHIELD_REINFORCE, pos.STRUCTURE_ARMOR_REINFORCE):
            stateName = const.pwnStructureStateReinforced
            stateTimestamp = slimItem.posTimestamp + slimItem.posDelayTime
            stateDelay = slimItem.posDelayTime
        elif slimItem.posState == pos.STRUCTURE_OPERATING:
            stateName = const.pwnStructureStateOnline
            delayMs = (blue.os.GetWallclockTime() - slimItem.posTimestamp) / 10000
            if delayMs < 0:
                stateName = const.pwnStructureStateOperating
                stateDelay = -delayMs
                stateTimestamp = blue.os.GetWallclockTime() + delayMs
        elif slimItem.posState == pos.STRUCTURE_ONLINE:
            stateName = const.pwnStructureStateOnline
        if slimItem.incapacitated:
            stateName = const.pwnStructureStateIncapacitated
        return (stateName, stateTimestamp, stateDelay)

    def EnterTowerPassword(self, towerID):
        password = utilWindows.NamePopup(caption=localization.GetByLabel('UI/Inflight/POS/TowerShieldHarmonic'), label=localization.GetByLabel('UI/Inflight/POS/EnterTheSharedSecret'), setvalue='', maxLength=50, passwordChar='*')
        if password is None:
            return
        posMgr = eveMoniker.GetPOSMgr()
        posMgr.SetTowerPassword(towerID, password)

    def EnterShipPassword(self):
        format = [{'type': 'text',
          'refreshheight': 1,
          'text': localization.GetByLabel('UI/Inflight/POS/EnterHarmonicPassword'),
          'frame': 0}, {'type': 'edit',
          'setvalue': '',
          'label': '_hide',
          'key': 'name',
          'maxLength': 50,
          'passwordChar': '*',
          'setfocus': 1,
          'frame': 0}]
        retval = uix.HybridWnd(format, caption=localization.GetByLabel('UI/Inflight/POS/ShipShieldHarmonic'), windowID='enterShipPassword', modal=1, buttons=uiconst.OKCANCEL, icon=uiconst.OKCANCEL, minW=360, minH=120, unresizeAble=True)
        if retval is not None:
            if session.stationid:
                eve.Message('CannotSetShieldHarmonicPassword')
            else:
                ship = eveMoniker.GetShipAccess()
                ship.SetShipPassword(retval['name'])

    def Anchor(self, itemID, position):
        item = sm.GetService('michelle').GetItem(itemID)
        if item is None:
            return
        for row in dogma.data.get_type_effects(item.typeID):
            if row.effectID == const.effectAnchorDropForStructures:
                posMgr = eveMoniker.GetPOSMgr()
                posMgr.AnchorStructure(itemID, position)
                break

    def CheckAnchoringPosition(self, itemID, position):
        item = self.michelle.GetItem(itemID)
        if item is None:
            return
        if item.categoryID != const.categoryStarbase:
            raise UserError('CantConfigureThat')
        bp = self.michelle.GetBallpark()
        shipBall = bp.GetBall(session.shipid)
        itemBall = bp.GetBall(itemID)
        if item.groupID == const.groupControlTower:
            actualDistance = bp.GetCenterDist(session.shipid, itemID) - shipBall.radius - itemBall.radius
            if actualDistance > 30000:
                raise UserError('CantConfigureDistant2', {'actual': actualDistance,
                 'needed': 30000})
            self.CheckForStructures(itemID)
        else:
            towerID = self.LocateControlTower(itemID, 'CantAnchorRequireTower')
            self.CheckTowerAvailablility(towerID, itemID)

    def CheckForStructures(self, towerID):
        bp = self.michelle.GetBallpark()
        if bp is None:
            return
        towerItem = self.michelle.GetItem(towerID)
        if towerItem is None:
            return
        typeID = towerItem.typeID
        maxRange = self.godma.GetType(typeID).maxStructureDistance
        self.LogInfo('CheckForStructures', towerID, maxRange)
        for ballID in bp.balls.itervalues():
            if ballID < 0:
                continue
            self.LogInfo('CheckForStructures.iteration', ballID)
            ballItem = self.michelle.GetItem(ballID)
            if ballItem is None:
                continue
            if ballItem.categoryID == const.categoryStarbase:
                ball = bp.GetBall(ballID)
                if not ball.isFree:
                    raise UserError('CantAnchorTowerInvalidStructures', {'typeID': ballItem.typeID})
                self.LogInfo('Anchor ignore', evetypes.GetName(ballItem.typeID))

    def LocateControlTower(self, locusID, raiseError = None):
        bp = self.michelle.GetBallpark()
        if bp is None:
            return
        for ballID in bp.GetBallIdsAndDistInRange(locusID, 300000):
            if ballID < 0:
                continue
            item = self.michelle.GetItem(ballID)
            if item is None or item.groupID != const.groupControlTower:
                continue
            maxDistance = self.godma.GetType(item.typeID).maxStructureDistance
            if bp.DistanceBetween(ballID, locusID) <= maxDistance:
                return ballID

        if raiseError is not None:
            item = self.michelle.GetItem(locusID)
            raise UserError(raiseError, {'itemTypeID': item.typeID})

    def CheckTowerAvailablility(self, towerID, structureID):
        if towerID is None:
            return
        if towerID != structureID:
            if not self.IsStructureFullyOnline(towerID):
                raise UserError('CantTowerNotOnline')

    def IsStructureFullyAnchored(self, itemID):
        slimItem = self.GetSlimItem(itemID)
        if slimItem is None:
            return 0
        if slimItem.posState != pos.STRUCTURE_ANCHORED:
            return 0
        if slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
            if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1

    def IsStructureFullyOnline(self, itemID):
        slimItem = self.GetSlimItem(itemID)
        if slimItem is None:
            return 0
        if not hasattr(slimItem, 'posState'):
            return 0
        if slimItem.posState not in ONLINE_STATES:
            return 0
        if slimItem.posState == pos.STRUCTURE_ONLINING and slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).onliningDelay
            if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1

    def IsStructureFullyUnanchored(self, itemID):
        slimItem = self.GetSlimItem(itemID)
        if slimItem is None:
            return 0
        if slimItem.posState != pos.STRUCTURE_UNANCHORED:
            return 0
        if slimItem.posTimestamp is not None:
            godmaSM = self.godma.GetStateManager()
            delayMs = godmaSM.GetType(slimItem.typeID).unanchoringDelay
            if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                return 0
        return 1

    def CanAnchorStructure(self, itemID):
        return self.IsStructureFullyUnanchored(itemID)

    def CanOnlineStructure(self, itemID, fullyAnchored = None):
        return self.IsStructureFullyAnchored(itemID)

    def CanOfflineStructure(self, itemID, fullyOnline = None):
        return self.IsStructureFullyOnline(itemID)

    def CanUnanchorStructure(self, itemID):
        slimItem = self.GetSlimItem(itemID)
        if slimItem is None:
            return 0
        godmaSM = self.godma.GetStateManager()
        if slimItem.posState == pos.STRUCTURE_ANCHORED:
            if slimItem.posTimestamp is not None:
                delayMs = godmaSM.GetType(slimItem.typeID).anchoringDelay
                if blue.os.GetWallclockTime() - slimItem.posTimestamp < delayMs * 10000:
                    return 0
        elif slimItem.posState in UNANCHORABLE_STATES:
            return 0
        return godmaSM.TypeHasEffect(slimItem.typeID, const.effectAnchorLiftForStructures)

    def StructureIsOrphan(self, itemID):
        item = self.michelle.GetItem(itemID)
        if item is None:
            return False
        if item.categoryID == const.categorySovereigntyStructure:
            return False
        if item.groupID == const.groupControlTower:
            return False
        controlTowerID = item.controlTowerID
        if controlTowerID is None:
            return True
        towerItem = self.michelle.GetItem(controlTowerID)
        if towerItem is None:
            return True
        return False

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::playerOwned')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, ballsToAdd):
        for ball, slimItem in ballsToAdd:
            try:
                if slimItem is None:
                    continue
                if slimItem.categoryID != const.categoryStarbase:
                    continue
                controllerID = slimItem.controllerID
                if controllerID is not None and controllerID == eve.session.shipid:
                    uthread.new(self.RelinquishStructureControl, slimItem)
            except:
                self.LogError('DoBallsAdded - failed to say i have control', (ball, slimItem))
                log.LogTraceback()
                sys.exc_clear()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem is None:
            return
        if slimItem.categoryID != const.categoryStarbase:
            return
        if slimItem.controllerID == eve.session.charid:
            uthread.new(self.RelinquishStructureControl, slimItem, silent=True, force=True)

    def DoSessionChanging(self, isRemote, session, change):
        if 'stationid' in change:
            self.currenttargets = {}
            self.currentcontrol = {}

    def CanAssumeControlStructure(self, structureID):
        item = sm.GetService('michelle').GetItem(structureID)
        if item is None:
            return 0
        for typeAttribute in dogma.data.get_type_attributes(item.typeID):
            if typeAttribute.attributeID == const.attributePosPlayerControlStructure:
                return 1

        return 0

    def AssumeStructureControl(self, slimItem, silent = False, force = False):
        item = sm.GetService('michelle').GetItem(slimItem.itemID) or slimItem
        if item and getattr(item, 'itemID', None) and (item.itemID in self.currentlyAssuming or item.itemID in self.currentcontrol):
            raise UserError('StructureControlled', {'item': (const.UE_TYPEID, item.typeID)})
        if slimItem.posState < pos.STRUCTURE_ONLINING:
            raise UserError('StructureNotControllableUntilOnline', {'item': (const.UE_TYPEID, item.typeID)})
        self.currentlyAssuming[item.itemID] = True
        if item and not item.controllerID or force:
            for typeAttribute in dogma.data.get_type_attributes(item.typeID):
                if typeAttribute.attributeID == const.attributePosPlayerControlStructure:
                    self.currentcontrol[item.itemID] = True
                    if not silent:
                        try:
                            posMgr = eveMoniker.GetPOSMgr()
                            posMgr.AssumeStructureControl(item.itemID)
                        except UserError as e:
                            del self.currentcontrol[item.itemID]
                            self.currentlyAssuming.pop(item.itemID, None)
                            eve.Message(e.msg, e.dict)
                            sys.exc_clear()

                    sm.ScatterEvent('OnAssumeStructureControl', item.itemID)
                    break

        self.currentlyAssuming.pop(item.itemID, None)

    def RelinquishStructureControl(self, slimItem, silent = False, force = False):
        item = sm.GetService('michelle').GetItem(slimItem.itemID) or slimItem
        if item and item.controllerID or force:
            for typeAttribute in dogma.data.get_type_attributes(item.typeID):
                if typeAttribute.attributeID == const.attributePosPlayerControlStructure:
                    if self.currentcontrol.has_key(item.itemID):
                        del self.currentcontrol[item.itemID]
                    if self.currenttargets.has_key(item.itemID):
                        del self.currenttargets[item.itemID]
                    if not silent:
                        try:
                            posMgr = eveMoniker.GetPOSMgr()
                            posMgr.RelinquishStructureControl(item.itemID)
                        except UserError as e:
                            eve.Message(e.msg, e.dict)
                            sys.exc_clear()

                    sm.ScatterEvent('OnRelinquishStructureControl', item.itemID)
                    break

    def UnlockStructureTarget(self, structureID):
        if self.currenttargets.has_key(structureID):
            sm.GetService('pwntarget').UnLockTargetOBO(structureID, self.currenttargets[structureID])
            del self.currenttargets[structureID]

    def GetControllerIDName(self, itemID):
        slimItem = self.GetSlimItem(itemID)
        if slimItem is None:
            return (0, '')
        controller = getattr(slimItem, 'controllerID', 0)
        if controller:
            ct = cfg.eveowners.Get(controller).name
        else:
            ct = localization.GetByLabel('UI/Generic/NotAvailableShort')
            if self.currenttargets.has_key(itemID):
                del self.currenttargets[itemID]
        return (controller, ct)

    def GetDogmaLM(self):
        return self.godma.GetStateManager().GetDogmaLM()

    def OnTargetOBO(self, what, sid = None, tid = None, reason = None):
        if what == 'add':
            self.currenttargets[sid] = tid
        elif what == 'lost':
            if self.currenttargets.has_key(sid):
                del self.currenttargets[sid]

    def ClrCurrentTarget(self, structureID = None):
        if structureID and self.currenttargets.has_key(structureID):
            del self.currenttargets[structureID]
            del self.currentcontrol[structureID]
        elif structureID is None:
            self.currenttargets = {}
            self.currentcontrol = {}

    def GetCurrentTarget(self, structureID = None):
        if structureID is None:
            return self.currenttargets
        return self.currenttargets.get(structureID, None)

    def GetCurrentControl(self, structureID = None):
        if structureID is None:
            return self.currentcontrol
        return self.currentcontrol.get(structureID, None)

    def GetSlimItem(self, itemID):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        slimItem = bp.GetInvItem(itemID)
        return slimItem

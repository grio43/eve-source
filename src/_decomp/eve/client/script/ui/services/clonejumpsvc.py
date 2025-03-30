#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\clonejumpsvc.py
import logging
import sys
import carbonui.const as uiconst
import eve.common.lib.appConst as const
import localization
import uthread2
from carbon.common.script.net.moniker import Moniker
from carbon.common.script.sys.service import Service
from eve.common.script.sys import eveCfg
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions import ExceptionEater, UserError
from inventorycommon.typeHelpers import GetAveragePrice
from menucheckers import SessionChecker
import blue
log = logging.getLogger(__name__)

class CloneJump(Service):
    __exportedcalls__ = {'GetClones': [],
     'GetCloneImplants': [],
     'GetShipClones': [],
     'GetStationClones': [],
     'HasCloneReceivingBay': [],
     'GetCloneAtLocation': [],
     'GetImplantsForClone': [],
     'DestroyInstalledClone': [],
     'CloneJump': [],
     'OfferShipCloneInstallation': [],
     'LastCloneJumpTime': [],
     'ValidateInstallJumpClone': []}
    __guid__ = 'svc.clonejump'
    __displayname__ = 'Clone Jump Service'
    __notifyevents__ = ['OnShipJumpCloneInstallationOffered',
     'OnShipJumpCloneInstallationDone',
     'OnJumpCloneCacheInvalidated',
     'OnShipJumpCloneCacheInvalidated',
     'OnStationJumpCloneCacheInvalidated',
     'OnShipJumpCloneInstallationCanceled',
     'OnSessionReset',
     'OnSessionChanged']
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        self.Initialize()

    def Initialize(self):
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.shipJustClonesShipID = None
        self.shipJumpClones = None
        self.timeLastJump = None
        self.stationJumpClones = None
        self.cloneInstallOfferActive = 0
        self.lastCloneJumpTime = None
        self.clonejumpCheck = None
        self.cloneJumpingFromShip = False

    def GetClones(self):
        self.GetCloneState()
        return self.jumpClones

    def GetCloneImplants(self):
        self.GetCloneState()
        return self.jumpCloneImplants

    def SetJumpCloneName(self, cloneID, newName):
        lm = self.GetLM()
        lm.SetJumpCloneName(cloneID, newName)

    def GetLM(self):
        if session.solarsystemid or session.structureid:
            return Moniker('jumpCloneSvc', (session.solarsystemid, const.groupSolarSystem))
        else:
            return Moniker('jumpCloneSvc', (session.stationid, const.groupStation))

    def GetCloneState(self):
        if self.jumpClones is None:
            lm = self.GetLM()
            kv = lm.GetCloneState()
            self.jumpClones = kv.clones
            self.jumpCloneImplants = kv.implants
            self.timeLastJump = kv.timeLastJump

    def GetShipClones(self):
        shipID = eveCfg.GetActiveShip()
        if not self.shipJumpClones or shipID != self.shipJustClonesShipID:
            lm = self.GetLM()
            self.shipJustClonesShipID = shipID
            self.shipJumpClones = lm.GetShipCloneState()
        return self.shipJumpClones

    def GetStationClones(self):
        if not self.stationJumpClones:
            lm = self.GetLM()
            self.stationJumpClones = lm.GetStationCloneState()
        return self.stationJumpClones

    def GetNumClonesInPilotsStructure(self):
        if session.structureid != session.shipid:
            return
        return self.GetLM().GetNumClonesInPilotsStructure()

    def OfferShipCloneInstallation(self, charID):
        lm = self.GetLM()
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/WaitingForAck'), localization.GetByLabel('UI/CloneJump/InstallationInviteSent', player=charID), 1, 2, abortFunc=self.CancelShipCloneInstallation)
        try:
            lm.OfferShipCloneInstallation(charID)
        except UserError as e:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
            raise

    def LastCloneJumpTime(self):
        self.GetCloneState()
        return self.timeLastJump

    def DestroyInstalledClone(self, cloneID):
        message = None
        clonePrice = self.GetPriceForClone(cloneID)
        myClones = self.GetClones()
        if myClones:
            myClones = myClones.Index('jumpCloneID')
            if cloneID in myClones:
                if myClones[cloneID].locationID == session.stationid:
                    message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneAtCurrentStation')
                else:
                    cfg.evelocations.Prime([myClones[cloneID].locationID])
                    message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneAtSomewhereElse', location=myClones[cloneID].locationID)
                if clonePrice:
                    cloneText = localization.GetByLabel('UI/CloneJump/EstimatedClonePrice', iskValue=clonePrice)
                    message = '%s<br>%s' % (message, cloneText)
        if not message:
            if eveCfg.GetActiveShip():
                shipClones = self.GetShipClones()
                if shipClones:
                    shipClones = shipClones.Index('jumpCloneID')
                    if cloneID in shipClones:
                        cfg.eveowners.Prime([shipClones[cloneID].ownerID])
                        cfg.evelocations.Prime([shipClones[cloneID].locationID])
                        message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneInShip', owner=shipClones[cloneID].ownerID, ship=shipClones[cloneID].locationID)
                        if clonePrice:
                            cloneText = localization.GetByLabel('UI/CloneJump/EstimatedClonePrice', iskValue=clonePrice)
                            message = '%s<br>%s' % (message, cloneText)
        if not message:
            return
        ret = eve.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            lm = self.GetLM()
            lm.DestroyInstalledClone(cloneID)

    def InstallCloneInStation(self):
        if not self.CanJumpCloneFromCurrentLocation():
            return
        lm = self.GetLM()
        cost = lm.GetPriceForClone()
        if cost > 0.0:
            response = eve.Message('AskAcceptJumpCloneCost', {'cost': cost}, uiconst.YESNO)
            if response != uiconst.ID_YES:
                return
        if session.stationid:
            lm.InstallCloneInStation()
        else:
            lm.InstallCloneInStructure()

    def CancelShipCloneInstallation(self, *args):
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
        lm = self.GetLM()
        lm.CancelShipCloneInstallation()

    def CanJumpCloneFromCurrentLocation(self):
        if session.stationid:
            return True
        if session.structureid:
            return True
        return False

    def ActivateCloneJumpCheck(self, cloneJumpCheck):
        self.clonejumpCheck = cloneJumpCheck

    def DeactivateCloneJumpCheck(self):
        self.clonejumpCheck = None

    def CheckCloneJump(self):
        if not callable(self.clonejumpCheck):
            return True
        return self.clonejumpCheck()

    def CloneJump(self, destLocationID, cloneID):
        if not self.CanJumpCloneFromCurrentLocation():
            eve.Message('NotAtStation')
            return
        if not self.CheckCloneJump():
            return
        lm = self.GetLM()
        cost = lm.GetPriceForClone()
        if cost > 0.0:
            response = eve.Message('AskAcceptJumpCloneCost', {'cost': cost}, uiconst.YESNO)
            if response != uiconst.ID_YES:
                return
        checker = SessionChecker(session, sm)
        inCapsule = checker.IsPilotInCapsule()
        if inCapsule and not GetJumpDelay():
            self._CloneJump(destLocationID, cloneID, cost)
        else:
            uthread2.start_tasklet(self.UnboardShipAndCloneJump_thread, destLocationID, cloneID, cost, inCapsule)

    def _CloneJump(self, destLocationID, cloneID, cost):
        self.cloneJumpingFromShip = None
        lm = self.GetLM()
        try:
            sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, cloneID, cost, False)
            sm.GetService('infoPanel').UpdateSessionTimer()
        except UserError as e:
            if e.msg not in ('JumpCheckWillLoseExistingClone', 'JumpCheckIntoShip', 'JumpCheckIntoStructure'):
                sm.ScatterEvent('OnCloneJumpUpdate')
                raise e
            if eve.Message(e.msg, e.dict, uiconst.YESNO) == uiconst.ID_YES:
                eve.session.ResetSessionChangeTimer('Retrying with confirmation approval')
                sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, cloneID, cost, True)
                sm.GetService('infoPanel').UpdateSessionTimer()
            else:
                sm.ScatterEvent('OnCloneJumpUpdate')
            sys.exc_clear()

    def UnboardShipAndCloneJump_thread(self, destLocationID, cloneID, cost, inCapsule = False):
        if self.cloneJumpingFromShip:
            return
        eve.Message('StartingCloneJumping')
        shipID = session.shipid
        ship = sm.GetService('godma').GetItem(shipID)
        self.cloneJumpingFromShip = (shipID, cloneID)
        if blue.os.GetSimTime() < session.nextSessionChange:
            sm.ScatterEvent('OnCloneJumpUpdate')
        while blue.os.GetSimTime() < session.nextSessionChange:
            blue.synchro.Yield()

        if not self.cloneJumpingFromShip or self.cloneJumpingFromShip[0] != shipID:
            sm.ScatterEvent('OnCloneJumpUpdate')
            return
        if not inCapsule:
            eve.Message('DisembarkingFromShip')
            sm.GetService('station').TryLeaveShip(ship)
        jumpDelay = GetJumpDelay()
        uthread2.Sleep(jumpDelay)
        while blue.os.GetSimTime() < session.nextSessionChange:
            blue.synchro.Yield()

        if self.cloneJumpingFromShip and self.cloneJumpingFromShip[0] == shipID:
            self._CloneJump(destLocationID, cloneID, cost)
        else:
            sm.ScatterEvent('OnCloneJumpUpdate')

    def GetCloneAtLocation(self, locationID):
        clones = self.GetClones()
        if clones:
            for c in clones:
                if locationID == c.locationID:
                    return (c.jumpCloneID, c.cloneName)

        return (None, None)

    def GetImplantsForClone(self, cloneID):
        cloneImplants = self.GetCloneImplants()
        if not cloneImplants:
            return []
        implantsByCloneID = cloneImplants.Filter('jumpCloneID')
        return implantsByCloneID.get(cloneID, [])

    def GetPriceForClone(self, cloneID):
        typeIDs = [ x for x in self.GetImplantsForClone(cloneID) ]
        if not typeIDs:
            return 0
        implantCost = sum((GetAveragePrice(x.typeID) or 0 for x in typeIDs))
        return implantCost

    def HasCloneReceivingBay(self):
        if eve.session.shipid:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            for module in ship.modules:
                if const.typeCloneVatBayI == module.typeID:
                    return True

        return False

    def OnJumpCloneCacheInvalidated(self):
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.timeLastJump = None
        sm.ScatterEvent('OnCloneJumpUpdate')

    def OnShipJumpCloneCacheInvalidated(self, locationID, charID):
        if eveCfg.GetActiveShip() == locationID:
            self.shipJumpClones = None
            sm.ScatterEvent('OnShipCloneJumpUpdate')

    def OnStationJumpCloneCacheInvalidated(self, locationID, charID):
        if session.stationid == locationID:
            self.stationJumpClones = None
            sm.ScatterEvent('OnCloneJumpUpdate')

    def OnShipJumpCloneInstallationOffered(self, args):
        offeringCharID, targetCharID, shipID, b = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 1
        cfg.eveowners.Prime([offeringCharID, targetCharID])
        offeringChar = cfg.eveowners.Get(offeringCharID)
        cfg.evelocations.Prime([shipID])
        ship = cfg.evelocations.Get(shipID)
        lm = self.GetLM()
        costs = lm.GetPriceForClone()
        ret = eve.Message('JumpCloneInstallationOffered', {'offerer': offeringChar.name,
         'shipname': ship.name,
         'costs': FmtISK(costs)}, uiconst.YESNO)
        try:
            if ret == uiconst.ID_YES:
                lm.AcceptShipCloneInstallation()
            elif ret != uiconst.ID_CLOSE:
                lm.CancelShipCloneInstallation()
        except UserError as e:
            eve.Message(e.msg, e.dict)
            sys.exc_clear()

        self.cloneInstallOfferActive = 0

    def OnShipJumpCloneInstallationDone(self, args):
        offeringCharID, targetCharID, shipID, b = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 0
        sm.ScatterEvent('OnShipJumpCloneUpdate')
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallFinished'), '', 1, 1)

    def OnShipJumpCloneInstallationCanceled(self, args):
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
            lm = self.GetLM()
            lm.CancelShipCloneInstallation()
        except UserError as e:
            self.LogInfo('Ignoring usererror', e.msg, 'while cancelling ship clone installation')
            sys.exc_clear()

    def OnSessionReset(self):
        self.Initialize()

    def OnSessionChanged(self, isRemote, session, change):
        if not self.cloneJumpingFromShip:
            return
        if len(change) == 1 and 'shipid' in change:
            oldShipID, newShipID = change['shipid']
            if oldShipID == self.cloneJumpingFromShip[0]:
                checker = SessionChecker(session, sm)
                if checker.IsPilotInCapsule():
                    return
        eve.Message('CloneJumpingCancelled')
        self.cloneJumpingFromShip = None

    def IsCloneJumping(self):
        return bool(self.cloneJumpingFromShip)

    def IsJumpingIntoClone(self, cloneID):
        if not self.IsCloneJumping():
            return False
        if self.cloneJumpingFromShip[1] == cloneID:
            return True
        return False

    def ValidateInstallJumpClone(self):
        try:
            error_labels = self.GetLM().ValidateInstallJumpClone()
        except Exception:
            log.exception('Unknown error caught during clone install validation')
            sys.exc_clear()
            error_labels = ['UI/Medical/Errors/UnknownValidationError']

        errors = []
        for label in error_labels:
            if isinstance(label, basestring):
                errors.append(localization.GetByLabel(label))
            else:
                with ExceptionEater():
                    label, args = label
                    errors.append(localization.GetByLabel(label, **args))

        return errors


def GetJumpDelay():
    jumpDelay = 0
    if session and session.nextSessionChange:
        duration = session.nextSessionChange - blue.os.GetSimTime()
        if duration > 0:
            jumpDelay = duration / const.SEC + 1
    return jumpDelay

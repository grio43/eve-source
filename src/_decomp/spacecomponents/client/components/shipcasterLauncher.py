#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\shipcasterLauncher.py
import logging
import trinity
import gametime
from carbon.common.lib.const import SEC, maxBigint
from eve.common.lib.appConst import factionAngelCartel, factionGuristasPirates
from shipcaster.landingPadUtil import GetMaxLandingPadLinks
from spacecomponents.client.ui.shipcaster.bracket import ShipcasterBracket
from carbon.common.script.util.format import FmtDate
from shipcaster.shipcasterConst import SHIPCASTER_SLIM_LINKED_TARGETS_ATTRIBUTE, CYCLE_IDLE_DURATION_SECONDS, CYCLE_TARGET_DURATION_SECONDS, SHIPCASTER_VFX_POWER_DOWN_DURATION
from spacecomponents import Component
from spacecomponents.client import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE, MSG_ON_LOAD_OBJECT
logger = logging.getLogger(__name__)

class ShipcasterLauncher(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self._activeTarget = None
        self._isIdle = None
        self._targetTimings = []
        self._lastPortalEndTime = None
        self._bracket_ui = None
        self._model = None
        self._itemID = itemID
        self._activationState = 2.0
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_LOAD_OBJECT, self.OnLoadObject)
        self.SubscribeToMessage(MSG_ON_SLIM_ITEM_UPDATED, self.OnSlimItemUpdated)

    @property
    def factionID(self):
        return self.attributes.factionID

    @property
    def extraLinkedFactionIDs(self):
        return tuple(self.attributes.extraLinkedFactionIDs or ())

    @property
    def validFactionIDsForUse(self):
        return (self.factionID,) + self.extraLinkedFactionIDs

    @property
    def targetSolarsystemID(self):
        if self._activeTarget is not None:
            return self._activeTarget[0]

    @property
    def nextTargetSolarsystemID(self):
        if self.targetSolarsystemID:
            return self.targetSolarsystemID
        if len(self._targetTimings):
            firstTargetInfo = self._targetTimings[0]
            if firstTargetInfo[0]:
                return firstTargetInfo[0][0]

    @property
    def nextTargetFactionID(self):
        if self._activeTarget is not None:
            return self._activeTarget[2]
        if len(self._targetTimings):
            firstTargetInfo = self._targetTimings[0]
            if firstTargetInfo[0]:
                return firstTargetInfo[0][2]

    @property
    def targetLandingPadID(self):
        if self._activeTarget is not None:
            return self._activeTarget[1]

    @property
    def numLinkedTargets(self):
        return len([ t for t in self._targetTimings if t[0] ])

    def OnAddedToSpace(self, slimItem):
        if self._bracket_ui is None:
            self._bracket_ui = ShipcasterBracket(slimItem.itemID, slimItem.typeID)

    def ReloadUI(self):
        if self._bracket_ui:
            self._bracket_ui.close()
            self._bracket_ui = None
        slimItem = sm.GetService('michelle').GetItem(self.itemID)
        self._bracket_ui = ShipcasterBracket(slimItem.itemID, slimItem.typeID)

    def _GetElapsedTime(self):
        elapsedTime = 0
        if self._isIdle and self._targetTimings[0][0] is not None:
            idlePhaseEndTime = self._targetTimings[0][1]
            elapsedTime = CYCLE_IDLE_DURATION_SECONDS - abs(idlePhaseEndTime - gametime.GetWallclockTime()) / SEC
        elif self._activeTarget is not None:
            targetPhaseStartTime = self._targetTimings[0][1]
            elapsedTime = gametime.GetWallclockTime() - targetPhaseStartTime
            elapsedTime = elapsedTime / SEC
        return elapsedTime

    def OnLoadObject(self, ball):
        trinity.WaitForResourceLoads()
        self._model = ball.model
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        slimItem = bp.GetInvItem(self._itemID)
        if slimItem is not None:
            self._ConfigureBaseModel(slimItem)
            self._OnTargetStateChanged()
        if self._model is not None:
            self._model.StartControllers()

    def _ConfigureBaseModel(self, slimItem):
        if self._model is not None:
            newTargetTimings = getattr(slimItem, SHIPCASTER_SLIM_LINKED_TARGETS_ATTRIBUTE, None)
            if newTargetTimings is not None:
                self._ConfigureTimings(newTargetTimings)
            if self._activeTarget is not None:
                self._model.SetControllerVariable('elapsedTime', float(self._GetElapsedTime()))
                self._model.SetControllerVariable('powerUpTimer', CYCLE_IDLE_DURATION_SECONDS)
            else:
                now = gametime.GetWallclockTime()
                nextStartTiming = maxBigint
                for each in self._targetTimings:
                    if each[0] is not None and each[1] > now:
                        if each[1] < nextStartTiming:
                            nextStartTiming = each[1]

                if nextStartTiming < maxBigint:
                    fillPhaseDuration = (nextStartTiming - now) / SEC
                    self._model.SetControllerVariable('powerUpTimer', float(fillPhaseDuration))
                    self._model.SetControllerVariable('elapsedTime', -1 * SHIPCASTER_VFX_POWER_DOWN_DURATION)
            self._model.SetControllerVariable('portalDuration', CYCLE_TARGET_DURATION_SECONDS)

    def OnSlimItemUpdated(self, slimItem):
        if self._model is None:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return
            ball = bp.GetBall(slimItem.itemID)
            if ball is not None:
                self._model = ball.model
            if self._model is not None:
                self._ConfigureBaseModel(slimItem)
        if self._model is not None:
            newTargetTimings = getattr(slimItem, SHIPCASTER_SLIM_LINKED_TARGETS_ATTRIBUTE, None)
            self._ConfigureTimings(newTargetTimings)
            self._OnTargetStateChanged()

    def _ConfigureTimings(self, newTargetTimings):
        if newTargetTimings is None:
            return
        now = gametime.GetWallclockTime()
        for target, startTime, endTime in newTargetTimings:
            if startTime < now < endTime:
                newActiveTarget = target
                newIsIdle = False
                break
        else:
            newActiveTarget = None
            newIsIdle = True

        if self._targetTimings == newTargetTimings and self._activeTarget == newActiveTarget and self._isIdle == newIsIdle:
            return
        if self._activeTarget is not None and newActiveTarget is None:
            self._lastPortalEndTime = gametime.GetWallclockTime()
        self._targetTimings = newTargetTimings
        self._activeTarget = newActiveTarget
        self._isIdle = newIsIdle

    def _OnTargetStateChanged(self):
        maxLandingPadLinks = GetMaxLandingPadLinks(self.typeID)
        logger.debug('Shipcaster %s _OnTargetStateChanged - isIdlePhase %s - numLinkedTargets %s/%s - targetSolarsystem %s - targetLandingPad %s', self.itemID, self._isIdle, self.numLinkedTargets, maxLandingPadLinks, self.targetSolarsystemID, self.targetLandingPadID)
        if self._isIdle and self._targetTimings[0][0] is not None:
            idlePhaseEndTime = self._targetTimings[0][1]
            idlePhaseStartTime = idlePhaseEndTime - CYCLE_IDLE_DURATION_SECONDS * SEC
            self._activationState = 2.0
            logger.debug('Shipcaster %s _OnTargetStateChanged - WARMUP from %s to %s', self.itemID, FmtDate(idlePhaseStartTime, 'sl'), FmtDate(idlePhaseEndTime, 'sl'))
        elif self._activeTarget is not None:
            targetPhaseStartTime = self._targetTimings[0][1]
            targetPhaseEndTime = self._targetTimings[0][2]
            self._activationState = 2.0
            logger.debug('Shipcaster %s _OnTargetStateChanged - TARGET from %s to %s', self.itemID, FmtDate(targetPhaseStartTime, 'sl'), FmtDate(targetPhaseEndTime, 'sl'))
        else:
            logger.debug('Shipcaster %s _OnTargetStateChanged - No current/next target', self.itemID)
            self._activationState = 0.0
        self._ConfigurePortalControllerState()
        sm.ScatterEvent('OnShipcasterTargetStateChanged', self.itemID)

    def _ConfigurePortalControllerState(self):
        if self._targetTimings is None:
            return
        if self._model is None:
            pass
        nextStartTiming = maxBigint
        now = gametime.GetWallclockTime()
        for each in self._targetTimings:
            if each[0] is not None and each[1] > now:
                if each[1] < nextStartTiming:
                    nextStartTiming = each[1]

        if self._lastPortalEndTime is not None:
            fillPhaseDuration = (nextStartTiming - self._lastPortalEndTime) / SEC
            self._model.SetControllerVariable('powerUpTimer', float(fillPhaseDuration + 1.5))
        if self._activeTarget is not None:
            self._model.SetControllerVariable('isPortalActive', 1.0)
        else:
            self._model.SetControllerVariable('isPortalActive', 0.0)
        self._model.SetControllerVariable('ActivationState', self._activationState)
        destination = self.GetCasterDestination()
        self._model.SetControllerVariable('Destination', destination)

    def CanCharacterJump(self, characterFactionID):
        if self.targetSolarsystemID is None:
            return False
        if characterFactionID not in self.validFactionIDsForUse:
            return False
        if characterFactionID != self.nextTargetFactionID:
            return False
        return True

    def IsCharging(self):
        if self._isIdle and self.nextTargetSolarsystemID:
            return True
        return False

    def GetTargetSystemAndTimingsForSlot(self, slotIdx):
        noResult = (None, None, None)
        numTargetTimings = len(self._targetTimings)
        if not numTargetTimings or numTargetTimings <= slotIdx:
            return noResult
        targetInfo = self._targetTimings[slotIdx]
        if not targetInfo or targetInfo[0] is None:
            return noResult
        return (targetInfo[0][0], targetInfo[1], targetInfo[2])

    def GetCasterDestination(self):
        destination = 0.0
        if self._activeTarget is not None and len(self._activeTarget) > 2:
            destinationFactionOwner = self._activeTarget[2]
            if destinationFactionOwner == factionAngelCartel:
                destination = 1.0
            if destinationFactionOwner == factionGuristasPirates:
                destination = 2.0
        return destination

    def OnRemovedFromSpace(self):
        if self._bracket_ui:
            self._bracket_ui.close()
            self._bracket_ui = None

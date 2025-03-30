#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\voidspace\client\void_space_activation_controller.py
import abc
import itertools
import blue
import eveexceptions
import evetypes
import localization
import signals
import uthread
from eve.client.script.ui.crimewatch import crimewatchConst
from evewar.warText import FmtDate
from voidspace.common.constants import VOID_SPACE_ENCOUNTER_LIFE_TIME, ACTIVATION_ERROR_DELAY
from voidspace.common.error import get_error_label, VoidSpaceJumpError
from voidspace.common.fsd_loaders import get_void_space_encounter_static_data

class VoidSpaceActivationController(object):
    __metaclass__ = abc.ABCMeta
    __notifyevents__ = ['OnAddFX',
     'OnPvpTimerUpdate',
     'OnInvulnCancelled',
     'OnInvulunOnUndockingUpdated',
     'OnRemoveFX',
     'OnRestoringInvulnUpdated',
     'OnSafetyLevelChanged',
     'OnSessionChanged',
     'OnSlimItemChange',
     'OnClientEvent_WarpStarted',
     'OnClientEvent_WarpFinished',
     'ProcessActiveShipChanged',
     'OnMatchFound',
     'OnMatchMakingFailure']
    _monitoredEffects = ('effects.Cloak', 'effects.CloakingCovertOps', 'effects.CloakingPrototype', 'effects.CloakingWarpSafe', 'effects.CloakNoAmim', 'effects.Tethering', 'effects.Uncloak')

    def __init__(self, item, validator):
        self._errors = None
        self._isFinished = False
        self._lockButton = False
        self._isActivating = False
        self._itemID = item.itemID
        self._typeID = item.typeID
        self._sessionChangeThread = None
        self._validator = validator
        self.onChange = signals.Signal(signalName='onChange')
        sm.RegisterNotify(self)
        self._service = sm.GetService('voidSpaceSvc')

    @property
    def errors(self):
        if self._errors is None:
            self.Validate()
        return self._errors

    @property
    def displayed_errors(self):
        result = []
        for error, errorArgs in set(itertools.islice(self.errors, 5)):
            result.append(get_error_label(localization.GetByLabel, error, *errorArgs))

        return result

    @property
    def itemID(self):
        return self._itemID

    @property
    def typeID(self):
        return self._typeID

    @property
    def name(self):
        return evetypes.GetName(self._typeID)

    @property
    def typeDescription(self):
        return localization.GetByMessageID(self.GetEncounterStaticData().encounterDescriptionID)

    @property
    def shipRestrictionDescription(self):
        return localization.GetByMessageID(self.GetEncounterStaticData().shipRestrictionsDescriptionID)

    @property
    def shipRestrictionTitle(self):
        return localization.GetByLabel('UI/RandomJump/ShipRestriction')

    @property
    def traceDescriptionTitle(self):
        return localization.GetByMessageID(self.GetEncounterStaticData().traceDescriptionTitleID)

    @property
    def traceDescription(self):
        return localization.GetByMessageID(self.GetEncounterStaticData().traceDescriptionID)

    @property
    def killTimerDescription(self):
        color = crimewatchConst.Colors.Red.GetHex()
        time = FmtDate(VOID_SPACE_ENCOUNTER_LIFE_TIME)
        return localization.GetByLabel('UI/VoidSpace/Encounter/timerDescription', color=color, time=time)

    @property
    def isFinished(self):
        return self._isFinished

    @property
    def isActivating(self):
        return self._isActivating

    @property
    def isReady(self):
        return not self._lockButton and not self.isActivating and not self.isFinished and not self._sessionChangeThread

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/PVPFilament/Activating')
        else:
            return localization.GetByLabel('UI/Abyss/Activate')

    def GetEncounterStaticData(self):
        return get_void_space_encounter_static_data(self.typeID)

    def _Validate(self):
        self._validator.validate_jump()

    def Validate(self):
        self._errors, existing = [], self._errors
        try:
            self._Validate()
        except VoidSpaceJumpError as error:
            self._errors = error.errors
        except eveexceptions.UserError:
            raise
        except Exception:
            self._errors.append((VoidSpaceJumpError.UNKNOWN_ERROR, ()))
            raise

        if any((error == VoidSpaceJumpError.SESSION_CHANGE_IN_PROGRESS for error, args in self._errors)):
            self.ValidateOnNextSessionChange()
        if existing != self._errors:
            self.onChange()

    def _RequestVoidSpaceJump(self):
        sm.GetService('sessionMgr').PerformSessionChange('VoidSpaceJump', sm.GetService('voidSpaceSvc').VoidSpaceJump, self.itemID, self.typeID)
        self._isFinished = True

    def RequestVoidSpaceJump(self):
        if not self.isReady:
            return
        try:
            self._errors = []
            self._isActivating = True
            self.onChange()
            activateTasklet = uthread.newJoinable(self._RequestVoidSpaceJump)
            uthread.waitForJoinable(activateTasklet, timeout=None)
        except eveexceptions.UserError as error:
            if error.msg == 'VoidSpaceJumpError':
                self._errors = error.dict['errors']
            else:
                raise
        except Exception:
            self._errors = [(VoidSpaceJumpError.UNKNOWN_ERROR, ())]
            raise
        finally:
            uthread.new(self._lockButtonThread)
            self.onChange()

    def Close(self):
        sm.UnregisterNotify(self)
        self.onChange.clear()

    def OnAddFX(self, effectGuid, ballID):
        if ballID == session.shipid and effectGuid in self._monitoredEffects:
            if effectGuid == 'effects.Cloak':
                self._validator.set_cloaking(True)
            self.Validate()

    def OnInvulnCancelled(self, shipID):
        if shipID == session.shipid:
            self._validator.set_invulnerable(False)
            self.Validate()

    def OnInvulunOnUndockingUpdated(self, shipID, endTime, duration):
        if shipID == session.shipid:
            self._validator.set_invulnerable(True)
            self.Validate()

    def OnPvpTimerUpdate(self, state, expiryTime):
        self.Validate()

    def OnRemoveFX(self, effectGuid, ballID):
        if ballID == session.shipid and effectGuid in self._monitoredEffects:
            if effectGuid == 'effects.Cloak':
                self._validator.set_cloaking(False)
            self.Validate()

    def OnRestoringInvulnUpdated(self, shipID, endTime, duration):
        if shipID == session.shipid:
            self._validator.set_invulnerable(True)
            self.Validate()

    def OnSafetyLevelChanged(self, safetyLevel):
        self.Validate()

    def OnSessionChanged(self, isRemote, session, change):
        if any((x in change for x in ('structureid', 'stationid'))):
            self._isFinished = True
        self.Validate()
        if session.nextSessionChange is not None and not self.isFinished:
            self.ValidateOnNextSessionChange()

    def OnClientEvent_WarpStarted(self, *args):
        self.Validate()

    def OnClientEvent_WarpFinished(self, *args):
        self.Validate()

    def _lockButtonThread(self):
        self._lockButton = True
        blue.synchro.Sleep(ACTIVATION_ERROR_DELAY)
        self._isActivating = False
        self._lockButton = False
        self.onChange()

    def ValidateOnNextSessionChange(self):
        if self._sessionChangeThread is not None:
            return
        self._sessionChangeThread = uthread.new(self._ValidateOnNextSessionChange)

    def _ValidateOnNextSessionChange(self):
        while blue.os.GetSimTime() < session.nextSessionChange:
            blue.synchro.Yield()

        self._sessionChangeThread = None
        self.Validate()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.Validate()

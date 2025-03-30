#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\pvpFilaments\client\activation_window\pvpFilamentController.py
import abc
import itertools
import blue
import eveexceptions
import evetypes
import localization
import signals
import uthread
from dogma.const import attributeMicroJumpPortalMaxShipCandidates
from eve.client.script.ui.crimewatch import crimewatchConst
from evewar.warText import FmtDate
from pvpFilaments import PVPJumpError, get_error_label
from pvpFilaments.common.constants import ACTIVATION_ERROR_DELAY, DEFAULT_PVP_CONTENT_DURATION

class PVPFilamentActivationController(object):
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
        self._isInQueue = False
        self._lockButton = False
        self._queueTimer = 0
        self._estimatedQueueTime = 0
        self._isActivating = False
        self._itemID = item.itemID
        self._typeID = item.typeID
        self._sessionChangeThread = None
        self._validator = validator
        self.onChange = signals.Signal(signalName='onChange')
        sm.RegisterNotify(self)
        self._service = sm.GetService('pvpFilamentSvc')
        self._eventInfo = None

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
        return localization.GetByMessageID(self.GetActiveEventInfo().filamentDescriptionID)

    @property
    def shipRestrictionDescription(self):
        return localization.GetByMessageID(self.GetActiveEventInfo().restrictionsDescriptionID)

    @property
    def is_event_active(self):
        return self._service.isEventActive(self._typeID)

    @property
    def inActiveText(self):
        return u'<center>{}</center>'.format(localization.GetByLabel('UI/PVPFilament/provingGroundsInActive'))

    @property
    def shipRestrictionTitle(self):
        return localization.GetByLabel('UI/RandomJump/ShipRestriction')

    @property
    def traceRestrictionTitle(self):
        return localization.GetByLabel('UI/PVPFilament/traceRestrictionTitle')

    @property
    def traceRestrictionDescription(self):
        return localization.GetByLabel('UI/PVPFilament/traceRestrictionDescription')

    @property
    def killTimerDescription(self):
        color = crimewatchConst.Colors.Red.GetHex()
        time = FmtDate(DEFAULT_PVP_CONTENT_DURATION)
        return localization.GetByLabel('UI/Abyss/TimerDescription', color=color, time=time)

    @property
    def isFinished(self):
        return self._isFinished

    @property
    def isActivating(self):
        return self._isActivating

    @property
    def isInQueue(self):
        return self._isInQueue

    @property
    def isReady(self):
        return not self._lockButton and not self.isActivating and not self.isFinished and not self._sessionChangeThread

    @property
    def timeInQueue(self):
        seconds = long(blue.os.GetWallclockTime() - self._queueTimer)
        return localization.formatters.FormatTimeIntervalShortWritten(seconds, showFrom='day', showTo='second')

    @property
    def estimatedQueueTime(self):
        if self._estimatedQueueTime < 1:
            return localization.GetByLabel('UI/PVPFilament/estimatedTimeUnknown')
        return localization.formatters.FormatTimeIntervalShortWritten(long(self._estimatedQueueTime), showFrom='day', showTo='second')

    @property
    def estimatedQueueTimeTitle(self):
        return localization.GetByLabel('UI/PVPFilament/estimatedQueueTimeTitle')

    @property
    def timeInqueueLabel(self):
        return localization.GetByLabel('UI/PVPFilament/timeInqueue')

    @property
    def estimatedTimeLabel(self):
        return localization.GetByLabel('UI/PVPFilament/estimatedTime')

    @property
    def provingGroundsHint(self):
        return localization.GetByLabel('UI/PVPFilament/provingGroundsHint')

    def GetActiveEventInfo(self):
        if self._eventInfo is None:
            self._eventInfo = self._service.GetActiveEventByTypeID(self._typeID)
        return self._eventInfo

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/PVPFilament/Activating')
        elif self.isInQueue:
            return localization.GetByLabel('UI/PVPFilament/LeaveQueue')
        else:
            return localization.GetByLabel('UI/Abyss/Activate')

    def _Validate(self):
        self._validator.validate_jump()

    def Validate(self):
        if self.isInQueue:
            return
        self._errors, existing = [], self._errors
        try:
            self._Validate()
        except PVPJumpError as error:
            self._errors = error.errors
        except eveexceptions.UserError:
            raise
        except Exception:
            self._errors.append((PVPJumpError.UNKNOWN_ERROR, ()))
            raise

        if any((error == PVPJumpError.SESSION_CHANGE_IN_PROGRESS for error, args in self._errors)):
            self.ValidateOnNextSessionChange()
        if existing != self._errors:
            self.onChange()

    def _JoinQueue(self):
        estimatedQueueTime = self._service.RequestToJoinPVPQueue(self.itemID, self.typeID)
        self._isInQueue = True
        self._estimatedQueueTime = estimatedQueueTime
        self._queueTimer = blue.os.GetWallclockTime()

    def JoinQueue(self):
        if not self.isReady:
            return
        try:
            self._errors = []
            self._isActivating = True
            self.onChange()
            activateTasklet = uthread.newJoinable(self._JoinQueue)
            uthread.waitForJoinable(activateTasklet, timeout=None)
        except eveexceptions.UserError as error:
            if error.msg == 'PVPJumpError':
                self._errors = error.dict['errors']
            else:
                raise
        except Exception:
            self._errors = [(PVPJumpError.UNKNOWN_ERROR, ())]
            raise
        finally:
            uthread.new(self._lockButtonThread)
            self.onChange()

    def LeaveQueue(self):
        if not self.isReady:
            return
        self._service.RequestToLeavePVPQueue(self.itemID, self.typeID)
        self._isInQueue = False
        self.onChange()

    def Close(self):
        if self.isInQueue:
            self.LeaveQueue()
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

    def OnMatchFound(self):
        self._isFinished = True
        self._isInQueue = False
        self.onChange()

    def OnMatchMakingFailure(self, errors):
        self._errors = errors
        self._isInQueue = False
        uthread.new(self._lockButtonThread)
        self.onChange()

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

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\abyss\baseActivationController.py
import abc
import abyss
import blue
import eveexceptions
import signals
import threadutils
import uthread

class BaseActivationController(object):
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
     'ProcessActiveShipChanged']
    _monitoredEffects = ('effects.Cloak', 'effects.CloakingCovertOps', 'effects.CloakingPrototype', 'effects.CloakingWarpSafe', 'effects.CloakNoAmim', 'effects.Tethering', 'effects.Uncloak')

    def __init__(self, itemID, validator):
        self._errors = None
        self._isFinished = False
        self._isActivating = False
        self._itemID = itemID
        self._remote_errors = []
        self._sessionChangeThread = None
        self._validator = validator
        self.onChange = signals.Signal(signalName='onChange')
        sm.RegisterNotify(self)

    @abc.abstractmethod
    def GetText(self):
        pass

    @abc.abstractmethod
    def _Validate(self):
        pass

    @abc.abstractmethod
    def _Activate(self):
        pass

    @property
    def errors(self):
        if self._errors is None:
            self.Validate()
        return set(self._errors + self._remote_errors)

    @property
    def itemID(self):
        return self._itemID

    @property
    def isFinished(self):
        return self._isFinished

    @property
    def isActivating(self):
        return self._isActivating

    @property
    def isReady(self):
        return not self._errors and not self.isActivating and not self.isFinished

    @property
    def isSuspicious(self):
        return self._validator.is_suspicious()

    def Validate(self):
        self._remote_errors = []
        self._errors, existing = [], self._errors
        try:
            self._Validate()
        except abyss.Error as error:
            self._errors = error.errors
        except eveexceptions.UserError:
            raise
        except Exception:
            self._errors.append((abyss.Error.UNKNOWN_ERROR, ()))
            raise

        if any((error == abyss.Error.SESSION_CHANGE_IN_PROGRESS for error, args in self._errors)):
            self.ValidateOnNextSessionChange()
        if existing != self._errors:
            self.onChange()

    @threadutils.throttled(2.0)
    def Activate(self):
        if not self.isReady:
            return
        try:
            self._remote_errors = []
            self._isActivating = True
            self.onChange()
            activateTasklet = uthread.newJoinable(self._Activate)
            uthread.waitForJoinable(activateTasklet, timeout=None)
        except eveexceptions.UserError as error:
            if error.msg == 'AbyssError':
                self._remote_errors = error.dict['errors']
            else:
                raise
        except Exception:
            self._remote_errors = [(abyss.Error.UNKNOWN_ERROR, ())]
            raise
        finally:
            self._isActivating = False
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

    def OnSlimItemChange(self, oldSlim, newSlim):
        if newSlim.itemID in (session.shipid, self._validator.get_gate_id()):
            self.Validate()

    def OnClientEvent_WarpStarted(self, *args):
        self.Validate()

    def OnClientEvent_WarpFinished(self, *args):
        self.Validate()

    def ValidateOnNextSessionChange(self):
        if self._sessionChangeThread is not None:
            return
        self._sessionChangeThread = uthread.new(self._ValidateOnNextSessionChange)

    def _ValidateOnNextSessionChange(self):
        while blue.os.GetSimTime() < session.nextSessionChange:
            blue.synchro.Yield()

        self.Validate()
        self._sessionChangeThread = None

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.Validate()

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\randomJump\client\randomJumpController.py
import abc
import blue
import eveexceptions
import evetypes
import localization
import signals
import threadutils
import uthread
from dogma.const import attributeMicroJumpPortalMaxShipCandidates, attributeFilamentDescriptionMessageID, attributeActiveSystemJump, attributeLightYearDistanceMax
from randomJump import RandomJumpError

class RandomJumpActivationController(object):
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

    def __init__(self, item, validator):
        self._errors = None
        self._isFinished = False
        self._isActivating = False
        self._itemID = item.itemID
        self._typeID = item.typeID
        self._remote_errors = []
        self._sessionChangeThread = None
        self._validator = validator
        self.onChange = signals.Signal(signalName='onChange')
        sm.RegisterNotify(self)

    def GetText(self):
        if self.isActivating:
            return localization.GetByLabel('UI/Abyss/Jumping')
        else:
            return localization.GetByLabel('UI/Abyss/Activate')

    def _Validate(self):
        self._validator.validate_activation()

    def _Activate(self):
        sm.GetService('sessionMgr').PerformSessionChange('RandomJump', sm.GetService('randomJumpSvc').ActivateRandomJumpFilament, self.itemID)
        self._isFinished = True

    @property
    def errors(self):
        if self._errors is None:
            self.Validate()
        return set(self._errors + self._remote_errors)

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
    def jumpAmount(self):
        return int(self.GetAttribute(self.typeID, attributeMicroJumpPortalMaxShipCandidates))

    @property
    def lightYearDistance(self):
        return self.GetAttribute(self.typeID, attributeLightYearDistanceMax)

    @property
    def activeSystem(self):
        return self.GetAttribute(self.typeID, attributeActiveSystemJump)

    @property
    def activeSystemDescription(self):
        return localization.GetByLabel('UI/RandomJump/ActiveSystemDescription')

    @property
    def typeDescription(self):
        return localization.GetByMessageID(int(self.GetAttribute(self.typeID, attributeFilamentDescriptionMessageID)), amount=self.jumpAmount, lightYears=self.lightYearDistance)

    @property
    def timerDescription(self):
        return localization.GetByLabel('UI/Crimewatch/Timers/PvpTimerTooltiip')

    @property
    def shipRestrictionDescription(self):
        return localization.GetByLabel('UI/RandomJump/RestrictionSubCaps')

    @property
    def shipRestrictionTitle(self):
        return localization.GetByLabel('UI/RandomJump/ShipRestriction')

    @property
    def isFinished(self):
        return self._isFinished

    @property
    def isActivating(self):
        return self._isActivating

    @property
    def isReady(self):
        return not self._errors and not self.isActivating and not self.isFinished

    def Validate(self):
        self._remote_errors = []
        self._errors, existing = [], self._errors
        try:
            self._Validate()
        except RandomJumpError as error:
            self._errors = error.errors
        except eveexceptions.UserError:
            raise
        except Exception:
            self._errors.append((RandomJumpError.UNKNOWN_ERROR, ()))
            raise

        if any((error == RandomJumpError.SESSION_CHANGE_IN_PROGRESS for error, args in self._errors)):
            self.ValidateOnNextSessionChange()
        if existing != self._errors:
            self.onChange()

    @threadutils.expiring_memoize(2)
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
            if error.msg == 'RandomJumpError':
                self._remote_errors = error.dict['errors']
            else:
                raise
        except Exception:
            self._remote_errors = [(RandomJumpError.UNKNOWN_ERROR, ())]
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

    def GetAttribute(self, typeID, attributeID):
        dogmaStaticSvc = sm.GetService('clientDogmaStaticSvc')
        return dogmaStaticSvc.GetTypeAttribute2(typeID, attributeID)

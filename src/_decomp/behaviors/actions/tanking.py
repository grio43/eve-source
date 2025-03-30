#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\actions\tanking.py
from ballpark.messenger.const import MESSAGE_ON_EFFECT_STARTED, MESSAGE_ON_DAMAGE_CHANGED
from behaviors.tasks import Task
from ccpProfile import TimedFunction
from dogma.attributes.health import GetCurrentArmorRatio, GetCurrentShieldRatio
from dogma.const import effectEntityArmorRepairingLarge, effectEntityArmorRepairingMedium, effectEntityArmorRepairingSmall
from dogma.const import effectEntityShieldBoostingLarge, effectEntityShieldBoostingMedium, effectEntityShieldBoostingSmall
from dogma.const import effectNpcBehaviorArmorRepairer, effectNpcBehaviorShieldBooster
from eveexceptions import UserError
from eveexceptions.exceptionEater import ExceptionEater
import logging
logger = logging.getLogger(__name__)
ARMOR_TANK_EFFECT_IDS = {effectEntityArmorRepairingLarge,
 effectEntityArmorRepairingMedium,
 effectEntityArmorRepairingSmall,
 effectNpcBehaviorArmorRepairer}
SHIELD_TANK_EFFECT_IDS = {effectEntityShieldBoostingLarge,
 effectEntityShieldBoostingMedium,
 effectEntityShieldBoostingSmall,
 effectNpcBehaviorShieldBooster}

class ActiveTank(Task):

    def __init__(self, attributes = None):
        super(ActiveTank, self).__init__(attributes)
        self.armorTank = EntityArmorTank()
        self.shieldTank = EntityShieldTank()

    @TimedFunction('behaviors::actions::tanking::ActiveTank::OnEnter')
    def OnEnter(self):
        self._InitTanks()
        try:
            self.ActivateTanks()
            self._SubscribeDamageChangesIfNotTanking()
        except RuntimeError:
            pass

        self.SetStatusToFailed()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_DAMAGE_CHANGED, self._OnDamageReceived)
        super(ActiveTank, self).CleanUp()

    def _SubscribeDamageChangesIfNotTanking(self):
        if all((not tank.IsTanking() for tank in self._IterTanks())):
            self.SubscribeItem(self.context.myItemId, MESSAGE_ON_DAMAGE_CHANGED, self._OnDamageReceived)

    @TimedFunction('behaviors::actions::tanking::ActiveTank::ActivateTanks')
    def ActivateTanks(self):
        for tank in self._IterTanks():
            tank.ActivateTankIfDamaged()

    @TimedFunction('behaviors::actions::tanking::ActiveTank::_InitTanks')
    def _InitTanks(self):
        for tank in self._IterTanks():
            self._InitEntityTank(tank)

    def _InitEntityTank(self, entityTank):
        if not entityTank.IsInitialized(self.context.myItemId):
            entityTank.Initialized(self.context.myItemId, self.context.mySlimItem.typeID, self.context.mySlimItem.ownerID, self.context.dogmaLM, self.context.ballpark.eventMessenger)

    def _OnDamageReceived(self, *args):
        for tank in self._IterTanks():
            if tank.CanActiveTank() and not tank.IsTanking() and not tank.IsAtFullHealth():
                self.behaviorTree.RequestReset(requestedBy=self)

    def _IterTanks(self):
        for tank in (self.shieldTank, self.armorTank):
            yield tank


class EffectStillActivatingError(Exception):
    pass


class EntityArmorTank(object):
    __validTankEffects__ = ARMOR_TANK_EFFECT_IDS

    def __init__(self):
        self.isTanking = False
        self.effectId = None
        self.itemId = None
        self.typeId = None
        self.ownerId = None
        self.dogmaLM = None
        self.eventMessenger = None

    def Initialized(self, itemId, typeId, ownerId, dogmaLM, eventMessenger):
        self.itemId = itemId
        self.typeId = typeId
        self.ownerId = ownerId
        self.dogmaLM = dogmaLM
        self.eventMessenger = eventMessenger
        self._DetermineValidTankEffect()

    def IsInitialized(self, itemId):
        return self.itemId is not None and self.itemId == itemId

    def ActivateTankIfDamaged(self):
        if not self.CanActiveTank():
            return
        if not self.IsAtFullHealth():
            self._StartTanking()

    def CanActiveTank(self):
        return self.effectId is not None and not self._IsExploding()

    def _IsExploding(self):
        return self.dogmaLM.ballpark.IsExploding(self.itemId)

    def IsTanking(self):
        return self.isTanking

    def IsAtFullHealth(self):
        return self.GetTankStatus() >= 1.0

    def _StartTanking(self):
        self.isTanking = True
        self.eventMessenger.SubscribeItem(self.itemId, (MESSAGE_ON_EFFECT_STARTED, self.effectId), self._OnTankRepaired)
        self._StartEffects()
        logger.debug('%s starting tanking with effectId %s', self.itemId, self.effectId)

    def _StopTanking(self):
        self._StopEffects()
        self.isTanking = False
        self.eventMessenger.UnsubscribeItem(self.itemId, (MESSAGE_ON_EFFECT_STARTED, self.effectId), self._OnTankRepaired)
        logger.debug('%s stopping tanking with effectId %s', self.itemId, self.effectId)

    def _OnTankRepaired(self, *args):
        if not self.IsTanking():
            return
        if self.IsAtFullHealth():
            self.TryStopTanking()

    def TryStopTanking(self):
        with ExceptionEater('Failed to stop active tanking'):
            try:
                self._StopTanking()
            except EffectStillActivatingError:
                pass

    @TimedFunction('behaviors::actions::tanking::EntityArmorTank::_IsTankEffectActive')
    def _IsTankEffectActive(self):
        return self.dogmaLM.GetActiveEffectData(self.itemId, self.effectId) is not None

    @TimedFunction('behaviors::actions::tanking::EntityArmorTank::_StartEffects')
    def _StartEffects(self):
        with ExceptionEater('Activating entity active tank'):
            if self._IsTankEffectActive():
                return
            self.dogmaLM.ActivateWithContext(self.ownerId, self.itemId, self.effectId, repeat=100)
            logger.debug('Item %s started tank effect %s', self.itemId, self.effectId)

    @TimedFunction('behaviors::actions::tanking::EntityArmorTank::_StopEffects')
    def _StopEffects(self):
        try:
            self.dogmaLM.StopEffect(self.effectId, self.itemId)
            logger.debug('Item %s stopped tank effect %s', self.itemId, self.effectId)
        except UserError as e:
            if e.msg == 'EffectStillActivating':
                raise EffectStillActivatingError()
            raise
        except:
            raise

    def _DetermineValidTankEffect(self):
        self.effectId = None
        for effectId in self.__validTankEffects__:
            if self.dogmaLM.dogmaStaticMgr.TypeHasEffect(self.typeId, effectId):
                self.effectId = effectId
                break

    @TimedFunction('behaviors::actions::tanking::EntityArmorTank::GetTankStatus')
    def GetTankStatus(self):
        return GetCurrentArmorRatio(self.dogmaLM, self.itemId)


class EntityShieldTank(EntityArmorTank):
    __validTankEffects__ = SHIELD_TANK_EFFECT_IDS

    @TimedFunction('behaviors::actions::tanking::EntityShieldTank::GetTankStatus')
    def GetTankStatus(self):
        return GetCurrentShieldRatio(self.dogmaLM, self.itemId)

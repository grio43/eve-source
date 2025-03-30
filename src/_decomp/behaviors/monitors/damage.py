#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\damage.py
import logging
import dogma.attributes.health as health
from ballpark.messenger.const import MESSAGE_ON_DAMAGE_CHANGED
from behaviors.tasks import Task
logger = logging.getLogger(__name__)

class ArmorDamageThresholdMonitor(Task):

    def OnEnter(self):
        self.SubscribeItem(self.context.myItemId, MESSAGE_ON_DAMAGE_CHANGED, self._OnDamageReceived)
        self.SetStatusToSuccess()

    def CleanUp(self):
        if not self.IsInvalid():
            self.UnsubscribeItem(self.context.myItemId, MESSAGE_ON_DAMAGE_CHANGED, self._OnDamageReceived)
        super(ArmorDamageThresholdMonitor, self).CleanUp()

    def _OnDamageReceived(self, *args):
        if self.IsInvalid():
            return
        armorRatio = health.GetCurrentArmorRatio(self.context.dogmaLM, self.context.myItemId)
        if armorRatio < self.attributes.armorRatioThreshold:
            logger.debug('Damage received armor ratio=%s threshold=%s', armorRatio, self.attributes.armorRatioThreshold)
            self.SendBlackboardValue(self.attributes.thresholdReachedAddress, True)
            self.behaviorTree.RequestReset(requestedBy=self)

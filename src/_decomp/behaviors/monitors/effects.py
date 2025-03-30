#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\monitors\effects.py
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class EffectUsageMonitor(Task):

    def OnEnter(self):
        self.SubscribeOnEffect()
        self.SetStatusToFailed()

    def CleanUp(self):
        self.UnsubscribeOnEffect()
        self.SetStatusToInvalid()

    @TimedFunction('behaviors::monitors::EffectUsageMonitor::OnEffect')
    def OnEffect(self, effect, start, active, env, otherTypeID, duration, repeat, error):
        if self.IsInvalid():
            return
        if not self.IsEffectMatch(effect):
            return
        if not self.IsShipEffect(env):
            return
        if not self.IsSameBubble(env):
            return
        self.UpdateShipIdSet(env)

    def SubscribeOnEffect(self):
        self.context.dogmaLM.RegisterEffectCallback(('OnEffect', self))

    def UnsubscribeOnEffect(self):
        self.context.dogmaLM.UnregisterEffectCallback(('OnEffect', self))

    def UpdateShipIdSet(self, dogmaEnvironment):
        shipSet = self.GetLastBlackboardValue(self.attributes.shipIdSetAddress) or set()
        if dogmaEnvironment.shipID in shipSet:
            return
        shipSet.add(dogmaEnvironment.shipID)
        self.SendBlackboardValue(self.attributes.shipIdSetAddress, shipSet)

    def IsEffectMatch(self, effect):
        return effect.effectID == self.attributes.effectId

    def IsSameBubble(self, dogmaEnvironment):
        shipBall = self.context.ballpark.GetBall(dogmaEnvironment.shipID)
        return shipBall.newBubbleId == self.context.myBall.newBubbleId

    def IsShipEffect(self, dogmaEnvironment):
        return dogmaEnvironment.shipID is not None

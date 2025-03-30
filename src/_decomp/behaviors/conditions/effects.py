#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\conditions\effects.py
from behaviors.tasks import Task
from ccpProfile import TimedFunction

class IsEffectActive(Task):

    @TimedFunction('behaviors::condition::effects::IsEffectActive::OnEnter')
    def OnEnter(self):
        if self.IsEffectActive():
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def IsEffectActive(self):
        return self.context.dogmaLM.GetActiveEffectData(self.context.myItemId, self.attributes.effectId) is not None


class IsEffectByAddressActive(Task):

    @TimedFunction('behaviors::condition::effects::IsEffectAddressActive::OnEnter')
    def OnEnter(self):
        if self.IsEffectActive():
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def IsEffectActive(self):
        effectID = self.GetLastBlackboardValue(self.attributes.effectIDAddress)
        return self.context.dogmaLM.GetActiveEffectData(self.context.myItemId, effectID) is not None


class IsAnyEffectActive(Task):

    @TimedFunction('behaviors::condition::effects::IsAnyEffectActive::OnEnter')
    def OnEnter(self):
        for effectId in self.attributes.effectIds:
            if self.IsEffectActive(effectId):
                self.SetStatusToSuccess()
                return

        self.SetStatusToFailed()

    def IsEffectActive(self, effectId):
        return self.context.dogmaLM.GetActiveEffectData(self.context.myItemId, effectId) is not None


class HasAnyEffectCondition(Task):

    @TimedFunction('behaviors::condition::effects::HasAnyEffectCondition::OnEnter')
    def OnEnter(self):
        if self.HasAnyEffects():
            self.SetStatusToSuccess()
        else:
            self.SetStatusToFailed()

    def HasAnyEffects(self):
        for effectId in self.attributes.effectIds:
            if self.HasEffect(effectId):
                return True

        return False

    def HasEffect(self, effectId):
        return self.context.dogmaLM.dogmaStaticMgr.TypeHasEffect(self.context.mySlimItem.typeID, effectId)

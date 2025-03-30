#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\services\corruptionSuppressionSvc.py
from caching import Memoize
from carbon.common.script.sys.service import Service
from eve.client.script.ui.services.insurgency.messenger import InsurgencyMessenger, SystemData
from fractions import Fraction
from fwwarzone.heroNotifications import FullSuppression, FullCorruption
from pirateinsurgency.client.utils import CalculateCurrentStageFromFraction

class CorruptionSuppressionSvc(Service):
    __displayname__ = 'CorruptionSuppression svc'
    __guid__ = 'svc.corruptionSuppressionSvc'
    __notifyevents__ = ['OnSessionChanged']
    __startupdependencies__ = ['publicGatewaySvc', 'heroNotification']

    def __init__(self):
        super(CorruptionSuppressionSvc, self).__init__()

    def Run(self, memStream = None):
        super(CorruptionSuppressionSvc, self).Run(memStream=memStream)
        self.messenger = InsurgencyMessenger(self.publicGatewaySvc)
        self.localCorruptionValue = None
        self.localSuppressionValue = None
        self.messenger.SubscribeToCorruptionValueUpdates(self._OnCorruptionValueChanged)
        self.messenger.SubscribeToSuppressionValueUpdates(self._OnSuppressionValueChanged)

    def OnSessionChanged(self, isRemove, sess, change):
        if 'solarsystemid2' in change:
            _oldSolarSystemID, newSolarSystemID = change['solarsystemid2']
            self.localCorruptionValue = None
            self.localSuppressionValue = None
            self.GetSystemCorruption.clear_memoized(self, newSolarSystemID)
            self.GetSystemSuppression.clear_memoized(self, newSolarSystemID)

    def IsCurrentSystemFullyCorrupted(self):
        currentStage = self.GetSystemCorruptionStage(session.solarsystemid2)
        thresholds = self.GetCorruptionStages()
        if currentStage is None or thresholds is None:
            return False
        return currentStage >= len(thresholds) - 1

    @Memoize(720)
    def GetCorruptionStages(self):
        return self.messenger.GetCorruptionStages()

    @Memoize(720)
    def GetSuppressionStages(self):
        return self.messenger.GetSuppressionStages()

    def GetCurrentSystemCorruptionStage(self):
        currentStageData = self.GetCurrentSystemCorruption_Cached()
        if currentStageData is None:
            return
        currentStage = currentStageData.stage
        return currentStage

    def GetSystemCorruptionStage(self, systemID):
        currentStageData = self.GetSystemCorruption(systemID)
        if currentStageData is None:
            return
        currentStage = currentStageData.stage
        return currentStage

    def GetCurrentSystemCorruption_Cached(self):
        if self.localCorruptionValue is not None:
            return self.localCorruptionValue
        systemID = session.solarsystemid2
        data = self.GetSystemCorruption(systemID)
        self.localCorruptionValue = data
        return data

    @Memoize(5)
    def GetSystemCorruption(self, systemID):
        data = self.messenger.GetCorruption(systemID)
        if systemID == session.solarsystemid2:
            self.localCorruptionValue = data
        return data

    def GetCurrentSystemSuppressionStage(self):
        currentStageData = self.GetCurrentSystemSuppression_Cached()
        if currentStageData is None:
            return
        currentStage = currentStageData.stage
        return currentStage

    def GetSystemSuppressionStage(self, systemID):
        currentStageData = self.GetSystemSuppression(systemID)
        if currentStageData is None:
            return
        currentStage = currentStageData.stage
        return currentStage

    def GetCurrentSystemSuppression_Cached(self):
        if self.localSuppressionValue is not None:
            return self.localSuppressionValue
        systemID = session.solarsystemid2
        data = self.GetSystemSuppression(systemID)
        self.localSuppressionValue = data
        return data

    @Memoize(5)
    def GetSystemSuppression(self, systemID):
        data = self.messenger.GetSuppression(systemID)
        if systemID == session.solarsystemid2:
            self.localSuppressionValue = data
        return data

    def _OnCorruptionValueChanged(self, systemID, value):
        if systemID != session.solarsystemid2:
            return
        newStage = CalculateCurrentStageFromFraction(value.newNumerator, value.newDenominator, self.GetCorruptionStages())
        self._UpdateLocalCorruptionCacheEntry(systemID, value.newNumerator, value.newDenominator, newStage, value.vanguardInstigated)
        if systemID == session.solarsystemid2:
            numerator = value.newNumerator
            denominator = value.newDenominator
            if numerator and numerator == denominator:
                self.ShowCorruptionHeroNotification(systemID)
        sm.ScatterEvent('OnCorruptionValueChanged_Local', systemID, self.localCorruptionValue)

    def _UpdateLocalCorruptionCacheEntry(self, systemID, newNumerator, newDenominator, newStage, vanguardInitiated = False):
        if self.localCorruptionValue is not None:
            if vanguardInitiated:
                currentNumerator = self.localCorruptionValue.numerator
                currentDenominator = self.localCorruptionValue.denominator
                currentVanguardNumerator = self.localCorruptionValue.vanguardNumerator
                currentVanguardDenominator = self.localCorruptionValue.vanguardDenominator
                diffFraction = Fraction(newNumerator, newDenominator) - Fraction(currentNumerator, currentDenominator)
                vanguardFraction = Fraction(currentVanguardNumerator, currentVanguardDenominator) + diffFraction
                self.localCorruptionValue.vanguardNumerator = vanguardFraction.numerator
                self.localCorruptionValue.vanguardDenominator = vanguardFraction.denominator
            self.localCorruptionValue.numerator = newNumerator
            self.localCorruptionValue.denominator = newDenominator
            self.localCorruptionValue.stage = newStage
        else:
            systemData = SystemData(systemID, newNumerator, newDenominator, newStage, vanguard_numerator=0, vanguard_denominator=0)
            self.localCorruptionValue = systemData

    def _OnSuppressionValueChanged(self, systemID, value):
        if systemID != session.solarsystemid2:
            return
        newStage = CalculateCurrentStageFromFraction(value.newNumerator, value.newDenominator, self.GetSuppressionStages())
        self._UpdateLocalSuppressionCacheEntry(systemID, value.newNumerator, value.newDenominator, newStage, value.vanguardInstigated)
        if systemID == session.solarsystemid2:
            numerator = value.newNumerator
            denominator = value.newDenominator
            if numerator and numerator == denominator:
                self.ShowSuppressionHeroNotification(systemID)
        sm.ScatterEvent('OnSuppressionValueChanged_Local', systemID, self.localSuppressionValue)

    def _UpdateLocalSuppressionCacheEntry(self, systemID, newNumerator, newDenominator, newStage, vanguardInitiated = False):
        if self.localSuppressionValue is not None:
            if vanguardInitiated:
                currentNumerator = self.localSuppressionValue.numerator
                currentDenominator = self.localSuppressionValue.denominator
                currentVanguardNumerator = self.localSuppressionValue.vanguardNumerator
                currentVanguardDenominator = self.localSuppressionValue.vanguardDenominator
                diffFraction = Fraction(newNumerator, newDenominator) - Fraction(currentNumerator, currentDenominator)
                vanguardFraction = Fraction(currentVanguardNumerator, currentVanguardDenominator) + diffFraction
                self.localSuppressionValue.vanguardNumerator = vanguardFraction.numerator
                self.localSuppressionValue.vanguardDenominator = vanguardFraction.denominator
            self.localSuppressionValue.numerator = newNumerator
            self.localSuppressionValue.denominator = newDenominator
            self.localSuppressionValue.stage = newStage
        else:
            systemData = SystemData(systemID, newNumerator, newDenominator, newStage, vanguard_numerator=0, vanguard_denominator=0)
            self.localSuppressionValue = systemData

    def ShowCorruptionHeroNotification(self, systemID):

        def PlayVideo(parent, cancellation_token):
            FullCorruption(parent, systemID)

        self.heroNotification.play(PlayVideo, 0)

    def ShowSuppressionHeroNotification(self, systemID):

        def PlayVideo(parent, cancellation_token):
            FullSuppression(parent, systemID)

        self.heroNotification.play(PlayVideo, 0)

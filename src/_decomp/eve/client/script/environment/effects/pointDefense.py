#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\pointDefense.py
import evetypes
from eve.client.script.environment.effects.GenericEffect import GenericEffect
import math

class PointDefense(GenericEffect):
    __guid__ = 'effects.PointDefense'
    START_STOP_CHECK_TIME = 20000

    def __init__(self, trigger, *args):
        GenericEffect.__init__(self, trigger, *args)
        self.ballIDs = [trigger.shipID]
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.trigger = trigger
        self.gfx = None
        self.candidateTypes = self._GetCandidateTypesFromTypeList()
        self.hitRange = self._GetHitRange()
        self.trackTargets = self._TrackTargets()
        self.bulletStormEffect = None
        self.active = None
        self.activeStates = []
        self._nextStateIndex = None

    def Prepare(self):
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        structureID = self.ballIDs[0]
        structureBall = self.fxSequencer.GetBall(structureID)
        fx = self.gfx.effectChildren[0]
        fx.sourceObject = getattr(structureBall, 'model', None)
        self.AddSoundToEffect(scaler=1, model=fx.sourceObject)
        self.gfx.translationCurve = getattr(fx.sourceObject, 'translationCurve')
        self.gfx.rotationCurve = getattr(fx.sourceObject, 'rotationCurve')
        scene = self.fxSequencer.GetScene()
        scene.objects.append(self.gfx)
        self.bulletStormEffect = self.gfx.effectChildren[0]
        self.bulletStormEffect.display = False
        self.active = False
        self.activeStates = [False] * int(self.START_STOP_CHECK_TIME / self.duration)
        self._nextStateIndex = 0

    def Start(self, duration):
        if self.gfx is not None:
            self.UpdateTargets()

    def Repeat(self, duration):
        if self.gfx is not None:
            self.UpdateTargets()

    def Stop(self, reason = None):
        if self.gfx is not None:
            scene = self.fxSequencer.GetScene()
            scene.objects.fremove(self.gfx)
            self.gfx = None
            self.bulletStormEffect = None
            self.SendAudioEvent('point_defense_battery_stop')

    def AddState(self, state):
        self.activeStates[self._nextStateIndex] = state
        self._nextStateIndex = int(math.fmod(self._nextStateIndex + 1, len(self.activeStates)))

    def ShouldChangeState(self):
        states = [ state != self.active for state in self.activeStates ]
        if not self.active:
            shouldChangeState = any(states)
        else:
            shouldChangeState = all(states)
        return shouldChangeState and self.bulletStormEffect.CanChangeState()

    def UpdateTargets(self):
        if isinstance(self.candidateTypes, list) and len(self.candidateTypes) == 0:
            self.bulletStormEffect.display = True
            if not self.active:
                self._StartEffect()
            return
        ballIDs = self.ballpark.GetBallsInRange(self.trigger.shipID, self.hitRange)
        shipModels = []
        for bID in ballIDs:
            b = self.fxSequencer.GetBall(bID)
            m = getattr(b, 'model', None)
            slimItem = self.fxSequencer.GetItem(bID)
            if self.candidateTypes is None or getattr(slimItem, 'typeID', None) in self.candidateTypes:
                if m is not None:
                    shipModels.append(m)

        self.AddState(self.candidateTypes is not None and len(shipModels) != 0)
        if self.ShouldChangeState():
            self.bulletStormEffect.display = True
            if not self.active:
                self._StartEffect()
            else:
                self._StopEffect()
        if self.trackTargets:
            del self.bulletStormEffect.targetObjects[:]
            for m in shipModels:
                self.bulletStormEffect.targetObjects.append(m)

    def _StartEffect(self):
        self.bulletStormEffect.StartEffect()
        self.SendAudioEvent('point_defense_battery_play')
        self.active = True

    def _StopEffect(self):
        self.bulletStormEffect.StopEffect()
        self.SendAudioEvent('point_defense_battery_stop')
        self.active = False

    def _TrackTargets(self):
        return self.graphicInfo is None or self.graphicInfo.get('trackTargets', True)

    def _GetCandidateTypesFromTypeList(self):
        if self.graphicInfo is None or 'candidateTypeListId' not in self.graphicInfo:
            return
        candidateTypeListId = self.graphicInfo['candidateTypeListId']
        if candidateTypeListId < 0:
            return []
        return evetypes.GetTypeIDsByListID(candidateTypeListId)

    def _GetHitRange(self):
        empFieldRange = self.fxSequencer.GetTypeAttribute(self.trigger.moduleTypeID, const.attributeEmpFieldRange)
        if self.graphicInfo is None:
            return empFieldRange
        return self.graphicInfo.get('hitRange', empFieldRange)

    def UpdateGraphicInfo(self, newGraphicInfo):
        self.graphicInfo = newGraphicInfo
        self.candidateTypes = self._GetCandidateTypesFromTypeList()
        self.hitRange = self._GetHitRange()
        self.trackTargets = self._TrackTargets()

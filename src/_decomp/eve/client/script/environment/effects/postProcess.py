#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\effects\postProcess.py
import blue
import uthread2
import yamlext
import trinity

class PostProcessEffect(object):
    __guid__ = 'effects.PostProcessEffect'
    __lerpFields__ = {'vignette': ['opacity', 'intensity']}

    def __init__(self, trigger, effect = None, graphicFile = None):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.graphicFile = graphicFile
        self.postProcess = None
        self.lerpValues = {}
        self.fadeInDuration = 1
        self.fadeOutDuration = 1
        self.forSelf = trigger.shipID == session.shipid

    def _GetPostProcess(self):
        return sm.GetService('sceneManager').GetActiveScene().postprocess

    def GetBalls(self):
        return self.ballIDs

    def GetEffectTargetID(self):
        try:
            return self.ballIDs[1]
        except IndexError:
            return None

    def Prepare(self):
        self.postProcess = self._GetPostProcess()
        yaml = yamlext.load(blue.paths.GetFileContentsWithYield(self.graphicFile))
        for postProcessMemberKey, postProcessMemberList in yaml.iteritems():
            postProcessMember = getattr(self.postProcess, postProcessMemberKey, None)
            if postProcessMember is None:
                postProcessMember = self.PPMemberToClass(postProcessMemberKey)()
                setattr(self.postProcess, postProcessMemberKey, postProcessMember)
            lerpField = self.__lerpFields__[postProcessMemberKey]
            for subMemberKey, value in postProcessMemberList.iteritems():
                if subMemberKey in lerpField:
                    if postProcessMemberKey not in self.lerpValues:
                        self.lerpValues[postProcessMemberKey] = {}
                    self.lerpValues[postProcessMemberKey][subMemberKey] = (getattr(postProcessMember, subMemberKey), value)
                else:
                    setattr(postProcessMember, subMemberKey, value)

    def Start(self, duration):
        if self.forSelf:
            uthread2.StartTasklet(self._FadeThread, self.fadeInDuration)

    def Stop(self, reason):
        if self.forSelf:
            uthread2.StartTasklet(self._FadeThread, self.fadeOutDuration, invert=True)

    def Repeat(self, duration):
        self.Start(duration)

    def _FadeThread(self, duration, invert = False):
        startTime = blue.os.GetSimTime()
        while True:
            blue.synchro.Yield()
            curTime = blue.os.GetSimTime()
            dif = min(blue.os.TimeDiffInMs(startTime, curTime) / 1000.0 / duration, 1)
            for postProcessMemberKey, subMemberDict in self.lerpValues.iteritems():
                postprocessMember = getattr(self.postProcess, postProcessMemberKey)
                for subMemberKey, subMemberLerpValues in subMemberDict.iteritems():
                    start, end = subMemberLerpValues
                    if invert:
                        start, end = end, 0
                    val = start + (end - start) * dif
                    setattr(postprocessMember, subMemberKey, val)

            if dif >= 1:
                break

    def PPMemberToClass(self, postProcessMember):
        ppMemberToClassMap = {'signalLoss': trinity.Tr2PPSignalLossEffect,
         'godRays': trinity.Tr2PPGodRaysEffect,
         'bloom': trinity.Tr2PPBloomEffect,
         'dynamicExposure': trinity.Tr2PPDynamicExposureEffect,
         'filmGrain': trinity.Tr2PPFilmGrainEffect,
         'desaturate': trinity.Tr2PPDesaturateEffect,
         'fade': trinity.Tr2PPFadeEffect,
         'lut': trinity.Tr2PPLutEffect,
         'vignette': trinity.Tr2PPVignetteEffect,
         'fog': trinity.Tr2PPFogEffect,
         'taa': trinity.Tr2PPTaaEffect}
        if postProcessMember in ppMemberToClassMap:
            return ppMemberToClassMap[postProcessMember]
        raise ValueError('Invalid post process member name passed into environment.effects.postprocess')

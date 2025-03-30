#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\structure.py
import blue
import uthread
import structures
import evetypes
from carbon.common.lib import const
from eve.client.script.environment.spaceObject.buildableStructure import BuildableStructure
from eve.client.script.environment.model.turretSet import TurretSet
from evegraphics.logoLoader import LogoLoader
STATE_CONSTRUCT = 'construct'
STATE_INVULNERABLE = 'invulnerable'
STATE_VULNERABLE_ACTIVE = 'vulnerable_active'
STATE_VULNERABLE_INACTIVE = 'vulnerable_inactive'
STATE_SIEGED_ACTIVE = 'sieged_active'
STATE_SIEGED_INACTIVE = 'sieged_inactive'
STATE_DECONSTRUCT = 'deconstruct'
STATES = {structures.STATE_UNKNOWN: (STATE_INVULNERABLE, STATE_INVULNERABLE),
 structures.STATE_UNANCHORED: (STATE_DECONSTRUCT, STATE_DECONSTRUCT),
 structures.STATE_ANCHORING: (STATE_CONSTRUCT, STATE_CONSTRUCT),
 structures.STATE_ONLINE_DEPRECATED: (STATE_INVULNERABLE, STATE_INVULNERABLE),
 structures.STATE_FITTING_INVULNERABLE: (STATE_INVULNERABLE, STATE_INVULNERABLE),
 structures.STATE_ONLINING_VULNERABLE: (STATE_VULNERABLE_INACTIVE, STATE_VULNERABLE_ACTIVE),
 structures.STATE_SHIELD_VULNERABLE: (STATE_VULNERABLE_INACTIVE, STATE_VULNERABLE_ACTIVE),
 structures.STATE_ARMOR_REINFORCE: (STATE_SIEGED_INACTIVE, STATE_SIEGED_ACTIVE),
 structures.STATE_ARMOR_VULNERABLE: (STATE_VULNERABLE_INACTIVE, STATE_VULNERABLE_ACTIVE),
 structures.STATE_HULL_REINFORCE: (STATE_SIEGED_INACTIVE, STATE_SIEGED_ACTIVE),
 structures.STATE_HULL_VULNERABLE: (STATE_VULNERABLE_INACTIVE, STATE_VULNERABLE_ACTIVE),
 structures.STATE_ANCHOR_VULNERABLE: (STATE_CONSTRUCT, STATE_CONSTRUCT),
 structures.STATE_DEPLOY_VULNERABLE: (STATE_CONSTRUCT, STATE_CONSTRUCT),
 structures.STATE_FOB_INVULNERABLE: (STATE_INVULNERABLE, STATE_INVULNERABLE)}

class Structure(BuildableStructure):
    __unloadable__ = True
    __notifyevents__ = ['OnAllianceLogoReady', 'OnCorpLogoReady', 'OnPortraitCreated']

    def __init__(self):
        BuildableStructure.__init__(self)
        self.logoLoader = LogoLoader((LogoLoader.ALLIANCE, LogoLoader.CORP, LogoLoader.CEO))
        sm.RegisterNotify(self)
        self.Init()

    def Release(self, origin = None):
        BuildableStructure.Release(self, origin)
        self.Init()

    def Init(self):
        self.fitted = False
        self.state = None
        self.timer = None
        self.upkeepState = None
        self.turrets = []
        self.modules = {}

    def Assemble(self):
        self.SetStaticRotation()
        self.SetupSharedAmbientAudio()

        def runInTasklet(func, *args):
            func(*args)

        self._OnSlimItemUpdated(self.typeData.get('slimItem'), runInTasklet)

    def OnSlimItemUpdated(self, item):
        BuildableStructure.OnSlimItemUpdated(self, item)
        self._OnSlimItemUpdated(item, uthread.new)

    def _OnSlimItemUpdated(self, item, taskletSpawner):
        if item is None:
            return
        self.typeData['slimItem'] = item
        if self.unloaded or self.model is None:
            return
        if item.state and (item.state != self.state or item.timer != self.timer or item.upkeepState != self.upkeepState):
            duration = 0
            elapsed = 0
            if item.timer and item.state == structures.STATE_ANCHORING:
                start, end, paused = item.timer
                duration = (end - start) / const.SEC
                elapsed = duration - max(end - blue.os.GetWallclockTime(), 0L) / const.SEC
            elif item.state == structures.STATE_ANCHOR_VULNERABLE:
                duration = 86400
                elapsed = 0
            elif item.state == structures.STATE_DEPLOY_VULNERABLE:
                if item.deployTimes is not None:
                    start, end = item.deployTimes
                    duration = (end - start) / const.SEC
                    elapsed = duration - max(end - blue.os.GetWallclockTime(), 0L) / const.SEC
            self.state = item.state
            self.timer = item.timer
            self.upkeepState = item.upkeepState
            isActiveUpkeep = self.upkeepState == structures.UPKEEP_STATE_FULL_POWER
            self._GotoState(STATES[self.state][int(isActiveUpkeep)], duration, elapsed, taskletSpawner)
        uthread.new(self.logoLoader.Load, self.model, item)
        if not item.state and set([ i[0] for i in item.modules or [] if evetypes.GetGraphicID(i[1]) is not None ]) != set(self.modules.keys()):
            uthread.new(self.ReloadHardpoints)

    def _GotoState(self, state, totalTime = 0, elapsedTime = 0, taskletSpawner = uthread.new):
        if state == STATE_CONSTRUCT:
            taskletSpawner(self.BuildStructure, float(totalTime), float(elapsedTime))
        elif state == STATE_DECONSTRUCT:
            taskletSpawner(self.TearDownStructure, float(totalTime), float(elapsedTime))
        else:
            taskletSpawner(self.LoadModelWithState, state)

    def LoadModelWithState(self, newState):
        if self.model is None:
            self.LoadModel()
        self.SetControllerVariable('BuildDuration', 0)
        self.SetControllerVariable('BuildElapsedTime', 0)
        self.SetControllerVariable('IsBuilt', True)
        self.ClearAnimationStateObjects()
        self.TriggerStateObject(newState)
        self.FitHardpoints()
        self._SetCorruptionAndSuppression()

    def _SetCorruptionAndSuppression(self):
        css = sm.GetService('corruptionSuppressionSvc')
        if css is not None:
            maximumSuppressionStages = max(len(css.GetSuppressionStages()), 1)
            maximumCorruptionStages = max(len(css.GetCorruptionStages()), 1)
            suppressionStage = css.GetSystemSuppressionStage(session.solarsystemid) or 0.0
            corruptionStage = css.GetSystemCorruptionStage(session.solarsystemid) or 0.0
            suppression = float(suppressionStage) / float(maximumSuppressionStages)
            corruption = float(corruptionStage) / float(maximumCorruptionStages)
            self.SetControllerVariable('suppression', suppression)
            self.SetControllerVariable('corruption', corruption)

    def LoadModel(self, fileName = None, loadedModel = None, notify = True, addToScene = True):
        self.model = self.GetStructureModel()
        self.logoLoader.Load(self.model, self.typeData['slimItem'])
        self.NotifyModelLoaded()

    def OnPortraitCreated(self, charID, _size):
        if self.logoLoader.HasID(charID):
            self.logoLoader.Update(self.model)

    def OnAllianceLogoReady(self, allianceID, _size):
        if self.logoLoader.HasID(allianceID):
            self.logoLoader.Update(self.model)

    def OnCorpLogoReady(self, corpID, _size):
        if self.logoLoader.HasID(corpID):
            self.logoLoader.Update(self.model)

    def ReloadHardpoints(self):
        self.UnfitHardpoints()
        self.FitHardpoints()

    def UnfitHardpoints(self):
        if not self.fitted:
            return
        self.logger.debug('Unfitting hardpoints')
        newModules = {}
        for key, val in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.logger.debug('Fitting hardpoints')
        self.fitted = True
        newTurretSetDict = TurretSet.FitTurrets(self.id, self.model, self.typeData.get('sofFactionName', None))
        self.turrets = []
        for key, val in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def StopStructureLoopAnimation(self):
        animationUpdater = self.GetStructureModel().animationUpdater
        if animationUpdater is not None:
            animationUpdater.PlayLayerAnimation('TrackMaskLayer1', 'Layer1Loop', False, 1, 0, 1, True)

    def IsValidSleep(self, delay):
        return delay < 86400000

    def BuildStructure(self, anchoringTime, elapsedTime):
        self.LoadUnLoadedModels()
        self.logger.debug('Structure: BuildStructure %s', self.GetTypeID())
        self.PreBuildingSteps()
        delay = int((anchoringTime - elapsedTime) * 1000)
        if self.IsValidSleep(delay):
            uthread.new(self._EndStructureBuild, delay)
        self.SetControllerVariable('BuildDuration', anchoringTime)
        self.SetControllerVariable('BuildElapsedTime', elapsedTime)
        self.SetControllerVariable('IsBuilt', True)

    def _EndStructureBuild(self, delay):
        blue.pyos.synchro.SleepSim(delay)
        if self.released or self.exploded:
            return
        self.PostBuildingSteps(True)
        self.SetupModel(False)

    def TearDownStructure(self, unanchoringTime, elapsedTime):
        self.LoadUnLoadedModels()
        self.logger.debug('Structure: TearDownStructure %s', self.GetTypeID())
        self.StopStructureLoopAnimation()
        self.PreBuildingSteps()
        delay = int((unanchoringTime - elapsedTime) * 1000)
        if self.IsValidSleep(delay):
            uthread.new(self._EndStructureTearDown, delay)
        self.SetControllerVariable('BuildDuration', unanchoringTime)
        self.SetControllerVariable('BuildElapsedTime', elapsedTime)
        self.SetControllerVariable('IsBuilt', False)

    def _EndStructureTearDown(self, delay):
        blue.pyos.synchro.SleepSim(delay)
        if self.released or self.exploded:
            return
        self.PostBuildingSteps(False)
        self.SetupModel(True)

    def PostSkinChangeCallback(self, oldModel, newModel):
        super(BuildableStructure, self).PostSkinChangeCallback(oldModel, newModel)

        def runInTasklet(func, *args):
            func(*args)

        self._OnSlimItemUpdated(self.typeData.get('slimItem'), runInTasklet)

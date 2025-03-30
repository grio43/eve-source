#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\spaceObject\station.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import evegraphics.utils as gfxutils
import uthread2
from eve.common.script.sys.idCheckers import IsTriglavianSystem
from stackless_response_router.exceptions import TimeoutException

class Station(SpaceObject):
    __notifyevents__ = ['OnSlimItemUpdated']

    def __init__(self):
        SpaceObject.__init__(self)
        self.OnSlimItemUpdated(self.typeData.get('slimItem'))
        sm.RegisterNotify(self)

    def GetDNA(self):
        materialSetID = self.typeData.get('slimItem').skinMaterialSetID
        return gfxutils.BuildSOFDNAFromGraphicID(self.typeData.get('graphicID'), materialSetID=materialSetID)

    def Assemble(self):
        super(Station, self).Assemble()
        if hasattr(self.model, 'ChainAnimationEx'):
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupAmbientAudio()
        self._SetAudioVariables()
        if IsTriglavianSystem(session.solarsystemid):
            self.TriggerStateObject('triglavianOwned')
        self.SetStaticRotation()
        uthread2.StartTasklet(self._SetCorruptionAndSuppression)

    def _SetAudioVariables(self):
        if self.model:
            races = ['amarr',
             'gallente',
             'caldari',
             'minmatar']
            race = self.model.dna.split(':')[2]
            specialStationNames = ['60008494',
             '60004588',
             '60011866',
             '60005686']
            if self.model.name in specialStationNames:
                specialStationValue = float(specialStationNames.index(self.model.name) + 1)
            else:
                specialStationValue = 0.0
            if race in races:
                raceValue = races.index(race) + 1
            else:
                raceValue = 0
            self.model.SetControllerVariable('boundingSphereRadius', self.model.boundingSphereRadius)
            self.model.SetControllerVariable('race', raceValue)
            self.model.SetControllerVariable('specialStation', specialStationValue)

    def _SetCorruptionAndSuppression(self):
        if self.model is None:
            return
        try:
            css = sm.GetService('corruptionSuppressionSvc')
            if css is not None and hasattr(session, 'solarsystemid'):
                corruptionStage, suppressionStage = (0, 0)
                maximumSuppressionStages = max(len(css.GetSuppressionStages()), 5)
                maximumCorruptionStages = max(len(css.GetCorruptionStages()), 5)
                corruptionStateData = css.GetCurrentSystemCorruption_Cached()
                if corruptionStateData is not None:
                    corruptionStage = corruptionStateData.stage or 0
                suppressionStateData = css.GetCurrentSystemSuppression_Cached()
                if suppressionStateData is not None:
                    suppressionStage = suppressionStateData.stage or 0
                suppression = float(suppressionStage) / float(maximumSuppressionStages)
                corruption = float(corruptionStage) / float(maximumCorruptionStages)
                self.model.SetControllerVariable('suppression', suppression)
                self.model.SetControllerVariable('corruption', corruption)
        except TimeoutException:
            self.logger.debug('Station._SetCorruptionAndSuppression corruptionSuppressionSvc timeout')

    def OnSlimItemUpdated(self, item):
        celestialEffect = getattr(item, 'celestialEffect', None)
        if celestialEffect is not None:
            effectGuid, graphicInfo = celestialEffect
            self.logger.debug('Station.OnSlimItemUpdated found celestialEffect %s %s', effectGuid, graphicInfo)
            sm.ScatterEvent('OnSpecialFX', self.id, None, None, None, None, effectGuid, False, 1, True, graphicInfo=graphicInfo)

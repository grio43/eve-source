#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evespacescene\playerdeath.py
import logging
import random
import blue
import trinity
import geo2
import eve.client.script.environment.spaceObject.corpse as corpse
import eve.client.script.environment.spaceObject.spaceObject as spaceObject
import evegraphics.utils as gfxutils
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.environment.sofService import GetSofService
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.view.transitions import SpaceToStationTransition
from eve.common.lib import appConst as const
from inventorycommon.const import typeCapsule, typeCapsuleGolden, typeCombatRespawnBooster
from localization import GetByLabel
logger = logging.getLogger(__name__)
CAPSULE_WRECKMAP = {typeCapsule: const.graphicIDBrokenPod,
 typeCapsuleGolden: const.graphicIDBrokenGoldenPod}

class PlayerDeathHandler(object):
    __notifyevents__ = ['OnPlayerPodDeath', 'OnPlayerPodRespawn']

    def __init__(self, sceneManager):
        self._sceneManager = sceneManager
        self.currentShipType = None
        self.podDeathScene = None
        sm.RegisterNotify(self)

    @staticmethod
    def _GetCurrentShipTypeID():
        if session.shipid and session.solarsystemid:
            shipItem = sm.GetService('godma').GetItem(session.shipid)
            if shipItem:
                return shipItem.typeID

    def OnPlayerPodDeath(self):
        if session.solarsystemid is None:
            return
        self.currentShipType = self._GetCurrentShipTypeID()
        sm.GetService('viewState').ActivateView('inflight')
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            shipBall = bp.GetBall(bp.ego)
            spaceObject.SpaceObject.Explode(shipBall)
            shipBall.Display(0)
        else:
            return
        shakeMagnitude = max(blue.os.desiredSimDilation, 0.2) * 250
        camera = sm.GetService('sceneManager').GetActiveCamera()
        camera.ShakeCamera(shakeMagnitude, (0, 0, 0))
        sm.GetService('audio').SendUIEvent('transition_pod_play')
        self.CopyMyScene()
        activeTransition = sm.GetService('viewState').activeTransition
        if activeTransition and isinstance(activeTransition, SpaceToStationTransition):
            return
        fadeTime = max(blue.os.desiredSimDilation, 0.3) * 2000
        sm.GetService('loading').FadeIn(fadeTime, color=(1.0, 1.0, 1.0, 1.0))

    def CopyMyScene(self):
        sceneOrg = self._sceneManager.GetRegisteredScene('default')
        if sceneOrg is None:
            return
        scene = trinity.EveSpaceScene()
        self.podDeathScene = scene
        scene.sunDiffuseColor = sceneOrg.sunDiffuseColor
        scene.ambientColor = sceneOrg.ambientColor
        scene.fogColor = sceneOrg.fogColor
        scene.backgroundRenderingEnabled = True
        scene.backgroundEffect = blue.classes.Copy(sceneOrg.backgroundEffect)
        for pathName in ['envMapResPath',
         'envMap1ResPath',
         'envMap2ResPath',
         'envMap3ResPath']:
            path = getattr(sceneOrg, pathName, '')
            setattr(scene, pathName, path)

        sunBall = trinity.Tr2TranslationAdapter()
        if sceneOrg.sunBall is not None:
            sunPos = sceneOrg.sunBall.GetVectorAt(blue.os.GetSimTime())
            sunBall.value = (sunPos.x, sunPos.y, sunPos.z)
        else:
            sunBall.value = geo2.Vec3Normalize((random.random(), random.random(), random.random()))
        scene.sunBall = sunBall
        time = blue.os.GetSimTime()
        objectLists = [(sceneOrg.lensflares, scene.lensflares, trinity.EveLensflare), (sceneOrg.planets, scene.planets, trinity.EvePlanet), (sceneOrg.objects, scene.objects, trinity.EveStation2)]
        for eachList, destination, allowedTypes in objectLists:
            for obj in eachList:
                if session.solarsystemid is None:
                    return
                try:
                    if not isinstance(obj, allowedTypes):
                        continue
                    if not obj.display:
                        continue
                    if getattr(obj, 'translationCurve', None) is not None and obj.translationCurve.__bluetype__ == 'destiny.ClientBall':
                        pos = obj.translationCurve.GetVectorAt(time)
                        if getattr(obj.translationCurve, 'translationCurve', None):
                            obj.translationCurve.resourceCallback = None
                        obj.translationCurve.model = None
                        translationCurve = trinity.Tr2TranslationAdapter()
                        translationCurve.value = (pos.x, pos.y, pos.z)
                        obj.translationCurve = translationCurve
                    if getattr(obj, 'rotationCurve', None) is not None and obj.rotationCurve.__bluetype__ == 'destiny.ClientBall':
                        obj.rotationCurve = None
                    destination.append(obj)
                except Exception:
                    pass

    def GetCorpseModel(self):
        return corpse.GetCorpseModelForCharacter(session.charid)

    def GetCapsuleModel(self):
        wreckGraphicId = CAPSULE_WRECKMAP.get(self.currentShipType, None)
        if wreckGraphicId is None:
            logger.error('Unable to look up capsule ID for death scene for typeID: ', self.currentShipType)
            return
        sofDNA = gfxutils.BuildSOFDNAFromGraphicID(wreckGraphicId)
        factory = GetSofService().spaceObjectFactory
        return factory.BuildFromDNA(sofDNA)

    def OnPlayerPodRespawn(self):
        sm.GetService('viewState').ActivateView('inflight')
        fadeInTime = 1.0
        wallclockHoldTime = 1.5
        simHoldTime = 1.5
        fadeOutTime = 1.5
        notifyContainer = ContainerAutoSize(name='notifyContainer', parent=uicore.layer.hint, state=uiconst.UI_DISABLED, align=uiconst.CENTER, width=500, opacity=0.0, idx=0)
        try:
            sm.GetService('loading').FadeIn(fadeInTime * 1000, sleep=False)
            respawnHeaderText = '<center>%s</center>' % GetByLabel('UI/Fleet/Respawn/CapsuleBreachDetected')
            respawnHeaderLabel = EveCaptionLarge(parent=notifyContainer, name='respawnHeaderLabel', text=respawnHeaderText, color=Color.RED, align=uiconst.TOTOP, bold=True)
            respawnSubText = '<center>%s</center>' % GetByLabel('UI/Fleet/Respawn/RecloningSubLabel', boosterTypeID=typeCombatRespawnBooster)
            respawnSubTextLabel = EveLabelLarge(parent=notifyContainer, name='respawnSubTextLabel', text=respawnSubText, align=uiconst.TOTOP, bold=True, padding=(5, 15, 5, 15))
            gauge = Gauge(parent=notifyContainer, color=Color.RED, align=uiconst.TOTOP, padding=(5, 5, 5, 5))
            uicore.animations.FadeIn(notifyContainer, duration=fadeInTime, sleep=True)
            midPoint = wallclockHoldTime / (wallclockHoldTime + simHoldTime / blue.os.desiredSimDilation)
            gauge.useRealTime = True
            gauge.SetValue(midPoint, duration=wallclockHoldTime)
            blue.synchro.Sleep(wallclockHoldTime * 1000)
            gauge.useRealTime = False
            gauge.SetValue(1.0, duration=simHoldTime)
            blue.synchro.SleepSim(simHoldTime * 1000)
            uicore.animations.FadeOut(notifyContainer, duration=fadeOutTime * 0.5)
        finally:
            sm.GetService('loading').FadeOut(fadeOutTime * 1000, opacityStart=1.0)
            notifyContainer.Close()

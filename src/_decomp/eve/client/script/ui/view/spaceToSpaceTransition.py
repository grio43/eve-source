#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\spaceToSpaceTransition.py
import logging
import geo2
import uthread
from eve.client.script.ui.services.viewStateSvc import Transition
from fsdBuiltData.common.graphicIDs import GetGraphicFile
logger = logging.getLogger(__name__)

class SpaceToSpaceTransition(Transition):
    __guid__ = 'viewstate.SpaceToSpaceTransition'

    def __init__(self, sceneManager = None):
        self.sceneManager = sceneManager
        if self.sceneManager is None:
            self.sceneManager = sm.GetService('sceneManager')
        self.scene = None
        self.effect = None
        self.active = False
        Transition.__init__(self)

    def _GetInflightCamera(self):
        return sm.GetService('sceneManager').GetActiveSpaceCamera()

    def _GetSolarSystemScene(self, destSolarSystemID):
        sceneRes = self.sceneManager.GetSceneForSystem(destSolarSystemID)
        return self.sceneManager.LoadScene(sceneRes, registerKey='default', applyScene=False)[0]

    def _GetClosest(self, position, rowSet, maxDist):
        closestDist = float('inf')
        closestPlanet = None
        for each in rowSet:
            pos = (each.x, each.y, each.z)
            dist = geo2.Vec3DistanceSq(position, pos)
            if dist < maxDist * maxDist and dist < closestDist:
                closestPlanet = each.itemID
                closestDist = dist

        return closestPlanet

    def _PrioritizeStargateLoads(self, stargateID, systemId):
        items = [stargateID]
        systemItems = sm.GetService('map').GetSolarsystemItems(systemId, False)
        stargateRow = systemItems.Filter('itemID')[stargateID][0]
        planet = self._GetClosest((stargateRow.x, stargateRow.y, stargateRow.z), systemItems.Filter('groupID')[const.groupPlanet], maxDist=const.AU * 0.5)
        if planet is not None:
            items.append(planet)
        sm.GetService('space').PrioritizeLoadingForIDs(items)

    def _GetSceneFromPath(self, path):
        return self.sceneManager.LoadScene(path, registerKey='default', applyScene=False)[0]

    def _ApplySceneInflightAttribs(self, scene):
        self.sceneManager.ApplyScene(scene, 'default')
        self.sceneManager.ApplySolarsystemAttributes(scene)
        self.sceneManager.ApplySceneInflightAttributes(scene)
        self.sceneManager.AddPersistentUIObjects(scene)

    def _SetScene(self, scene):
        self.sceneManager.SetActiveScene(scene, 'default')

    def SetTransitionEffect(self, effect):
        self.effect = effect

    def InitializeGateTransition(self, destSolarSystemID, destObjectID = None):
        self.active = True
        self.destObjectID = destObjectID
        self.destSolarSystemID = destSolarSystemID
        self.camera = self._GetInflightCamera()
        self.scene = self._GetSolarSystemScene(destSolarSystemID)
        uthread.new(self._PrioritizeStargateLoads, destObjectID, destSolarSystemID)

    def InitializeCynoTransition(self, destSolarSystemID):
        self.active = True
        self.destSolarSystemID = destSolarSystemID
        self.camera = self._GetInflightCamera()
        self.scene = self._GetSolarSystemScene(destSolarSystemID)

    def InitializeWormholeTransition(self, scenePath):
        self.active = True
        self.camera = self._GetInflightCamera()
        self.scene = self._GetSceneFromPath(scenePath)

    def InitializeAbyssalTransition(self, destSolarSystemID, nebulaGraphicID):
        self.active = True
        self.camera = self._GetInflightCamera()
        self.nebulaGraphicID = nebulaGraphicID
        if nebulaGraphicID:
            logging.debug('initializing abyssal transition with nebula %s', nebulaGraphicID)
            nebulaResPath = GetGraphicFile(nebulaGraphicID)
            self.scene = self.sceneManager.LoadScene(nebulaResPath, registerKey='default', applyScene=False)[0]
        else:
            logging.debug('initializing abyssal transition with nebula from solar system %s', destSolarSystemID)
            self.scene = self._GetSolarSystemScene(destSolarSystemID)

    def Finalize(self):
        logging.debug('finalizing transition')
        self._ApplySceneInflightAttribs(self.scene)
        self.effect.Stop()
        self.scene = None
        self.camera = None
        self.effect = None
        self.active = False

    def Abort(self):
        self._ApplySceneInflightAttribs(self.sceneManager.GetRegisteredScene('default'))
        self.sceneManager.SetRegisteredScenes('default')
        self.scene = None
        self.camera = None
        self.effect = None
        self.active = False

    def ApplyDestinationScene(self):
        if self.effect is None or self.scene is None:
            return
        self.effect.SetScene(self.scene)
        self._SetScene(self.scene)

    def StartTransition(self, fromView, toView):
        self.ApplyDestinationScene()

    def EndTransition(self, fromView, toView):
        pass

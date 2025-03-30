#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\parklife\environmentSvc.py
from carbon.common.lib import telemetry
from carbon.common.script.sys.service import Service
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.sys.idCheckers import IsSolarSystem, IsKnownSpaceSystem
from evedungeons.client.environmenttemplates.loader import DungeonEnvironmentTemplateData
from evedungeons.client.environmenttemplates.tracker import DungeonEnvironmentTemplateTracker
from evegraphics.environments.environment import EnvironmentObject
from evegraphics.environments.environmentManager import EnvironmentManager
from evegraphics.settings import UI_ASTEROID_ATMOSPHERICS
from evegraphics.skyBoxEffects.skyBoxEffectManager import SkyBoxEffectManager
from fsdBuiltData.client.environmentTemplates import GetAllSubEnvironmentTypeIDs, HasAssociatedTemplateID, GetTemplateID, EnvironmentTemplates
from tacticalNavigation.ballparkFunctions import GetBallpark
SOLARSYSTEM_VISUALEFFECT_ENVIRONMENT_ID = {'INCURSION': 2,
 'SHATTEREDWORMHOLE_OVERLAY': 3,
 'THERA': 2519,
 'TRIGLAVIAN_HOME': 2570}

def GetEnvironmentService():
    return sm.GetService('environment')


class EnvironmentService(Service):
    __guid__ = 'svc.environment'
    __servicename__ = 'environment'
    __displayname__ = 'Environment Service'
    __exportedcalls__ = {}
    __notifyevents__ = ['OnSessionChanged',
     'DoBallsRemove',
     'DoBallsAdded',
     'OnEnteringDungeonRoom',
     'OnExitingDungeon',
     'OnGraphicSettingsChanged',
     'OnPrimaryViewChanged',
     'OnClientEvent_JumpStarted',
     'OnClientEvent_JumpExecuted',
     'OnComponentRemovedSystemEnvironment',
     'OnSessionReset',
     'OnLoadScene']
    __startupdependencies__ = ['sceneManager']
    __dependencies__ = ['incursion']
    viewStatesWithoutEnvironments = [ViewState.Hangar]
    viewStatesWithEnvironments = [ViewState.Structure, ViewState.Space]

    def __init__(self):
        super(EnvironmentService, self).__init__()
        self.subEnvironmentTypes = None
        self.skyBoxEffectManager = None

    def Run(self, *args):
        Service.Run(self, *args)
        self.subEnvironmentTypes = GetAllSubEnvironmentTypeIDs()
        EnvironmentTemplates.CacheTemplates()
        EnvironmentTemplates.ConnectToOnReload(EnvironmentTemplates.CacheTemplates)
        EnvironmentManager.GetInstance().SetGetCameraFunction(self.sceneManager.GetActiveCamera)
        EnvironmentManager.GetInstance().SetGetRenderJobFunction(self.sceneManager.GetFisRenderJob)
        templateData = DungeonEnvironmentTemplateData()
        self.dungeonEnvironmentTemplateTracker = DungeonEnvironmentTemplateTracker(templateData)

    def OnSessionReset(self):
        self.ClearAllEnvironments()

    def OnSessionChanged(self, isremote, session, change):
        if 'locationid' in change:
            oldLocation, newLocation = change['locationid']
            if IsSolarSystem(newLocation):
                self.ChangeSolarSystem(oldLocation, newLocation)

    def OnLoadScene(self, scene, key):
        if self.skyBoxEffectManager is None:
            systemPositions = {systemId:system.center for systemId, system in cfg.mapSystemCache.iteritems()}
            self.skyBoxEffectManager = SkyBoxEffectManager(systemPositions)
        if key != 'default' or not IsKnownSpaceSystem(session.solarsystemid):
            return
        if session.stationid is not None:
            return
        self.skyBoxEffectManager.EnterSolarSystem(session.solarsystemid, scene)

    def ChangeSolarSystem(self, oldSolarSystemID, newSolarSystemID):
        EnvironmentManager.GetInstance().RemoveEnvironmentForSolarSystem(oldSolarSystemID)
        self.RefreshSystemWideEnvironment(newSolarSystemID)

    def RefreshSystemWideEnvironment(self, solarSystemID):
        system = cfg.mapSolarSystemContentCache[solarSystemID]
        if self.incursion.IsSystemInIncursion(solarSystemID):
            self._AddSystemEnvironment('incursion', SOLARSYSTEM_VISUALEFFECT_ENVIRONMENT_ID['INCURSION'])
        elif hasattr(system, 'visualEffect'):
            templateID = SOLARSYSTEM_VISUALEFFECT_ENVIRONMENT_ID.get(system.visualEffect, None)
            if templateID is not None:
                self._AddSystemEnvironment(system.visualEffect, templateID)

    def IsDockedInHangar(self):
        return sm.GetService('viewState').GetActiveViewName() in EnvironmentService.viewStatesWithoutEnvironments

    def AddBallEnvironment(self, ball, environmentTemplateID):
        if not EnvironmentManager.ENABLED:
            return
        ballPos = (ball.x, ball.y, ball.z)
        environmentName = str(ball.id)
        systemId = session.solarsystemid or session.solarsystemid2
        EnvironmentManager.GetInstance().AddEnvironment(environmentName, ballPos, environmentTemplateID, systemId)

    def AddSystemEnvironment(self, name, environmentID):
        if self.IsDockedInHangar():
            return
        self._AddSystemEnvironment(name, environmentID)

    def _AddSystemEnvironment(self, name, environmentID):
        if not EnvironmentManager.ENABLED:
            return
        EnvironmentManager.GetInstance().AddEnvironment(name, (0, 0, 0), environmentID, session.solarsystemid2)

    def RemoveEnvironment(self, name):
        envManager = EnvironmentManager.GetInstance()
        envManager.RemoveEnvironment(name)

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, listOfBalls, isRelease):
        manager = EnvironmentManager.GetInstance()
        anchors = manager.GetAllAnchorIDs()
        ballRemovalList = [ ball.id for ball, slimItem, terminal in listOfBalls if ball.id in anchors and HasAssociatedTemplateID(slimItem.typeID, slimItem.skinMaterialSetID) ]
        for ballId in ballRemovalList:
            manager.RemoveEnvironmentAnchor(ballId)

    @telemetry.ZONE_METHOD
    def DoBallsAdded(self, ballsAndSlimItemsToAdd):
        if not EnvironmentManager.ENABLED:
            return
        applicableTypeIDs = [ (slimItem.typeID, slimItem.skinMaterialSetID, ball) for ball, slimItem in ballsAndSlimItemsToAdd if HasAssociatedTemplateID(slimItem.typeID, slimItem.skinMaterialSetID) or slimItem.typeID in self.subEnvironmentTypes ]
        environmentObjects = []
        for typeID, materialSetID, ball in applicableTypeIDs:
            environmentName = str(ball.id)
            systemId = session.solarsystemid or session.solarsystemid2
            templateID = GetTemplateID(typeID, materialSetID)
            ballPos = (ball.x, ball.y, ball.z)
            if EnvironmentManager.GetInstance().IsSubEnvironmentObject(ballPos, typeID):
                environmentObjects.append(EnvironmentObject(typeID, ballPos, ball.radius, ball))
            elif templateID is not None:
                self.LogInfo('Adding environment with template %s and typeID %s' % (templateID, typeID))
                newEnvironment = EnvironmentManager.GetInstance().AddEnvironment(environmentName, ballPos, templateID, systemId, ball.radius, ball, ball.id)
                environmentsToRemove = []
                for environment in EnvironmentManager.GetInstance().GetEnvironmentsForPosition(ballPos):
                    anchorBalls = [ sm.GetService('michelle').GetBall(anchorID) for anchorID in environment.anchorIDs ]
                    anchorBallTypeIDs = [ getattr(anchorBall, 'typeData', {}).get('typeID', None) for anchorBall in anchorBalls ]
                    if all([ ballTypeId in newEnvironment.subEnvironmentTypeIDs for ballTypeId in anchorBallTypeIDs ]):
                        environmentsToRemove.append(environment)
                        for b in anchorBalls:
                            environmentObjects.append(EnvironmentObject(b.typeData['typeID'], (b.x, b.y, b.z), b.radius, b))

                for env in environmentsToRemove:
                    EnvironmentManager.GetInstance().RemoveEnvironment(env.name)

        if len(environmentObjects) != 0:
            self.LogInfo('Adding sub objects [%s]' % ', '.join([ str(e.typeID) for e in environmentObjects ]))
            EnvironmentManager.GetInstance().AddObjectsInEnvironment(environmentObjects)

    def OnGraphicSettingsChanged(self, changes):
        thingsChanged = [ c for c, _ in changes ]
        if UI_ASTEROID_ATMOSPHERICS not in thingsChanged:
            return
        EnvironmentManager.GetInstance().RefreshEnvironments()
        ballpark = GetBallpark()
        if ballpark is None:
            return
        environmentObjects = []
        for ball, slimItem in GetBallpark().GetBallsAndItems():
            ballPos = (ball.x, ball.y, ball.z)
            if EnvironmentManager.GetInstance().IsSubEnvironmentObject(ballPos, slimItem.typeID):
                environmentObjects.append(EnvironmentObject(slimItem.typeID, ballPos, ball.radius, ball))

        if len(environmentObjects) != 0:
            self.LogInfo('OnGraphicSettingsChanged Adding sub objects [%s]' % ', '.join([ str(e.typeID) for e in environmentObjects ]))
            EnvironmentManager.GetInstance().AddObjectsInEnvironment(environmentObjects)

    def OnPrimaryViewChanged(self, oldView, newView):
        disabledState = EnvironmentService.viewStatesWithoutEnvironments
        enabledState = EnvironmentService.viewStatesWithEnvironments
        oldState = getattr(oldView, 'name', None)
        newState = getattr(newView, 'name', None)
        if oldState in enabledState and newState in disabledState:
            EnvironmentManager.GetInstance().ClearAllEnvironments()
        elif newState in enabledState and oldState in disabledState:
            self.RefreshSystemWideEnvironment(session.solarsystemid2)

    def FreezeEnvironments(self, frozen):
        EnvironmentManager.GetInstance().frozen = frozen

    def ClearAllEnvironments(self):
        EnvironmentManager.GetInstance().ClearAllEnvironments()

    def OnClientEvent_JumpStarted(self, *args):
        self.FreezeEnvironments(True)

    def OnClientEvent_JumpExecuted(self, itemID):
        self.FreezeEnvironments(False)
        self.RefreshSystemWideEnvironment(session.solarsystemid2)

    def OnComponentRemovedSystemEnvironment(self, solarSystemID):
        EnvironmentManager.GetInstance().RemoveEnvironmentForSolarSystem(solarSystemID)

    def OnEnteringDungeonRoom(self, dungeonID, roomID, roomPosition, instanceID, dungeonValues):
        self._RemoveActiveDungeonEnvironmentTemplate()
        self.dungeonEnvironmentTemplateTracker.change_dungeon_room(dungeonID, roomID, roomPosition)
        self._AddActiveDungeonEnvironmentTemplate()

    def _AddActiveDungeonEnvironmentTemplate(self):
        dungeonEnvironmentTemplates = self.dungeonEnvironmentTemplateTracker.get_active_dungeon_environment_templates()
        for template in dungeonEnvironmentTemplates:
            EnvironmentManager.GetInstance().AddEnvironment(template.name, template.position, template.template_id, session.solarsystemid2)

    def OnExitingDungeon(self, dungeonID):
        self._RemoveActiveDungeonEnvironmentTemplate()
        self.dungeonEnvironmentTemplateTracker.change_dungeon_room(None, None, None)

    def _RemoveActiveDungeonEnvironmentTemplate(self):
        for template in self.dungeonEnvironmentTemplateTracker.get_active_dungeon_environment_templates():
            EnvironmentManager.GetInstance().RemoveEnvironment(template.name)

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\insider.py
import eveformat
import serverInfo
from agentinteraction.debugwindow import CareerAgentDebugWnd
from carbon.common.script.sys import service, serviceConst
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER, ROLE_GMH, ROLE_GML, ROLE_PROGRAMMER, ROLE_QA
from carbon.common.script.util.format import FmtDate
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.contextMenu.menuEntryData import MenuEntryData, MenuEntryDataCheckbox
from carbonui.control.window import Window
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.services.setting import SessionSettingBool
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.fwEnlistmentWnd import FwEnlistmentWnd
from eve.client.script.ui.skillTree.skillTreeDockablePanel import SkillTreeDockablePanel
from eve.devtools.script.form_sounds import InsiderSoundPlayer
from eve.devtools.script.form_viewer import BinkVideoViewer
from eve.devtools.script.glow import GlowTestWindow
from eve.devtools.script.quasarHijackWnd import ServerRequestHijackWindow, ClientRequestHijackWindow
from eve.devtools.script.svc_invtools import InvToolsWnd
from eve.devtools.script.svc_settingsMgr import SettingsMgr
from eve.devtools.script.type_browser import TypeBrowser
from eve.devtools.script.warpVector import WarpVectorWnd
from eveclientqatools.shaderDebugger import ShaderDebugger
from eveclientqatools.textureViewer import TextureWindow
from eveicon.client.browser import IconBrowserWindow
from eve.devtools.script.menu_bar import MenuBar
from eve.devtools.script.shipEmblems import ShipEmblemsTool
from eve.devtools.script.uiAnimationTest import TestAnimationsWnd
from eve.client.script.environment.spaceObject.nonInteractableObject import NonInteractableObject
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.fileDialog import FileDialog
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.client.script.ui.cosmetics.ship.shipSKINRWindow import ShipSKINRWindow
from eve.client.script.ui.cosmetics.structure.paintToolWnd import PaintToolWnd
from eve.client.script.ui.util import uix
from eve.client.script.ui.util.gradientEdit import GradientEditor
from eve.client.script.ui.view.hangarView import HangarView
from eve.common.script.sys import idCheckers
from eve.devtools.script import localizationTools
from eve.devtools.script.abyssal_content_tool import AbyssalContentToolWindow
from eve.devtools.script.abyssal_npc_spawn_tool import AbyssalNpcSpawnToolWindow
from eve.devtools.script.behaviortools.cluster_debugger import ClusterVisualizerWindow
from eve.devtools.script.cameraTool import CameraTool
from eve.devtools.script.colors import ColorPicker
from eve.devtools.script.colorThemeEditor import ColorThemeEditor
from eve.devtools.script.connectiontest import ConnectionLoopTest
from eve.devtools.script.textStyleTest import TextStyleTest
from eve.devtools.script.uiDebugger import UIDebugger
from eve.devtools.script.uiEventListener import UIEventListener
from eve.devtools.script.uiPerformanceTestWnd import UIPerformanceTestWnd
from eve.devtools.script.uiScaling import UIScaling
from eve.devtools.script.uiSpriteTest import UISpriteTest
from eve.devtools.script.windowManager import WindowManager
from inventorycommon import const as invconst
import evetypes
import blue
import sys
import os
from eve.devtools.script.autobot import AutoBotWindow
import eve.devtools.script.behaviortools.clientdebugadaptors
import trinity
import types
import uthread
import log
import carbonui.const as uiconst
import eveclientqatools.gfxpreviewer as gfxpreviewer
import eveclientqatools.tablereports as gfxreports
import eveclientqatools.corpseviewer as corpseviewer
import eveclientqatools.blueobjectviewer as blueobjviewer
from eveclientqatools import impactVisualizationWnd
from eveclientqatools.environmentTemplateDebugger import EnvironmentTemplateDebugger
from eveclientqatools.environmentTemplateSwitcher import EnvironmentTemplateSwitcher
from eveclientqatools.moonMiningDebug import OpenMoonMiningDebugWindow
from eveclientqatools.performancebenchmark import PerformanceBenchmarkWindow
from eveclientqatools.skyBoxEffectDebugger import SkyBoxEffectDebugger
from eveclientqatools.typevalidationtools import TypeValidationWindow
from eve.devtools.script.uiControlCatalog.controlCatalogWindow import ControlCatalogWindow
from eve.devtools.script.cycleNebulaPanel import CycleNebulaPanel
from eve.devtools.script.renderjobprofiler import RenderJobProfiler
import evegraphics.settings as gfxsettings
from eveclientqatools.explosions import ExplosionDebugger
from eveclientqatools.postProcessDebugger import OpenPostProcessDebugger
from eve.devtools.script.tournamentRefereeTools import RefWindowSpawningWindow
from eve.devtools.script.form_tournament import TournamentWindow
from eve.devtools.script.sunwidget import SunWidgetWindow
from eveclientqatools.audio import AudioActionLog, AudioPrioritizationDebugger, AudioPrioritizationIntrospectionDebugger, AudioEmitterDebugger, MusicDebugger, SoundbankDebugger, SoundPrioritizationConfiguration
from UITree import UITree
from eve.devtools.script.enginetools import EngineToolsLauncher
from eveexceptions import UserError
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from fsdBuiltData.client.travelEffects import GetTravelEffectsGuids
from eve.devtools.script.graphstest import TestGraph
from carbonui.graphs.datafortesting import TogglePriceHistoryTestData
from carbonui.uicore import uicore
from eveservices.menu import StartMenuService
from eveclientqatools.sofpreviewer.viewcontroller import SofPreviewerController
from eveclientqatools.modelstatedebugger import ModelStateDebuggerController
from carbonui.control.contextMenu.contextMenu import CreateMenuView
from carbonui.control.contextMenu.menuDataFactory import CreateMenuDataFromRawTuples
from menu import MenuList
import uihider
from shipprogression.boarding_moment import qa as boarding_moment_qa
from shipprogression.shipUnlockSvc import GetShipUnlockService
FILE_BUNKERS = 'Bunkers.txt'
FILE_ENTITIES = 'Entities.txt'
FILE_GATES = 'GateTest.txt'
FILE_STELLAR = 'StellarReport.txt'
FILE_BELTS = 'BeltTest.txt'
FILE_FWREPORT = 'FacWarReport.txt'
ICON_VISIBILITY_ON = 'res:/UI/Texture/classes/insider/visibility_on_18.png'
ICON_VISIBILITY_OFF = 'res:/UI/Texture/classes/insider/visibility_off_18.png'
Progress = lambda title, text, current, total: sm.GetService('loading').ProgressWnd(title, text, current, total)
qa_green_screen_setting = SessionSettingBool(False)

class InsiderWnd(Window):
    default_top = 0
    default_left = '__center__'
    default_windowID = 'insider'
    default_iconNum = 'res:/UI/Texture/windowIcons/insider.png'
    default_isLightBackground = True
    default_isCompact = True
    default_apply_content_padding = False

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.MakeUncollapseable()
        self.SetCaption('Insider')
        self.SetScope(uiconst.SCOPE_ALL)

    def _OnClose(self, *args):
        settings.public.ui.Set('Insider', False)

    def Reload(self, *args):
        pass


class InsiderService(service.Service):
    __module__ = __name__
    __doc__ = 'Insider v2.0'
    __exportedcalls__ = {'Show': []}
    __guid__ = 'svc.insider'
    __servicename__ = 'insider'
    __displayname__ = 'Insider Service'
    __startupdependencies__ = ['stateSvc', 'uihider']
    __notifyevents__ = ['OnSessionChanged',
     'OnUIRefresh',
     'OnLoadScene',
     'OnViewStateChanged',
     'OnBallparkModelsLoaded']

    def __init__(self):
        super(InsiderService, self).__init__()
        self._res_live_reloader = None
        self.controlCatalogInstanceID = 0
        if self.IsResourceLiveReloadingAvailable():
            from eve.devtools.script.res_live_reload import ResLiveReloader
            self._res_live_reloader = ResLiveReloader()

    def Run(self, memStream = None):
        super(InsiderService, self).Run()
        self.UpdateResourceLiveReloader()

    def HealRemoveAllContainers(self):
        containers = [invconst.groupAuditLogSecureContainer,
         invconst.groupCargoContainer,
         invconst.groupFreightContainer,
         invconst.groupSecureCargoContainer,
         invconst.groupWreck]
        for entry in containers:
            self.HealRemove(entry)

    def HealRemove(self, type, group = True):
        targets = []
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            if group:
                for ballID in bp.balls.keys():
                    item = bp.GetInvItem(ballID)
                    if item and item.groupID == type:
                        targets.append(item.itemID)

            else:
                for ballID in bp.balls.keys():
                    item = bp.GetInvItem(ballID)
                    if item and item.categoryID == type:
                        if type == invconst.categoryStarbase:
                            if sm.GetService('pwn').GetStructureState(item)[0] == 'unanchored':
                                targets.append(item.itemID)
                        elif type == invconst.categoryShip:
                            if not bp.GetBall(ballID).isInteractive:
                                targets.append(item.itemID)
                        else:
                            targets.append(item.itemID)

            for itemID in targets:
                sm.GetService('slash').SlashCmd('heal %d 0' % itemID)

            blue.pyos.synchro.SleepSim(250)

    def SlashBtnClick(self, cmd):
        return lambda : sm.GetService('slash').SlashCmd(cmd)

    def GetInsiderDir(self, *args):
        path = os.path.normpath(blue.sysinfo.GetUserDocumentsDirectory())
        path = os.path.join(path, 'EVE', 'insider')
        return path

    def GetTimestamp(self, *args):
        invalidChars = '\\/:*?"<>| '
        timestamp = FmtDate(blue.os.GetWallclockTime())
        for char in invalidChars:
            timestamp = timestamp.replace(char, '.')

        return timestamp

    def WaitOutSession(self, *args):
        if blue.os.GetSimTime() <= session.nextSessionChange:
            ms = 1000 + 1000L * (session.nextSessionChange - blue.os.GetSimTime()) / 10000000L
            blue.pyos.synchro.SleepSim(ms)

    @staticmethod
    def MakeMenu(list, anchor):
        mv = CreateMenuView(CreateMenuDataFromRawTuples(list), None, None)
        anchorwindow = InsiderWnd.GetIfOpen()
        x = max(anchorwindow.GetChild(anchor).GetAbsolute()[0], 0)
        y = anchorwindow.top + anchorwindow.height
        if anchorwindow.top + anchorwindow.height + mv.height > uicore.desktop.height:
            mv.top = min(anchorwindow.top - mv.height, y)
        else:
            mv.top = min(uicore.desktop.width - mv.height, y)
        mv.left = min(uicore.desktop.width - mv.width, x)
        uicore.layer.menu.children.insert(0, mv)

    def TravelTo(self, destination, *args):
        try:
            sm.GetService('slash').SlashCmd('/tr me %s' % destination)
        except UserError as e:
            if e.msg == 'SystemCheck_TransferFailed_Loading':
                uicore.Message('CustomNotify', {'notify': 'Spooling up system. Please wait.'})
                blue.pyos.synchro.SleepSim(10000)
                sm.GetService('slash').SlashCmd('/tr me %s' % destination)
            sys.exc_clear()

    def TravelToLocation(self, destination, *args):
        if idCheckers.IsSolarSystem(destination):
            currentSys = session.solarsystemid2
            while currentSys != destination:
                self.TravelTo(destination)
                currentSys = session.solarsystemid2

        else:
            try:
                self.TravelTo(destination)
            except UserError as e:
                uicore.Message('CustomNotify', {'notify': 'Spooling up system. Please wait.'})
                blue.pyos.synchro.SleepSim(10000)
                self.TravelTo(destination)

            sys.exc_clear()

    def RegionBunkerTest(self, positive = True, faction = 'All', *args):
        amarr = [10000036, 10000038]
        caldari = [10000033, 10000069]
        gallente = [10000064, 10000068, 10000048]
        minmatar = [10000030, 10000042]
        all = amarr + caldari + gallente + minmatar
        lookUp = {'amarr': amarr,
         'caldari': caldari,
         'gallente': gallente,
         'minmatar': minmatar,
         'all': all}

        def Populate(regionID):
            constellations = []
            systems = []
            constellations = sm.GetService('map').GetChildren(regionID)
            for sys in constellations:
                systems += sm.GetService('map').GetChildren(sys)

            return systems

        allSystems = []
        systemsInFacWar = []
        systemsNotInFacWar = []
        if faction:
            regions = lookUp[faction.lower()]
            for region in regions:
                allSystems += Populate(region)

            fwWarzoneSvc = sm.GetService('fwWarzoneSvc')
            for system in allSystems:
                if fwWarzoneSvc.IsWarzoneSolarSystem(system):
                    systemsInFacWar.append(system)
                else:
                    systemsNotInFacWar.append(system)

            if positive:
                testSystems = systemsInFacWar
                testType = 'Positive'
            else:
                testSystems = systemsNotInFacWar
                testType = 'Negative'
            testLength = len(testSystems)
            testMinutes = testLength / 2
            if uicore.Message('CustomQuestion', {'header': 'Search for bunkers?',
             'question': 'Do you really want to search the region for bunkers? It is %d systems, and will take approximately %d minutes to run.' % (testLength, testMinutes)}, uiconst.YESNO) == uiconst.ID_YES:
                filename = '%s.%s.%s.%s' % (self.GetTimestamp(),
                 faction,
                 testType,
                 FILE_BUNKERS)
                TARGET = os.path.join(self.GetInsiderDir(), filename)
                f = blue.classes.CreateInstance('blue.ResFile')
                if not f.Open(TARGET, 0):
                    f.Create(TARGET)
                f.Write('Bunker typeID\tBunker Name\tBunker itemID\tSystem Occupier\tSystem Sovereignty\tSystem Name\tSystem ID\tConstellation Name\tConstellation ID\tRegion Name\tRegion ID')
                f.Write('\r\n')
                for system in testSystems:
                    self.WaitOutSession()
                    self.TravelToLocation(system)
                    bunkers = []
                    blue.pyos.synchro.SleepSim(5000)
                    bp = sm.GetService('michelle').GetBallpark()
                    if bp:
                        for ballID in bp.balls.keys():
                            item = bp.GetInvItem(ballID)
                            if item and item.groupID in (invconst.groupControlBunker,):
                                bunkers.append(item)

                    systemName = cfg.evelocations.Get(system).name
                    constellation = cfg.evelocations.Get(session.constellationid).name
                    region = cfg.evelocations.Get(session.regionid).name
                    systemSov = cfg.eveowners.Get(sm.RemoteSvc('stationSvc').GetSolarSystem(system).factionID).name
                    if bunkers:
                        for bunker in bunkers:
                            bunkertypeID = bunker.typeID
                            bunkerName = evetypes.GetName(bunkertypeID)
                            bunkeritemID = bunker.itemID
                            occupierID = sm.GetService('facwar').GetSystemOccupier(system)
                            systemOccupier = cfg.eveowners.Get(occupierID).name
                            f.Write('%s' % bunkertypeID)
                            f.Write('\t%s' % bunkerName.encode('utf8'))
                            f.Write('\t%s' % bunkeritemID)
                            f.Write('\t%s' % systemOccupier.encode('utf8'))
                            f.Write('\t%s' % systemSov.encode('utf8'))
                            f.Write('\t%s' % systemName.encode('utf8'))
                            f.Write('\t%s' % system)
                            f.Write('\t%s' % constellation.encode('utf8'))
                            f.Write('\t%s' % session.constellationid)
                            f.Write('\t%s' % region.encode('utf8'))
                            f.Write('\t%s' % session.regionid)
                            f.Write('\r\n')

                    else:
                        bunkertypeID = '-'
                        bunkerName = '-'
                        bunkeritemID = '-'
                        systemOccupier = '-'
                        f.Write('%s' % bunkertypeID)
                        f.Write('\t%s' % bunkerName.encode('utf8'))
                        f.Write('\t%s' % bunkeritemID)
                        f.Write('\t%s' % systemOccupier.encode('utf8'))
                        f.Write('\t%s' % systemSov.encode('utf8'))
                        f.Write('\t%s' % systemName.encode('utf8'))
                        f.Write('\t%s' % system)
                        f.Write('\t%s' % constellation.encode('utf8'))
                        f.Write('\t%s' % session.constellationid)
                        f.Write('\t%s' % region.encode('utf8'))
                        f.Write('\t%s' % session.regionid)
                        f.Write('\r\n')

        try:
            f.Close()
        except:
            sys.exc_clear()

    def EntitySpawn(self, label = None, chosenGroup = None, *args):
        entityDict = {}
        lootEntities = []
        respawnEntities = []
        if label:
            label = label.replace(' ', '_')
            label = label.replace("'", '')
        if chosenGroup.__class__ != list:
            chosenGroup = [chosenGroup]
        for group in chosenGroup:
            if evetypes.GetCategoryIDByGroup(group) in (invconst.categoryEntity,):
                entityDict[group] = []

        for typeID in evetypes.GetTypeIDsByGroups(entityDict.keys()):
            entityDict[evetypes.GetGroupID(typeID)].append(typeID)

        for values in entityDict.itervalues():
            for typeID in values:
                name = evetypes.GetName(typeID)
                if not name.lower().__contains__('test'):
                    lootEntities.append(typeID)

        if uicore.Message('CustomQuestion', {'header': 'Spawn NPCs?',
         'question': "Do you really want to spawn all those NPCs? It's quite alot (%d entities in %d groups)" % (len(lootEntities), len(entityDict))}, uiconst.YESNO) == uiconst.ID_YES:
            filename = '%s.%s.%s' % (self.GetTimestamp(), label, FILE_ENTITIES)
            TARGET = os.path.join(self.GetInsiderDir(), filename)
            f = blue.classes.CreateInstance('blue.ResFile')
            if not f.Open(TARGET, 0):
                f.Create(TARGET)
            f.Write('Status\tLoot\tEmpty\tTypeID\tEntity Type\tWreck Type\tEntity Name\tWreck Name\tWreck State')
            f.Write('\r\n')
            for entity in lootEntities:
                dudSpawn = False
                if evetypes.GetIsGroupAnchoredByGroup(evetypes.GetGroupID(entity)):
                    respawnEntities.append(entity)
                    print 'appended entity %s' % entity
                    continue
                else:
                    blue.pyos.synchro.SleepSim(1000)
                    sm.GetService('slash').SlashCmd('/entity deploy 10 %d' % entity)
                blue.pyos.synchro.SleepSim(1000)
                sm.GetService('slash').SlashCmd('/nuke')
                blue.pyos.synchro.SleepSim(2000)
                wrecks = []
                count = 1000
                while not wrecks and count:
                    count -= 1
                    bp = sm.GetService('michelle').GetBallpark()
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.groupID in (invconst.groupWreck, invconst.groupCargoContainer):
                            wrecks.append(item.itemID)

                if not wrecks:
                    blue.pyos.synchro.SleepSim(5000)
                    bp = sm.GetService('michelle').GetBallpark()
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.groupID in (invconst.groupWreck, invconst.groupCargoContainer):
                            wrecks.append(item.itemID)

                if not wrecks:
                    dudSpawn = True
                emptyWreck = int()
                okWreck = int()
                entityType = evetypes.GetGroupName(entity)
                entityName = evetypes.GetName(entity)
                idealWreckName = '%s Wreck' % entityName
                if not dudSpawn:
                    actualWreckName = 'None'
                    for wreckID in wrecks:
                        empty = self.stateSvc.CheckWreckEmpty(bp.GetInvItem(wreckID))
                        if empty:
                            emptyWreck += 1
                        else:
                            okWreck += 1
                        actualWreckName = cfg.evelocations.Get(wreckID).name
                        wreckType = evetypes.GetName(sm.GetService('michelle').GetBallpark().GetInvItem(wreckID).typeID)

                    wreckNameState = 'Error'
                    if idealWreckName == actualWreckName:
                        wreckNameState = 'OK'
                    try:
                        if okWreck > emptyWreck:
                            f.Write('OK')
                            f.Write('\t%s' % okWreck)
                            f.Write('\t%s' % emptyWreck)
                            f.Write('\t%s' % entity)
                            f.Write('\t%s' % entityType.encode('utf8'))
                            f.Write('\t%s' % wreckType.encode('utf8'))
                            f.Write('\t%s' % entityName.encode('utf8'))
                            f.Write('\t%s' % actualWreckName.encode('utf8'))
                            f.Write('\t%s' % wreckNameState)
                            f.Write('\r\n')
                        elif not okWreck:
                            f.Write('Critical')
                            f.Write('\t-\t-\t%s' % entity)
                            f.Write('\t%s' % entityType.encode('utf8'))
                            f.Write('\t%s' % wreckType.encode('utf8'))
                            f.Write('\t%s' % entityName.encode('utf8'))
                            f.Write('\t%s' % actualWreckName.encode('utf8'))
                            f.Write('\t%s' % wreckNameState)
                            f.Write('\r\n')
                        else:
                            f.Write('Warning')
                            f.Write('\t%s' % okWreck)
                            f.Write('\t%s' % emptyWreck)
                            f.Write('\t%s' % entity)
                            f.Write('\t%s' % entityType.encode('utf8'))
                            f.Write('\t%s' % wreckType.encode('utf8'))
                            f.Write('\t%s' % entityName.encode('utf8'))
                            f.Write('\t%s' % actualWreckName.encode('utf8'))
                            f.Write('\t%s' % wreckNameState)
                            f.Write('\r\n')
                    except:
                        sys.exc_clear()
                        f.Write('\r\n')
                        f.Write('Fail')
                        f.Write('\t-\t-\t%s' % entity)
                        f.Write('\t%s' % entityType.encode('utf8'))
                        f.Write('\t%s' % entityName.encode('utf8'))
                        f.Write('\r\n')

                else:
                    f.Write('Null')
                    f.Write('\t-\t-\t%s' % entity)
                    f.Write('\t%s' % entityType.encode('utf8'))
                    f.Write('\t%s' % entityName.encode('utf8'))
                    f.Write('\tNone\tNone\tNone')
                    f.Write('\r\n')
                self.HealRemove(invconst.groupWreck)
                self.HealRemove(invconst.groupCargoContainer)

            if respawnEntities:
                f.Write('\r\n')
                f.Write('The following entities respawn over time and were not tested:')
                f.Write('\r\n')
                for entity in respawnEntities:
                    entityType = evetypes.GetGroupName(entity)
                    entityName = evetypes.GetName(entity)
                    f.Write('Unspawned')
                    f.Write('\t\t\t%s' % entity)
                    f.Write('\t%s' % entityType.encode('utf8'))
                    f.Write('\t%s' % entityName.encode('utf8'))
                    f.Write('\r\n')

        try:
            f.Close()
        except:
            sys.exc_clear()

    def RegionGateTest(self, constellation = None, *args):

        def Populate(areaOfInterest):
            data = {}
            systems = []
            mapSvc = sm.GetService('map')
            systemmapSvc = sm.GetService('systemmap')
            if areaOfInterest.__class__ != list:
                areaOfInterest = [areaOfInterest]
            for constellation in areaOfInterest:
                systems += mapSvc.GetChildren(constellation)

            for system in systems:
                title = 'Examining Systems...'
                systemName = cfg.evelocations.Get(system).name
                constellationID = cfg.evelocations.Get(mapSvc.GetParent(system))
                constellationName = cfg.evelocations.Get(constellationID).name
                regionID = cfg.evelocations.Get(mapSvc.GetParent(constellationID.id))
                regionName = cfg.evelocations.Get(regionID).name
                text = '%s, %s, %s' % (systemName, constellationName, regionName)
                Progress(title, text, systems.index(system), len(systems))
                systemItems = systemmapSvc.GetSolarsystemData(system)
                systemItems = systemItems.Index('itemID')
                stargates = {}
                for object in systemItems:
                    item = systemItems[object]
                    if evetypes.GetGroupID(item.typeID) in (invconst.groupStargate,):
                        stargates[item.itemName] = {'gateID': item.itemID,
                         'destGateID': item.destinations[0]}

                data[system] = stargates

            Progress('Mapping Complete!', 'Done!', 1, 1)
            return data

        def Wait(count, *args):
            blue.pyos.synchro.SleepSim(count * 1000)

        sysCount = int()
        jumpCount = int()
        regionData = Populate(constellation)
        for k, v in regionData.iteritems():
            sysCount += 1
            jumpCount += len(v)

        approxDuration = jumpCount * 0.5
        if uicore.Message('CustomQuestion', {'header': 'Travel the universe?',
         'question': 'Do you really want to visit all the gates in this region? It will take approximately %d minutes.' % approxDuration}, uiconst.YESNO) == uiconst.ID_YES:
            filename = '%s.%s.%s' % (self.GetTimestamp(), cfg.evelocations.Get(session.regionid).name, FILE_GATES)
            f = blue.classes.CreateInstance('blue.ResFile')
            TARGET = os.path.join(self.GetInsiderDir(), filename)
            if not f.Open(TARGET, 0):
                f.Create(TARGET)
            gok = int()
            gfail = int()
            sok = int()
            sfail = int()
            stargates = []
            self.WaitOutSession()
            for system, gates in regionData.iteritems():
                f.Write('%s' % cfg.evelocations.Get(system).name.encode('utf8'))
                f.Write('\r\n')
                for name, info in gates.iteritems():
                    sysdest = name.split('(')[1].split(')')[0]
                    f.Write('-> %s' % sysdest.encode('utf8'))
                    f.Write('\r\n')
                    sysdestID = sm.RemoteSvc('lookupSvc').LookupLocationsByGroup(invconst.groupSolarSystem, sysdest)
                    for each in sysdestID:
                        sysdestID = each.itemID

                    Wait(5)
                    self.TravelToLocation(system)
                    Wait(5)
                    bp = sm.GetService('michelle').GetBallpark()
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.groupID in (invconst.groupStargate,):
                            stargates.append(item.itemID)

                    if info['gateID'] in stargates:
                        self.TravelToLocation(info['gateID'])
                        self.WaitOutSession()
                        Wait(5)
                        try:
                            sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.GetService('michelle').GetRemotePark().CmdStargateJump, info['gateID'], info['destGateID'], session.shipid)
                            Wait(10)
                        except:
                            sys.exc_clear()
                            f.Write('\t\tERROR: Jump failed')
                            f.Write('\r\n')

                    stargates = []
                    bp = sm.GetService('michelle').GetBallpark()
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.groupID in (invconst.groupStargate,):
                            data = sm.GetService('tactical').GetEntryData(item, bp.GetBall(item.itemID))
                            distance = data.ball().surfaceDist
                            stargates.append(item.itemID)

                    if info['destGateID'] in stargates:
                        item = bp.GetInvItem(info['destGateID'])
                        distance = sm.GetService('tactical').GetEntryData(item, bp.GetBall(item.itemID)).ball().surfaceDist
                        if distance < 50000:
                            gok += 1
                            f.Write('\t\tGate: OK')
                            f.Write('\r\n')
                        else:
                            f.Write('\t\tGate: There, but distant')
                            f.Write('\r\n')
                    else:
                        gfail += 1
                        f.Write('\t\tGate: FAIL')
                        f.Write('\r\n')
                    if cfg.evelocations.Get(session.locationid).name == sysdest:
                        sok += 1
                        f.Write('\t\tSystem: OK')
                        f.Write('\r\n')
                    else:
                        sfail += 1
                        f.Write('\t\tSystem: FAIL')
                        f.Write('\r\n')
                    self.WaitOutSession()

                f.Write('-----------------')
                f.Write('\r\n')

            f.Write('Gates:')
            f.Write('\r\n')
            f.Write('\tOK: %s' % gok)
            f.Write('\r\n')
            f.Write('\tFAIL: %s' % gfail)
            f.Write('\r\n')
            f.Write('Systems:')
            f.Write('\r\n')
            f.Write('\tOK: %s' % sok)
            f.Write('\r\n')
            f.Write('\tFAIL: %s' % sfail)
            f.Write('\r\n')
            f.Close()

    def StoreRegionData(self, *args):
        constellations = []
        systems = []
        constellations = sm.GetService('map').GetChildren(session.regionid)
        for sys in constellations:
            systems += sm.GetService('map').GetChildren(sys)

        regionName = cfg.evelocations.Get(session.regionid).name
        filename = '%s.%s.%s' % (self.GetTimestamp(), regionName, FILE_STELLAR)
        f = blue.classes.CreateInstance('blue.ResFile')
        TARGET = os.path.join(self.GetInsiderDir(), filename)
        if not f.Open(TARGET, 0):
            f.Create(TARGET)
        f.Write('Object itemID\tObject typeID\tObject Type\tName\tLocation ID\tDestination\tx\ty\tz\tObject orbitID')
        f.Write('\r\n')
        for system in systems:
            title = 'Examining Systems...'
            systemName = cfg.evelocations.Get(system).name
            constellationID = cfg.evelocations.Get(sm.GetService('map').GetParent(system))
            constellationName = cfg.evelocations.Get(constellationID).name
            text = '%s, %s' % (systemName, constellationName)
            Progress(title, text, systems.index(system), len(systems))
            systemItems = sm.GetService('systemmap').GetSolarsystemData(system)
            for object in systemItems:
                f.Write('%s' % object.itemID)
                f.Write('\t%s' % object.typeID)
                f.Write('\t%s' % evetypes.GetName(object.typeID).encode('utf8'))
                f.Write('\t%s' % object.itemName.encode('utf8'))
                f.Write('\t%s' % object.locationID)
                f.Write('\t%s' % object.destinations.__str__())
                f.Write('\t%g' % object.x)
                f.Write('\t%g' % object.y)
                f.Write('\t%g' % object.z)
                f.Write('\t%s' % object.orbitID)
                f.Write('\r\n')

        try:
            f.Close()
        except:
            sys.exc_clear()

        Progress('Mapping Complete!', 'Done!', 1, 1)

    def RegionBeltTest(self, constellation = None, *args):

        def Populate(areaOfInterest):
            systems = []
            belts = []
            if areaOfInterest.__class__ != list:
                areaOfInterest = [areaOfInterest]
            for constellation in areaOfInterest:
                systems += sm.GetService('map').GetChildren(constellation)

            for system in systems:
                title = 'Examining Systems...'
                systemName = cfg.evelocations.Get(system).name
                constellationID = cfg.evelocations.Get(sm.GetService('map').GetParent(system))
                constellationName = cfg.evelocations.Get(constellationID).name
                regionID = cfg.evelocations.Get(sm.GetService('map').GetParent(constellationID.id))
                regionName = cfg.evelocations.Get(regionID).name
                text = '%s, %s, %s' % (systemName, constellationName, regionName)
                Progress(title, text, systems.index(system), len(systems))
                systemItems = sm.GetService('systemmap').GetSolarsystemData(system)
                systemItems = systemItems.Index('itemID')
                for object in systemItems:
                    item = systemItems[object]
                    if evetypes.GetGroupID(item.typeID) in (invconst.groupAsteroidBelt,):
                        belts.append(item.itemID)

            Progress('Mapping Complete!', 'Done!', 1, 1)
            return (belts, systems)

        def Wait(count, *args):
            blue.pyos.synchro.SleepSim(count * 1000)

        if not constellation:
            return
        regionBeltData, regionSystemData = Populate(constellation)
        sysCount = len(regionSystemData)
        approxDuration = sysCount * 0.5
        if uicore.Message('CustomQuestion', {'header': 'Travel the universe?',
         'question': 'Do you really want to visit all the belts in this region? It will take approximately %d minutes.' % approxDuration}, uiconst.YESNO) == uiconst.ID_YES:
            filename = '%s.%s.%s' % (self.GetTimestamp(), cfg.evelocations.Get(session.regionid).name, FILE_BELTS)
            f = blue.classes.CreateInstance('blue.ResFile')
            TARGET = os.path.join(self.GetInsiderDir(), filename)
            if not f.Open(TARGET, 0):
                f.Create(TARGET)
            asteroidGroups = []
            for groupID in evetypes.GetGroupIDsByCategory(invconst.categoryAsteroid):
                asteroidGroups.append(groupID)

            f.Write('Solarsystem itemID\tSolarsystem Name\tBelt itemID\tBelt Name\tAsteroid Types Present')
            f.Write('\r\n')
            for belt in regionBeltData:
                survey = []
                try:
                    self.TravelToLocation(belt)
                except:
                    sys.exc_clear()
                    self.WaitOutSession()
                    self.TravelToLocation(belt)

                Wait(5)
                bp = sm.GetService('michelle').GetBallpark()
                gotBelt = False
                bpCount = int()
                while not gotBelt:
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.itemID == belt:
                            gotBelt = True
                            break

                    bpCount += 1
                    if bpCount > 10:
                        break
                    Wait(5)
                    bp = sm.GetService('michelle').GetBallpark()

                if gotBelt:
                    for ballID in bp.balls.keys():
                        item = bp.GetInvItem(ballID)
                        if item and item.groupID in asteroidGroups:
                            if survey.__contains__(item.typeID):
                                pass
                            else:
                                survey.append(item.typeID)

                    if not survey:
                        Wait(5)
                        bp = sm.GetService('michelle').GetBallpark()
                        for ballID in bp.balls.keys():
                            item = bp.GetInvItem(ballID)
                            if item and item.groupID in asteroidGroups:
                                if survey.__contains__(item.typeID):
                                    pass
                                else:
                                    survey.append(item.typeID)

                    survey.sort()
                    f.Write('%s' % session.locationid)
                    f.Write('\t%s' % cfg.evelocations.Get(session.solarsystemid2).name.encode('utf8'))
                    f.Write('\t%s' % belt)
                    f.Write('\t%s' % cfg.evelocations.Get(belt).name.encode('utf8'))
                    f.Write('\t')
                    for asteroid in survey:
                        f.Write('%s, ' % evetypes.GetName(asteroid).encode('utf8'))

                    f.Write('\r\n')

            try:
                f.Close()
            except:
                sys.exc_clear()

    def _V3TestingLoop(self, path):
        myShip = sm.GetService('michelle').GetBallpark().GetBall(eve.session.shipid)
        myShip.model.display = False
        f = open(path, 'rt')
        fc = f.readlines()
        errorCount = 0
        i = 1
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        if scene is not None:
            for li in fc:
                log.LogError('LOADING ' + str(i) + ' of ' + str(len(fc)) + ' : ' + str(int(li)))
                redFile = GetGraphicFile(int(li))
                log.LogError(redFile)
                if redFile is None:
                    errorCount += 1
                else:
                    ship = trinity.Load(redFile)
                    scene.objects.append(ship)
                    blue.synchro.Sleep(2000)
                    scene.objects.remove(ship)
                i += 1

        log.LogError('FINISHED V3 testing...')
        log.LogError('DETECTED at least ' + str(errorCount) + ' problems!')
        myShip.model.display = True

    def CycleNebulas(self, *args):
        CycleNebulaPanel(parent=uicore.layer.main, name='CycleNebulaPanel', caption='Cycle Nebulas')

    def _RenderJobProfiler(self, *args):
        RenderJobProfiler()

    def _CrashVideoDriver(self, *_):
        from trinity.crashdriver import crash
        uthread.new(crash)

    @property
    def _SofPreviewerViewController(self):
        if not hasattr(self, '__sofpreviewerViewController'):
            self.__sofpreviewerViewController = SofPreviewerController()
        return self.__sofpreviewerViewController

    def V3Testing(self, *args):
        log.LogError('Starting V3 testing...')
        dlgRes = FileDialog.SelectFiles(fileExtensions=['.txt'], multiSelect=False)
        if dlgRes is not None:
            scriptPath = dlgRes.Get('files')[0]
            log.LogWarn('script: ' + str(scriptPath))
            uthread.new(self._V3TestingLoop, str(scriptPath))

    def Automated(self, *args):
        allIDs = []
        usedIDs = []
        spawnMenu = MenuList()
        fw = MenuList()
        entitySpawnGroups = ['Asteroid Angel Cartel',
         'Asteroid Blood Raiders',
         'Asteroid Guristas',
         'Asteroid Rogue Drone',
         "Asteroid Sansha's Nation",
         'Asteroid Serpentis',
         'Deadspace Angel Cartel',
         'Deadspace Blood Raiders',
         'Deadspace Guristas',
         'Deadspace Overseer',
         'Deadspace Rogue Drone',
         "Deadspace Sansha's Nation",
         'Deadspace Serpentis',
         'Mission Amarr Empire',
         'Mission CONCORD',
         'Mission Caldari State',
         'Mission Drone',
         'Mission Gallente Federation',
         'Mission Generic',
         'Mission Khanid',
         'Mission Minmatar Republic',
         'Mission Mordu',
         'Mission Thukker',
         'Storyline',
         'Other']
        noLootEntities = [invconst.groupConcordDrone, invconst.groupFactionDrone, invconst.groupPoliceDrone]
        dontSpawn = [invconst.groupBillboard,
         invconst.groupSentryGun,
         invconst.groupCapturePointTower,
         invconst.groupProtectiveSentryGun,
         invconst.groupCustomsOfficial]
        entitiesDict = {}
        nameDict = {}
        entityByGroup = {}
        for groupID in evetypes.GetGroupIDsByCategory(invconst.categoryEntity):
            if groupID not in noLootEntities:
                if groupID not in dontSpawn:
                    entitiesDict[groupID] = []

        for typeID in evetypes.GetTypeIDsByGroups(entitiesDict.keys()):
            entitiesDict[evetypes.GetGroupID(typeID)].append(typeID)

        for id in entitiesDict.iterkeys():
            nameDict[id] = [evetypes.GetGroupNameByGroup(id)]

        for group in entitySpawnGroups:
            for id, name in nameDict.iteritems():
                if name[0].lower().startswith(group.lower()):
                    if entityByGroup.has_key(group):
                        entityByGroup[group].append(id)
                        usedIDs.append(id)
                        allIDs.append(id)
                    else:
                        entityByGroup[group] = [id]
                        usedIDs.append(id)
                        allIDs.append(id)

        for id in nameDict.iterkeys():
            if id not in usedIDs:
                if entityByGroup.has_key('Other'):
                    entityByGroup['Other'].append(id)
                    allIDs.append(id)
                else:
                    entityByGroup['Other'] = [id]
                    allIDs.append(id)

        for displayName, idList in entityByGroup.iteritems():
            spawnMenu.append((displayName, lambda label = displayName, ids = idList: self.EntitySpawn(label, ids)))

        spawnMenu.sort()
        spawnMenu.append(None)
        spawnMenu.append(('No loot entities', lambda label = 'noloot', ids = noLootEntities: self.EntitySpawn(label, ids)))
        spawnMenu.append(None)
        spawnMenu.append(('<color=0xffff8080>All', lambda label = 'All', ids = allIDs: self.EntitySpawn(label, ids)))
        if session.regionid:
            beltMenu = MenuList()
            constellationInRegion = cfg.mapRegionCache[session.regionid].constellationIDs
            for constellationID in constellationInRegion:
                label = cfg.evelocations.Get(constellationID).name
                beltMenu.append((label, lambda ids = constellationID: self.RegionBeltTest(ids)))

            beltMenu.sort()
            beltMenu.append(None)
            beltMenu.append(('<color=0xffff8080>All', lambda ids = constellationInRegion: self.RegionBeltTest(ids)))
            gateMenu = MenuList()
            for constellationID in constellationInRegion:
                label = cfg.evelocations.Get(constellationID).name
                gateMenu.append((label, lambda ids = constellationID: self.RegionGateTest(ids)))

            gateMenu.sort()
            gateMenu.append(None)
            gateMenu.append(('<color=0xffff8080>All', lambda ids = constellationInRegion: self.RegionGateTest(ids)))
            (fw.append(('FW Bunker Locations', [('Amarr - Positive', lambda : self.RegionBunkerTest(True, 'Amarr')),
               ('Amarr - Negative', lambda : self.RegionBunkerTest(False, 'Amarr')),
               None,
               ('Caldari - Positive', lambda : self.RegionBunkerTest(True, 'Caldari')),
               ('Caldari - Negative', lambda : self.RegionBunkerTest(False, 'Caldari')),
               None,
               ('Gallente - Positive', lambda : self.RegionBunkerTest(True, 'Gallente')),
               ('Gallente - Negative', lambda : self.RegionBunkerTest(False, 'Gallente')),
               None,
               ('Minmatar - Positive', lambda : self.RegionBunkerTest(True, 'Minmatar')),
               ('Minmatar - Negative', lambda : self.RegionBunkerTest(False, 'Minmatar')),
               None,
               ('<color=0xffff8080>All - Positive', lambda : self.RegionBunkerTest(True, 'All')),
               ('<color=0xffff8080>All - Negative', lambda : self.RegionBunkerTest(False, 'All'))])),)
            fw.append(None)
            fw.append(('NPC Loot Test', spawnMenu))
            fw.append(None)
            fw.append(('Belt Contents Survey', beltMenu))
            fw.append(('Gate Jump Test', gateMenu))
            fw.append(None)
            fw.append(('Client ReConnection Loop', lambda : ConnectionLoopTest.Open()))
            fw.append(None)
            fw.append(('Stellar Objects Report', lambda : self.StoreRegionData()))
            fw.append(None)
            fw.append(('Spambot 2000', lambda : sm.GetService('cspam').Show()))
            fw.append(None)
            fw.append(('Type Validation', TypeValidationWindow.Open))
        return fw

    def OnSessionChanged(self, isRemote, sess, change):
        debugRenderJob = None
        for job in trinity.renderJobs.recurring:
            if job.name == 'DebugRender':
                debugRenderJob = job
                break

        if debugRenderJob:
            trinity.renderJobs.recurring.remove(debugRenderJob)
        AudioEmitterDebugger.EnableDebuggerInScene()

    def OnLoadScene(self, scene, key):
        AudioEmitterDebugger.EnableDebuggerInScene()

    def OnBallparkModelsLoaded(self):
        AudioEmitterDebugger.EnableDebuggerInScene()

    def OnViewStateChanged(self, oldView, newView):
        AudioEmitterDebugger.EnableDebuggerInScene()

    def QAMenu(self, *args):
        m = MenuList()
        m.append(('Automated Tasks', self.Automated()))
        m.append(None)

        def SetAntiAliasing(aaType):
            gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, aaType, False)
            sm.ScatterEvent('OnGraphicSettingsChanged', [gfxsettings.GFX_ANTI_ALIASING])

        def ToggleGreenscreen():
            qa_green_screen_setting.toggle()
            scm = sm.GetService('sceneManager')
            scene = scm.GetRegisteredScene('default')
            scene.backgroundRenderingEnabled = not qa_green_screen_setting.is_enabled()
            clearStep = scm.fisRenderJob.GetStep('CLEAR')
            clearStep.color = (0, 1, 0, 1)

        def ToggleSceneGraphics():
            scm = sm.GetService('sceneManager')
            scene = scm.GetRegisteredScene('default')
            rj = scm.fisRenderJob
            display = not scene.display
            rj.EnablePostProcessing(display)
            scene.display = display

        def RemoveSun():
            solarsystem = cfg.mapSolarSystemContentCache[session.solarsystemid]
            sunID = solarsystem.star.id
            sm.GetService('michelle').GetBall(sunID).Release()

        def EnableSpaceMouseInMaps():
            from eve.client.script.ui.shared.mapView import mapViewNavigation
            mapViewNavigation.spaceMouseSupportEnabled = True

        def ToggleNonInteractability():
            m = sm.GetService('michelle')
            bp = m.GetBallpark()
            for ball, slim in bp.GetBallsAndItems():
                if isinstance(ball, NonInteractableObject) and hasattr(getattr(ball, 'model'), 'isPickable'):
                    ball.model.isPickable = not ball.model.isPickable

        def SetLag(time):
            time = float(time)
            blue.os.slugTimeMinMs = time
            blue.os.slugTimeMaxMs = time

        def SetReflectionProbe(use):
            scm = sm.GetService('sceneManager')
            scene = scm.GetActiveScene()
            scene.reflectionProbe = trinity.Tr2ReflectionProbe() if use else None

        def CreateEffectOverrideLambda(guid):
            return lambda : sm.GetService('subway').SetEffectOverride(guid)

        def CreateOverrideHangarSceneLambda(sceneType):
            return lambda : HangarView.SetHangarOverride(sceneType)

        def ToggleDroneBehaviorSystem():
            scm = sm.GetService('sceneManager')
            scene = scm.GetActiveScene()
            droneSystem = scene.objects.Find('trinity.EveChildBehaviorSystem')
            for sys in droneSystem:
                sys.display = not sys.display

        def GetSceneVisulaizationMethods():
            return {getattr(trinity.EveVisualizeMethod, n):n for n in dir(trinity.EveVisualizeMethod) if not callable(getattr(trinity.EveVisualizeMethod, n))}

        def SetSceneVisualizationCallback(value):

            def __inner__():
                sm.GetService('sceneManager').GetActiveScene().visualizeMethod = value

            return __inner__

        def GetSceneVisualization():
            return sm.GetService('sceneManager').GetActiveScene().visualizeMethod

        m.append(('Audio', [('Audio Introspection', AudioActionLog.Open),
          ('Music Debugger', MusicDebugger.Open),
          ('Reload Soundbanks', SoundbankDebugger.Toggle),
          ('%s Audio Emitters' % ['Show', 'Hide'][sm.GetService('audio').GetDebugDisplayAllEmitters()], AudioEmitterDebugger.Toggle),
          ('%s Audio Prioritization' % ['Enable', 'Disable'][AudioPrioritizationDebugger.GetCullingEnabled()], AudioPrioritizationDebugger.Toggle),
          ('Audio Emitter Priority', AudioPrioritizationIntrospectionDebugger.Open),
          ('Sound Prioritization Configuration', SoundPrioritizationConfiguration.Open)]))
        m.append(('Graphics', [('Tools', (('Environment Template', (('Debugger', EnvironmentTemplateDebugger().ShowUI), ('Switcher', EnvironmentTemplateSwitcher().ShowUI))),
            ('Explosions', ExplosionDebugger().ShowUI),
            ('Moon Mining', OpenMoonMiningDebugWindow),
            ('PostProcess', OpenPostProcessDebugger),
            ('Sky Box Effect', SkyBoxEffectDebugger().ShowUI),
            ('SOF Previewer', lambda : self._SofPreviewerViewController.ShowUI()),
            ('Sun', lambda : SunWidgetWindow()),
            ('Scene Debugging', [('Visualizations', [ (v + (' - Selected' if GetSceneVisualization() == k else ''), SetSceneVisualizationCallback(k)) for k, v in GetSceneVisulaizationMethods().iteritems() ]), ('Shader Debugger', lambda : ShaderDebugger(object=sm.GetService('sceneManager').GetActiveScene()))]))),
          ('Textures', (('Depth', OpenDepthTextureView),
            ('Reflection', OpenReflectionTextureView),
            ('Normal', OpenNormalTextureView),
            ('SSAO', OpenSSAOTextureView),
            ('Shadow', OpenShadowTextureView),
            ('Velocity', OpenVelocityTextureView))),
          ('V3 testing', lambda : self.V3Testing()),
          ('Cycle nebulas', lambda : self.CycleNebulas()),
          ('Toggle non interactable object picking', lambda : ToggleNonInteractability()),
          ('Performance Benchmark', lambda : PerformanceBenchmarkWindow()),
          ('Render Job Profiler', self._RenderJobProfiler),
          ('Crash Video Driver', self._CrashVideoDriver),
          ('Corpse Previewer', corpseviewer.CorpsePreviewer(sm.GetService('sceneManager')).ShowUI),
          ('Asset Previewer', gfxpreviewer.AssetPreviewer(sm.GetService('sceneManager')).ShowUI),
          ('Warp Effect Debug', gfxreports.ShowWarpEffectReport),
          ('Flight Controls Debug', sm.GetService('flightControls').simulation.ToggleDebug),
          ('Toggle Drone Behavior System', ToggleDroneBehaviorSystem),
          ('Hangar Override', tuple([(['None', 'None - Selected'][HangarView.HANGAR_TYPE_OVERRIDE is None], CreateOverrideHangarSceneLambda(None))] + [ ([ht, '%s - Selected' % ht][HangarView.HANGAR_TYPE_OVERRIDE == ht], CreateOverrideHangarSceneLambda(ht)) for ht in HangarView.HANGAR_TYPE_OVERRIDE_VALUES ])),
          ('SSAO Quality', (('Disabled', lambda : SetSSAOQuality(0)),
            ('Low', lambda : SetSSAOQuality(1)),
            ('Medium', lambda : SetSSAOQuality(2)),
            ('High', lambda : SetSSAOQuality(3)))),
          ('GDPR', (('Enable', lambda : EnableGDPR(True)), ('Disable', lambda : EnableGDPR(False)))),
          ('Upscaling', (('Enable', lambda : EnableUpscaling(True)), ('Disable', lambda : EnableUpscaling(False)))),
          ('Raytracing', (('Enable', lambda : EnableRaytracing(True)), ('Disable', lambda : EnableRaytracing(False)))),
          ('Jump Effects', (('%s New Jump Effects' % ['Enable', 'Disable'][sm.GetService('subway').Enabled()], sm.GetService('subway').Toggle),
            ('%s Jump Effect Kill Switch' % ['Enable', 'Disable'][sm.GetService('subway').FORCE_KILL_SWITCH], sm.GetService('subway').ToggleKillSwitch),
            ('Set Jump Delay', SetJumpDelay),
            ('Jump Effect Overrides', [('None' + ['', ' - enabled'][sm.GetService('subway').JUMP_EFFECT_OVERRIDE == None], CreateEffectOverrideLambda(None))] + [ (guid + ['', ' - enabled'][sm.GetService('subway').JUMP_EFFECT_OVERRIDE == guid], CreateEffectOverrideLambda(guid)) for guid in GetTravelEffectsGuids() ]))),
          ('Green Background', ToggleGreenscreen),
          ('Delete Sun', RemoveSun),
          ('Toggle Graphics', ToggleSceneGraphics),
          ('AntiAliasing', (('Disabled', lambda : SetAntiAliasing(gfxsettings.AA_QUALITY_DISABLED)),
            ('Low TAA', lambda : SetAntiAliasing(gfxsettings.AA_QUALITY_TAA_LOW)),
            ('Medium TAA', lambda : SetAntiAliasing(gfxsettings.AA_QUALITY_TAA_MEDIUM)),
            ('High TAA', lambda : SetAntiAliasing(gfxsettings.AA_QUALITY_TAA_HIGH)))),
          ('Reflection probe', (('Enable', lambda : SetReflectionProbe(True)), ('Disable', lambda : SetReflectionProbe(False)))),
          ('Enable SpaceMouse In Maps', EnableSpaceMouseInMaps),
          ('Set Lag in MS', (('None', lambda : SetLag(0)),
            ('50', lambda : SetLag(50)),
            ('100', lambda : SetLag(100)),
            ('500', lambda : SetLag(500)),
            ('1000', lambda : SetLag(1000)),
            ('2000', lambda : SetLag(2000)),
            ('3000', lambda : SetLag(3000)))),
          None,
          ('Managed RT Report', gfxreports.ShowManagedRTReport),
          ('Blue Resources', gfxreports.ShowBlueResourceReport),
          None,
          ('LOD Report', gfxreports.ShowLODOverviewReport),
          ('Explosion Pool Report', gfxreports.ShowExplosionPoolReport),
          ('Effect Activation Report', gfxreports.ShowEffectActivationReport),
          None,
          ('Planet Texture Report', gfxreports.ShowPlanetTextureReport),
          ('Planet Status Report', gfxreports.ShowPlanetStatusReport),
          None,
          ('Inspect Scene', lambda : blueobjviewer.Show(sm.GetService('sceneManager').GetActiveScene())),
          ('Inspect RenderJob', lambda : blueobjviewer.Show(sm.GetService('sceneManager').fisRenderJob))]))
        from eve.client.script.ui.shared.launchdarkly.debugwindow import LaunchDarklyDebugWindow
        from eve.devtools.script.methodcallsmonitor import MethodCallsMonitor
        m.append(('Network', [(MethodCallsMonitor.default_caption, MethodCallsMonitor.Open), ('LaunchDarkly', LaunchDarklyDebugWindow.Open)]))
        m.append(('Quasar', [("Client Request Hijacker ('eve_public')", ClientRequestHijackWindow.Open), ("Server Request Hijacker ('eve')", ServerRequestHijackWindow.Open)]))
        m.append(None)
        m.append(('Abyssal Deadspace', [('Abyssal Content Tool', AbyssalContentToolWindow.Open), ('Abyssal Npc Spawn Tool', AbyssalNpcSpawnToolWindow.Open)]))
        import assetholding.client.qa as asset_holding
        m.append(asset_holding.get_insider_qa_menu())
        m.append(('Camera', [('Debug Camera', lambda : CameraTool.Open())]))
        if session.stationid is not None:
            m.append(('Hangar', [('Model state debugger', lambda : ModelStateDebuggerController(itemID=None).ShowUI())]))
        m.append(uihider.qa.get_command_blocker_menu())

        def open_emanation_locks_esp():
            esp_url = serverInfo.GetServerInfo().espUrl
            action = 'gm/emanationLocks.py?action=EmanationLockDetails&character_id=' + str(session.charid)
            blue.os.ShellExecute('http://%s/%s' % (esp_url, action))

        m.append(('Emanation Locks Eve Server Page', open_emanation_locks_esp))
        import dynamicresources.client.ess.bracket.debug
        m.append(dynamicresources.get_insider_qa_menu())
        import homestation.client
        m.append(homestation.get_insider_qa_menu())
        import raffles.client
        m.append(raffles.get_insider_qa_menu())
        m.append(('Jump Clones', [('Reset last clone jump time', ResetLastCloneJumpTime)]))
        m.append(('Market', (('Toggle Market Price History Test Data', TogglePriceHistoryTestData),)))
        import sovereignty.mercenaryden.client.qa.insider as mercenary_dens
        m.append(mercenary_dens.get_insider_qa_menu())
        m.append(('New Eden Store', [('Clear cache', lambda : sm.GetService('vgsService').ClearCache())]))
        import redeem.client
        m.append(redeem.get_insider_qa_menu())
        m.append(MenuEntryData('Contextual Offers', subMenuData=[MenuEntryData('Trigger test offer 1', sm.GetService('contextualOfferSvc').Debug_AddMockOffer1), MenuEntryData('Trigger test offer 2', sm.GetService('contextualOfferSvc').Debug_AddMockOffer2), MenuEntryData('Trigger test offer 3', sm.GetService('contextualOfferSvc').Debug_AddMockOffer3)]))
        m.append(('Scope Network', [('Reload FSD Seasons', lambda : self.ReloadFsdData())]))
        m.append(('Starmap', [('Clear cache', lambda : sm.GetService('starmap').ClearMapCache())]))
        m.append(('Skills', (('Skill Tree Window', SkillTreeDockablePanel.Open), ('Reset Ship Progression', GetShipUnlockService().QA_ResetAll))))
        from cosmetics.client.ships.qa.skin_states_table import SkinStatesTableWindow
        from cosmetics.client.ships.qa.skin_licenses_table import SkinLicensesTableWindow
        from cosmetics.client.ships.qa.component_licenses_table import ComponentLicensesTableWindow
        m.append(('Ship Cosmetics', (('Ship Emblems', ShipEmblemsTool.Open),
          ('Cached Ship Skin States', SkinStatesTableWindow.Open),
          ('Component Licenses', ComponentLicensesTableWindow.Open),
          ('Skin Licenses', SkinLicensesTableWindow.Open))))
        import cosmetics.client.messengers.entitlements.corporation.structure.qa as structureCosmeticsQA
        m.append(structureCosmeticsQA.get_insider_qa_menu())
        m.append(('Structure SKINR', (('Structure SKINR', PaintToolWnd.Open),)))
        m.append(('Ship SKINR', (('Ship SKINR', ShipSKINRWindow.Open),)))
        import dailygoals.client.qa as dailygoalsQA
        m.append(dailygoalsQA.get_insider_qa_menu())
        m.append(('Tutorial UI Hider', (('Reveal All',
           self.uihider.get_ui_hider().reveal_everything,
           (),
           (ICON_VISIBILITY_ON, 18)), ('Hide All',
           self.uihider.get_ui_hider().hide_everything,
           (),
           (ICON_VISIBILITY_OFF, 18)))))
        m.append(('Overview Blocker', (('Unblock',
           sm.GetService('overviewPresetSvc').UnblockOverview,
           (),
           (ICON_VISIBILITY_ON, 18)), ('Block',
           sm.GetService('overviewPresetSvc').BlockOverview,
           (),
           (ICON_VISIBILITY_OFF, 18)))))
        from uiblinker.insider import get_ui_blinker_menu
        m.append(get_ui_blinker_menu())
        m.append(('Career Agents', (('Open Debug window', CareerAgentDebugWnd.Open),)))
        m.append(MenuEntryData('Boarding Moment', subMenuData=[MenuEntryDataCheckbox(text='QA UI', setting=boarding_moment_qa.overlay_setting), MenuEntryData('Reset boarding moments', boarding_moment_qa.clear_data)]))
        m.append(None)
        m.append(('Open Impact window', lambda : impactVisualizationWnd.ImpactVisualizationWnd.Open()))
        from nodegraph.client.ui.window import NodeGraphEditorWindow
        m.append(('Open Node Graph Editor', lambda : NodeGraphEditorWindow.Open()))
        m.append(('Open Warp Vector window', lambda : WarpVectorWnd.Open()))
        from eve.devtools.script.dotWeapons import DotWeaponWnd
        m.append(('Open DOT Weapons window', lambda : DotWeaponWnd.Open()))
        m.append(None)
        m.append(('Auto Bot', AutoBotWindow.Open))
        m.append(None)
        m.append(('Cluster Visualizer', ClusterVisualizerWindow.Open))
        return m

    def ReloadFsdData(self):
        svc = sm.RemoteSvc('seasonManager')
        svc.reload_fsd_data()

    def ImplantsMenu(self, *args):
        m = MenuList()
        implantsmenu = sm.GetService('implant').ImplantMenu()
        for entry in implantsmenu:
            try:
                m.append((entry[0], entry[1]))
            except:
                sys.exc_clear()
                m.append(None)

        return m

    def DroneMenu(self, *args):
        m = MenuList()
        dronemenu = sm.GetService('charge').DroneMenu()
        fighterMenu = sm.GetService('fighters').FightersMenu()
        for menu in [dronemenu, fighterMenu]:
            for entry in menu:
                try:
                    m.append((entry[0], entry[1]))
                except:
                    sys.exc_clear()
                    m.append(None)

        return m

    def ChargeMenu(self, *args):
        m = MenuList()
        chargemenu = sm.GetService('charge').ChargeMenu()
        for entry in chargemenu:
            try:
                if entry.__class__ == dict:
                    m.append((entry['label'], None))
                    m.append(None)
                else:
                    m.append((entry[0], entry[1]))
            except:
                sys.exc_clear()
                m.append(None)

        return m

    def ToggleMyShip(self):
        ship = sm.GetService('michelle').GetBall(session.shipid)
        if ship and ship.model:
            ship.model.display = not ship.model.display

    def ShipMenu(self, *args):
        shipmenu = sm.StartService('copycat').GetMenu_Ship()
        if shipmenu is None:
            return
        shipmenu += [None, ('Show/Hide My Ship', self.ToggleMyShip)]
        menu = MenuList()
        submenu = MenuList()
        for menuentry in shipmenu:
            if isinstance(menuentry, types.TupleType):
                if len(menuentry) == 2:
                    display, func = menuentry
                    if isinstance(func, types.TupleType):
                        subFunc = func[1]()
                        for entry in subFunc:
                            if isinstance(entry, types.TupleType):
                                submenu.append((entry, None))
                                submenu.append(None)
                            elif isinstance(entry, types.DictType):
                                submenu.append((entry['label'], entry['action'], entry['args']))

                        if len(submenu) == 0:
                            submenu = [('Nothing found', None)]
                        menu.append((display, submenu))
                        submenu = MenuList()
                    else:
                        menu.append((display, func))
                elif len(menuentry) == 3:
                    display, func, args = menuentry
                    menu.append((display, func, args))
            elif isinstance(menuentry, types.NoneType):
                menu.append(None)

        return menu

    def MacroMenu(self, *args):
        m = MenuList()
        lines = sm.GetService('slash').GetMacros()
        lines.sort()
        for macroName, comseq in lines:
            m.append((macroName, self.SlashBtnClick(comseq)))

        return m

    def UIMenu(self, *args):
        menu = MenuData(iconSize=18)
        menu.AddCaption('Tools')
        menu.AddEntry(text='Animations', func=lambda : TestAnimationsWnd.Open(), texturePath='res:/UI/Texture/classes/insider/animation_18.png')
        menu.AddEntry(text='Color Picker', func=lambda : ColorPicker.Open(), texturePath='res:/UI/Texture/classes/insider/color_picker_18.png')
        if not blue.pyos.packaged:
            menu.AddEntry(text='Control Catalog', func=lambda : self.OpenControlCatalogWindow(), texturePath='res:/UI/Texture/classes/insider/control_catalog_18.png')
        menu.AddEntry(text='Debugger', func=lambda : UIDebugger.Open(), texturePath='res:/UI/Texture/classes/insider/ui_debugger_18.png')
        menu.AddEntry(text='Event Listener', func=lambda : UIEventListener.Open(), texturePath='res:/UI/Texture/classes/insider/event_listener_18.png')
        menu.AddEntry(text='Gradient Editor', func=lambda : GradientEditor.Open(), texturePath='res:/UI/Texture/classes/insider/gradient_18.png')
        menu.AddEntry(text='Icons', func=lambda : IconBrowserWindow.Open(), texturePath='res:/UI/Texture/classes/insider/icons_18.png')
        menu.AddEntry(text='Keybindings Overview', func=self.OpenKeyboardWindow, texturePath='res:/UI/Texture/classes/insider/keyboard_18.png')
        menu.AddEntry(text='Sprites', func=lambda : UISpriteTest.Open(), texturePath='res:/UI/Texture/classes/insider/image_18.png')
        menu.AddEntry(text='Toggle Black Background', func=self.ToggleBlackBackground, texturePath='res:/UI/Texture/classes/insider/lightbulb_18.png')
        menu.AddEntry(text='Tree', func=lambda : UITree.Open(), texturePath='res:/UI/Texture/classes/insider/ui_tree_18.png')
        menu.AddEntry(text='Window Manager', func=lambda : WindowManager.Open(), texturePath='res:/UI/Texture/classes/insider/window_manager_18.png')
        menu.AddSeparator()
        menu.AddCaption('Live Reload')
        menu.AppendMenuEntryData(self.GetLabelLiveReloadOption())
        menu.AppendMenuEntryData(self.GetLiveReloadUiTexturesOption())
        menu.AddEntry(text='Manual Reload', subMenuData=[MenuEntryData(text='Localization', func=self.ReloadFSDLocalizationPickles, texturePath='res:/UI/Texture/classes/insider/localization_18.png'), MenuEntryData(text='Shaders', func=self.ReloadUIShader, texturePath='res:/UI/Texture/classes/insider/shader_18.png'), MenuEntryData(text='Textures', func=self.ReloadUITextures, texturePath='res:/UI/Texture/classes/insider/image_18.png')])
        menu.AddSeparator()
        menu.AddCaption('Tests')
        menu.AddEntry(text='Button Bazaar', func=open_button_bazaar, texturePath='res:/UI/Texture/classes/insider/button_bazaar_18.png')
        menu.AppendMenuEntryData(self.GetGammaCorrectTextOption())
        menu.AddEntry(text='Glow', func=lambda : GlowTestWindow.Open(), texturePath='res:/UI/Texture/classes/insider/glow_18.png')
        menu.AddEntry(text='Graphs', func=lambda : TestGraph.Open(), texturePath='res:/UI/Texture/classes/insider/chart_18.png')
        menu.AppendMenuEntryData(self.GetLinearColorSpaceOption())
        menu.AddEntry(text='Notifications', func=open_notification_dev_window, texturePath='res:/UI/Texture/classes/insider/notification_18.png')
        menu.AddEntry(text='Performance', func=lambda : UIPerformanceTestWnd.Open(), texturePath='res:/UI/Texture/classes/insider/fire_18.png')
        menu.AddEntry(text='Text Styles', func=TextStyleTest.Open, texturePath='res:/UI/Texture/classes/insider/text_styles_18.png')
        menu.AddEntry(text='Theme', func=lambda : ColorThemeEditor.Open(), texturePath='res:/UI/Texture/classes/insider/theme_18.png')
        menu.AddEntry(text='UI Scale', func=lambda : UIScaling.Open(), texturePath='res:/UI/Texture/classes/insider/ui_scale_18.png')
        return menu

    def OpenControlCatalogWindow(self):
        self.controlCatalogInstanceID += 1
        ControlCatalogWindow.Open(windowInstanceID=str(self.controlCatalogInstanceID))

    def GetLiveReloadUiTexturesOption(self):
        return self.GetToggleOption(label='Textures', callback=self.ToggleResourceLiveReload, enabled=self.IsResourceLiveReloadingEnabled())

    def IsResourceLiveReloadingAvailable(self):
        return not blue.pyos.packaged

    def IsResourceLiveReloadingEnabled(self):
        if not self.IsResourceLiveReloadingAvailable():
            return False
        return settings.public.ui.Get('insider.res_live_reload_enabled', True)

    def ToggleResourceLiveReload(self):
        if not self.IsResourceLiveReloadingAvailable():
            uicore.Message('CustomNotify', {'notify': 'Texture live reloading is not available in built clients.'})
            return
        is_enabled = self.IsResourceLiveReloadingEnabled()
        settings.public.ui.Set('insider.res_live_reload_enabled', not is_enabled)
        self.UpdateResourceLiveReloader()

    def UpdateResourceLiveReloader(self):
        if not self.IsResourceLiveReloadingAvailable():
            return
        if self.IsResourceLiveReloadingEnabled():
            self._res_live_reloader.start()
        else:
            self._res_live_reloader.stop()

    def GetGammaCorrectTextOption(self):
        return self.GetToggleOption(label='Gamma Correct Text', callback=self.ToggleUIGammaCorrectText, enabled=uicore.desktop.renderObject.gammaCorrectText)

    def ToggleUIGammaCorrectText(self):
        uicore.desktop.renderObject.gammaCorrectText = not uicore.desktop.renderObject.gammaCorrectText

    def GetLinearColorSpaceOption(self):
        return self.GetToggleOption(label='Linear Color Space', callback=self.ToggleUILinearColorSpace, enabled=uicore.desktop.renderObject.useLinearColorSpace)

    def GetToggleOption(self, label, callback, enabled):
        if enabled:
            icon = 'res:/UI/Texture/classes/insider/toggle_on_18.png'
        else:
            icon = 'res:/UI/Texture/classes/insider/toggle_off_18.png'
        return MenuEntryData(text=label, func=callback, texturePath=icon)

    def GetLabelLiveReloadOption(self):
        return self.GetToggleOption(label='Localization', callback=self.ToggleLabelLiveReloading, enabled=self.IsLabelLiveReloadEnabled())

    def ToggleUILinearColorSpace(self):
        uicore.desktop.renderObject.useLinearColorSpace = not uicore.desktop.renderObject.useLinearColorSpace

    def TournamentMenu(self, *args):
        toolMenu = MenuList()
        toolMenu.append(('Tournament Camera Tool', TournamentWindow.Open))
        toolMenu.append(('Tournament Referee Tool', RefWindowSpawningWindow.Open))
        return toolMenu

    def ReloadFSDLocalizationPickles(self):
        localizationTools.ReloadFSDLocalizationPickle()
        msg = 'FSD localization pickles successfully reloaded on client'
        if sm.RemoteSvc('localizationServer').ReloadFSDPickle():
            msg += ' and server'
        ShowQuickMessage(msg)

    def OpenKeyboardWindow(self):
        from eve.client.script.ui.shared.shortcuts import KeyboardWnd
        wnd = KeyboardWnd.GetIfOpen()
        if wnd:
            wnd.Close()
        KeyboardWnd.Open()

    def ShowDogmaTimeWindow(self):
        from eve.devtools.script.dogmaTimeWnd import OpenWindow
        OpenWindow()

    def ReloadUITextures(self):
        for resPath in blue.motherLode.GetNonCachedKeys():
            isIcon = resPath.startswith('res:/dx9/model') and 'icons' in resPath
            isTexture = resPath.startswith('res:/ui/texture')
            isUberShader = 'ubershader' in resPath
            if isIcon or isTexture or isUberShader:
                res = blue.motherLode.Lookup(resPath)
                if res:
                    if hasattr(res, 'Reload'):
                        res.Reload()

    def ReloadIcons(self):
        for resPath in blue.motherLode.GetNonCachedKeys():
            if resPath.startswith('res:/dx9/model') and 'icons' in resPath:
                res = blue.motherLode.Lookup(resPath)
                if res:
                    if hasattr(res, 'Reload'):
                        res.Reload()

    def ReloadUIShader(self):
        res = blue.motherLode.Lookup('res:/graphics/effect.dx11/ui/ubershader.sm_hi')
        if res:
            res.Reload()
        res = blue.motherLode.Lookup('res:/graphics/effect.dx11/ui/ubershader.sm_lo')
        if res:
            res.Reload()

    def ToggleBlackBackground(self):
        for c in uicore.desktop.children:
            if c.name == 'colorFill':
                c.Close()
                break
        else:
            color = Color.FUCHSIA if uicore.uilib.Key(uiconst.VK_SHIFT) else Color.BLACK
            c = Fill(name='colorFill', parent=uicore.desktop, color=color)

    def ToggleLabelLiveReloading(self):
        if blue.pyos.packaged:
            message = 'This feature is not available in a built client'
        else:
            isEnabled = localizationTools.localization.ToggleLabelOverride()
            message = 'Localization label live reloading is '
            message += 'enabled' if isEnabled else 'disabled'
        ShowQuickMessage(message)

    def IsLabelLiveReloadEnabled(self):
        if blue.pyos.packaged:
            return False
        else:
            import localization.labelOverride
            return localization.labelOverride.GetConfigValue()

    def ToolMenu(self, *args):
        toolMenu = MenuList()
        toolMenu.append(('Settings', [('Export', sm.GetService('settingsLoader').Export, ()), ('Load', sm.GetService('settingsLoader').Load, ())]))
        toolMenu.append(('Convert Dogma Datetime', self.ShowDogmaTimeWindow))
        if session.role & ROLE_GML:
            toolMenu.append(('Fighter debugger', lambda : sm.GetService('fighters').ShowDebugWindow()))
            toolMenu.append(('Sound Player', InsiderSoundPlayer.Open))
            toolMenu.append(('Video Player', BinkVideoViewer.Open))
            toolMenu.append(('Ballpark exporter', lambda : sm.GetService('ballparkExporter').Show()))
            toolMenu.append(('Destroyable Items', lambda : sm.GetService('destroyableItems').ConstructLayout()))
            toolMenu.append(('Grid Utilities', lambda : sm.GetService('gridutils').ConstructLayout()))
            toolMenu.append(('Starbase Tools', lambda : sm.GetService('poser').Show()))
        if session.role & ROLE_GMH:
            toolMenu.append(('Inventory Tools', InvToolsWnd.Open))
            toolMenu.append(('Settings Manager', SettingsMgr.Open))
        if session.role & ROLE_QA:
            toolMenu.append(('Module Test', lambda : sm.GetService('modtest').Show()))
            toolMenu.append(('Skill Tool', lambda : sm.GetService('trainer').Show()))
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            toolMenu.append(('Copycat', lambda : sm.GetService('copycat').Show()))
            toolMenu.append(('Cap Simulator', lambda : sm.GetService('capsim').Show()))
            toolMenu.append(('Slash Console', lambda : sm.GetService('slash').ConstructLayout()))
            toolMenu.append(('Type Browser', TypeBrowser.Open))
        toolMenu.sort()
        if session.role & ROLE_PROGRAMMER:
            toolMenu.append(None)
            toolMenu.append((eveformat.color('Python Console', eveColor.WARNING_ORANGE), lambda : sm.GetService('console').ConstructLayout()))
        toolMenu.append(None)
        action = 'gd/npc.py?action=BrowseSolarSystem&solarSystemID=' + str(session.solarsystemid2)
        toolMenu.append(('Solar system NPC info', StartMenuService().GetFromESP, (action,)))
        if trinity.IsFpsEnabled():
            toolMenu.append(('Turn FPS Monitor OFF', trinity.SetFpsEnabled, (False,)))
            settings.public.ui.Set('isFpsRenderJobEnabled', False)
        else:
            toolMenu.append(('Turn FPS Monitor ON', trinity.SetFpsEnabled, (True,)))
            settings.public.ui.Set('isFpsRenderJobEnabled', True)
        toolMenu.append(('Engine tools', lambda : EngineToolsLauncher.Open()))
        toolMenu.append(('Report Bug', lambda : sm.GetService('bugReporting').StartCreateBugReport()))
        toolMenu.append(('Shared texture viewer', self.SharedTextureViewer))
        return toolMenu

    def SharedTextureViewer(self):
        from eve.devtools.script.sharedtextureviewer import SharedTextureViewer
        SharedTextureViewer.Open()

    def Hide(self, *args):
        self.Show(show=False)

    def Reload(self):
        self.Hide()
        self.Show(force=True)
        uicore.Message('CustomNotify', {'notify': 'Insider has been reloaded.'})

    def OnUIRefresh(self):
        InsiderWnd.CloseIfOpen()
        self.Show(force=True)

    def Show(self, show = True, force = False):
        if not session.role & serviceConst.ROLEMASK_ELEVATEDPLAYER:
            return
        INSIDERDIR = self.GetInsiderDir()
        if not os.path.exists(INSIDERDIR):
            os.mkdir(INSIDERDIR)
        InsiderWnd.CloseIfOpen()
        if not show:
            return
        settings.public.ui.Set('Insider', show)
        btn = []
        menus = MenuList([['Tools', self.ToolMenu, serviceConst.ROLE_GML],
         ['Macro', self.MacroMenu, serviceConst.ROLE_GML],
         ['Ship', self.ShipMenu, serviceConst.ROLE_GML],
         ['Charges', self.ChargeMenu, serviceConst.ROLE_GML],
         ['Drones', self.DroneMenu, serviceConst.ROLE_GML],
         ['Implants', self.ImplantsMenu, serviceConst.ROLE_GML],
         ['QA', self.QAMenu, serviceConst.ROLE_QA],
         ['UI', self.UIMenu, serviceConst.ROLE_QA],
         ['Tournament', self.TournamentMenu, serviceConst.ROLE_TOURNAMENT]])
        for label, func, role in menus:
            if session.role & role:
                btn.append([label,
                 func,
                 None,
                 None])

        wnd = InsiderWnd.Open()
        if wnd:

            def resize_window():
                if wnd.destroyed:
                    return
                if len(wnd.header.extra_content.children) == 0:
                    return
                window_width = wnd.width
                extra_content_width, _ = wnd.header.extra_content.GetCurrentAbsoluteSize()
                menu_bar_width = wnd.header.extra_content.children[0].width
                wnd.width = window_width - (extra_content_width - menu_bar_width)
                _, new_window_height = wnd.GetWindowSizeForContentSize(height=0)
                wnd.SetFixedHeight(new_window_height)

            toolbar = MenuBar(parent=wnd.header.extra_content, align=uiconst.TOLEFT, on_size_changed=resize_window)
            for label, func, _, _ in btn:
                toolbar.AddMenu(text=label, entries=func)

    def Toggle(self, forceShow = False, *args):
        if settings.public.ui.Get('Insider', False):
            self.Hide()
        else:
            self.Show(force=forceShow)

    def WarpTo(self, itemID = None):
        if itemID:
            sm.GetService('slash').SlashCmd('warpto %d' % itemID)


def ResetLastCloneJumpTime():
    sm.GetService('clonejump').GetLM().ResetLastCloneJumpTime()


def SetJumpDelay():
    currentDelay = sm.GetService('subway').JUMP_FINISH_DELAY / 1000
    result = uix.QtyPopup(minvalue=0, maxvalue=10000, caption='How long?', label='', hint='How long to stall jumps in seconds? (currently %d)' % currentDelay)
    if result:
        sm.GetService('subway').JUMP_FINISH_DELAY = result['qty'] * 1000


def open_button_bazaar():
    import eve.devtools.script.buttonbazaar.window
    eve.devtools.script.buttonbazaar.window.ButtonBazaarWindow.Open()


def open_notification_dev_window():
    from notifications.client.development.notificationDevUI import NotificationDevWindow
    NotificationDevWindow.Open()


def SetSSAOQuality(quality):
    from trinity import sceneRenderJobSpace
    sceneRenderJobSpace.SSAOSetting = quality
    sm.GetService('sceneManager').fisRenderJob.SetSettingsBasedOnPerformancePreferences()


def EnableGDPR(enable):
    trinity.ModifyGlobalEffectOptions([('BINDLESS_RENDERING', 'BINDLESS_RENDERING_ENABLED' if enable else 'BINDLESS_RENDERING_DISABLED')], [])
    trinity.settings.SetValue('gdrEnabled', enable)


def EnableRaytracing(enabled):
    trinity.settings.SetValue('raytracingEnabled', enabled)
    if not enabled and gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY) == 3:
        gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 2, False)
        sm.GetService('sceneManager').fisRenderJob.SetSettingsBasedOnPerformancePreferences()


def EnableUpscaling(enabled):
    trinity.settings.SetValue('newUpscalersEnabled', enabled)
    trinity.device.UpdateAvailableUpscalingTechniques()
    currentTechnique = gfxsettings.Get(gfxsettings.GFX_UPSCALING_TECHNIQUE)
    if currentTechnique not in (gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE, gfxsettings.GFX_UPSCALING_TECHNIQUE_FSR1):
        gfxsettings.Set(gfxsettings.GFX_UPSCALING_TECHNIQUE, gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE, False)
        trinity.device.SetUpscaling(gfxsettings.GFX_UPSCALING_TECHNIQUE_NONE, gfxsettings.GFX_UPSCALING_SETTING_NATIVE, False)


def OpenReflectionTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.reflectionProbe.reflectionTexture, label='Reflection')


def OpenDepthTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.depthTexture, label='Depth')


def OpenNormalTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.normalTexture, label='Normal')


def OpenSSAOTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.SSAO.outputTarget, label='SSAO')


def OpenShadowTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.cascadedShadowMap.shadowMapResultRT, label='Shadow')


def OpenVelocityTextureView():
    scene = sm.GetService('sceneManager').GetActiveScene()
    TextureWindow(texture=scene.velocityMap, label='Velocity')

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\environmentTemplateDebugger.py
import blue
import trinity
import uthread2
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.parklife.environmentSvc import GetEnvironmentService
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from carbonui.control.window import Window
from evegraphics.environments import BaseEnvironmentObject
from evegraphics.environments.environmentManager import EnvironmentManager
from fsdBuiltData.client import environmentTemplates

class DistanceFieldDebugWatchdog:

    def __init__(self, scene):
        if scene.debugRenderer is None:
            scene.debugRenderer = trinity.Tr2DebugRenderer()
        self.debugRenderer = scene.debugRenderer
        self.scene = scene
        self.distanceFields = []
        self.running = False

    def _Tick(self):
        while self.running:
            for each in self.distanceFields[:]:
                if each not in self.scene.distanceFields:
                    self.distanceFields.remove(each)

            for each in self.scene.distanceFields:
                if each not in self.distanceFields:
                    self.distanceFields.append(each)
                    self.debugRenderer.SetOptions(each, ['DistanceField'])

            blue.synchro.Yield()

    def Start(self):
        self.running = True
        uthread2.start_tasklet(self._Tick)

    def Stop(self):
        self.running = False
        for each in self.distanceFields:
            self.debugRenderer.SetOptions(each, [])


class EnvironmentTemplateDebugger(object):
    __notifyevents__ = ['OnLoadScene']

    def __init__(self):
        self.name = 'Environment Template Debugger'
        self.windowID = 'Environment_Template_' + self.name
        self.availableTemplates = None
        self.mainContainer = None
        self.distanceDebug = None
        self.updateThread = None
        sm.RegisterNotify(self)

    def OnClose(self, *args):
        sm.UnregisterNotify(self)
        BaseEnvironmentObject.DisableDebugMode()

    def ShowUI(self):
        wnd = Window.ToggleOpenClose(windowID=self.windowID)
        if wnd is None:
            return
        wnd.SetMinSize([550, 640], refresh=True)
        wnd.SetCaption(self.name)
        wnd._OnClose = self.OnClose
        main = wnd.GetMainArea()
        BaseEnvironmentObject.EnableDebugMode()
        buttonContiner = Container(name='buttonContainer', parent=main, align=uiconst.TOBOTTOM, padTop=10, padBottom=10, padLeft=10, padRight=10, height=Button.default_height)
        containers = Container(name='container', parent=main, align=uiconst.TOALL, padTop=10, padBottom=10, padLeft=10, padRight=10)
        availableOverviewContainer = Container(name='overviewContainer', parent=containers, align=uiconst.TOTOP, height=250, padLeft=10, padRight=10)
        EveLabelMediumBold(name='availableTemplates', parent=availableOverviewContainer, align=uiconst.TOTOP, text='Loaded Templates', left=4)
        self.availableTemplates = eveScroll.Scroll(parent=availableOverviewContainer, multiSelect=False)
        self.availableTemplates.sr.id = 'availableTemplates'
        allTemplatesOverviewContainer = Container(name='overviewContainer2', parent=containers, align=uiconst.TOTOP, padTop=10, padLeft=10, padRight=10, height=250)
        EveLabelMediumBold(name='allTemplates', parent=allTemplatesOverviewContainer, align=uiconst.TOTOP, text='All Templates (this was correct at the time of writing)', left=4)
        self.allTemplates = eveScroll.Scroll(parent=allTemplatesOverviewContainer, multiSelect=False)
        self.allTemplates.sr.id = 'allTemplates'
        Button(name='ReloadEnvironments', align=uiconst.TOLEFT, parent=buttonContiner, label='Reload All', func=self.Reload, padRight=4)
        self.chkDistanceDebug = Checkbox(name='myCheckbox', parent=buttonContiner, text='DistanceField Debug', checked=False, callback=self.OnDistanceDebug, align=uiconst.TOLEFT, width=120)
        self.SetupAvailableTemplateTable()
        self.SetupAllTemplateTable()
        self.updateThread = AutoTimer(500, self.SetupAvailableTemplateTable)

    def OnDistanceDebug(self, checkbox):
        if checkbox.GetValue():
            if self.distanceDebug is not None:
                self.distanceDebug.Stop()
            self.distanceDebug = DistanceFieldDebugWatchdog(sm.GetService('sceneManager').GetActiveScene())
            self.distanceDebug.Start()
        elif self.distanceDebug is not None:
            self.distanceDebug.Stop()
            self.distanceDebug = None

    def OnLoadScene(self, scene, key):
        self.OnDistanceDebug(self.chkDistanceDebug)

    def SetupAvailableTemplateTable(self):
        layout = '%s<t>%s<t>%s<t>%s<t>%s'
        headers = ['AnchorID',
         'Template',
         'Template ID',
         'Active',
         'Radius']
        content = []
        instance = EnvironmentManager.GetInstance()
        for environment in instance.environments:
            info = (environment.name,
             environmentTemplates.GetDescription(environment.templateID),
             environment.templateID,
             environment.isActive,
             environment.radius)
            label = layout % info
            entry = ScrollEntryNode(decoClass=SE_GenericCore, label=label, OnGetMenu=self.RightClickMenuCmd(environment.templateID, ['/tr me %s' % list(environment.anchorIDs)[0]]))
            content.append(entry)

        self.availableTemplates.Load(contentList=content, headers=headers, fixedEntryHeight=18)

    def SetupAllTemplateTable(self):
        layout = '%s<t>%s<t>%s<t>%s'
        headers = ['Template',
         'Template ID',
         'Spawn type',
         'Slash command']
        content = []
        for environmentID, environment in environmentTemplates.GetEnvironmentTemplates().iteritems():
            usage = environment.exampleUsage
            spawnType = usage.usageType
            usageID = usage.id
            commands = []
            if spawnType == environmentTemplates.EXAMPLE_USAGE_UNKNOWN:
                commands = ['unknown']
            elif spawnType == environmentTemplates.EXAMPLE_USAGE_SPAWNABLE:
                commands = ['/spawn %d' % usageID]
            elif spawnType == environmentTemplates.EXAMPLE_USAGE_LOCATION:
                commands = ['/tr me %d' % usageID]
            elif spawnType == environmentTemplates.EXAMPLE_USAGE_DUNGEON:
                commands = ['/dplay %d' % usageID]
            elif spawnType == environmentTemplates.EXAMPLE_USAGE_ABYSS:
                commands = ['/tr me 32000001', '/abyss generate tier=1 weather=%d duration= 10' % usageID]
            info = (environmentTemplates.GetDescription(environmentID),
             environmentID,
             spawnType,
             '\n'.join(commands))
            label = layout % info
            entry = ScrollEntryNode(decoClass=SE_GenericCore, label=label, OnGetMenu=self.RightClickMenuCmd(environmentID, commands))
            content.append(entry)

        self.allTemplates.Load(contentList=content, headers=headers, fixedEntryHeight=18)

    def RightClickMenuCmd(self, templateID, commands):
        return lambda x: self.RightClickMenu(templateID, commands)

    def RightClickMenu(self, templateID, commands):
        m = [('Run command \n\t%s' % '\n\t'.join(commands), self.RunCommands, (commands,)), ('Reload %s' % environmentTemplates.GetDescription(templateID), self.ReloadEnvironment, (templateID,)), ('Info', self.GetTemplateInfo(templateID))]
        return m

    def GetTemplateInfo(self, templateID):
        environmentTemplate = environmentTemplates.GetEnvironmentTemplate(templateID)
        options = [('description: %s' % environmentTemplates.GetDescription(templateID), blue.pyos.SetClipboardData, (environmentTemplates.GetDescription(environmentTemplate),)), ('isSystemWide: %s' % environmentTemplates.IsSystemWide(environmentTemplate), blue.pyos.SetClipboardData, (environmentTemplates.IsSystemWide(environmentTemplate),)), ('activationRadius: %s' % environmentTemplates.GetActivationRadius(environmentTemplate), blue.pyos.SetClipboardData, (environmentTemplates.GetActivationRadius(environmentTemplate),))]
        for attributeName, attribute in environmentTemplates.GetAllEnvironmentModifiers(environmentTemplate).iteritems():
            options += [(attributeName, self.CreateSubMenu(attribute))]

        return tuple(options)

    def CreateSubMenu(self, attribute):
        options = []
        if any([ isinstance(attribute, c) for c in [int,
         long,
         float,
         str,
         unicode,
         bool,
         tuple] ]):
            options += [('%s' % attribute, blue.pyos.SetClipboardData, (attribute,))]
        else:
            for attributeName in dir(attribute):
                if attributeName.startswith('_'):
                    continue
                attributeValue = getattr(attribute, attributeName)
                if callable(attributeValue):
                    continue
                if any([ isinstance(attributeValue, c) for c in [int,
                 long,
                 float,
                 str,
                 unicode,
                 bool,
                 tuple] ]):
                    options += [('%s: %s' % (attributeName, attributeValue), blue.pyos.SetClipboardData, (attributeValue,))]
                elif type(attributeValue).__name__.endswith('_vector'):
                    options += [('%s: %s' % (attributeName, tuple(attributeValue)), blue.pyos.SetClipboardData, (attributeValue,))]
                elif isinstance(attributeValue, dict):
                    options += [(attributeName, tuple(((k, self.CreateSubMenu(v)) for k, v in attributeValue.iteritems())))]
                elif isinstance(attributeValue, (list, tuple)):
                    options += [(attributeName, tuple(((i, self.CreateSubMenu(v)) for i, v in enumerate(attributeValue))))]
                else:
                    options += [(attributeName, self.CreateSubMenu(attributeValue))]

        return tuple(options)

    def RunCommands(self, commands):

        def inner(_commands):
            for command in _commands:
                if not command.startswith('/'):
                    return
                sm.GetService('slash').SlashCmd(command[1:])
                blue.synchro.SleepSim(500)

        uthread2.StartTasklet(inner, commands)

    def ReloadEnvironment(self, templateID):
        EnvironmentManager.GetInstance().RefreshEnvironment(templateID)

    def Reload(self, *args):
        environmentTemplates.EnvironmentTemplates.ReloadDataFromDisk()
        ballsAndItems = sm.GetService('michelle').GetBallpark().GetBallsAndItems()
        EnvironmentManager.GetInstance().CreateCache()
        envService = GetEnvironmentService()
        envService.ChangeSolarSystem(session.solarsystemid, session.solarsystemid)
        envService.DoBallsAdded(ballsAndItems)
        self.SetupAvailableTemplateTable()

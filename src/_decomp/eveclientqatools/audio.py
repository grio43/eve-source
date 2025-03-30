#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\audio.py
import os
import yaml
import audio2
import blue
import carbonui.const as uiconst
import trinity
import gametime
import uthread
import uthread2
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.forms import formComponent
from carbonui.control.forms.form import Form, FormActionSubmit
from carbonui.control.forms.formContainer import FormContainer
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.slider import Slider
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.message import ShowQuickMessage
from carbonui.control.window import Window
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eveaudio.audactionrecords import ALL_ACTION_RECORD_TYPES
from eveaudio.helpers import CreateReloadBankMessage
from eveaudio.eveaudiomanager import GetAudioManager
from evedungeons.client.data import GetDungeon
from fsd import GetBranchRoot, AbsJoin
from fsd.common.fsdYamlExtensions import FsdYamlLoader
from spacecomponents.common.helper import HasBoomboxComponent

class AudioActionLog(Window):
    default_windowID = 'audioActionLog'
    default_caption = 'Audio Action Log'
    default_width = 400
    default_height = 300
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.audio_svc = sm.GetService('audio')
        self.actionsScrollList = []
        self._allowedRecordTypes = set()
        mainCont = Container(name='audioActionMainCont', parent=self.sr.main, align=uiconst.TOALL)
        for each in ALL_ACTION_RECORD_TYPES:
            Checkbox(name='enableActionListening{}'.format(each.__name__), parent=mainCont, text='Enable {} Logging'.format(each.GetLabel()), checked=False, callback=lambda checkbox, recType = each: self.OnLoggingEnableCheckbox(recType, checkbox))

        self.actionFilterEdit = QuickFilterEdit(name='actionFilterEdit', parent=mainCont, hintText='Filter audio actions', maxLength=64, align=uiconst.TOTOP, padding=10, left=4, OnClearFilter=self.OnActionFilterEditCleared, width=120, isTypeField=True)
        self.actionFilterEdit.ReloadFunction = self.OnActionFilterEdit
        Button(name='clear', align=uiconst.TOTOP, parent=mainCont, label='Clear List', func=self.OnClear, padding=5, height=30, width=30)
        Button(name='copy', align=uiconst.TOTOP, parent=mainCont, label='Copy To Clipboard', padding=5, func=self.Copy, height=30, width=30)
        self.label = EveLabelLarge(name='audioActionsLabel', parent=mainCont, text='List of actions', padding=10, align=uiconst.TOTOP)
        self.scroll = Scroll(parent=mainCont)
        self.scroll.id = 'audioActionScroll'
        self.actionsScrollTimer = AutoTimer(200, self.UpdateActionScroll)

    def OnClear(self, _):
        self.ClearList()

    def ClearList(self):
        self.actionsScrollList = []

    def Copy(self, _):
        copied_content = ''
        for entry in self.actionsScrollList:
            copied_content += '{}\n'.format(entry['label'])

        blue.pyos.SetClipboardData(copied_content)

    def UpdateActions(self, action):
        if not isinstance(action, tuple(self._allowedRecordTypes)):
            return
        text = str(action)
        filterText = self.actionFilterEdit.GetValue().strip().lower()
        if filterText in text.lower():
            self._UpdateScrollList(action, self.actionsScrollList)

    def _UpdateScrollList(self, action, scrollList):
        label = '%s<t>%s<t>%s' % (action.GetTimestampString(), action.label, action.GetDataAsString())
        entry = GetFromClass(Generic, {'label': label})
        scrollList.insert(0, entry)

    def UpdateActionScroll(self):
        headers = ['time', 'type', 'actions']
        self.scroll.Load(contentList=self.actionsScrollList, headers=headers, ignoreSort=True)

    def OnActionFilterEditCleared(self):
        self.ClearList()
        return self.actionsScrollList

    def OnActionFilterEdit(self):
        self.ClearList()
        return self.actionsScrollList

    def EnableLogging(self, enabled):
        if enabled:
            self.audio_svc.SetDebugLogCallback(self.UpdateActions)
        else:
            self.audio_svc.StopDebugLogging()

    def OnLoggingEnableCheckbox(self, recordType, checkbox):
        loggingWasEnabled = len(self._allowedRecordTypes) > 0
        if checkbox.checked:
            self._allowedRecordTypes.add(recordType)
        else:
            self._allowedRecordTypes.remove(recordType)
        loggingNowEnabled = len(self._allowedRecordTypes) > 0
        if loggingWasEnabled != loggingNowEnabled:
            self.EnableLogging(loggingNowEnabled)

    def Close(self, *args, **kwargs):
        self.actionScrollTimer = None
        Window.Close(self, args, kwargs)
        self.audio_svc.StopDebugLogging()


class SoundbankDebugger(object):

    @classmethod
    def Toggle(cls, *args, **kwargs):
        failedBanks = sm.GetService('audio').ReloadBanks()
        msg = CreateReloadBankMessage(failedBanks)
        eve.Message('CustomInfo', {'info': msg}, modal=1)


class AudioEmitterDebugger(object):

    @classmethod
    def EnableDebuggerInScene(cls):
        if sm.GetService('audio').GetDebugDisplayAllEmitters():
            scene = sm.GetService('sceneManager').GetActiveScene()
            if not scene.debugRenderer:
                scene.debugRenderer = trinity.Tr2DebugRenderer()

    @classmethod
    def Toggle(cls, *args, **kwargs):
        audioSvc = sm.GetService('audio')
        debugDisplayAllEmitters = audioSvc.GetDebugDisplayAllEmitters()
        if debugDisplayAllEmitters:
            audioSvc.DisableDebugShowAllEmitters()
        else:
            try:
                audioSvc.EnableDebugShowAllEmitters()
            except AttributeError:
                msg = 'The client was not run with the /audiodev flag. This feature is only available if you use /audiodev.'
                eve.Message('CustomInfo', {'info': msg}, modal=1)

        cls.EnableDebuggerInScene()


class AudioPrioritizationDebugger(object):

    @classmethod
    def Toggle(cls, *args, **kwargs):
        audioManager = GetAudioManager()
        if audioManager.GetSoundPrioritizationEnabled():
            audioManager.DisableSoundPrioritization()
        else:
            audioManager.EnableSoundPrioritization()
        wnd = AudioPrioritizationIntrospectionDebugger.GetIfOpen()
        if wnd:
            wnd.RefreshToggle()

    @classmethod
    def GetCullingEnabled(cls, *args, **kwargs):
        audioManager = GetAudioManager()
        return audioManager.GetSoundPrioritizationEnabled()


class MusicDebugger(Window):
    default_windowID = 'musicDebugger'
    default_caption = 'Music Debugger'
    default_width = 630
    default_height = 350
    default_minSize = (500, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.audio_svc = sm.GetService('audio')
        self.musicDebuggerSvc = sm.GetService('musicDebugger')
        self.dynamicMusicSvc = sm.GetService('dynamicMusic')
        self.eventsScrollList = []
        self.currentDungeon = None
        self.leftCont = Container(name='leftcont', parent=self.content, align=uiconst.TOLEFT, width=300)
        self.attributeCont = Container(name='attributeCont', parent=self.leftCont, clipChildren=False)
        self.dungeonInfoContainer = ContainerAutoSize(parent=self.attributeCont, align=uiconst.TOTOP, padding=8)
        self.stopMusicButton = Button(parent=self.attributeCont, align=uiconst.TOTOP, name='stopMusicButton', label='Stop Music', padding=(4, 24, 4, 4), func=self.OnStopMusicButtonClick, hint='Stop the currently playing music.')
        self.sendEventText = SingleLineEditText(parent=self.attributeCont, align=uiconst.TOTOP, padding=(4, 40, 4, 4), name='sendEventText', label='Music event')
        self.sendEventButton = Button(parent=self.attributeCont, align=uiconst.TOTOP, name='sendEventButton', label='Send Event to Music System', padding=(4, 4, 4, 4), func=self.OnSendEventButtonClick, hint='Sends the event from the text box above to the music system.')
        mainWindow = Container(align=uiconst.TOALL, parent=self.content)
        leftCont = Container(name='leftCont', align=uiconst.TOLEFT_PROP, parent=mainWindow, width=1)
        self.clearEventsButton = Button(parent=self.attributeCont, align=uiconst.TOTOP, name='clearEventsButton', label='Clear Events List', padding=(4, 4, 4, 4), func=self.OnClearEventsButtonClick, hint='Clears the list of events that have been sent.')
        self.copyButton = Button(parent=self.attributeCont, align=uiconst.TOTOP, name='copyButton', label='Copy Events to Clipboard', padding=(4, 4, 4, 4), func=self.Copy, hint='Copy the currently shown events to your clipboard.')
        self.label = EveLabelLarge(name='musicDebuggerLabel', parent=leftCont, text='Music Events', padding=10, align=uiconst.TOTOP)
        self.scroll = Scroll(parent=leftCont)
        self.scroll.id = 'musicTriggersScroll'
        for event, time, sent in self.dynamicMusicSvc.GetProcessedMusicEvents():
            self._UpdateMusicTriggersScrollList(event, sent, time)

        self.musicTriggerScrollTimer = AutoTimer(200, self.UpdateEventScroll)
        self.dynamicMusicSvc.SetDebugMusicTriggerCallback(self.UpdateMusicTriggers)
        self.musicDebuggerSvc.SetDungeonChangeCallback(self.UpdateDungeonInfo)
        self.ShowDungeonInfo()
        self.refreshThread = uthread.worker('MusicDebugger::UpdateDungeonInfoThread', self.UpdateDungeonInfoThread)
        self.UpdateDungeonInfo(sm.GetService('dungeonTracking').GetCurrentDungeonID())

    def ConvertDungeonIDToFilepath(self, dungeonID):
        return AbsJoin(GetBranchRoot(), 'eve', 'staticData', 'dungeons', 'dungeons', '{}.staticdata'.format(dungeonID))

    def GetDungeonInfo(self, dungeonID):
        useDefaultSpaceMusic = False
        boomboxes = []
        musicUrls = []
        dungeonInfo = {}
        cfsdDungeon = GetDungeon(dungeonID)
        with open(self.ConvertDungeonIDToFilepath(dungeonID)) as dungeonFile:
            dungeonInfo = yaml.load(dungeonFile, Loader=FsdYamlLoader)
        if dungeonInfo and dungeonID in dungeonInfo.keys():
            dungeonData = dungeonInfo[dungeonID]
            useDefaultSpaceMusic = bool(getattr(cfsdDungeon, 'useDefaultSpaceMusic', False))
            musicUrls = self._GetMusicUrlsFromDungeon(dungeonData)
            boomboxes = self._GetBoomboxesInDungeon(dungeonData)
        return (useDefaultSpaceMusic, boomboxes, musicUrls)

    def UpdateMusicTriggers(self, event, playingID):
        sent = False
        if playingID > 0:
            sent = True
        self._UpdateMusicTriggersScrollList(event, sent, FmtDate(gametime.GetSimTime()))

    def _UpdateMusicTriggersScrollList(self, text, sent, time):
        label = '%s<t>%s<t>%s' % (time, text, sent)
        entry = GetFromClass(Generic, {'label': label})
        self.eventsScrollList.insert(0, entry)

    def UpdateEventScroll(self):
        headers = ['time', 'events', 'sent']
        self.scroll.Load(contentList=self.eventsScrollList, headers=headers, ignoreSort=True)

    def UpdateDungeonInfo(self, dungeonID):
        self.currentDungeon = dungeonID

    def UpdateDungeonInfoThread(self):
        while self.IsOpen():
            blue.pyos.synchro.SleepWallclock(500)
            if self.IsOpen():
                self.Refresh()

    def OnStopMusicButtonClick(self, *args):
        self.dynamicMusicSvc.StopMusic()

    def OnSendEventButtonClick(self, *args):
        inputText = self.sendEventText.GetValue()
        playingID = self.dynamicMusicSvc.SendMusicEvent(inputText, forcePlay=True)
        if playingID == 0:
            eve.Message('CustomError', {'error': '"{}" is not a valid Wwise event'.format(inputText)})

    def OnClearEventsButtonClick(self, *args):
        self.eventsScrollList = []
        self.UpdateEventScroll()

    def ShowDungeonInfo(self):
        EveLabelMedium(parent=self.dungeonInfoContainer, text='Current dungeon ID: {}'.format(self.currentDungeon), align=uiconst.TOTOP)
        if self.currentDungeon > 0:
            try:
                useDefaultSpaceMusic, boomboxes, musicUrls = self.GetDungeonInfo(self.currentDungeon)
                EveLabelMedium(parent=self.dungeonInfoContainer, text='Dungeon boomboxes: {}'.format(len(boomboxes)), align=uiconst.TOTOP)
                EveLabelMedium(parent=self.dungeonInfoContainer, text='Connection musicUrls: {}'.format(len(musicUrls)), align=uiconst.TOTOP)
                EveLabelMedium(parent=self.dungeonInfoContainer, text='Use default space music: {}'.format(useDefaultSpaceMusic), align=uiconst.TOTOP)
            except RuntimeError:
                EveLabelMedium(parent=self.dungeonInfoContainer, text='More info about this dungeon is not available in a built client.', align=uiconst.TOTOP)

    def Refresh(self):
        self.dungeonInfoContainer.Flush()
        self.ShowDungeonInfo()

    def Close(self, *args, **kwargs):
        self.musicTriggerScrollTimer = None
        self.musicHooksScrollTimer = None
        self.clientEventsScrollTimer = None
        self.musicDebuggerSvc = None
        sm.StopService('musicDebugger')
        Window.Close(self, args, kwargs)

    def Copy(self, _):
        copied_content = ''
        for entry in self.eventsScrollList:
            copied_content += '{}\n'.format(entry['label'].replace('<t>', ' '))

        blue.pyos.SetClipboardData(copied_content)

    def _DungeonUsesDefaultSpaceMusic(self, dungeonData):
        useDefaultSpaceMusic = False
        if 'useDefaultSpaceMusic' in dungeonData.keys():
            useDefaultSpaceMusic = dungeonData['useDefaultSpaceMusic']
        return useDefaultSpaceMusic

    def _GetBoomboxInRoom(self, dungeonData, queryRoomID):
        roomObj = self._GetRoom(dungeonData, queryRoomID)
        if 'objects' in roomObj.values()[0]:
            for objectID, objectInfo in roomObj.values()[0]['objects'].iteritems():
                if HasBoomboxComponent(objectInfo['typeID']):
                    return objectInfo

        return {}

    def _GetBoomboxesInDungeon(self, dungeonData):
        boomboxes = []
        if 'rooms' in dungeonData.keys():
            for roomID, roomInfo in dungeonData['rooms'].iteritems():
                boombox = self._GetBoomboxInRoom(dungeonData, roomID)
                if boombox:
                    boomboxes.append(boombox)

        return boomboxes

    def _GetRoom(self, dungeonInfo, queryRoomID):
        for roomID, roomInfo in dungeonInfo['rooms'].iteritems():
            if roomID == queryRoomID:
                return {roomID: roomInfo}

        return {}

    def _GetMusicUrlsFromDungeon(self, dungeonData):
        musicUrls = []
        if 'connections' in dungeonData.keys():
            for connection in dungeonData['connections']:
                if 'musicUrl' in connection.keys():
                    musicUrls.append(connection['musicUrl'])

        return musicUrls


class AudioPrioritizationIntrospectionDebugger(Window):
    default_windowID = 'audioPrioritizationIntrospection'
    default_caption = 'Audio Prioritization Introspection'
    default_width = 400
    default_height = 300
    default_minSize = (default_width, default_height)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.audioManager = GetAudioManager()
        mainWindow = Container(align=uiconst.TOALL, parent=self.sr.maincontainer, padding=6)
        self.label = EveLabelLarge(name='audioPrioritizationIntrospectionLabel', parent=mainWindow, text='Prioritized Audio Emitters', padding=10, align=uiconst.TOTOP)
        self.emitterCheckbox = Checkbox(name='enableAudioPrioritizationIntrospection', parent=mainWindow, align=uiconst.TOBOTTOM, padding=4, text='Enable Introspection Updates', checked=True, callback=self.OnAudioPrioritizationInspectionCheckbox)
        self.prioritizationCheckbox = Checkbox(name='enableAudioPrioritization', parent=mainWindow, align=uiconst.TOBOTTOM, padding=4, text='Enable Audio Prioritization', checked=self.audioManager.GetSoundPrioritizationEnabled(), callback=self.OnAudioPrioritizationCheckbox)
        scrollCont = Container(name='scrollCont', align=uiconst.TOALL, parent=mainWindow)
        self.scroll = Scroll(parent=scrollCont, padding=6)
        self.scroll.id = 'prioritizedEmittersScroll'
        self.LoadEmitterScroll()
        self.prioritizedEmitterScrollUpdateThread = uthread.worker('AudioPrioritizationIntrospectionDebugger::PrioritzeEmitterInspectionUpdateThread', self.PrioritizeEmitterInspectionUpdateThread)

    def PrioritizeEmitterInspectionUpdateThread(self):
        while not self.destroyed:
            blue.pyos.synchro.SleepWallclock(500)
            if not self.destroyed:
                self.RefreshEmitterScroll()

    def OnAudioPrioritizationInspectionCheckbox(self, cb):
        if self.prioritizedEmitterScrollUpdateThread:
            self.prioritizedEmitterScrollUpdateThread.kill()
        if cb.checked:
            self.RefreshEmitterScroll()
            self.prioritizedEmitterScrollUpdateThread = uthread.worker('AudioPrioritizationIntrospectionDebugger::PrioritzeEmitterInspectionUpdateThread', self.PrioritizeEmitterInspectionUpdateThread)
        else:
            self.prioritizedEmitterScrollUpdateThread = None

    def OnAudioPrioritizationCheckbox(self, cb):
        if cb.checked:
            self.audioManager.EnableSoundPrioritization()
        else:
            self.audioManager.DisableSoundPrioritization()

    def RefreshToggle(self):
        self.prioritizationCheckbox.SetChecked(self.audioManager.GetSoundPrioritizationEnabled())

    def LoadEmitterScroll(self):
        emittersScrollList = []
        emitters = self.audioManager.manager.GetPrioritizedEmitters()
        self.label.text = 'Prioritized Audio Emitters, %s in total' % len(emitters)
        for idx, (emitterID, emitterData) in enumerate(emitters, start=1):
            label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (idx,
             emitterID,
             emitterData.name,
             emitterData.IsCulled(),
             emitterData.IsMuted(),
             emitterData.cumulativeWeight)
            entry = GetFromClass(Generic, {'label': label,
             'OnDblClick': self.EntryDetails,
             'GetMenu': self.EntryMenu,
             'emitterID': emitterID})
            emittersScrollList.append(entry)

        headers = ['Index',
         'Emitter ID',
         'Emitter Name',
         'Culled',
         'Muted',
         'Cumulative Weight']
        self.scroll.Load(contentList=emittersScrollList, headers=headers, sortby='Index')

    def RefreshEmitterScroll(self):
        newEmitters = self.audioManager.manager.GetPrioritizedEmitters()
        self.label.text = 'Prioritized Audio Emitters, %s in total' % len(newEmitters)
        newEmittersDict = {}
        for idx, (emitterID, emitterData) in enumerate(newEmitters, start=1):
            newEmittersDict[emitterID] = (idx, emitterData)

        updateList = self.scroll.sr.nodes
        nodesToRemove = []
        for node in updateList:
            if node.emitterID in newEmittersDict:
                idx, emitterData = newEmittersDict.pop(node.emitterID)
                newLabel = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (idx,
                 node.emitterID,
                 emitterData.name,
                 emitterData.IsCulled(),
                 emitterData.IsMuted(),
                 emitterData.cumulativeWeight)
                if newLabel != node.label:
                    node.label = newLabel
                    if node.panel:
                        node.panel.Load(node)
            else:
                nodesToRemove.append(node)

        nodesToAdd = []
        for emitterID, (idx, emitterData) in newEmittersDict.iteritems():
            label = '%s<t>%s<t>%s<t>%s<t>%s' % (idx,
             emitterID,
             emitterData.name,
             emitterData.IsCulled(),
             emitterData.cumulativeWeight)
            entry = GetFromClass(Generic, {'label': label,
             'OnDblClick': self.EntryDetails,
             'GetMenu': self.EntryMenu,
             'emitterID': emitterID})
            nodesToAdd.append(entry)

        if nodesToRemove:
            self.scroll.RemoveNodes(nodesToRemove)
        if nodesToAdd:
            self.scroll.AddNodes(-1, nodesToAdd)
        else:
            self.scroll.Sort('Index')

    def EntryMenu(self, entry):
        m = [('Open Details', self.EntryDetails, (entry,))]
        return m

    def EntryDetails(self, entry):
        wnd = AudioEmitterDetails.GetIfOpen()
        if wnd:
            wnd.Switch(entry.sr.node.emitterID)
            wnd.Maximize()
        else:
            AudioEmitterDetails.Open(emitterID=entry.sr.node.emitterID)

    def Close(self, *args, **kwargs):
        if self.prioritizedEmitterScrollUpdateThread:
            self.prioritizedEmitterScrollUpdateThread.kill()
            self.prioritizedEmitterScrollUpdateThread = None
        self.scroll = None
        Window.Close(self, args, kwargs)


class AudioGmMenu(object):

    def __init__(self, itemID):
        self.itemID = itemID

    def GetEmitterMenu(self):
        emitters = sm.GetService('audio').GetAudioEmittersOnItem(self.itemID)
        emitterMenu = []
        for emitter in emitters:
            emitterMenu.append(('{}: {}'.format(emitter.ID, emitter.name), self.EmitterDetails, (emitter.ID,)))

        return emitterMenu

    def EmitterDetails(self, emitterID):
        wnd = AudioEmitterDetails.GetIfOpen()
        if wnd:
            wnd.Switch(emitterID)
            wnd.Maximize()
        else:
            AudioEmitterDetails.Open(emitterID=emitterID)


class AudioEmitterDetails(Window):
    default_caption = 'Audio Emitter Details'
    default_windowID = 'audioemitterdetails'
    default_minSize = (300, 300)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.audioManager = GetAudioManager()
        self.emitterID = attributes.emitterID
        self.main = Container(name='main', align=uiconst.TOALL, parent=self.content)
        self.emitterDetailsContainer = Container(parent=self.main, align=uiconst.TOTOP_PROP, height=0.5)
        self.emitterButtonsContainer = Container(parent=self.main, align=uiconst.TOBOTTOM_PROP, height=0.2)
        self.playingEventsListCont = Container(name='playingEventsListCont', parent=self.main, align=uiconst.TOLEFT_PROP, width=0.5)
        self.switchesListCont = Container(name='switchesListCont', parent=self.main, align=uiconst.TOLEFT_PROP, width=0.5)
        self.ShowEmitterDetail()
        self._ready = True
        self.refreshThread = uthread.worker('AudioEmitterDetails::UpdateAudioEmitterDetailsThread', self.UpdateAudioEmitterDetailsThread)
        Button(name='forceCullingStateChange', align=uiconst.TOTOP, parent=self.emitterButtonsContainer, label='Force Culling State Change', func=self.ForceCullingStateChange, padding=3)
        Button(name='resetForcedCullingState', align=uiconst.TOTOP, parent=self.emitterButtonsContainer, label='Release Forced Culling State', func=self.ReleaseForcedCullingState, padding=3)
        Button(name='mute', align=uiconst.TOTOP, parent=self.emitterButtonsContainer, label='Mute', func=self.Mute, padding=3)
        Button(name='unmute', align=uiconst.TOTOP, parent=self.emitterButtonsContainer, label='Unmute', func=self.Unmute, padding=3)

    def UpdateAudioEmitterDetailsThread(self):
        while self.IsOpen():
            blue.pyos.synchro.SleepWallclock(500)
            if self.IsOpen():
                self.Refresh()

    def GetEmitterData(self, emitterID):
        emitters = self.audioManager.manager.GetPrioritizedEmitters()
        return next((x for _id, x in emitters if _id == emitterID), None)

    def Refresh(self):
        self.emitterDetailsContainer.Flush()
        self.playingEventsListCont.Flush()
        self.switchesListCont.Flush()
        self.ShowEmitterDetail()

    def Switch(self, emitterID):
        if not self._ready:
            return
        self.emitterID = emitterID
        self.Refresh()
        self._ready = True

    def ShowEmitterDetail(self):
        emitterData = self.GetEmitterData(self.emitterID)
        if not emitterData:
            EveLabelLarge(parent=self.emitterDetailsContainer, text='Emitter no longer available', align=uiconst.TOTOP)
            return
        EveLabelLarge(parent=self.playingEventsListCont, text='Events', align=uiconst.TOTOP, padding=3)
        EveLabelLarge(parent=self.switchesListCont, text='Switches', align=uiconst.TOTOP, padding=3)
        EveLabelLarge(parent=self.emitterDetailsContainer, text='EmitterID: {}'.format(emitterData.ID), align=uiconst.TOTOP)
        EveLabelLarge(parent=self.emitterDetailsContainer, text='Emitter name: {}'.format(emitterData.name), align=uiconst.TOTOP)
        if hasattr(emitterData, 'debugPosition'):
            EveLabelMedium(parent=self.emitterDetailsContainer, text='Debug Position: {}'.format(emitterData.debugPosition), align=uiconst.TOTOP, top=20)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Muted: {}'.format(emitterData.IsMuted()), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Culled: {}'.format(emitterData.IsCulled()), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Culling State is Forced: {}'.format(emitterData.forceCullingState), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Cumulative weight: {}'.format(emitterData.cumulativeWeight), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Is used: {}'.format(emitterData.isUsed), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Is visible: {}'.format(emitterData.isVisible), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='In range of the listener: {}'.format(emitterData.listenerInRange), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Playing a 2D sound: {}'.format(emitterData.playing2DSound), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Playing a vital sound: {}'.format(emitterData.playingVitalSound), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Custom additional culling weight: {}'.format(emitterData.additionalCullingWeight), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Distance from listener: {}'.format(emitterData.distanceFromListener), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Max attenuation radius: {}'.format(emitterData.maxAttenuationRadius), align=uiconst.TOTOP)
        EveLabelMedium(parent=self.emitterDetailsContainer, text='Scaling factor: {}'.format(emitterData.scalingFactor), align=uiconst.TOTOP)
        if len(emitterData.GetPlayingEvents()):
            self.scroll = Scroll(parent=self.playingEventsListCont, id='emitterdetailseventsscroll')
            self.PopulatePlayingEventsScroll(emitterData)
        else:
            EveLabelMedium(parent=self.playingEventsListCont, text='Currently no events playing on this emitter', align=uiconst.TOTOP, top=20)
        if len(emitterData.GetSwitches()):
            self.scroll = Scroll(parent=self.switchesListCont, id='emitterdetailsswitchesscroll')
            self.PopulateSwitchesScroll(emitterData)
        else:
            EveLabelMedium(parent=self.switchesListCont, text='There are currently no switches set on this emitter.', align=uiconst.TOTOP, top=20)

    def PopulatePlayingEventsScroll(self, emitterData):
        self.eventScrollList = []
        for eventID, eventName in emitterData.GetPlayingEvents().iteritems():
            label = '%s<t>%s' % (eventID, eventName)
            entry = GetFromClass(Generic, {'label': label})
            self.eventScrollList.append(entry)

        headers = ['ID', 'Event Name']
        self.scroll.Load(contentList=self.eventScrollList, headers=headers, ignoreSort=True)

    def PopulateSwitchesScroll(self, emitterData):
        self.eventScrollList = []
        for switchGroup, switch in emitterData.GetSwitches().iteritems():
            label = '%s<t>%s' % (switchGroup, switch)
            entry = GetFromClass(Generic, {'label': label})
            self.eventScrollList.append(entry)

        headers = ['Switch Group', 'Switch']
        self.scroll.Load(contentList=self.eventScrollList, headers=headers, ignoreSort=True)

    def Close(self, *args, **kwargs):
        if hasattr(self, 'refreshThread'):
            self.refreshThread.kill()
            self.refreshThread = None
        Window.Close(self, args, kwargs)

    def ForceCullingStateChange(self, *args):
        emitterData = self.GetEmitterData(self.emitterID)
        if emitterData:
            emitterData.ForceCullingStateChange()

    def ReleaseForcedCullingState(self, *args):
        emitterData = self.GetEmitterData(self.emitterID)
        if emitterData:
            emitterData.ReleaseForcedCullingState()

    def Mute(self, *args):
        emitterData = self.GetEmitterData(self.emitterID)
        if emitterData:
            emitterData.Mute()

    def Unmute(self, *args):
        emitterData = self.GetEmitterData(self.emitterID)
        if emitterData:
            emitterData.Unmute()


class SoundPrioritizationConfiguration(Window):
    default_caption = 'Sound Prioritization Configuration'
    default_windowID = 'sp_internals'
    default_minSize = (512, 512)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.audioManager = audio2.GetOrCreateManager()
        self.main = Container(name='main', align=uiconst.TOALL, parent=self.content, width=16)
        self.configurations = {'maxAwakeGameObjects': {'label': 'Maximum Active Audio Emitters',
                                 'hint': 'The maximum number of audio emitters that can be active at any one time.',
                                 'useBaseValue': False},
         'oneShotWindow': {'label': 'One shot window in milliseconds (tied to waiting one shot weight)',
                           'hint': "The window, in milliseconds, that a one shot has to get prioritized if it's audio emitter is currently inactive.",
                           'useBaseValue': False},
         'playing2DWeight': {'label': 'Playing 2D Weight',
                             'hint': 'The weight applied to a game object if it is currently playing a 2D sound.',
                             'useBaseValue': True},
         'rangeWeight': {'label': 'In Range Weight',
                         'hint': 'The weight applied to an audio emitter if sounds currently playing, or waiting to be played, are in range of the listener.',
                         'useBaseValue': True},
         'activeSoundsWeight': {'label': 'Active Sounds Weight',
                                'hint': 'The weight applied to an audio emitter if it has sounds currently playing or waiting to be played.',
                                'useBaseValue': True},
         'waitingOneShotWeight': {'label': 'Waiting One Shot Weight (tied to one shot window)',
                                  'hint': 'The weight applied to an audio emitter if there is a one shot sound waiting to play. The one shot window determines how long this has the ability to add priority after receiving a one shot event.',
                                  'useBaseValue': True},
         'visibleWeight': {'label': 'Visible Weight',
                           'hint': 'The weight applied to an audio emitter if it is visible to the listener.',
                           'useBaseValue': True},
         'usedEmitterWeight': {'label': 'Used Emitter Weight',
                               'hint': 'Weight given to an audio emitter if it has ever had any events sent to it in the past.',
                               'useBaseValue': True}}
        components = []
        for configName, configInfo in self.configurations.iteritems():
            container = ContainerAutoSize(parent=self.main, align=uiconst.TOTOP, padding=8)
            textBoxValue = self.GetPrioritizationConfigValue(configName, useBaseValue=configInfo['useBaseValue'])
            if type(textBoxValue) == float:
                component = formComponent.Float(name=configName, label=configInfo['label'], value=textBoxValue, hint=configInfo['hint'])
            else:
                component = formComponent.Integer(name=configName, label=configInfo['label'], value=textBoxValue, hint=configInfo['hint'])
            components.append(component)

        self.form = Form(components, actions=(FormActionSubmit('Submit New Values', self.SubmitWeights),))
        container = ContainerAutoSize(parent=self.main, width=20, align=uiconst.TOTOP)
        FormContainer(parent=container, form=self.form, align=uiconst.TOTOP)
        container2 = ContainerAutoSize(parent=self.main, align=uiconst.CENTERBOTTOM)
        Button(name='reset', align=uiconst.CENTERBOTTOM, parent=container2, label='Reset to Default Values', func=self.ResetSettings, padding=2, height=30, width=30)

    def SubmitWeights(self, form):
        for component in form.components:
            setattr(self.audioManager, component.get_name(), component.get_value())

        ShowQuickMessage('Sound prioritization parameters have been updated!')

    def GetBaseWeightValue(self, weightWithMultiplier):
        return weightWithMultiplier / self.audioManager.weightMultiplier

    def GetPrioritizationConfigValue(self, attributeName, useBaseValue = False):
        weightWithMultiplier = getattr(self.audioManager, attributeName)
        if useBaseValue:
            return self.GetBaseWeightValue(weightWithMultiplier)
        else:
            return weightWithMultiplier

    def ResetSettings(self, _):
        self.audioManager.ResetCullingSettings()
        for component in self.form.components:
            configInfo = self.configurations[component.get_name()]
            textBoxValue = self.GetPrioritizationConfigValue(component.get_name(), useBaseValue=configInfo['useBaseValue'])
            component.set_value(textBoxValue)

        ShowQuickMessage('Sound prioritization values have been reset to their defaults!')

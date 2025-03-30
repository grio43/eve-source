#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\incursionSvc.py
import carbonui.fontconst
from carbon.common.script.sys.service import Service
from carbonui.decorative.panelUnderlay import PanelUnderlay
from grouprewards import REWARD_TYPE_ISK
from grouprewards.data import get_immediate_reward_tables
from grouprewards.data import get_max_player_count_from_reward_tables
from grouprewards.data import get_max_reward_from_tables_with_reward_type
from grouprewards.data import get_min_player_count_from_reward_tables
from grouprewards.data import get_reward_for_player_count
from grouprewards.data import is_security_criteria_all
from grouprewards.data import is_security_criteria_high
from grouprewards.data import is_security_criteria_low
import blue
import uthread
import math
import localization
from eve.client.script.parklife.environmentSvc import GetEnvironmentService
from eveservices.xmppchat import GetChatService
from fsdBuiltData.common.soundIDs import GetSoundEventName
from fsdBuiltData.client.environmentTemplates import INCURSION_ENVIRONMENT_TEMPLATE_ID
from talecommon.const import INCURSION_TEMPLATE_CLASSES
from talecommon.const import templateClass
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelLarge
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.transform import Transform
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.util.color import Color
import carbonui.graphs.axislabels as axislabels
import carbonui.graphs.axis as axis
INCURSION_CHAT_WARNING_DELAY = 20
INCURSION_CHAT_CLOSE_DELAY = 120
COLOR_HIGH_SEC = (0.0,
 0.65,
 0.0,
 1.0)
COLOR_LOW_NULL_SEC = (1.0,
 0.0,
 0.0,
 1.0)
INCURSION_ENVIRONMENT_TEMPLATE = 2

class IncursionSvc(Service):
    __guid__ = 'svc.incursion'
    __notifyevents__ = ['OnTaleRemove', 'OnSessionChanged', 'OnTaleData']
    __startupdependencies__ = ['settings']

    def Run(self, *args):
        Service.Run(self, *args)
        self.incursionData = None
        self.enableSoundOverrides = False
        self.stationAudioPlaying = False
        self.addStationSoundThreadRunning = False
        self.isDisablingHud = False
        self.isActivatingHud = False
        self.incursionChatInfoByTaleId = {}
        self.waitingIncursionChannelTaleID = set()
        self.rewardsByID = {}
        self.soundUrlByKey = {'hangar': 10004,
         const.groupStation: 10007,
         const.groupAsteroidBelt: 10003,
         'enterSystem': 10005}

    def OnTaleData(self, solarSystemID, data):
        for taleData in data.itervalues():
            self.SetIncursion(taleData, fadeEffect=False, reason='Entered incursion system')

    def SetIncursion(self, data, fadeEffect = False, reason = None):
        if data.templateClassID in INCURSION_TEMPLATE_CLASSES:
            self.LogInfo('Starting the incursion UI for tale', data.taleID, '. Reason:', reason)
            self.incursionData = data
            self.enableSoundOverrides = True
            self.JoinIncursionChat(data.taleID)
            soundURL = self.GetSoundUrlByKey('enterSystem')
            if soundURL is not None:
                sm.GetService('audio').SendUIEvent(soundURL)
            if session.stationid is not None:
                self.AddIncursionStationSoundIfApplicable()
            sm.GetService('infoPanel').UpdateIncursionsPanel()
            GetEnvironmentService().AddSystemEnvironment('incursion', INCURSION_ENVIRONMENT_TEMPLATE_ID)

    def OnTaleRemove(self, taleID, templateClassID, templateID):
        if templateClassID not in INCURSION_TEMPLATE_CLASSES:
            return
        if self.incursionData is None:
            return
        self.LogInfo('OnTaleRemove', taleID)
        self.enableSoundOverrides = False
        GetEnvironmentService().RemoveEnvironment('incursion')
        self.incursionData = None
        sm.GetService('infoPanel').UpdateIncursionsPanel()
        self.StartTimeoutOfIncursionChat(taleID)

    def OnSessionChanged(self, isremote, sess, change):
        for taleID in self.incursionChatInfoByTaleId:
            self.StartTimeoutOfIncursionChat(taleID)

        if 'solarsystemid2' in change:
            oldSolarsystem, newSolarsystem = change['solarsystemid2']
            if self.incursionData:
                if self.IsSystemInIncursion(oldSolarsystem):
                    self.enableSoundOverrides = False
                if self.IsSystemInIncursion(newSolarsystem):
                    self.enableSoundOverrides = True
                else:
                    self.incursionData = None
                sm.GetService('infoPanel').UpdateIncursionsPanel()
        if 'stationid' in change:
            self.stationAudioPlaying = False
            oldStationID, newStationID = change['stationid']
            if newStationID != None:
                self.AddIncursionStationSoundIfApplicable()

    def IsSystemInIncursion(self, solarsystemID):
        return self.incursionData is not None and solarsystemID in self.incursionData.incursedSystems

    def GetMusicState(self, solarsystemid):
        if self.IsSystemInIncursion(solarsystemid):
            if self.incursionData is not None:
                return getattr(self.incursionData, 'musicState', None)

    def _EndTimeoutOfIncursionChat(self, taleID):
        if taleID in self.waitingIncursionChannelTaleID:
            self.waitingIncursionChannelTaleID.remove(taleID)

    def IsTaleInTheCurrentSystem(self, taleID):
        if self.incursionData is not None:
            if self.incursionData.taleID == taleID:
                return True
        return False

    def IsIncursionActive(self):
        if self.incursionData is not None:
            return self.incursionData.templateClassID in INCURSION_TEMPLATE_CLASSES
        return False

    def GetActiveIncursionData(self):
        return self.incursionData

    def TimeoutOfIncursionChat_Thread(self, taleID):
        blue.pyos.synchro.SleepWallclock(INCURSION_CHAT_WARNING_DELAY * 1000)
        if self.IsTaleInTheCurrentSystem(taleID):
            self._EndTimeoutOfIncursionChat(taleID)
            return
        channelID = self._GetChannelId(taleID)
        self._AnnounceChatClosure(channelID)
        blue.pyos.synchro.SleepWallclock(INCURSION_CHAT_CLOSE_DELAY * 1000)
        if self.IsTaleInTheCurrentSystem(taleID):
            self._EndTimeoutOfIncursionChat(taleID)
            return
        GetChatService().LeaveChannel(channelID)
        if taleID in self.incursionChatInfoByTaleId:
            del self.incursionChatInfoByTaleId[taleID]
        self._EndTimeoutOfIncursionChat(taleID)

    def _GetChannelId(self, taleId):
        return self.incursionChatInfoByTaleId[taleId]['incursionType'] + '_' + str(taleId)

    def _AnnounceChatClosure(self, channelID):
        window = GetChatService().GetGroupChatWindow(channelID)
        if window:
            window.Receive(const.ownerSystem, localization.GetByLabel('UI/Incursion/LeaveChat', minutesRemaining=INCURSION_CHAT_CLOSE_DELAY / 60))

    def StartTimeoutOfIncursionChat(self, taleID):
        if taleID not in self.waitingIncursionChannelTaleID:
            self.waitingIncursionChannelTaleID.add(taleID)
            uthread.new(self.TimeoutOfIncursionChat_Thread, taleID).context = 'IncursionSvc::StartTimeoutOfIncursionChat'

    def JoinIncursionChat(self, taleID):
        uthread.new(self._JoinIncursionChat, taleID)

    def _JoinIncursionChat(self, taleID):
        while not sm.GetService('settings').IsCharSettingsLoaded():
            blue.synchro.Yield()

        if not hasattr(self.incursionData, 'hasChat') or not self.incursionData.hasChat:
            return
        if taleID not in self.incursionChatInfoByTaleId:
            self._SetIncursionChatInfo(taleID)
            channelID = self._GetChannelId(taleID)
            GetChatService().JoinChannel(channelID)
            self._PostIncursionChatAnnouncement(channelID)
        else:
            channelID = self._GetChannelId(taleID)
            GetChatService().JoinChannel(channelID)

    def _PostIncursionChatAnnouncement(self, channelID):
        retries = 0
        while retries < 3:
            window = GetChatService().GetGroupChatWindow(channelID)
            if window:
                break
            blue.synchro.SleepWallclock(1000)
            retries += 1

        if not window or not self.incursionData.chatAnnouncementMessageId:
            return
        if self._IsConstellationIncursion():
            constellationName = cfg.evelocations.Get(session.constellationid).name
            message = localization.GetByMessageID(self.incursionData.chatAnnouncementMessageId, constellationName=constellationName)
        elif self._IsSpreadingIncursion():
            message = localization.GetByMessageID(self.incursionData.chatAnnouncementMessageId)
        else:
            return
        window.Receive(const.ownerSystem, message)

    def _SetIncursionChatInfo(self, taleID):
        self.incursionChatInfoByTaleId[taleID] = {'constellationId': session.constellationid,
         'distributionNameId': self.incursionData.templateNameID}
        self.incursionChatInfoByTaleId[taleID]['incursionType'] = ''
        if self._IsConstellationIncursion():
            self.incursionChatInfoByTaleId[taleID]['incursionType'] = 'incursion'
        elif self._IsSpreadingIncursion():
            self.incursionChatInfoByTaleId[taleID]['incursionType'] = 'spreadingIncursion'

    def _IsConstellationIncursion(self):
        return self.incursionData.templateClassID == templateClass.incursion

    def _IsSpreadingIncursion(self):
        return self.incursionData.templateClassID == templateClass.spreadingIncursion

    def GetConstellationNameFromTaleIDForIncursionChat(self, taleID):
        if taleID in self.incursionChatInfoByTaleId and self.incursionChatInfoByTaleId[taleID]['constellationId']:
            return cfg.evelocations.Get(self.incursionChatInfoByTaleId[taleID]['constellationId']).name
        return ''

    def GetDistributionName(self, taleId):
        distributionNameId = self.incursionChatInfoByTaleId.get(taleId, None)['distributionNameId']
        if distributionNameId:
            return localization.GetByMessageID(distributionNameId)
        return localization.GetByLabel('UI/Generic/Unknown')

    def GetDelayedRewards(self, rewardGroupID):
        return self.GetDelayedRewardsByGroupIDs([rewardGroupID]).get(rewardGroupID)

    def GetDelayedRewardsByGroupIDs(self, rewardGroupIDs):
        rewardGroupIDs.sort()
        rewardsByRewardGroupID = sm.RemoteSvc('rewardMgr').GetDelayedRewardsByGroupIDs(tuple(rewardGroupIDs))
        return rewardsByRewardGroupID

    def DoRewardChart(self, rewardID, parent):

        def GetRewardData():
            maxRewardValue = 0
            minPlayerCount = 0
            maxPlayerCount = 0
            allSecurityBandTable = None
            lowSecurityBandTable = None
            highSecurityBandTable = None
            rewardTables = get_immediate_reward_tables(rewardID)
            for rewardTable in rewardTables:
                if not rewardTables:
                    continue
                if is_security_criteria_all(rewardTable):
                    maxRewardValue = get_max_reward_from_tables_with_reward_type(rewardTables, REWARD_TYPE_ISK)
                    minPlayerCount = get_min_player_count_from_reward_tables(rewardTables)
                    maxPlayerCount = get_max_player_count_from_reward_tables(rewardTables)
                    allSecurityBandTable = rewardTables[0]
                    break
                if is_security_criteria_high(rewardTable):
                    highSecurityBandTable = rewardTable
                elif is_security_criteria_low(rewardTable):
                    lowSecurityBandTable = rewardTable
                else:
                    continue
                maxRewardValue = max(maxRewardValue, get_max_reward_from_tables_with_reward_type(rewardTables, REWARD_TYPE_ISK))
                minPlayerCount = min(minPlayerCount, get_min_player_count_from_reward_tables(rewardTables))
                maxPlayerCount = max(maxPlayerCount, get_max_player_count_from_reward_tables(rewardTables))

            scale = 1.0 / maxRewardValue
            majorTick = (maxPlayerCount - minPlayerCount) / 4
            majorTick = 1 if majorTick < 2 else majorTick
            data1 = []
            data2 = [] if allSecurityBandTable is None else None
            labels = []
            for x in xrange(minPlayerCount, maxPlayerCount + 1):
                if allSecurityBandTable is not None:
                    quantity = get_reward_for_player_count(allSecurityBandTable, x) * scale
                    data1.append(quantity)
                else:
                    quantityHigh = get_reward_for_player_count(highSecurityBandTable, x) * scale
                    quantityLow = get_reward_for_player_count(lowSecurityBandTable, x) * scale
                    data1.append(quantityHigh)
                    data2.append(quantityLow)
                labels.append(x)

            return (data1,
             data2,
             labels,
             majorTick)

        valuesHigh, valuesLow, players, majorTick = GetRewardData()
        axisValues = (0.0, 0.5, 1.0)
        main = PanelUnderlay(parent=parent, align=uiconst.TOALL, bgColor=Color.GetGrayRGBA(0.0, 0.25))

        def valueFilter(x):
            if x not in axisValues:
                return ''
            return str(x)

        def playerFilter(x):
            if x % majorTick != 0:
                return ''
            return str(int(x))

        verticalAxis = axis.AutoTicksAxis((0.0, 1.0), tickCount=5, margins=(0.01, 0.01), labelFormat=valueFilter)
        horizontalAxis = axis.CategoryAxis(players, labelFormat=playerFilter)
        EveLabelLarge(parent=main, align=uiconst.TOTOP, padTop=6, padBottom=0, text='<center>%s</center>' % localization.GetByLabel('UI/Incursion/Reward/Title'))
        EveLabelSmall(parent=main, align=uiconst.TOBOTTOM, width=120, padBottom=6, text='<center>%s</center>' % localization.GetByLabel('UI/Incursion/Reward/NumberPilots'))
        axislabels.AxisLabels(parent=main, align=uiconst.TORIGHT, width=24, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, minFactor=1.0, maxFactor=0.0, padBottom=17, padTop=7)
        axislabels.AxisLabels(parent=main, align=uiconst.TOBOTTOM, height=24, axis=horizontalAxis, orientation=axis.AxisOrientation.HORIZONTAL, textAlignment=uiconst.CENTER, padLeft=24)
        sideTransform = Transform(name='myTransform', parent=main, align=uiconst.TOLEFT, width=24, rotationCenter=(0.5, 0.5), rotation=math.pi / 2)
        EveLabelSmall(name='myLabel', parent=sideTransform, width=120, align=uiconst.CENTER, text='<center>%s</center>' % localization.GetByLabel('UI/Incursion/Reward/PayoutMultiplier'))
        legendContainer = Container(name='container', parent=main, height=14, align=uiconst.TOTOP)
        graphArea = GraphArea(name='graph', parent=main, align=uiconst.TOALL, bgColor=Color.GetGrayRGBA(0.2, 0.5))
        graphArea.AddAxis(axis.AxisOrientation.HORIZONTAL, horizontalAxis, 0.0, 1.0)
        graphArea.AddAxis(axis.AxisOrientation.VERTICAL, verticalAxis, 1.0, 0.0)
        Grid(parent=graphArea, axis=verticalAxis, orientation=axis.AxisOrientation.VERTICAL, color=Color.GetGrayRGBA(1.0, 0.4))

        def _createLegend(items, legendParent):
            container = legendParent
            for item, text in items:
                item.height = 10
                item.width = 10
                item.align = uiconst.TOLEFT
                item.padding = (6, 1, 2, 3)
                item.SetParent(container)
                Label(parent=container, align=uiconst.TOLEFT, text=text, color=(1.0, 1.0, 1.0, 0.5), fontsize=carbonui.fontconst.EVE_SMALL_FONTSIZE)

        def _lineGraph(color, values):
            ranges = []
            i0 = 0
            while i0 < len(values) - 1:
                val0 = values[i0]
                repeatRange = [i0, i0]
                i1 = i0 + 1
                while i1 < len(values):
                    val1 = values[i1]
                    if val1 != val0:
                        break
                    else:
                        repeatRange[1] = i1
                    i1 += 1

                i0 = i1
                if repeatRange[0] != repeatRange[1]:
                    ranges.append(repeatRange)

            dataPoints = range(len(values))
            valuesPruned = values[:]
            ranges.reverse()
            for i0, i1 in ranges:
                valuesPruned = valuesPruned[:i0 + 1] + valuesPruned[i1:]
                dataPoints = dataPoints[:i0 + 1] + dataPoints[i1:]

            return LineGraph(parent=graphArea, categoryAxis=horizontalAxis, valueAxis=verticalAxis, values=valuesPruned, lineColor=color, lineWidth=1, dataPoints=dataPoints)

        l0 = _lineGraph(COLOR_HIGH_SEC, valuesHigh)
        label1 = localization.GetByLabel('UI/Common/Ratio')
        if valuesLow is not None:
            label1 = localization.GetByLabel('UI/Common/HighSec')
        legendItems = [(l0.GetLegendItem(), label1)]
        if valuesLow is not None:
            l1 = _lineGraph(COLOR_LOW_NULL_SEC, valuesLow)
            legendItems.append((l1.GetLegendItem(), localization.GetByLabel('UI/Common/LowNullSec')))
        _createLegend(legendItems, legendContainer)

    def GetSoundUrlByKey(self, key):
        if self.enableSoundOverrides == False:
            return
        soundID = self.soundUrlByKey.get(key, None)
        if soundID is not None:
            soundUrl = GetSoundEventName(soundID)
            if soundUrl is None:
                self.LogError('Unable to find a sound for key', key, 'and soundID', soundID)
        else:
            soundUrl = None
        return soundUrl

    def AddIncursionStationSoundIfApplicable(self):
        if not self.addStationSoundThreadRunning and self.enableSoundOverrides:
            self.addStationSoundThreadRunning = True
            uthread.new(self.AddIncursionStationSoundIfApplicableThread).context = 'incursionSvc::AddIncursionStationSoundIfApplicableThread'

    def AddIncursionStationSoundIfApplicableThread(self):
        count = 0
        success = False
        while success == False and count < 60:
            blue.synchro.SleepWallclock(1000)
            count += 1
            if session.stationid is None:
                success = True
                break
            try:
                if not self.stationAudioPlaying:
                    activeScene = sm.GetService('sceneManager').GetRegisteredScene('hangar')
                    stringToMatch = 'invisible_sound_locator_'
                    soundLocator = FindSoundLocatorThatStartsWith(activeScene, stringToMatch)
                    addedSound = self.GetSoundUrlByKey('hangar')
                    if addedSound is not None and soundLocator is not None:
                        ReplaceHangarSound(soundLocator, addedSound)
                        self.stationAudioPlaying = True
                        success = True
            except:
                self.LogInfo('Could not add incursion station sound trying again in 1 second')

        if success == False:
            self.LogError('Incursion station audio could not be added after 60 tries')
        self.addStationSoundThreadRunning = False


def FindSoundLocatorThatStartsWith(scene, startingString):
    for transform in scene.objects:
        if transform.name.startswith(startingString):
            return transform


def ReplaceHangarSound(soundLocator, soundEvent):
    if not soundLocator.observers:
        return
    for objects in soundLocator.observers:
        objects.observer.SendEvent('fade_out')

    soundLocator.observers[0].observer.SendEvent(soundEvent[6:])

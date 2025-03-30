#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\journal.py
from operator import attrgetter
import blue
import telemetry
import carbonui.const as uiconst
import evetypes
import geo2
import localization
import log
import uthread
import utillib
from carbon.common.script.sys.service import Service
from carbon.common.script.util.format import FmtDate, FmtSimpleDateUTC, FmtTimeInterval, ParseDate, ParseSmallDate
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveEdit, eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.divider import Divider
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from carbonui.window.header.tab_navigation import TabNavigationWindowHeader
from eve.client.script.ui.shared.incursionJournal import GlobalIncursionReportEntry, IncursionTab
from eve.client.script.ui.shared.neocom.activeMissionController import ActiveMissionController
from eve.client.script.ui.station.agents import agentUtil
from eve.client.script.ui.station.agents.agentConst import MISSIONSTATELABELS
from eve.client.script.ui.station.agents.agentDialogueUtil import GetAgentNameAndLevel
from eve.client.script.ui.station.missions.missionentry import VirtualAgentMissionEntry
from eve.common.lib import appConst
from eve.common.lib import appConst as const
from eve.common.lib.appConst import factionDrifters
from eve.common.script.mgt import appLogConst
from eve.common.script.mgt import appLogConst as logConst
from eve.common.script.sys.rowset import IndexRowset
from evePathfinder.core import IsUnreachableJumpCount
from eveservices.menu import GetMenuService
from grouprewards import REWARD_TYPE_ISK
from grouprewards import REWARD_TYPE_LP
from grouprewards.data import get_max_reward_value_by_reward_type
from inventorycommon.const import ownerAmarrNavy
from localization import GetByLabel
from menu import MenuLabel, MenuList
MAX_COL_LENGTH = 60

class ReportSortBy():
    Constellation, LP, Jumps, Influence, StagingSolarSystem, Security = range(6)


REPORT_SORT_PARAMETERS = (('constellationName', False),
 ('loyaltyPoints', True),
 ('jumps', False),
 ('influence', True),
 ('stagingSolarSystemName', False),
 ('security', True))
REWARD_SCOUT = 8
REWARD_VANGUARD = 1
REWARD_ASSAULT = 2
REWARD_HQ = 3
REWARD_BOSS = 10
REWARD_THRONE_WORLDS_LIGHT = 15
REWARD_THRONE_WORLDS_MEDIUM = 16
REWARD_THRONE_WORLDS_HEAVY = 17
INCURSION_DUNGEONS = {'scout': (utillib.KeyVal(severity='scout', index=1, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/OneText'),
           utillib.KeyVal(severity='scout', index=2, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/TwoText'),
           utillib.KeyVal(severity='scout', index=3, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/ThreeText'),
           utillib.KeyVal(severity='scout', index=4, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/FourText')),
 'vanguard': (utillib.KeyVal(severity='vanguard', index=1, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/OneText'), utillib.KeyVal(severity='vanguard', index=2, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/TwoText'), utillib.KeyVal(severity='vanguard', index=3, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/ThreeText')),
 'assault': (utillib.KeyVal(severity='assault', index=1, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/OneText'), utillib.KeyVal(severity='assault', index=2, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/TwoText'), utillib.KeyVal(severity='assault', index=3, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/ThreeText')),
 'hq': (utillib.KeyVal(severity='hq', index=1, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/OneText'),
        utillib.KeyVal(severity='hq', index=2, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/TwoText'),
        utillib.KeyVal(severity='hq', index=3, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/ThreeText'),
        utillib.KeyVal(severity='hq', index=4, rewardID=REWARD_BOSS, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FourText'),
        utillib.KeyVal(severity='hq', index=5, rewardID=REWARD_BOSS, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Five', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FiveText')),
 'amarr': (utillib.KeyVal(severity='defensiveOutpost', index=1, rewardID=REWARD_THRONE_WORLDS_LIGHT, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpost', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpostText'), utillib.KeyVal(severity='encampment', index=2, rewardID=REWARD_THRONE_WORLDS_MEDIUM, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampment', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampmentText'), utillib.KeyVal(severity='battalion', index=3, rewardID=REWARD_THRONE_WORLDS_HEAVY, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalion', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalionText')),
 'drifters': (utillib.KeyVal(severity='moderateInflux', index=1, rewardID=REWARD_THRONE_WORLDS_LIGHT, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInfluxText'), utillib.KeyVal(severity='severeInflux', index=2, rewardID=REWARD_THRONE_WORLDS_MEDIUM, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInfluxText'), utillib.KeyVal(severity='criticalInflux', index=3, rewardID=REWARD_THRONE_WORLDS_HEAVY, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInfluxText'))}
ENGLISH_MISSIONS_SETTING = 'AgentMissionsInEnglish'

def _GetIncursionJournalEntry(label, **kwargs):
    label_path = '/'.join(['UI/Incursion/Journal', label])
    return GetByLabel(label_path, **kwargs)


def _GetInvasionJournalEntry(label, **kwargs):
    label_path = '/'.join(['UI/Invasion/Journal', label])
    return GetByLabel(label_path, **kwargs)


def FormatJournalEntry(label, rewardID, **kwargs):
    if rewardID == appConst.rewardInvasions:
        return _GetInvasionJournalEntry(label, **kwargs)
    return _GetIncursionJournalEntry(label, **kwargs)


class LPTypeFilter():
    LPLost = -1
    LPPayedOut = -2


class JournalSvc(Service):
    __exportedcalls__ = {'Refresh': [],
     'GetMyAgentJournalDetails': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.journal'
    __notifyevents__ = ['ProcessSessionChange',
     'OnAgentMissionChange',
     'OnEscalatingPathMessage',
     'OnEscalatingPathChange',
     'OnFleetEscalatingPathMessage',
     'ProcessUIRefresh',
     'OnSessionReset']
    __servicename__ = 'journal'
    __displayname__ = 'Journal Client Service'
    __dependencies__ = ['window', 'settings']

    def Run(self, memStream = None):
        log.LogInfo('Starting Journal')
        self.Reset()
        self.outdatedAgentJournals = []
        self.pathPlexPositionByInstanceID = {}

    def Stop(self, memStream = None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()

    def OnSessionReset(self):
        self.Reset()
        self.outdatedAgentJournals = []
        self.pathPlexPositionByInstanceID = {}

    def ProcessSessionChange(self, isremote, session, change):
        if eve.session.charid is None:
            self.Stop()
            self.Reset()
        if 'locationid' in change:
            self.pathPlexPositionByInstanceID = {}

    def ProcessUIRefresh(self):
        self.Reset()

    @telemetry.ZONE_METHOD
    def OnAgentMissionChange(self, missionState, agentID):
        if agentID is None:
            self.agentjournal = None
        elif agentID not in self.outdatedAgentJournals:
            self.outdatedAgentJournals.append(agentID)
        sm.GetService('addressbook').RefreshWindow()
        wnd = self.GetWnd()
        if (not wnd or wnd.destroyed) and missionState not in (appConst.agentMissionDeclined,
         appConst.agentMissionCompleted,
         appConst.agentMissionQuit,
         appConst.agentMissionOfferDeclined,
         appConst.agentMissionDungeonMoved):
            hint = GetByLabel('UI/Neocom/Blink/AgentMissionStatusChanged', agentID=agentID)
            sm.GetService('neocom').Blink(JournalWindow.default_windowID, hint)
        sm.ScatterEvent('OnAgentMissionChanged', missionState, agentID)

    def OnEscalatingPathMessage(self, instanceID):
        exp1 = self.GetEscalations()
        exp2 = IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if instanceID not in exp2:
            exp1 = self.GetEscalations(1)
            exp2 = IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if instanceID in exp2:
            data = utillib.KeyVal()
            data.rec = exp2[instanceID]
            self.PopupDungeonDescription(data)
        else:
            log.LogInfo("Someone tried loading a message that isn't there")

    def OnEscalatingPathChange(self, *args):
        self.GetEscalations(1)

    def OnFleetEscalatingPathMessage(self, charID, journalEntryTemplateID):
        if charID != eve.session.charid:
            if cfg.eveowners.GetIfExists(charID) is not None:
                dungeonName = GetByLabel('UI/Journal/JournalWindow/Dungeons/DungeonName', character=charID)
            else:
                dungeonName = GetByLabel('UI/Journal/JournalWindow/Dungeons/DungeonNameUnknown')
            journalEntry = localization.GetByMessageID(journalEntryTemplateID)
            data = utillib.KeyVal()
            data.instanceID = 0
            data.dungeonName = dungeonName
            data.pathEntry = GetByLabel('UI/Journal/JournalWindow/Dungeons/UpdatedJournalEntry', character=charID, journalEntry=journalEntry)
            data.fakerec = True
            data.rec = data
            self.PopupDungeonDescription(data)

    def Reset(self):
        self.agentjournal = None
        self.semaphore = uthread.Semaphore()
        self.notext = None
        self.escalationRowset = None
        self._activeMissions = []

    def Refresh(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.maintabs.ReloadVisible()

    def GetWnd(self, new = 0, skipAutoSelect = False):
        if new:
            wnd = JournalWindow.Open(skipAutoSelect=skipAutoSelect)
        else:
            wnd = JournalWindow.GetIfOpen()
        return wnd

    def ShowIncursionTab(self, flag = None, constellationID = None, taleID = None, open = False):
        wnd = self.GetWnd(new=open, skipAutoSelect=True)
        if wnd is not None and not wnd.destroyed:
            blue.pyos.synchro.Yield()
            wnd.ShowIncursionTab(flag, constellationID, taleID)

    def GetEscalations(self, force = 0):
        if self.escalationRowset is None or force:
            self.escalationRowset = sm.RemoteSvc('dungeonExplorationMgr').GetMyEscalatingPathDetails()
            sm.ScatterEvent('OnEscalationsDataUpdated')
        return self.escalationRowset

    def PopupDungeonDescription(self, node):
        if node.get('fakerec', None):
            did = node.instanceID
            dname = node.dungeonName
            djentry = node.pathEntry
        else:
            if node.rec:
                dungeonDstData = node.rec.destDungeon
                dungeonSrcData = node.rec.srcDungeon
                dungeonInstanceID = node.rec.dungeon.instanceID
                journalEntryTemplateID = node.rec.journalEntryTemplateID
            else:
                dungeonDstData = node.destDungeon
                dungeonSrcData = node.srcDungeon
                dungeonInstanceID = node.dungeon.instanceID
                journalEntryTemplateID = node.journalEntryTemplateID
            did = dungeonInstanceID
            if dungeonDstData is not None:
                dname = localization.GetByMessageID(dungeonDstData.dungeonNameID)
            elif dungeonSrcData is not None:
                dname = localization.GetByMessageID(dungeonSrcData.dungeonNameID)
            else:
                log.LogError('No dungeon data to get dungeon name from. id:', did)
                return
            djentry = localization.GetByMessageID(journalEntryTemplateID)
        data = utillib.KeyVal()
        data.rec = node
        data.header = dname
        data.icon = '40_14'
        data.text = djentry
        data.caption = GetByLabel('UI/Common/Expeditions')
        data.hasDungeonWarp = True
        data.instanceID = did
        wnd = sm.GetService('transmission').OnIncomingTransmission(data)

    def GetMyAgentJournalDetails(self):
        self._CheckUpdateMissionData()
        return self.agentjournal

    def _CheckUpdateMissionData(self):
        s = getattr(self, 'semaphore', None)
        if s is not None:
            s.acquire()
        try:
            if self.agentjournal is None:
                self._UpdateMissionDataFull()
                self._UpdateActiveMissions()
            elif self.outdatedAgentJournals:
                self._UpdateMissionDataPartial()
                self._UpdateActiveMissions()
        finally:
            if s is not None:
                s.release()

    def _UpdateMissionDataFull(self):
        self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
        for mission in self.agentjournal[0]:
            for b in mission[6]:
                if getattr(b, 'originalHint', None) is None:
                    b.originalHint = b.hint
                b.hint = GetByLabel(b.originalHint, location=b.locationID, index=b.locationNumber + 1)

    def _UpdateMissionDataPartial(self):
        parallelCalls = []
        tmp = self.outdatedAgentJournals
        for agentID in self.outdatedAgentJournals:
            parallelCalls.append((sm.GetService('agents').GetAgentMoniker(agentID).GetMyJournalDetails, ()))

        self.outdatedAgentJournals = []
        parallelResults = uthread.parallel(parallelCalls)
        self.i = parallelResults
        if self.agentjournal is None:
            self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
        else:
            for agentID in tmp:
                for mission in self.agentjournal[0]:
                    if mission[4] == agentID:
                        self.agentjournal[0].remove(mission)
                        break

            for i in range(len(parallelResults)):
                for mission in parallelResults[i][0]:
                    for b in mission[6]:
                        if getattr(b, 'originalHint', None) is None:
                            b.originalHint = b.hint
                        b.hint = GetByLabel(b.originalHint, location=b.locationID, index=b.locationNumber + 1)

                agentID = tmp[i]
                for n in range(2):
                    self.agentjournal[n].extend(parallelResults[i][n])

    def _UpdateActiveMissions(self):
        self._activeMissions = []
        for missionData in self.agentjournal[:1][0]:
            self._activeMissions.append(ActiveMissionController(*missionData))

    def GetActiveMissions(self):
        self._CheckUpdateMissionData()
        return self._activeMissions

    def GetActiveMissionForAgent(self, agentID):
        for mission in self.GetActiveMissions():
            if mission.agentID == agentID:
                return mission

    def GetActiveStorylineMissions(self):
        return [ mission for mission in self.GetActiveMissions() if mission.isImportantMission ]

    def GetAgentMissions(self):
        return self.GetMyAgentJournalDetails()[:1][0]

    def IsMissionActiveWithAgent(self, agentID):
        for _, _, _, _, _agentID, _, _, _, _, _ in self.GetAgentMissions():
            if _agentID == agentID:
                return True

        return False

    def GetMyAgentJournalBookmarks(self):
        ret = []
        missions = self.GetMyAgentJournalDetails()[0]
        if len(missions):
            i = 0
            for i in range(len(missions)):
                missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                ret.append((missionName, bookmarks, agentID))

        return ret

    def CheckUndock(self, stationID):
        missions = self.GetMyAgentJournalDetails()[0]
        if len(missions):
            for i in range(len(missions)):
                missionState, importantMission, missionType, missionNameID, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                if missionState == const.agentMissionStateAccepted:
                    for b in bookmarks:
                        if b.itemID == stationID and b.locationType == 'objective.source':
                            if not sm.GetService('agents').CheckCourierCargo(agentID, b.itemID, contentID):
                                missionName = sm.GetService('agents').ProcessMessage((missionNameID, contentID), agentID)
                                return uicore.Message('CourierUndockMissingCargo', {'missionName': missionName}, uiconst.YESNO) == uiconst.ID_YES

        return True


class PlanetaryInteractionLaunchEntry(Generic):
    __guid__ = 'listentry.PlanetaryInteractionLaunchEntry'
    OnSelectCallback = None

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.node = node
        self.sr.label.text = node.label
        self.OnSelectCallback = node.Get('callback', None)
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.state = uiconst.UI_NORMAL
        self.sr.label.Update()

    def GetMenu(self):
        node = self.sr.node
        m = MenuList()
        if not node.expired:
            if node.rec.solarSystemID is not None:
                m += GetMenuService().CelestialMenu(node.rec.solarSystemID).filter('UI/Inflight/BookmarkLocation')
                m.append(None)
            if node.rec.solarSystemID == eve.session.solarsystemid:
                mickey = sm.StartService('michelle')
                me = mickey.GetBall(eve.session.shipid)
                dist = geo2.Vec3DistanceD((node.rec.x, node.rec.y, node.rec.z), (me.x, me.y, me.z))
                if dist < const.minWarpDistance:
                    m.append((MenuLabel('UI/Inflight/ApproachLocation'), self.Approach, list((node.rec.itemID, node))))
                else:
                    m.append((MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToLaunchPickup, (node.rec.launchID, node)))
        else:
            m.append(None)
            m.append((MenuLabel('UI/Commands/Remove'), self.DeleteLaunchEntry, (node.rec.launchID, node)))
        return m

    def Approach(self, launchID, node):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdFollowBall(launchID, 50)

    def WarpToLaunchPickup(self, launchID, node, *args):
        sm.GetService('michelle').CmdWarpToStuff('launch', launchID)

    def DeleteLaunchEntry(self, launchID, *args):
        rm = []
        for entry in self.sr.node.scroll.GetNodes():
            if entry.id == launchID:
                rm.append(entry)

        if rm:
            self.sr.node.scroll.RemoveEntries(rm)
        uthread.new(sm.RemoteSvc('planetMgr').DeleteLaunch, launchID)
        uthread.new(sm.GetService('planetUI').GetLaunches, force=1)


class JournalWindow(Window):
    __guid__ = 'form.Journal'
    __notifyevents__ = ['ProcessSessionChange', 'OnAgentMissionChange']
    default_width = 525
    default_height = 300
    default_minSize = (465, 300)
    default_windowID = 'journal'
    default_captionLabelPath = 'UI/Journal/JournalWindow/Caption'
    default_descriptionLabelPath = 'Tooltips/Neocom/Journal_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/journal.png'
    default_scrollPanelPadding = 10

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.entry = None
        self.showingIncursionTab = False
        self.incursionLPLogData = None
        skipAutoSelect = attributes.Get('skipAutoSelect', False)
        self.SetScope(uiconst.SCOPE_INGAME)
        self.clientPathfinderService = sm.GetService('clientPathfinderService')
        width = settings.char.ui.Get('journalIncursionEncounterScrollWidth', 100)
        self.sr.incursionEncounterScroll = eveScroll.Scroll(parent=self.sr.main, name='encounterScroll', align=uiconst.TOLEFT, width=width, state=uiconst.UI_HIDDEN)
        self.LoadIncursionDistributions()
        divider = Divider(name='incursionEncountersDivider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_HIDDEN)
        dividerMin = 100
        dividerMax = self.sr.incursionEncounterScroll.GetMaxTextWidth(200) + self.default_scrollPanelPadding
        divider.Startup(self.sr.incursionEncounterScroll, 'width', 'x', dividerMin, dividerMax)
        divider.OnSizeChanged = self.OnIncursionEncounterResize
        self.sr.incursionEncounterDivider = divider
        self.incursionReportFilter = Container(name='incursionGlobalReportFilter', parent=self.sr.main, align=uiconst.TOTOP, height=Button.default_height, state=uiconst.UI_HIDDEN)
        options = ((GetByLabel('UI/Common/Constellation'), ReportSortBy.Constellation),
         (GetByLabel('UI/Incursion/Journal/StagingSystem'), ReportSortBy.StagingSolarSystem),
         (GetByLabel('UI/Common/Jumps'), ReportSortBy.Jumps),
         (GetByLabel('UI/Common/Security'), ReportSortBy.Security),
         (GetByLabel('UI/LPStore/LP'), ReportSortBy.LP),
         (GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'), ReportSortBy.Influence))
        self.incursionReportSortCombo = Combo(label=GetByLabel('UI/Common/SortBy'), parent=self.incursionReportFilter, options=options, name='reportSortByCombo', callback=self.OnReportSortByComboChange, align=uiconst.TOLEFT, width=200, select=settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation), padLeft=4)
        Button(parent=self.incursionReportFilter, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/Icons/105_32_22.png', iconSize=24, hint=GetByLabel('UI/Incursion/Journal/RefreshGlobalReport'), func=lambda : self.ShowIncursionTab(IncursionTab.GlobalReport), args=())
        self.incursionLPLogFilters = Container(name='incursionLPLogFilters', parent=self.sr.main, height=Button.default_height, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=16)
        self.incursionLPLoadbutton = Button(parent=self.incursionLPLogFilters, label=GetByLabel('UI/Generic/Load'), align=uiconst.BOTTOMRIGHT, func=self.LoadIncursionLPLog)
        now = FmtDate(blue.os.GetWallclockTime(), 'sn')
        self.incursionLPDate = SingleLineEditText(name='incursionFromdate', parent=self.incursionLPLogFilters, setvalue=now, align=uiconst.TOLEFT, maxLength=16, label=GetByLabel('UI/Common/Date'), padding=(4, 0, 0, 0), width=110)
        options = [(GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        self.incursionLPTaleIDFilter = Combo(label=GetByLabel('UI/Incursion/Journal/Incursion'), parent=self.incursionLPLogFilters, options=options, name='incursionTaleIDFilter', width=110, align=uiconst.TOLEFT, padding=(4, 0, 0, 0))
        options = [(GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None)]
        self.incursionLPTaleIDFilter = Combo(label=GetByLabel('UI/Incursion/Journal/Types'), parent=self.incursionLPLogFilters, options=options, name='incursionTypeFilter', width=110, align=uiconst.TOLEFT, padding=(4, 0, 0, 0))
        self.sr.incursionEncounterEdit = eveEdit.Edit(parent=self.sr.main, name='incursionEncounterEdit', state=uiconst.UI_HIDDEN, readonly=True, align=uiconst.TOALL)
        self.sr.main = self.GetChild('main')
        self.sr.agentEnglishMissionsCnt = Container(name='agentEnglishMissionCnt', parent=self.sr.main, padding=(const.defaultPadding,) * 4, height=20, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN)
        self.sr.agentEnglishMissions = Checkbox(parent=self.sr.agentEnglishMissionsCnt, name='agentMissionEnglish', text=GetByLabel('UI/Journal/JournalWindow/Agents/ShowEnglishMissionNames'), checked=settings.user.localization.Get(ENGLISH_MISSIONS_SETTING, False), callback=self.OnAgentEnglishCheckBoxChange)
        self.sr.scroll = eveScroll.Scroll(parent=self.sr.main)
        self.sr.scroll.multiSelect = 0
        self.ConstructTabGroup(skipAutoSelect)
        sm.RegisterNotify(self)

    def Prepare_Header_(self):
        self.header = TabNavigationWindowHeader()

    def ConstructTabGroup(self, skipAutoSelect):
        self.tabGroup = self.header.tab_group
        self.tabGroup.AddTab(GetByLabel('UI/PeopleAndPlaces/AgentMissions'), self.sr.scroll, self, ('agent_missions', 0), hint=GetByLabel('UI/Journal/JournalWindow/Agents/MissionsHint'))
        if not skipAutoSelect:
            self.tabGroup.AutoSelect()

    def MouseDown(self, *args):
        sm.GetService('neocom').BlinkOff(self.default_windowID)

    def LoadIncursionDistributions(self):
        self._ConstructIncursionDistributionData()
        scrolllist = []
        for distributionId, distributionData in self.incursionDistributions.iteritems():
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.LoadIncursionEncounters,
             'label': distributionData['distributionName'],
             'sublevel': 0,
             'selected': False,
             'id': ('distribution', distributionId),
             'showlen': False,
             'state': 'locked',
             'BlockOpenWindow': True,
             'showicon': 'hide'}))

        scrolllist.sort(key=lambda encounter: encounter['label'])
        self.sr.incursionEncounterScroll.LoadContent(contentList=scrolllist)

    def LoadIncursionEncounters(self, distributionNodeData, *args):
        scrolllist = []
        distributionId = distributionNodeData['id'][1]
        infestationTypes = self.incursionDistributions[distributionId]['infestationTypes']
        for encounterId, encounterLabel in infestationTypes.iteritems():
            scrolllist.append(GetFromClass(ListGroup, {'GetSubContent': self.GetIncursionDungeons,
             'label': encounterLabel,
             'encounterId': encounterId,
             'sublevel': 1,
             'selected': False,
             'id': ('encounter', encounterId),
             'showlen': False,
             'state': 'locked',
             'BlockOpenWindow': True,
             'showicon': 'hide'}))

        scrolllist.sort(key=lambda encounter: encounter['label'])
        return scrolllist

    def GetIncursionDungeons(self, encounterDataNode, *args):
        scrolllist = []
        incursionSvc = sm.GetService('incursion')
        for dungeon in INCURSION_DUNGEONS[encounterDataNode['encounterId']]:
            scrolllist.append(GetFromClass(Generic, {'label': localization.GetImportantByLabel(dungeon.name),
             'OnClick': self.ShowEncounter,
             'dungeon': dungeon,
             'sublevel': 2,
             'id': ('dungeon', localization.GetImportantByLabel(dungeon.name)),
             'lpAmount': get_max_reward_value_by_reward_type(dungeon.rewardID, REWARD_TYPE_LP),
             'iskAmount': get_max_reward_value_by_reward_type(dungeon.rewardID, REWARD_TYPE_ISK)}))

        return scrolllist

    def _ConstructIncursionDistributionData(self):
        self.incursionDistributions = {'sansha': {'distributionName': localization.GetImportantByLabel('UI/TaleDistributions/SanshaIncursion'),
                    'infestationTypes': {'scout': localization.GetImportantByLabel('UI/Incursion/Common/Scout'),
                                         'vanguard': localization.GetImportantByLabel('UI/Incursion/Common/Vanguard'),
                                         'assault': localization.GetImportantByLabel('UI/Incursion/Common/Assault'),
                                         'hq': localization.GetImportantByLabel('UI/Incursion/Common/HQ')}},
         'drifters': {'distributionName': GetByLabel('UI/TaleDistributions/DefenseOfTheThroneWorldsIncursion'),
                      'infestationTypes': {'amarr': localization.GetByMessageID(cfg.eveowners.Get(ownerAmarrNavy).ownerNameID),
                                           'drifters': localization.GetByMessageID(cfg.eveowners.Get(factionDrifters).ownerNameID)}}}

    def ShowEncounter(self, node):
        data = node.sr.node
        imgLink = '<img size=250 style=margin-left:8;margin-top:8 src=reward:{rewardID} align=right>'
        html = GetByLabel(data.dungeon.text)
        self.sr.incursionEncounterEdit.SetText(html)

    def OnIncursionEncounterResize(self):
        settings.char.ui.Set('journalIncursionEncounterScrollWidth', self.sr.incursionEncounterScroll.width)

    def OnReportSortByComboChange(self, combo, key, value):
        self.SortIncursionGlobalReport(value)

    def Load(self, args):
        key, flag = args
        self.sr.scroll.ShowHint(None)
        self.incursionReportFilter.Hide()
        self.sr.incursionEncounterScroll.Hide()
        self.sr.incursionEncounterEdit.Hide()
        self.sr.scroll.Hide()
        self.incursionLPLogFilters.Hide()
        self.sr.agentEnglishMissionsCnt.Hide()
        if key == 'agents':
            self.sr.scroll.Show()
        elif key[:6] == 'agent_':
            self.sr.scroll.Show()
            self.ShowAgentTab(flag)
        elif key.startswith('incursions'):
            self.ShowIncursionTab(IncursionTab.LPLog)

    def OnAgentEnglishCheckBoxChange(self, checkbox):
        if checkbox.checked:
            settings.user.localization.Set(ENGLISH_MISSIONS_SETTING, True)
        else:
            settings.user.localization.Delete(ENGLISH_MISSIONS_SETTING)
        if getattr(self.sr, 'maintabs', None):
            self.tabGroup.ReloadVisible()

    def ShowAgentTab(self, statusflag = -1):
        self._SelectTab(self.tabGroup.sr.Get(GetByLabel('UI/Journal/JournalWindow/AgentsTab') + '_tab'))
        self.ShowLoad()
        showEnglishTitles = localization.util.GetLanguageID() != localization.const.LOCALE_SHORT_ENGLISH and settings.user.localization.Get(ENGLISH_MISSIONS_SETTING, False)
        if statusflag == 0:
            missions = sm.GetService('journal').GetMyAgentJournalDetails()[0]
            scrolllist = []
            if len(missions):
                missionIconData = []
                maxOptionalIcons = 0
                for i in xrange(len(missions)):
                    missionIconData.append(self.GetMissionIconDataForAgentTab(missions[i]))
                    maxOptionalIcons = max(maxOptionalIcons, len(missionIconData[i]))

                for i in xrange(len(missions)):
                    missionState, importantMission, missionTypeLabel, missionNameID, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                    missionType = GetByLabel(missionTypeLabel)
                    if isinstance(missionNameID, (int, long)):
                        missionName = localization.GetByMessageID(missionNameID)
                        if showEnglishTitles:
                            enMissionName = localization.GetByMessageID(missionNameID, languageID=localization.const.LOCALE_SHORT_ENGLISH)
                    else:
                        enMissionName = missionName = missionNameID
                    sm.GetService('agents').PrimeMessageArguments(agentID, contentID)
                    blankIconID = 'ui_38_16_39'
                    for j in xrange(maxOptionalIcons - len(missionIconData[i])):
                        missionIconData[i].insert(0, (blankIconID, ''))

                    missionLogInfo = '%s mission %d (%s) %s' % (MISSIONSTATELABELS[missionState],
                     i,
                     missionName,
                     'expires in ' + FmtTimeInterval(expirationTime - blue.os.GetWallclockTime()) if expirationTime else 'does not expire')
                    log.LogInfo('Journal::ShowAgentTab:', missionLogInfo)
                    if importantMission:
                        missionType = '<color=0xFFFFFF00>' + GetByLabel('UI/Journal/JournalWindow/Agents/ImportantMission', missionType=missionType) + '<color=0xffffffff>'
                    stateText, expirationText = agentUtil.GetMissionExpirationAndStateText(missionState, expirationTime)
                    level = sm.GetService('agents').GetAgentByID(agentID).level
                    agentName = GetAgentNameAndLevel(agentID, level)
                    if showEnglishTitles:
                        text = '<t>'.join([stateText,
                         agentName,
                         missionName,
                         enMissionName,
                         missionType,
                         expirationText])
                    else:
                        text = '<t>'.join([stateText,
                         agentName,
                         missionName,
                         missionType,
                         expirationText])
                    scrolllist.append(GetFromClass(VirtualAgentMissionEntry, {'missionState': missionState,
                     'agentID': agentID,
                     'label': text,
                     'missionIconData': missionIconData[i]}))

            if showEnglishTitles:
                headers = [GetByLabel('UI/Journal/JournalWindow/Agents/HeaderStatus'),
                 GetByLabel('UI/Agents/Agent'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderMission'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/EnglishName'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderType'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderExpiration')]
            else:
                headers = [GetByLabel('UI/Journal/JournalWindow/Agents/HeaderStatus'),
                 GetByLabel('UI/Agents/Agent'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderMission'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderType'),
                 GetByLabel('UI/Journal/JournalWindow/Agents/HeaderExpiration')]
            self.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=GetByLabel('UI/Journal/JournalWindow/Agents/NoMissionsOfferedOrAccepted'))
            if localization.util.GetLanguageID() != localization.const.LOCALE_SHORT_ENGLISH:
                self.sr.agentEnglishMissionsCnt.Show()
        self.HideLoad()

    def _SelectTab(self, tab):
        if tab is None:
            return
        if not tab.IsSelected():
            tab.Select(True)

    def GetMissionIconDataForAgentTab(self, missionJournalDetails):
        missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missionJournalDetails
        missionIconData = []
        chatBubbleIconID = 'ui_38_16_38'
        remoteMissionHints = []
        if remoteOfferable:
            remoteMissionHints.append(GetByLabel('UI/Agents/Dialogue/StandardMission/AcceptRemotelyHint'))
        if remoteCompletable:
            remoteMissionHints.append(GetByLabel('UI/Agents/Dialogue/StandardMission/CompleteRemotelyHint'))
        if remoteOfferable or remoteCompletable:
            remoteMissionHintText = '<br>'.join(remoteMissionHints)
            missionIconData.append((chatBubbleIconID, remoteMissionHintText))
        return missionIconData

    def GetJumpCount(self, toID):
        jumps = self.clientPathfinderService.GetAutopilotJumpCount(session.solarsystemid2, toID)
        if IsUnreachableJumpCount(jumps):
            return None
        return jumps

    def ShowIncursionTab(self, flag = None, constellationID = None, taleID = None):
        if self.showingIncursionTab:
            return
        self.showingIncursionTab = True
        if flag is None:
            flag = settings.char.ui.Get('journalIncursionTab', IncursionTab.GlobalReport)
        settings.char.ui.Set('journalIncursionTab', flag)
        self._SelectTab(self.tabGroup.sr.Get(GetByLabel('UI/Journal/JournalWindow/IncursionsTab') + '_tab'))
        if flag == IncursionTab.GlobalReport:
            self.sr.scroll.Show()
            self.incursionReportFilter.state = uiconst.UI_PICKCHILDREN
            starmap = sm.GetService('starmap')
            map = starmap.map
            report = sm.RemoteSvc('map').GetIncursionGlobalReport()
            rewardGroupIDs = [ r.rewardGroupID for r in report ]
            delayedRewards = sm.GetService('incursion').GetDelayedRewardsByGroupIDs(rewardGroupIDs)
            scrolllist = []
            factionsToPrime = set()
            for data in report:
                data.jumps = self.GetJumpCount(data.stagingSolarSystemID)
                data.influenceData = utillib.KeyVal(influence=data.influence, lastUpdated=data.lastUpdated, graceTime=data.graceTime, decayRate=data.decayRate)
                ssitem = map.GetItem(data.stagingSolarSystemID)
                data.stagingSolarSystemName = ssitem.itemName
                data.security = map.GetSecurityStatus(data.stagingSolarSystemID)
                data.constellationID = ssitem.locationID
                data.constellationName = map.GetItem(ssitem.locationID).itemName
                data.factionID = ssitem.factionID or starmap.GetAllianceSolarSystems().get(data.stagingSolarSystemID, None)
                factionsToPrime.add(data.factionID)
                rewards = delayedRewards.get(data.rewardGroupID, None)
                data.loyaltyPoints = rewards[0].rewardQuantity if rewards else 0
                scrolllist.append(GetFromClass(GlobalIncursionReportEntry, data))

            cfg.eveowners.Prime(list(factionsToPrime))
            self.sr.scroll.LoadContent(contentList=scrolllist, scrollTo=0.0)
            self.SortIncursionGlobalReport()
        elif flag == IncursionTab.LPLog:
            self.incursionLPLogFilters.Show()
            self.sr.scroll.Show()
            if taleID is not None and constellationID is not None:
                self.LoadIncursionLPLog(self.sr.scroll, taleID, constellationID)
            elif self.incursionLPLogData is None:
                self.sr.scroll.Clear()
                self.sr.scroll.ShowHint(GetByLabel('UI/Incursion/Journal/LoadData'))
            else:
                self.UpdateIncursionLPLog(self.incursionLPLogData)
        elif flag == IncursionTab.Encounters:
            self.sr.incursionEncounterEdit.Show()
            self.sr.incursionEncounterScroll.Show()
            self.sr.incursionEncounterDivider.Show()
        self.showingIncursionTab = False

    def SortIncursionGlobalReport(self, sortBy = None):
        if sortBy is None:
            sortBy = settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation)
        else:
            settings.char.ui.Set('journalIncursionReportSort', sortBy)
        attrName, reverse = REPORT_SORT_PARAMETERS[sortBy]
        scroll = self.sr.scroll
        scroll.sr.nodes = sorted(scroll.sr.nodes, key=attrgetter(attrName), reverse=reverse)
        scroll.UpdatePositionThreaded(fromWhere='SortIncursionGlobalReport')

    def LoadIncursionLPLog(self, scroll, taleID = None, constellationID = None):
        rewardMgr = session.ConnectToRemoteService('rewardMgr')
        self.incursionLPLogData = rewardMgr.GetRewardLPLogs()
        self.UpdateIncursionLPLog(self.incursionLPLogData, taleID, constellationID)

    def UpdateIncursionLPLog(self, data, selectedTaleID = None, selectedConstellationID = None):
        mapsvc = sm.GetService('map')
        taleIDFilter = self.incursionLPTaleIDFilter.selectedValue
        solarsystemTypeFilter = self.incursionLPTaleIDFilter.selectedValue
        try:
            fromDate = ParseSmallDate(self.incursionLPDate.GetValue())
        except (Exception, TypeError):
            dateString = localization.formatters.FormatDateTime(blue.os.GetWallclockTime(), dateFormat='short', timeFormat='none')
            fromDate = ParseDate(dateString)
            self.incursionLPDate.SetValue(dateString)

        fromDate += const.DAY
        dungeonTypes = set()
        taleIDs = {}
        filteredData = []
        for d in data:
            dungeonTypes.add(d.rewardMessageKey)
            constellationID = mapsvc.GetParent(d.solarSystemID)
            if constellationID is not None:
                constellation = mapsvc.GetItem(constellationID)
                if constellation is not None:
                    taleIDs[d.taleID] = constellation.itemName
            if selectedTaleID is not None:
                if selectedTaleID != d.taleID:
                    continue
            if taleIDFilter is not None and selectedTaleID is None:
                if taleIDFilter != d.taleID:
                    continue
            if solarsystemTypeFilter is not None:
                shouldAdd = False
                if solarsystemTypeFilter == LPTypeFilter.LPPayedOut:
                    if d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                        shouldAdd = True
                elif solarsystemTypeFilter == LPTypeFilter.LPLost:
                    if d.eventTypeID == logConst.eventRewardLPPoolLost:
                        shouldAdd = True
                elif solarsystemTypeFilter == d.rewardMessageKey:
                    shouldAdd = True
                if not shouldAdd:
                    continue
            if fromDate < d.date:
                continue
            filteredData.append(d)

        if selectedTaleID is not None:
            if selectedTaleID not in taleIDs:
                constellation = mapsvc.GetItem(selectedConstellationID)
                if constellation is not None:
                    taleIDs[selectedTaleID] = constellation.itemName
        scrolllist = []
        for d in filteredData:
            solarSystemType = ''
            if d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                solarSystemType = FormatJournalEntry('CompletedAndPaidOut', d.rewardID)
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                solarSystemType = FormatJournalEntry('CompletedAndNotPaidOut', d.rewardID)
            elif d.rewardMessageKey is not None and isinstance(d.rewardMessageKey, int):
                solarSystemType = localization.GetByMessageID(d.rewardMessageKey)
            elif d.rewardMessageKey is not None and d.rewardMessageKey != '':
                solarSystemType = GetByLabel(d.rewardMessageKey)
            if d.lpAmountAddedToPool is None:
                d.lpAmountAddedToPool = 0
            if d.lpAmountAddedToPool == 0:
                LPAmountAddedToPool = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountAddedToPool = '<color=0xFFFFFF00>' + localization.formatters.FormatNumeric(d.lpAmountAddedToPool) + '</color>'
            if d.lpAmountPayedOut is None:
                d.lpAmountPayedOut = 0
            if d.lpAmountPayedOut == 0:
                LPAmountPayedOut = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                LPAmountPayedOut = '<color=0xFFFF0000>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountPayedOut = '<color=0xFF00FF00>' + localization.formatters.FormatNumeric(d.lpAmountPayedOut) + '</color>'
            if d.numberOfPlayers is None:
                d.numberOfPlayers = 0
            description = ''
            if d.eventTypeID == logConst.eventRewardDisqualified:
                if d.disqualifierType == const.rewardIneligibleReasonTrialAccount:
                    description = FormatJournalEntry('DisqualifiedTrialAccount', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonInvalidGroup:
                    groupName = evetypes.GetGroupNameByGroup(d.disqualifierData)
                    description = FormatJournalEntry('DisqualifiedInvalidShipGroup2', d.rewardID, groupName=groupName)
                elif d.disqualifierType == const.rewardIneligibleReasonShipCloaked:
                    description = FormatJournalEntry('DisqualifiedCloaked', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonNotInFleet:
                    description = FormatJournalEntry('DisqualifiedNoFleet', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonNotBestFleet:
                    description = FormatJournalEntry('DisqualifiedNotBestFleet', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonNotTop5:
                    description = FormatJournalEntry('DisqualifiedNotInTopFive', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonNotTopN:
                    maxWinners = d.disqualifierData
                    description = FormatJournalEntry('DisqualifiedNotInTopN', d.rewardID, n=maxWinners)
                elif d.disqualifierType == const.rewardIneligibleReasonNotRightAmountOfPlayers:
                    description = FormatJournalEntry('DisqualifiedNotEnoughParticipants', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonTaleAlreadyEnded:
                    description = FormatJournalEntry('DisqualifiedExpired', d.rewardID)
                elif d.disqualifierType == const.rewardIneligibleReasonLowContribution:
                    description = FormatJournalEntry('DisqualifiedLowContribution', d.rewardID)
            elif d.eventTypeID == logConst.eventRewardLPStoredInPool:
                description = FormatJournalEntry('LoyaltyPointPilotRewardCount', d.rewardID, rewardedPlayers=d.numberOfPlayers)
            elif d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                description = FormatJournalEntry('LoyaltyPointPoolPaidOut', d.rewardID)
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                description = FormatJournalEntry('LoyaltyPointPoolLost', d.rewardID)
            elif d.eventTypeID == appLogConst.eventRewardLPPaidDirectly:
                description = FormatJournalEntry('LPPaidDirectly', d.rewardID, rewardedPlayers=d.numberOfPlayers)
            hint = description
            texts = [FmtSimpleDateUTC(d.date),
             solarSystemType,
             d.dungeonName,
             LPAmountAddedToPool,
             LPAmountPayedOut,
             description]
            scrolllist.append(GetFromClass(Generic, {'label': '<t>'.join(texts),
             'sort_' + GetByLabel('UI/Incursion/Journal/StoredLP'): d.lpAmountAddedToPool,
             'sort_' + GetByLabel('UI/Incursion/Journal/PaidLP'): d.lpAmountPayedOut,
             'hint': hint}))

        headers = [GetByLabel('UI/Common/Date'),
         GetByLabel('UI/Incursion/Journal/Type'),
         GetByLabel('UI/Incursion/Journal/EncounterName'),
         GetByLabel('UI/Incursion/Journal/StoredLP'),
         GetByLabel('UI/Incursion/Journal/PaidLP'),
         GetByLabel('UI/Incursion/Journal/Description')]
        options = [(GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        for taleID, constellationName in taleIDs.iteritems():
            options.append((constellationName, taleID))

        self.incursionLPTaleIDFilter.LoadOptions(options)
        if selectedTaleID is None:
            self.incursionLPTaleIDFilter.SelectItemByValue(taleIDFilter)
        else:
            self.incursionLPTaleIDFilter.SelectItemByValue(selectedTaleID)
        options = [(GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None), (GetByLabel('UI/Incursion/Journal/CompletedAndNotPaidOut'), LPTypeFilter.LPLost), (GetByLabel('UI/Incursion/Journal/CompletedAndPaidOut'), LPTypeFilter.LPPayedOut)]
        for dungeonType in dungeonTypes:
            if dungeonType is not None and dungeonType != '':
                if isinstance(dungeonType, int):
                    options.append((localization.GetByMessageID(dungeonType), dungeonType))
                else:
                    options.append((GetByLabel(dungeonType), dungeonType))

        self.incursionLPTaleIDFilter.LoadOptions(options)
        self.incursionLPTaleIDFilter.SelectItemByValue(solarsystemTypeFilter)
        if scrolllist:
            sortBy = self.sr.scroll.GetSortBy()
            sortDirection = self.sr.scroll.GetSortDirection()
            self.sr.scroll.LoadContent(contentList=scrolllist, reversesort=1, headers=headers, scrollTo=0.0)
            if sortBy is None:
                self.sr.scroll.Sort(by=GetByLabel('UI/Common/Date'), reversesort=1)
            else:
                self.sr.scroll.Sort(by=sortBy, reversesort=sortDirection)
        else:
            self.sr.scroll.Clear()
            self.sr.scroll.ShowHint(GetByLabel('UI/Incursion/Journal/NoRecordFound'))

    def MouseExitHighlightOff(self, obj, *args):
        obj.SetRGB(1.0, 1.0, 1.0)

    def MouseEnterHighlightOn(self, obj, *args):
        obj.SetRGB(1.0, 1.0, 0.0)

    def OnComboChange(self, *args):
        pass

    def ProcessSessionChange(self, isremote, session, change):
        self.header.tab_group.ReloadVisible()

    def OnAgentMissionChange(self, what, agentID):
        self.header.tab_group.ReloadVisible()

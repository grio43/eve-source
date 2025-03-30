#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelSvc.py
import sys
import eveformat.client
import evelink.client
import localization
import log
import telemetry
import uthread
import uthread2
from carbon.common.script.sys import service
from carbon.common.script.util import commonutils
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util import colorblind
from eve.client.script.ui.crimewatch import crimewatchTimers
from eve.client.script.ui.shared.careerPortal.cpSignals import on_cp_goal_tracking_removed, on_cp_goal_tracking_added
from eve.client.script.ui.shared.infoPanels import sessionTimeIndicator
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.const import infoPanelUIConst
from eve.client.script.ui.shared.infoPanels.infoPanelContainer import InfoPanelContainer
from eve.client.script.ui.shared.infoPanels.milestoneTimer.milestoneTimer import MilestoneTimer
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eveformat.client import solar_system_security_status
from jobboard.client import job_board_signals
from milestones.common.constants import MILESTONE_REWARD_MINUTES, MILESTONE_HUNDRED_AND_TWENTY_MINUTES_ID
from operations.common.const import OPERATION_CATEGORY_RECOMMENDATIONS
from uthread2 import StartTasklet
from spacecomponents.common.components.linkWithShip import LINKSTATE_RUNNING
MISSION_INFO_PANEL_UPDATE_DELAY_MSEC = 1000
OPERATION_INFO_PANEL_UPDATE_DELAY_MSEC = 1000
RECOMMENDATION_INFO_PANEL_UPDATE_DELAY_SEC = 0.5
AIR_NPE_INFO_PANEL_UPDATE_DELAY_SEC = 0.5

class InfoPanelSvc(service.Service):
    __update_on_reload__ = 1
    __guid__ = 'svc.infoPanel'
    __startupdependencies__ = ['missionObjectivesTracker']
    __notifyevents__ = ['OnSessionChanged',
     'OnClientEvent_WarpFinished',
     'OnViewStateChanged',
     'OnSovereigntyChanged',
     'OnSystemStatusChanged',
     'OnEntitySelectionChanged',
     'OnChallengeProgressUpdate',
     'OnChallengeCompleted',
     'OnRWDungeonEnteredInClient',
     'OnRWDungeonExitedInClient',
     'OnRWTimerEndedInClient',
     'OnOperationMadeActive',
     'OnOperationCompleted',
     'OnOperationReplayed',
     'OnOperationTaskTransition',
     'OnTutorialSkipped',
     'OnOperationDeactivatedUpdate',
     'OnRecommendationsUpdated',
     'OnAirNpeStateChanged',
     'OnAirNpeObjectiveUpdated',
     'OnInsurgencyCampaignStartedForLocation_Local',
     'OnInsurgencyCampaignEndingForLocation_Local',
     'OnInsurgencyCampaignUpdatedForLocation_Local']

    def Run(self, *args):
        self.sidePanel = None
        self.infoPanelContainer = None
        self.sessionTimer = None
        self.sessionTimerUpdatePending = False
        self.operationInfoPanelUpdater = None
        self.recommendationsInfoPanelUpdater = None
        self.missionInfoPanelUpdater = None
        self.airNpeInfoPanelUpdater = None
        self.combatTimerContainer = None
        self.milestoneTimer = None
        self.expandedMission = None

    def Reload(self):
        if self.sidePanel:
            self.sidePanel.Close()
            self.sidePanel = None
        if self.sessionTimer:
            self.sessionTimer.Close()
        if self.combatTimerContainer:
            self.combatTimerContainer.Release()
        if self.milestoneTimer:
            self.milestoneTimer.Close()
            self.milestoneTimer = None
        self.ReconstructAllPanels()
        self.DisconnectSignals()

    @telemetry.ZONE_FUNCTION
    def ConstructSidePanel(self):
        self.sidePanel = Container(parent=uicore.layer.sidePanels, name='sidePanel', align=uiconst.TOLEFT_NOPUSH, width=infoPanelUIConst.PANELWIDTH, padding=(0, 12, 0, 0))
        self.sidePanel.cacheContents = True
        self.combatTimerContainer = crimewatchTimers.TimerContainer(parent=self.sidePanel, left=infoPanelUIConst.LEFTPAD)
        self.infoPanelContainer = InfoPanelContainer(parent=self.sidePanel, align=uiconst.TOTOP)
        self.sessionTimer = sessionTimeIndicator.SessionTimeIndicator(parent=self.sidePanel, pos=(16, 35, 24, 24), state=uiconst.UI_HIDDEN, align=uiconst.TOPLEFT)
        if self.sessionTimerUpdatePending:
            self.UpdateSessionTimer()
        self.missionObjectivesTracker.RegisterMissionTracking()

    def ConstructMilestoneTimer(self):
        milestoneSvc = sm.GetService('milestoneSvc')
        timeLeft = milestoneSvc.GetTimeLeftInMilestone()
        if timeLeft is None:
            return
        self.milestoneTimer = MilestoneTimer(parent=self.sidePanel, left=10, iconPath='res:/UI/Texture/Crimewatch/iskIcon.png', timeLeft=timeLeft, totalTime=MILESTONE_REWARD_MINUTES, milestoneID=MILESTONE_HUNDRED_AND_TWENTY_MINUTES_ID)

    def UpdateSessionTimer(self):
        if self.sessionTimer:
            StartTasklet(self.sessionTimer.AnimSessionChange)
            self.sessionTimerUpdatePending = False
        else:
            self.sessionTimerUpdatePending = True

    def ShowHideSidePanel(self, hide = 1, *args):
        if self.sidePanel is not None and not self.sidePanel.destroyed:
            if hide:
                self.sidePanel.state = uiconst.UI_HIDDEN
            else:
                self.sidePanel.state = uiconst.UI_PICKCHILDREN

    def GetPanelByTypeID(self, panelTypeID):
        if self.infoPanelContainer:
            return self.infoPanelContainer.GetPanelByTypeID(panelTypeID)

    @telemetry.ZONE_FUNCTION
    def OnViewStateChanged(self, oldView, newView):
        self.ReconstructAllPanels(animate=True, settingsID=newView)

    @telemetry.ZONE_FUNCTION
    def ReconstructAllPanels(self, animate = False, settingsID = None):
        if not session.charid:
            return
        if not self.sidePanel:
            self.ConstructSidePanel()
        if not self.milestoneTimer:
            self.ConstructMilestoneTimer()
        if not settingsID:
            settingsID = sm.GetService('viewState').GetCurrentView().name
        self.infoPanelContainer.ReconstructPanels(settingsID, animate)

    def UpdateAllPanels(self):
        if not session.charid or not self.sidePanel:
            return
        sm.ChainEvent('ProcessUpdateInfoPanel', None)

    def ConnectSignals(self):
        on_cp_goal_tracking_added.connect(self.OnCareerProgramTrackingUpdated)
        on_cp_goal_tracking_removed.connect(self.OnCareerProgramTrackingUpdated)
        job_board_signals.on_job_board_feature_availability_changed.connect(self.OnJobBoardAvailabilityChanged)
        job_board_signals.on_tracked_jobs_changed.connect(self.OnTrackedJobsChanged)
        colorblind.on_colorblind_mode_changed.connect(self.OnColorBlindModeChanged)

    def DisconnectSignals(self):
        on_cp_goal_tracking_added.disconnect(self.OnCareerProgramTrackingUpdated)
        on_cp_goal_tracking_removed.disconnect(self.OnCareerProgramTrackingUpdated)
        job_board_signals.on_job_board_feature_availability_changed.disconnect(self.OnJobBoardAvailabilityChanged)
        job_board_signals.on_tracked_jobs_changed.disconnect(self.OnTrackedJobsChanged)
        colorblind.on_colorblind_mode_changed.disconnect(self.OnColorBlindModeChanged)

    @telemetry.ZONE_FUNCTION
    def OnSessionChanged(self, isRemote, sess, change):
        if not session.charid:
            return
        if 'charid' in change and change['charid'][1] is not None:
            self.Reload()
            self.ConnectSignals()
        self.UpdateSessionTimer()
        self.UpdateFactionalWarfarePanel()
        self.UpdateLocationInfoPanel()
        self.UpdateOperationsPanel()
        self.UpdateAirNpePanel()

    def OnClientEvent_WarpFinished(self, *args, **kwargs):
        self.UpdateOperationsPanel()
        self.UpdateAirNpePanel()

    def OnAirNpeStateChanged(self, *args, **kwargs):
        self.UpdateAirNpePanel(skip_wait=True)

    def GetActiveOperationObjective(self):
        if not session.charid or not self.infoPanelContainer:
            return None
        panel = self.GetPanelByTypeID(infoPanelConst.PANEL_OPERATIONS)
        if not panel or not panel.IsAvailable():
            return None
        return panel.GetFirstActiveObjective()

    def IsPanelAvailable(self, panelTypeID):
        if not session.charid or not self.infoPanelContainer:
            return False
        panel = self.GetPanelByTypeID(panelTypeID)
        if not panel or not panel.IsAvailable():
            return False
        return True

    def IsMissionsPanelActive(self):
        return self.IsPanelAvailable(infoPanelConst.PANEL_MISSIONS)

    def OnSovereigntyChanged(self, solarSystemID, allianceID):
        self.UpdateAllPanels()

    def OnSystemStatusChanged(self, *args):
        self.UpdateAllPanels()

    def OnEntitySelectionChanged(self, entityID):
        self.UpdateAllPanels()

    def OnColorBlindModeChanged(self):
        self.ReconstructAllPanels()

    def OnRWDungeonEnteredInClient(self):
        self.UpdatePanel(infoPanelConst.PANEL_RESOURCE_WARS)

    def OnRWDungeonExitedInClient(self):
        self.UpdatePanel(infoPanelConst.PANEL_RESOURCE_WARS)

    def OnRWTimerEndedInClient(self):
        self.UpdatePanel(infoPanelConst.PANEL_RESOURCE_WARS)

    @telemetry.ZONE_FUNCTION
    def UpdateMissionsPanel(self, callback = None):
        if self.missionInfoPanelUpdater is None:
            self.missionInfoPanelUpdater = AutoTimer(interval=MISSION_INFO_PANEL_UPDATE_DELAY_MSEC, method=self._UpdateMissionsPanelThread, callback=callback)

    def _UpdateMissionsPanelThread(self, callback):
        self.missionInfoPanelUpdater = None
        self.UpdatePanel(infoPanelConst.PANEL_MISSIONS, False)
        if callback:
            callback()

    def SetExpandedMission(self, featureID, missionID):
        if missionID == -1 and self.expandedMission.get('featureID') != featureID:
            return
        if self.expandedMission and self.expandedMission.get('featureID') == featureID and self.expandedMission.get('missionID') == missionID:
            return
        self.expandedMission = {'featureID': featureID,
         'missionID': missionID}
        settings.char.ui.Set('infoPanelExpandedMission', self.expandedMission)
        sm.ScatterEvent('OnExpandedMissionChanged', **self.expandedMission)

    def GetExpandedMission(self):
        if self.expandedMission is None:
            self.expandedMission = settings.char.ui.Get('infoPanelExpandedMission', {})
        return self.expandedMission

    def UpdateExpandedAgentMission(self):
        agentID = self.missionObjectivesTracker.GetAgentForLastAcceptedMission()
        panel = self.GetPanelByTypeID(infoPanelConst.PANEL_MISSIONS)
        if panel and panel.IsAvailable():
            panel.UpdateExpandedStateForMissionID(agentID)

    @telemetry.ZONE_FUNCTION
    def UpdateOperationsPanel(self, categoryID = None):
        if categoryID == OPERATION_CATEGORY_RECOMMENDATIONS or categoryID is None:
            self.LogInfo('UpdateOperationsPanel::Recommendations - categoryID: %s' % categoryID)
            if self.recommendationsInfoPanelUpdater:
                return
            self.recommendationsInfoPanelUpdater = uthread2.call_after_wallclocktime_delay(self._UpdateRecommendationsPanelThread, RECOMMENDATION_INFO_PANEL_UPDATE_DELAY_SEC)
            if categoryID == OPERATION_CATEGORY_RECOMMENDATIONS:
                return
        if self.operationInfoPanelUpdater is None:
            self.operationInfoPanelUpdater = AutoTimer(interval=OPERATION_INFO_PANEL_UPDATE_DELAY_MSEC, method=self._UpdateOperationsPanelThread)

    def _UpdateOperationsPanelThread(self):
        self.operationInfoPanelUpdater = None
        self.UpdatePanel(infoPanelConst.PANEL_OPERATIONS)

    def _UpdateRecommendationsPanelThread(self):
        self.recommendationsInfoPanelUpdater = None
        self.UpdatePanel(infoPanelConst.PANEL_RECOMMENDATIONS, False)

    @telemetry.ZONE_FUNCTION
    def UpdateAirNpePanel(self, skip_wait = False):
        if skip_wait:
            if self.airNpeInfoPanelUpdater:
                self.airNpeInfoPanelUpdater.kill()
                self.airNpeInfoPanelUpdater = None
            self.UpdatePanel(infoPanelConst.PANEL_AIR_NPE, False)
            return
        if self.airNpeInfoPanelUpdater:
            return
        self.airNpeInfoPanelUpdater = uthread2.call_after_wallclocktime_delay(self._UpdateAirNpePanelThread, AIR_NPE_INFO_PANEL_UPDATE_DELAY_SEC)

    def _UpdateAirNpePanelThread(self):
        self.airNpeInfoPanelUpdater = None
        self.UpdatePanel(infoPanelConst.PANEL_AIR_NPE, False)

    @telemetry.ZONE_FUNCTION
    def UpdateFactionalWarfarePanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_FACTIONAL_WARFARE)

    @telemetry.ZONE_FUNCTION
    def UpdateLocationInfoPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_LOCATION_INFO)

    @telemetry.ZONE_FUNCTION
    def UpdateIncursionsPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_INCURSIONS)

    @telemetry.ZONE_FUNCTION
    def UpdateDungeonProgressionPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_DUNGEON_PROGRESSION)

    @telemetry.ZONE_FUNCTION
    def UpdateChallengesPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_SEASONS)

    def UpdateJobBoardPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_JOB_BOARD)

    def UpdateSkyhookTheftPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_SKYHOOK_THEFT)

    def UpdateWorldEventsPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_WORLD_EVENTS)

    def UpdateAbyssPanel(self):
        self.UpdatePanel(infoPanelConst.PANEL_ABYSS)

    def OnOperationMadeActive(self, categoryID, operationID, oldCategoryID, oldOperationID, isSilent):
        self.UpdateOperationsPanel(categoryID)

    def OnOperationCompleted(self, categoryID, operationID):
        if categoryID != OPERATION_CATEGORY_RECOMMENDATIONS:
            self.UpdateOperationsPanel(categoryID)

    def OnOperationReplayed(self, categoryID, operationID):
        self.UpdateOperationsPanel(categoryID)

    def OnOperationQuit(self, categoryID, operationID):
        self.UpdateOperationsPanel(categoryID)

    def OnOperationTaskTransition(self, categoryID, operationID, taskID, fromState, toState):
        if categoryID != OPERATION_CATEGORY_RECOMMENDATIONS:
            self.UpdateOperationsPanel(categoryID)

    def OnTutorialSkipped(self):
        self.UpdateOperationsPanel()

    def OnOperationDeactivatedUpdate(self):
        self.UpdateOperationsPanel()

    def OnChallengeProgressUpdate(self, challengeID, newProgress):
        self.UpdateChallengesPanel()

    def OnChallengeCompleted(self, *args):
        self.UpdateChallengesPanel()

    def OnInsurgencyCampaignStartedForLocation_Local(self, campaignSnapshot):
        self.ReconstructAllPanels()

    def OnInsurgencyCampaignEndingForLocation_Local(self):
        self.ReconstructAllPanels()

    def OnInsurgencyCampaignUpdatedForLocation_Local(self, campaignSnapshot):
        self.ReconstructAllPanels()

    @telemetry.ZONE_FUNCTION
    def UpdatePanel(self, panelTypeID, ignoreViewSettings = True):
        if not session.charid:
            return
        sm.ChainEvent('ProcessUpdateInfoPanel', panelTypeID)
        if not self.infoPanelContainer:
            return
        uthread.Lock(self.infoPanelContainer)
        try:
            self.infoPanelContainer.UpdatePanel(panelTypeID, ignoreViewSettings)
        finally:
            uthread.UnLock(self.infoPanelContainer)

    def EnsureSolarSystemIDOrRaise(self, itemID):
        if idCheckers.IsStation(itemID):
            solar_system_id = cfg.stations.Get(itemID).solarSystemID
        elif idCheckers.IsSolarSystem(itemID):
            solar_system_id = itemID
        else:
            structure = sm.GetService('structureDirectory').GetStructureInfo(itemID)
            if structure is None:
                raise RuntimeError('Invalid destination')
            solar_system_id = structure.solarSystemID
        return solar_system_id

    def GetSolarSystemNameAndSecurityStatusDisplayString(self, solar_system_id, altText = None):
        if altText:
            altText = commonutils.StripTags(altText, stripOnly=['localized'])
        solar_system_text = self.GetSolarSystemText(solar_system_id, solarSystemAlt=altText)
        return solar_system_text

    def GetSolarSystemRegionAndConstellationTraceDisplayString(self, solar_system_id, traceFontSize = 12):
        solar_system_info = cfg.mapSystemCache.Get(solar_system_id)
        constellation_id = solar_system_info.constellationID
        region_id = solar_system_info.regionID
        if idCheckers.IsWormholeRegion(region_id):
            return None
        else:
            trace = u'{sep}{constellation}{sep}{region}'.format(constellation=evelink.location_link(constellation_id), region=evelink.location_link(region_id), sep=u'{space}&lt;{space}'.format(space=eveformat.font_size(' ', size=8)))
            if traceFontSize:
                trace = eveformat.font_size(trace, traceFontSize)
            return trace

    def GetSolarSystemTrace(self, itemID, altText = None, traceFontSize = 12):
        solar_system_id = self.EnsureSolarSystemIDOrRaise(itemID)
        solar_system_text = self.GetSolarSystemNameAndSecurityStatusDisplayString(solar_system_id, altText=altText)
        trace = self.GetSolarSystemRegionAndConstellationTraceDisplayString(solar_system_id, traceFontSize=traceFontSize)
        if trace:
            return u'{solar_system}{trace}'.format(solar_system=solar_system_text, trace=trace)
        else:
            return solar_system_text

    def GetLawlessSolarSystemTrace(self, itemID, traceFontSize = 12):
        solar_system_id = self.EnsureSolarSystemIDOrRaise(itemID)
        solar_system_text = cfg.evelocations.Get(solar_system_id).name
        trace = self.GetSolarSystemRegionAndConstellationTraceDisplayString(solar_system_id, traceFontSize=traceFontSize)
        if trace:
            return u'<b>{solar_system}</b> {lawlessText}<br>{trace}'.format(solar_system=solar_system_text, lawlessText=solar_system_security_status(solar_system_id, lawless=True), trace=trace)
        else:
            return solar_system_text

    def GetSolarSystemText(self, solarSystemID, solarSystemAlt = None):
        try:
            return u'{solar_system_name}</b> {security_status}'.format(solar_system_name=evelink.location_link(solarSystemID, hint=solarSystemAlt), security_status=self.GetSecurityStatusText(solarSystemID))
        except Exception:
            self.LogError('Solar system not found', solarSystemID)
            return ''

    def GetSecurityStatusText(self, solarSystemID):
        try:
            return eveformat.hint(hint=localization.GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.solar_system_security_status(solarSystemID))
        except Exception:
            log.LogException()
            sys.exc_clear()
            return ''

    def OnRecommendationsUpdated(self, *args, **kwargs):
        self.UpdatePanel(infoPanelConst.PANEL_RECOMMENDATIONS)

    def OnAirNpeObjectiveUpdated(self, current_goal = None, *args, **kwargs):
        if current_goal:
            panel = self.GetPanelByTypeID(infoPanelConst.PANEL_AIR_NPE)
            if not panel:
                self.SetExpandedMission('air_npe', 0)
        self.UpdateAirNpePanel(skip_wait=True)

    def OnCareerProgramTrackingUpdated(self, *args, **kwargs):
        self.UpdatePanel(infoPanelConst.PANEL_CAREER_PROGRAM)

    def OnJobBoardAvailabilityChanged(self, *args, **kwargs):
        self.UpdateMissionsPanel()
        self.UpdateJobBoardPanel()

    def OnTrackedJobsChanged(self, *args, **kwargs):
        self.UpdateJobBoardPanel()

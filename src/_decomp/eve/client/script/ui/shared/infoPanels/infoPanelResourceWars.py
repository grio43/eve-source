#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelResourceWars.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_RESOURCE_WARS, MODE_NORMAL
from localization import GetByLabel
from resourcewars.client.const import RW_PANEL_ICON, RW_PANEL_TITLE_LABEL
from resourcewars.client.rwinfopanelhaulertaskentry import RWInfoPanelHaulerTaskEntry
from resourcewars.client.rwinfopanelorehauledtaskentry import RWInfoPanelOreHauledTaskEntry
from resourcewars.client.rwinfopanelpiratetaskentry import RWInfoPanelPirateTaskEntry, PROGRESS_FRAME_CORNER_SIZE
from resourcewars.client.rwinfopanelcountdowntimer import CountdownTimerLabel

class InfoPanelResourceWars(InfoPanelBase):
    default_name = 'InfoPanelResourceWars'
    default_iconTexturePath = RW_PANEL_ICON
    default_state = uiconst.UI_PICKCHILDREN
    default_mode = MODE_NORMAL
    default_height = 120
    label = RW_PANEL_TITLE_LABEL
    hasSettings = False
    panelTypeID = PANEL_RESOURCE_WARS
    challengeContainer = None
    __notifyevents__ = ['OnHaulerEnteredInClient',
     'OnHaulerFullInClient',
     'OnRWPirateDestroyedInClient',
     'OnRWTimerStartedInClient']

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        self.rwService = sm.GetService('rwService')
        self.michelle = sm.GetService('michelle')
        self.ballpark = self.michelle.GetBallpark()
        self.haulerTaskEntries = {}
        self.titleLabel = self.headerCls(name='title', text=GetByLabel(self.label), parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        deadline = self.rwService.get_deadline()
        criticalTime = self.rwService.get_critical_time()
        self.timerPadContainer = Container(name='rwCountdownTimerPadContainer', parent=self.headerCont, padRight=PROGRESS_FRAME_CORNER_SIZE)
        self.countdownTimer = CountdownTimerLabel(name='rwCountdownTimer', parent=self.timerPadContainer, align=uiconst.BOTTOMRIGHT, deadline=deadline, criticalTime=criticalTime, rwService=self.rwService, state=uiconst.UI_NORMAL)
        self.countdownTimer.hint = GetByLabel('UI/ResourceWars/TimerHint')
        self.haulerContainer = None
        self._ConstructHaulerContainer()
        self._ConstructHaulerDetails()
        sm.RegisterNotify(self)

    def OnRWTimerStartedInClient(self, deadline, criticalTime):
        self.countdownTimer.InitiateCountdown(deadline, criticalTime)

    @staticmethod
    def IsAvailable():
        return sm.GetService('rwService').is_in_rw_dungeon()

    def _ConstructHaulerContainer(self):
        if not self.haulerContainer or self.haulerContainer.destroyed:
            self.mainCont.Flush()
            self.haulerContainer = ContainerAutoSize(parent=self.mainCont, name='haulerContainer', align=uiconst.TOTOP)

    def _ConstructHaulerDetails(self):
        haulersPresent = self.rwService.get_haulers_present()
        haulerProgress = self.rwService.get_hauler_progress()
        siteTarget = self.rwService.get_site_target()
        self.oreHauledTaskEntry = RWInfoPanelOreHauledTaskEntry(name='OreHauledTaskEntry', parent=self.haulerContainer, align=uiconst.TOTOP, progress=self.rwService.get_site_progress(), target=siteTarget)
        for haulerID, haulerProgress in haulerProgress.iteritems():
            if haulerID in haulersPresent:
                self._ConstructHaulerEntry(haulerID, haulerProgress)

        self.pirateEntry = RWInfoPanelPirateTaskEntry(name='PirateTaskEntry', parent=self.haulerContainer, align=uiconst.TOTOP, progress=self.rwService.get_pirates_killed())

    def OnHaulerEnteredInClient(self, haulerID, haulerProgress):
        self._ConstructHaulerEntry(haulerID, haulerProgress)

    def _ConstructHaulerEntry(self, haulerID, haulerProgress):
        if haulerID in self.haulerTaskEntries:
            return
        haulerTaskEnty = RWInfoPanelHaulerTaskEntry(name='haulerTaskEntry', parent=self.haulerContainer, align=uiconst.TOTOP, haulerID=haulerID, haulerProgress=haulerProgress, ballpark=self.ballpark)
        self.haulerTaskEntries[haulerID] = haulerTaskEnty
        if hasattr(self, 'pirateEntry'):
            self.pirateEntry.SetOrder(-1)

    def OnRWPirateDestroyedInClient(self, pirateKillCount):
        if hasattr(self, 'pirateEntry'):
            self.pirateEntry.register_progress(pirateKillCount)

    def OnHaulerFullInClient(self, haulerID):
        haulerTaskEntry = self.haulerTaskEntries.pop(haulerID, None)
        if haulerTaskEntry is not None:
            oreSaved = haulerTaskEntry.get_capacity()
            self.oreHauledTaskEntry.register_progress(oreSaved)

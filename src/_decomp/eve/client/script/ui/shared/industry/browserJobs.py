#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\browserJobs.py
import threadutils
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.viewModeButtons import ViewModeButtons
from eve.client.script.ui.shared.industry.industryUIConst import ACTIVITY_NAMES
from eve.client.script.ui.quickFilter import QuickFilterEdit
import carbonui.const as uiconst
import localization
import industry
import blue
from eve.client.script.ui.shared.industry.jobEntry import JobEntry
import uthread
import log
import telemetry
STATION_CURRENT = -1
STATION_ALL = -2
OWNER_ME = 1
OWNER_CORP = 2
INSTALLER_ANY = 1
INSTALLER_ME = 2
INSTALLER_CORPMATE = 3
STATUS_COMPLETED = 1
STATUS_INCOMPLETE = 2
STATUS_READY = 3
STATUS_INSTALLED = 4
STATUS_PAUSED = 5
STATUS_ICONS = {STATUS_INSTALLED: 'res:/UI/Texture/Classes/industry/status/installed.png',
 STATUS_PAUSED: 'res:/UI/Texture/Classes/industry/status/halted.png',
 STATUS_READY: 'res:/UI/Texture/Classes/industry/status/ready.png',
 STATUS_COMPLETED: 'res:/UI/Texture/Classes/industry/status/delivered.png'}
INTERVAL_FLASH = 5000
INTERVAL_UPDATE = 500

class BrowserJobs(Container):
    default_name = 'BrowserJobs'
    __notifyevents__ = ['OnIndustryJobClient', 'OnFacilitiesReloaded', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.callback = attributes.callback
        self.isInitialized = False

    def _OnClose(self, *args):
        sm.UnregisterNotify(self)

    def OnTabSelect(self):
        if self.isInitialized:
            self.UpdateOwnerCombo()
            self.UpdateInstallerCombo()
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=32, padding=(0, 6, 0, 6))
        self.bottomButtons = ButtonGroup(parent=self)
        self.deliverSelectedBtn = self.bottomButtons.AddButton(localization.GetByLabel('UI/Industry/DeliverSelectedJobs'), self.DeliverSelectedJobs)
        self.deliverAllBtn = self.bottomButtons.AddButton(localization.GetByLabel('UI/Industry/DeliverAllJobs'), self.DeliverAllJobs)
        self.scroll = Scroll(parent=self, id='JobBrowser')
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.Confirm = self.OnScrollReturn
        self.viewModeButtons = ViewModeButtons(parent=self.topPanel, align=uiconst.TORIGHT, controller=self, settingsID='IndustryBlueprintBrowserViewMode')
        self.ownerCombo = Combo(name='ownerCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnOwnerCombo, width=128, padRight=4)
        self.statusCombo = Combo(name='statusCombo', parent=self.topPanel, align=uiconst.TOLEFT, prefsKey='IndustryJobStatus', callback=self.OnStatusCombo, width=134, padRight=4)
        self.activityCombo = Combo(name='activityCombo', parent=self.topPanel, align=uiconst.TOLEFT, prefsKey='IndustryBlueprintActivity', callback=self.OnActivityCombo, options=self.GetActivityOptions(), width=120, padRight=4, maxVisibleEntries=7)
        self.installerCombo = Combo(name='installerCombo', parent=self.topPanel, align=uiconst.TOLEFT, callback=self.OnInstallerCombo, options=self.GetInstallerOptions(), width=140, padRight=4)
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self.topPanel, maxLength=64, align=uiconst.TORIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4, isTypeField=True, width=144)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.UpdateStatusCombo()
        self.UpdateOwnerCombo()
        self.UpdateInstallerCombo()
        self.UpdateScroll()
        uthread.new(self._UpdateJobCountersThread)

    def OnTabDeselect(self):
        if self.isInitialized:
            self.scroll.Clear()

    def OnScrollSelectionChange(self, entries):
        if entries:
            self.callback(entries[0].jobData)
        self.UpdateDeliverButtons()

    def OnScrollReturn(self, *args):
        self.DeliverJobs(self.scroll.GetSelected())

    def OnFilterEdit(self):
        self.UpdateScroll()

    def OnFilterEditCleared(self):
        self.UpdateScroll()

    def OnViewModeChanged(self, viewMode):
        self.UpdateScroll()

    @telemetry.ZONE_METHOD
    def OnIndustryJobClient(self, jobID = None, status = None, successfulRuns = None, **kwargs):
        if self.destroyed or self.IsHidden():
            return
        if self.isInitialized and self.display:
            self.UpdateJobEntry(jobID, status, successfulRuns)
            self.UpdateDeliverButtons()

    def OnFacilitiesReloaded(self, facilityIDs):
        if self.destroyed or self.IsHidden() or not (self.isInitialized and self.display):
            return
        if facilityIDs is None:
            self.UpdateScroll()
            return
        for node in self.scroll.GetNodes():
            if node.jobData.facilityID in facilityIDs:
                self.UpdateScroll()
                return

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change or 'stationid' in change:
            self.UpdateScroll()
        if 'corpid' in change:
            self.UpdateOwnerCombo()
            self.UpdateScroll()

    @telemetry.ZONE_METHOD
    def UpdateJobEntry(self, jobID, status, successfulRuns):
        for node in self.scroll.GetNodes():
            if node.jobData.jobID == jobID:
                if node.panel:
                    node.panel.OnStatusChanged(status, successfulRuns)
                else:
                    node.jobData.status = status
                    node.jobData.successfulRuns = successfulRuns
                break
        else:
            log.LogInfo("UpdateJobEntry: Reloading scroll because job couldn't be found, jobId=", jobID)
            self.UpdateScroll_throttled()

    def IsSomeJobReady(self):
        for node in self.scroll.GetNodes():
            if node.jobData.status == industry.STATUS_READY:
                return True

        return False

    def IsSomeReadyJobSelected(self):
        for node in self.scroll.GetSelected():
            if node.jobData.status == industry.STATUS_READY:
                return True

        return False

    @telemetry.ZONE_METHOD
    def UpdateDeliverButtons(self):
        self.deliverAllBtn.display = self.IsSomeJobReady()
        self.bottomButtons.display = self.deliverAllBtn.display
        self.deliverSelectedBtn.display = self.IsSomeReadyJobSelected()
        self.bottomButtons.ResetLayout()

    @threadutils.throttled(1.0)
    def UpdateScroll_throttled(self):
        self.UpdateScroll()

    @telemetry.ZONE_METHOD
    def UpdateScroll(self):
        if not self.isInitialized:
            return
        self.scroll.ShowLoading()
        statusFilter = self.statusCombo.selectedValue
        jobs = self.GetJobData(statusFilter == STATUS_COMPLETED)
        toPrime = filter(None, [ x.outputLocationID for x in jobs if not x.IsOutputLocationSameAsFacility() ])
        cfg.evelocations.Prime(toPrime)
        scrollList = self.GetScrollList(jobs)
        self.scroll.sr.defaultColumnWidth = JobEntry.GetDefaultColumnWidth()
        isPersonalJob = self.ownerCombo.GetValue() == OWNER_ME
        self.scroll.LoadContent(contentList=scrollList, headers=JobEntry.GetHeaders(isPersonalJob=isPersonalJob), noContentHint=localization.GetByLabel('UI/Industry/NoJobsFound'))
        self.scroll.HideLoading()
        self.UpdateDeliverButtons()

    def GetJobData(self, includeCompleted):
        if self.IsCorpSelected():
            jobs = sm.GetService('industrySvc').GetCorporationJobs(includeCompleted)
        else:
            jobs = sm.GetService('industrySvc').GetCharacterJobs(includeCompleted)
        return jobs

    @telemetry.ZONE_METHOD
    def GetScrollList(self, jobs):
        scrollList = []
        for jobData in jobs:
            if self.IsFilteredOut(jobData):
                continue
            node = Bunch(jobData=jobData, decoClass=JobEntry, sortValues=JobEntry.GetColumnSortValues(jobData, jobData.distance), viewMode=self.viewModeButtons.GetViewMode(), jumps=max(0, jobData.distance), name=u'JobEntry_{}'.format(jobData.blueprint.typeID))
            scrollList.append(node)

        return scrollList

    def IsFilteredOut(self, jobData):
        statusFilter = self.statusCombo.selectedValue
        if statusFilter == STATUS_INCOMPLETE and jobData.completed or statusFilter == STATUS_READY and not jobData.status == industry.STATUS_READY or statusFilter == STATUS_INSTALLED and not jobData.status == industry.STATUS_INSTALLED or statusFilter == STATUS_COMPLETED and not jobData.completed or statusFilter == STATUS_PAUSED and not jobData.status == industry.STATUS_PAUSED:
            return True
        if self.IsCorpSelected():
            installerType = self.installerCombo.GetValue()
            if installerType == INSTALLER_ME and jobData.installerID != session.charid:
                return True
            if installerType == INSTALLER_CORPMATE and jobData.installerID == session.charid:
                return True
        filterText = self.filterEdit.GetValue().strip().lower()
        if filterText:
            text = jobData.blueprint.GetName() + jobData.GetFacilityName() + jobData.GetInstallerName()
            if text.lower().find(filterText) == -1:
                return True
        activityValue = self.activityCombo.GetValue()
        if activityValue and activityValue != jobData.activityID:
            return True
        return False

    def OnStatusCombo(self, combo, key, value):
        settings.user.ui.Set('IndustryJobBrowserStatus', value)
        self.UpdateScroll()

    def UpdateStatusCombo(self):
        options = ((localization.GetByLabel('UI/Industry/StatusAllActiveJobs'), STATUS_INCOMPLETE),
         (localization.GetByLabel('UI/Industry/StatusInProgress'),
          STATUS_INSTALLED,
          None,
          STATUS_ICONS[STATUS_INSTALLED]),
         (localization.GetByLabel('UI/Industry/StatusReady'),
          STATUS_READY,
          None,
          STATUS_ICONS[STATUS_READY]),
         (localization.GetByLabel('UI/Industry/StatusHalted'),
          STATUS_PAUSED,
          None,
          STATUS_ICONS[STATUS_PAUSED]),
         (localization.GetByLabel('UI/Industry/StatusHistory'),
          STATUS_COMPLETED,
          None,
          STATUS_ICONS[STATUS_COMPLETED]))
        select = settings.user.ui.Get('IndustryJobBrowserStatus', STATUS_INCOMPLETE)
        self.statusCombo.LoadOptions(options, select=select)

    def OnActivityCombo(self, *args):
        self.UpdateScroll()

    def GetActivityOptions(self):
        ret = [ (localization.GetByLabel(ACTIVITY_NAMES[activityID]),
         activityID,
         None,
         industryUIConst.ACTIVITY_ICONS_SMALL[activityID]) for activityID in industry.ACTIVITIES ]
        ret.insert(0, (localization.GetByLabel('UI/Industry/AllActivities'), 0))
        return ret

    def GetInstallerOptions(self):
        return ((localization.GetByLabel('UI/Industry/InstalledByAnyone'), INSTALLER_ANY), (localization.GetByLabel('UI/Industry/InstalledByMe'),
          INSTALLER_ME,
          None,
          'res:/UI/Texture/classes/Industry/iconPersonal.png'), (localization.GetByLabel('UI/Industry/InstalledByCorpmates'),
          INSTALLER_CORPMATE,
          None,
          'res:/UI/Texture/classes/Industry/iconCorp.png'))

    def OnInstallerCombo(self, combo, key, value):
        settings.user.ui.Set('IndustryJobsBrowserInstaller', value)
        self.UpdateScroll()

    def UpdateInstallerCombo(self):
        self.installerCombo.display = self.IsCorpSelected()
        value = settings.user.ui.Get('IndustryJobsBrowserInstaller', INSTALLER_ANY)
        self.installerCombo.SelectItemByValue(value)

    def OnOwnerCombo(self, combo, key, value):
        settings.user.ui.Set('IndustryBlueprintBrowserOwner', value)
        self.UpdateInstallerCombo()
        self.UpdateScroll()

    def IsCorpSelected(self):
        return self.ownerCombo.GetValue() == OWNER_CORP

    def UpdateOwnerCombo(self):
        options = [(localization.GetByLabel('UI/Industry/OwnedByMe'), OWNER_ME)]
        if sm.GetService('blueprintSvc').CanSeeCorpBlueprints():
            options.append((localization.GetByLabel('UI/Industry/OwnedByCorp'),
             OWNER_CORP,
             None,
             'res:/UI/Texture/classes/Industry/iconCorp.png'))
        select = settings.user.ui.Get('IndustryBlueprintBrowserOwner', OWNER_ME)
        self.ownerCombo.LoadOptions(options, select=select)

    def _UpdateJobCountersThread(self):
        msecs = 0
        while not self.destroyed:
            animate = False
            msecs += INTERVAL_UPDATE
            if msecs >= INTERVAL_FLASH:
                msecs = 0
                animate = True
            nodes = self.scroll.GetVisibleNodes()
            for i, node in enumerate(nodes):
                if node.panel:
                    node.panel.UpdateValues(animate, i)

            blue.synchro.SleepWallclock(INTERVAL_UPDATE)

    def DeliverAllJobs(self, *args):
        self.DeliverJobs(self.scroll.GetNodes())

    def DeliverSelectedJobs(self, *args):
        self.DeliverJobs(self.scroll.GetSelected())

    def DeliverJobs(self, nodes):
        jobIDsAndSolarSystems = [ (node.jobData.jobID, node.jobData.solarSystemID) for node in nodes if node.jobData.status == industry.STATUS_READY ]
        sm.GetService('industrySvc').CompleteJobs(jobIDsAndSolarSystems)
        sm.GetService('audio').SendUIEvent('ind_jobDelivered')

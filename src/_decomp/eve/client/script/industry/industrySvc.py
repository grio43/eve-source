#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\industry\industrySvc.py
import weakref
from collections import defaultdict
import industry
import uthread
import telemetry
import blue
import gametime
import evetypes
import structures
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import SERVICE_RUNNING
from carbon.common.script.util.format import DateToBlue
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.common.lib import appConst
from eve.common.script.util import industryCommon
from eve.common.script.sys.idCheckers import IsStation, IsStructure, IsTriglavianSystem
from eveaccounting import get_accounting_key_for_name
from eveexceptions import UserError
from evestations.standingsrestriction import get_station_standings_restriction
from uthread2 import call_after_wallclocktime_delay

class IndustryService(Service):
    __guid__ = 'svc.industrySvc'
    __servicename__ = 'Industry'
    __displayname__ = 'Industry Service'
    __dependencies__ = ['blueprintSvc', 'facilitySvc', 'clientPathfinderService']
    __notifyevents__ = ['OnIndustryMaterials',
     'OnIndustryJob',
     'OnSessionChanged',
     'OnAccountChange',
     'OnSkillsChanged',
     'OnSessionReset']

    def __init__(self):
        super(IndustryService, self).__init__()
        self.monitoring = weakref.ref(set())
        self.installed = weakref.WeakValueDictionary()
        self._jobs = {}
        self._ownerJobs = defaultdict(dict)
        self._ownerJobsFetchedCompleted = set()
        self.slots = None
        self.slotworker = None

    def Run(self, *args, **kwargs):
        uthread.new(self._PollJobCompletion)
        Service.Run(self, *args, **kwargs)

    def Initialize(self):
        self.monitoring = weakref.ref(set())
        self.installed = weakref.WeakValueDictionary()
        self.slots = None
        self.slotworker = None

    def GetJobByID(self, jobID, useCached = False):
        if useCached and jobID in self._jobs:
            return self._jobs[jobID]
        return self._JobInstance(sm.RemoteSvc('industryManager').GetJob(jobID), fetchBlueprint=True)

    @telemetry.ZONE_METHOD
    def GetOwnerJobs(self, ownerID, includeCompleted = False, useCached = False):
        if useCached and ownerID in self._ownerJobs:
            if not includeCompleted:
                return [ job for job in self._ownerJobs[ownerID].values() if job.status < industry.STATUS_COMPLETED ]
            if ownerID in self._ownerJobsFetchedCompleted:
                return self._ownerJobs[ownerID].values()
        jobs = []
        locations = set()
        self._ownerJobs[ownerID].clear()
        self._ownerJobsFetchedCompleted.discard(ownerID)
        for data in sm.RemoteSvc('industryManager').GetJobsByOwner(ownerID, includeCompleted):
            job = self._JobInstance(data, fetchBlueprint=False)
            self._ownerJobs[ownerID][job.jobID] = job
            jobs.append(job)
            if not job.completed:
                locations.add(job.facilityID)

        if includeCompleted:
            self._ownerJobsFetchedCompleted.add(ownerID)
        cfg.evelocations.Prime(locations)
        return jobs

    def GetCharacterJobs(self, includeCompleted = False, useCached = False):
        return self.GetOwnerJobs(session.charid, includeCompleted, useCached)

    def GetCorporationJobs(self, includeCompleted = False, useCached = False):
        return self.GetOwnerJobs(session.corpid, includeCompleted, useCached)

    @telemetry.ZONE_METHOD
    def CreateJob(self, blueprint, activityID, facilityID, runs = 1):
        job = industry.Job(blueprint, activityID)
        job.runs = runs
        job.status = industry.STATUS_UNSUBMITTED
        job.extras = industryCommon.GetOptionalMaterials(job)
        job.prices = industryCommon.JobPrices(activityID)
        industryCommon.AttachSessionToJob(job, session)
        self._UpdateSkills(job)
        self._UpdateSlots()
        self._UpdateModifiers(job)
        self._UpdateDistance(job)
        self._UpdateAccounts(job)
        job.on_facility.connect(self.LoadLocations)
        job.on_delete.connect(self.DisconnectJob)
        job.on_input_location.connect(self.ConnectJob)
        job.on_validate.connect(self._ValidateJob)
        self._ApplyJobSettings(job)
        job.facility = self.facilitySvc.GetFreshFacility(facilityID)
        return job

    def RecreateJob(self, existing):
        try:
            blueprint = self.blueprintSvc.GetBlueprintItem(existing.blueprintID)
            if blueprint.ownerID != existing.ownerID:
                raise UserError
        except UserError:
            blueprint = self.blueprintSvc.GetBlueprintType(existing.blueprintTypeID, not existing.blueprint.original)

        job = self.CreateJob(blueprint, existing.activityID, existing.facilityID)
        job.outputLocation = industryCommon.MatchLocation(job, existing.outputLocationID, existing.outputFlagID, checkCapacity=True)
        job.productTypeID = existing.productTypeID
        job.runs = existing.runs
        job.licensedRuns = existing.licensedRuns
        for material in job.optional_materials:
            material.select(None)
            if getattr(existing, 'optionalTypeID', None) in material.all_types():
                material.select(existing.optionalTypeID)
            if getattr(existing, 'optionalTypeID2', None) in material.all_types():
                material.select(existing.optionalTypeID2)

        return job

    def JobDataWithBlueprint(self, existing):
        job = self._JobInstance(existing.data, fetchBlueprint=True)
        job.extras = industryCommon.GetOptionalMaterials(job)
        return job

    def InstallJob(self, job):
        try:
            return sm.RemoteSvc('industryManager').InstallJob(job.dump())
        except UserError:
            self.facilitySvc.Reload(job.facilityID)
            raise

    @staticmethod
    def CompleteJob(jobID, solarSystemID):
        sm.RemoteSvc('industryManager').CompleteJob(int(jobID), solarSystemID)

    @staticmethod
    def CompleteJobs(jobs):
        sm.RemoteSvc('industryManager').CompleteManyJobs([ (jobID, solarSystemID) for jobID, solarSystemID in jobs ])

    @staticmethod
    def CancelJob(jobID, solarSystemID):
        sm.RemoteSvc('industryManager').CancelJob(int(jobID), solarSystemID)

    def _ValidateJob(self, job):
        if not job.facility:
            return
        if IsStation(job.facility.facilityID):
            standing_restrictions = get_station_standings_restriction(appConst.stationServiceFactory, job.facility.facilityID, job.ownerID)
            if standing_restrictions:
                job.add_error(industry.Error.STANDINGS_RESTRICTION, standing_restrictions)
        if IsStructure(evetypes.GetCategoryID(job.facility.typeID)) and IsTriglavianSystem(job.facility.solarSystemID):
            if job.structure_service_id in (structures.SERVICE_MANUFACTURING_CAPITAL, structures.SERVICE_MANUFACTURING_SUPERCAPITAL):
                job.add_error(industry.Error.FACILITY_TYPE, job.blueprint.blueprintTypeID)

    def _PollJobCompletion(self):
        while self.state == SERVICE_RUNNING:
            uthread.new(self._PollJobCompletionThreaded)
            blue.pyos.synchro.SleepWallclock(1000)

    def _PollJobCompletionThreaded(self):
        for job in self.installed.values():
            if job.status == industry.STATUS_INSTALLED and DateToBlue(job.endDate) < blue.os.GetWallclockTime():
                job.status = industry.STATUS_READY
                sm.ScatterEvent('OnIndustryJob', job.jobID, job.ownerID, job.blueprintID, job.installerID, job.status, None)

    def _JobInstance(self, data, fetchBlueprint = False):
        if fetchBlueprint:
            blueprint = self.blueprintSvc.GetBlueprint(data.blueprintID, data.blueprintTypeID)
        else:
            blueprint = self.blueprintSvc.GetBlueprintType(data.blueprintTypeID, data.blueprintCopy)
        job = industryCommon.JobData(data, blueprint)
        if data.facilityID:
            job.facility = self.facilitySvc.GetFreshFacility(data.facilityID)
        self._UpdateSkills(job)
        self._UpdateSlots()
        self._UpdateModifiers(job)
        self._UpdateDistance(job)
        if job.status == industry.STATUS_INSTALLED:
            self.installed[job.jobID] = job
        else:
            self.installed.pop(job.jobID, None)
        self._jobs[job.jobID] = job
        return job

    @telemetry.ZONE_METHOD
    def _UpdateModifiers(self, job):
        if job:
            job.modifiers = industryCommon.GetJobModifiers(job, session.charid)

    @telemetry.ZONE_METHOD
    def _UpdateDistance(self, job):
        if job and isinstance(job, industry.JobData):
            job._distance = self.clientPathfinderService.GetJumpCountFromCurrent(job.solarSystemID)

    @telemetry.ZONE_METHOD
    def _UpdateSkills(self, job):
        if job:
            skills = {}
            mySkills = sm.GetService('skills').GetSkill
            for typeID in [ skill.typeID for skill in job.all_skills ]:
                skillInfo = mySkills(typeID)
                skills[typeID] = skillInfo.effectiveSkillLevel if skillInfo else 0

            job.skills = skills

    def _UpdateSlots(self):
        callinterval = 3
        callthread = self.slotworker
        startTime = getattr(callthread.tasklet, 'startTime', gametime.GetWallclockTimeNow()) if callthread else gametime.GetWallclockTimeNow()
        delay = 1 if callthread is None else callinterval
        if callthread is None or not callthread.IsAlive() or gametime.GetSecondsSinceWallclockTime(startTime) > delay:
            self.slotworker = call_after_wallclocktime_delay(self._UpdateSlots_thread, delay)

    def _UpdateSlots_thread(self):
        self.slots = sm.RemoteSvc('industryManager').GetJobCounts(session.charid)
        self.slotworker = None
        sm.ScatterEvent('OnIndustrySlotsUpdated')

    @telemetry.ZONE_METHOD
    def _UpdateAccounts(self, job, ownerID = None, account = None, balance = None):
        if job:
            accounts = {(session.charid, appConst.accountingKeyCash): sm.GetService('wallet').GetWealth()}
            if session.corpAccountKey and walletUtil.HaveAccessToCorpWalletDivision(session.corpAccountKey):
                if ownerID and account and balance and session.corpid == ownerID and session.corpAccountKey == account:
                    accounts[session.corpid, session.corpAccountKey] = balance
                else:
                    accounts[session.corpid, session.corpAccountKey] = sm.GetService('wallet').GetCorpWealthCached1Min(session.corpAccountKey)
            job.accounts = accounts
            if job.account not in job.accounts:
                for accountOwner, accountKey in job.accounts.keys():
                    if job.ownerID == accountOwner:
                        job.account = (accountOwner, accountKey)
                        return

                job.account = job.accounts.keys()[0]

    def OnSessionChanged(self, isRemote, session, change):
        industryCommon.AttachSessionToJob(self.monitoring(), session)
        if 'corpAccountKey' in change:
            self._UpdateAccounts(self.monitoring())
        if 'corprole' in change:
            self._UpdateAccounts(self.monitoring())
            self.LoadLocations(self.monitoring())

    def OnSessionReset(self):
        self.Initialize()

    def OnAccountChange(self, accountKey, ownerID, balance):
        keyID = get_accounting_key_for_name(accountKey)
        self._UpdateAccounts(self.monitoring(), ownerID, keyID, balance)

    def OnSkillsChanged(self, *args):
        self._UpdateSkills(self.monitoring())
        self._UpdateModifiers(self.monitoring())

    @telemetry.ZONE_METHOD
    def OnIndustryJob(self, jobID, ownerID, blueprintID, installerID, status, successfulRuns):
        if installerID == session.charid:
            self._UpdateSlots()
        if jobID in self._jobs:
            self._jobs[jobID].status = status
            self._jobs[jobID].successfulRuns = successfulRuns
        if ownerID in self._ownerJobs and jobID not in self._ownerJobs[ownerID]:
            self._ownerJobs.pop(ownerID)
            self._ownerJobsFetchedCompleted.discard(ownerID)
        sm.ScatterEvent('OnIndustryJobClient', jobID=jobID, ownerID=ownerID, blueprintID=blueprintID, installerID=installerID, status=status, successfulRuns=successfulRuns)

    @telemetry.ZONE_METHOD
    def ConnectJob(self, job):
        self.monitoring = weakref.ref(job)
        job.monitorID, job.available = sm.RemoteSvc('industryMonitor').ConnectJob(job.dump())

    @telemetry.ZONE_METHOD
    def DisconnectJob(self, job):
        if job is None or self.monitoring() == job:
            sm.RemoteSvc('industryMonitor').DisconnectJob(job.monitorID if job else None)

    @telemetry.ZONE_METHOD
    def LoadLocations(self, job):
        if job:
            job.locations = self.facilitySvc.GetFacilityLocations(job.facilityID, job.ownerID)
            if len(job.locations):
                self._ApplyJobSettings(job)

    def OnIndustryMaterials(self, jobID, materials):
        job = self.monitoring()
        if job and hasattr(job, 'monitorID') and job.monitorID == jobID:
            job.available = materials

    def _UpdateJobSettings(self, job):
        settings.char.ui.Set('industry_b:%s_a:%s_runs' % (job.blueprint.blueprintTypeID, job.activityID), job.runs)
        settings.char.ui.Set('industry_b:%s_a:%s_productTypeID' % (job.blueprint.blueprintTypeID, job.activityID), job.productTypeID)
        settings.char.ui.Set('industry_b:%s_a:%s_licensedRuns' % (job.blueprint.blueprintTypeID, job.activityID), job.licensedRuns)
        settings.char.ui.Set('industry_account:%s' % (job.ownerID,), job.account)
        if job.inputLocation is not None and job.facility is not None:
            settings.char.ui.Set('industry_b:%s_a:%s_f:%s_input' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.inputLocation.itemID, job.inputLocation.flagID))
        if job.outputLocation is not None and job.facility is not None:
            settings.char.ui.Set('industry_b:%s_a:%s_f:%s_output' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.outputLocation.itemID, job.outputLocation.flagID))
        if len(job.optional_materials):
            settings.char.ui.Set('industry_b:%s_a:%s_materials' % (job.blueprint.blueprintTypeID, job.activityID), list([ material.typeID for material in job.optional_materials if material.typeID ]))

    def _ApplyJobSettings(self, job):
        job.runs = settings.char.ui.Get('industry_b:%s_a:%s_runs' % (job.blueprint.blueprintTypeID, job.activityID), 1)
        job.productTypeID = settings.char.ui.Get('industry_b:%s_a:%s_productTypeID' % (job.blueprint.blueprintTypeID, job.activityID), None)
        job.licensedRuns = min(job.maxLicensedRuns, settings.char.ui.Get('industry_b:%s_a:%s_licensedRuns' % (job.blueprint.blueprintTypeID, job.activityID), job.maxLicensedRuns))
        account = settings.char.ui.Get('industry_account:%s' % (job.ownerID,), job.account)
        job.account = account if account in job.accounts else job.account
        if job.facility:
            inputLocation = industryCommon.MatchLocation(job, *settings.char.ui.Get('industry_b:%s_a:%s_f:%s_input' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.blueprint.location.itemID, job.blueprint.location.flagID)))
            if inputLocation != job.inputLocation:
                job.inputLocation = inputLocation
            outputLocation = industryCommon.MatchLocation(job, checkCapacity=True, *settings.char.ui.Get('industry_b:%s_a:%s_f:%s_output' % (job.blueprint.blueprintTypeID, job.activityID, job.facility.facilityID), (job.blueprint.location.itemID, job.blueprint.location.flagID)))
            if outputLocation != job.outputLocation:
                job.outputLocation = outputLocation
        materials = settings.char.ui.Get('industry_b:%s_a:%s_materials' % (job.blueprint.blueprintTypeID, job.activityID), [])
        for material in job.materials:
            for option in material.options:
                if option.typeID in materials:
                    material.select(option)

        job.on_updated.connect(self._UpdateJobSettings)

    def GetJobCountForActivity(self, activityID):
        if self.slots is None:
            self._UpdateSlots()
            return
        return self.slots.get(activityID, 0)

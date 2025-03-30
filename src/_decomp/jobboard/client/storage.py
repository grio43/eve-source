#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\storage.py
from collections import OrderedDict
from jobboard.client import job_board_signals, features, ProviderType
from jobboard.client.util import sort_jobs, get_provider_id_from_job_id
from metadata.common.content_tags import on_content_tags_reloaded
PROVIDERS = [features.AgentMissionsJobProvider,
 features.CorporationGoalsProvider,
 features.CombatAnomaliesProvider,
 features.CosmicSignaturesProvider,
 features.DailyGoalsProvider,
 features.EpicArcsProvider,
 features.EscalationSitesProvider,
 features.FactionalWarfareProvider,
 features.FactionalWarfareEnlistmentProvider,
 features.HomefrontOperationsProvider,
 features.IceBeltsProvider,
 features.OreAnomaliesProvider,
 features.PirateInsurgenciesProvider,
 features.TriglavianSitesProvider,
 features.StorylinesProvider,
 features.MTOJobProvider,
 features.SeasonsProvider,
 features.WorldEventsProvider]
PROVIDERS_IN_REWARDS_TAB = [ProviderType.DAILY_GOALS, ProviderType.CORPORATION_GOALS]

class JobBoardStorage(object):
    __notifyevents__ = []

    def __init__(self):
        self._jobs = {}
        self._closing = False
        self._providers = {provider_class.PROVIDER_ID:provider_class(job_storage=self) for provider_class in PROVIDERS}
        self.primary_feature_tags = {}
        self._construct_primary_feature_tags()
        settings.char.ui.Set('opportunities_selected_page', {})
        self._register()

    def _register(self):
        sm.RegisterNotify(self)
        job_board_signals.on_job_provider_state_changed.connect(self._on_job_provider_state_changed)
        on_content_tags_reloaded.connect(self._on_content_tags_reloaded)

    def _unregister(self):
        sm.UnregisterNotify(self)
        job_board_signals.on_job_provider_state_changed.disconnect(self._on_job_provider_state_changed)
        on_content_tags_reloaded.disconnect(self._on_content_tags_reloaded)

    def get_provider(self, provider_id):
        return self._providers.get(provider_id, None)

    def get_provider_for_feature_tag(self, feature_tag_id):
        for provider in self._providers.itervalues():
            if provider.is_enabled and provider.feature_tag_id == feature_tag_id:
                return provider

    def get_job(self, job_id, wait = True):
        if wait and job_id not in self._jobs:
            self._try_fetch_job(job_id)
        return self._jobs.get(job_id, None)

    def get_jobs(self, filters = None, provider_id = None):
        provider = self.get_provider(provider_id)
        jobs = provider.get_jobs() if provider else self._jobs
        if filters is None:
            return sort_jobs(jobs.values())
        content_tag_ids = (filters or {}).get('content_tag_ids', [])
        keywords = [ keyword.lower() for keyword in (filters or {}).get('keywords', []) ]
        self._wait_for_providers(content_tag_ids)
        results = []
        for job in jobs.values():
            if job.check_filters(content_tag_ids, keywords):
                results.append(job)

        return sort_jobs(results)

    def get_available_jobs(self, filters = None, provider_id = None):
        provider = self.get_provider(provider_id)
        jobs = provider.get_jobs() if provider else self._jobs
        content_tag_ids = (filters or {}).get('content_tag_ids', [])
        keywords = [ keyword.lower() for keyword in (filters or {}).get('keywords', []) ]
        self._wait_for_providers(content_tag_ids)
        results = []
        for job in jobs.values():
            if not job.is_available_in_browse:
                continue
            if job.check_filters(content_tag_ids, keywords):
                results.append(job)

        return sort_jobs(results)

    def get_active_jobs(self, filters = None):
        content_tag_ids = (filters or {}).get('content_tag_ids', None)
        keywords = [ keyword.lower() for keyword in (filters or {}).get('keywords', []) ]
        self._wait_for_providers(content_tag_ids)
        results = []
        for job in self._jobs.values():
            if not job.is_available_in_active:
                continue
            if job.check_filters(content_tag_ids, keywords):
                results.append(job)

        return sort_jobs(results)

    def get_jobs_with_unclaimed_rewards(self, provider_id = None):
        if provider_id:
            provider = self.get_provider(provider_id)
            jobs = provider.get_jobs()
        else:
            jobs = {}
            for provider_id in PROVIDERS_IN_REWARDS_TAB:
                provider = self.get_provider(provider_id)
                jobs.update(provider.get_jobs())

        return [ job for job in jobs.values() if job.has_claimable_rewards ]

    def get_tracked_jobs(self):
        tracked_job_ids = {}
        for provider in self._providers.itervalues():
            if not provider.is_enabled:
                continue
            tracked_job_ids.update(provider.get_tracked_job_ids())

        sorted_tracked_jobs = [ job_id for job_id, timestamp in sorted(tracked_job_ids.items(), key=lambda x: x[1], reverse=True) ]
        return [ self._jobs[job_id] for job_id in sorted_tracked_jobs if job_id in self._jobs ]

    def get_related_jobs(self, relevance_profile):
        jobs_score = []
        for job in self._jobs.values():
            if not job.is_available_in_browse:
                continue
            score = relevance_profile.calculate_relevance_score(job.content_tag_ids, job.solar_system_id)
            if score:
                jobs_score.append((score, job))

        return [ job_score[1] for job_score in sorted(jobs_score, reverse=True) ]

    def _wait_for_providers(self, content_tag_ids):
        if not content_tag_ids:
            return
        for provider in self._providers.itervalues():
            provider.wait_for_provider_by_tags(content_tag_ids)

    def get_provider_from_job_id(self, job_id):
        provider_id = get_provider_id_from_job_id(job_id)
        return self.get_provider(provider_id)

    def _try_fetch_job(self, job_id):
        provider = self.get_provider_from_job_id(job_id)
        if provider:
            provider.try_fetch_job(job_id)

    def close(self):
        self._closing = True
        self._unregister()
        for provider in self._providers.itervalues():
            provider.close()

        self._jobs.clear()

    def add_job(self, job):
        if job.job_id not in self._jobs:
            self._jobs[job.job_id] = job
            job_board_signals.on_job_added(job)

    def remove_job(self, job_id):
        job = self._jobs.pop(job_id, None)
        if job:
            job_board_signals.on_job_removed(job)

    def _construct_primary_feature_tags(self):
        feature_tags = {}
        for provider in self._providers.itervalues():
            if not provider.is_enabled:
                continue
            content_tag = provider.feature_tag
            if not content_tag:
                continue
            feature_tags[content_tag.id] = content_tag

        self.primary_feature_tags = OrderedDict([ (tag.id, tag) for tag in sorted(feature_tags.values(), key=lambda ct: ct.title) ])

    def _on_job_provider_state_changed(self, *args, **kwargs):
        self._construct_primary_feature_tags()

    def _on_content_tags_reloaded(self, *args, **kwargs):
        self._construct_primary_feature_tags()

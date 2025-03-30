#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evebannerads\banner_ad_service.py
import uthread2
from carbon.common.script.sys.service import Service
from evebannerads.banner_ad_retrieval import retrieve_adglare_ad
from evebannerads.const import AD_DEFAULT_ROTATION_INTERVAL

class BannerAdService(Service):
    __guid__ = 'svc.BannerAdService'
    serviceName = 'svc.bannerAdService'
    __displayname__ = 'BannerAdService'
    __servicename__ = 'BannerAdService'

    def Run(self, *args, **kwargs):
        self._ad_threads_by_owner = {}
        self._ad_request_by_owner = {}
        Service.Run(self, *args, **kwargs)

    def request_single_ad(self, banner_ad_request):
        ad_data = self._get_ad_to_display(banner_ad_request)
        if ad_data:
            banner_ad_request.load_ad(ad_data)
        else:
            self._notify_failed_request(banner_ad_request)

    def request_rotating_ads(self, banner_ad_request):
        if banner_ad_request.banner_owner in self._ad_threads_by_owner:
            self._attach_to_existing_thread(banner_ad_request)
        else:
            self._start_new_ad_thread(banner_ad_request)

    def remove_ad_rotation_request(self, banner_owner):
        ad_thread = self._ad_threads_by_owner.get(banner_owner)
        if ad_thread:
            ad_thread.kill()
        self._remove_thread_and_data_for_owner(banner_owner)

    def pause_ad_rotation_request(self, banner_owner):
        if banner_owner in self._ad_request_by_owner:
            self._ad_request_by_owner[banner_owner].paused = True

    def _notify_failed_request(self, banner_ad_request):
        failure_callback = banner_ad_request.failure_callback
        if failure_callback is not None:
            failure_callback()

    def _attach_to_existing_thread(self, banner_ad_request):
        banner_owner = banner_ad_request.banner_owner
        banner_ad_request.received_data = self._ad_request_by_owner[banner_owner].received_data
        self._ad_request_by_owner[banner_owner] = banner_ad_request
        if banner_ad_request.received_data:
            banner_ad_request.load_ad(banner_ad_request.received_data)

    def _remove_thread_and_data_for_owner(self, banner_owner):
        self._ad_threads_by_owner.pop(banner_owner, None)
        self._ad_request_by_owner.pop(banner_owner, None)

    def _start_new_ad_thread(self, banner_ad_request):
        banner_owner = banner_ad_request.banner_owner
        self._ad_request_by_owner[banner_owner] = banner_ad_request
        ad_thread = uthread2.start_tasklet(self._display_ad_thread, banner_owner)
        self._ad_threads_by_owner[banner_owner] = ad_thread

    def _display_ad_thread(self, banner_owner):
        while True:
            rotation_delay = AD_DEFAULT_ROTATION_INTERVAL
            ad_request = self._ad_request_by_owner[banner_owner]
            if ad_request.paused:
                uthread2.sleep(rotation_delay)
                continue
            ad_data = self._get_ad_to_display(ad_request)
            if ad_data is None:
                break
            try:
                ad_request.load_ad(ad_data)
                rotation_delay = ad_data.rotation_interval
                ad_request.received_data = ad_data
            except StandardError:
                break

            uthread2.sleep(rotation_delay)

        ad_request = self._ad_request_by_owner[banner_owner]
        self._remove_thread_and_data_for_owner(banner_owner)
        self._notify_failed_request(ad_request)
        self.LogInfo('Banner ad rotation retrieval failed, thread aborted.')

    def _get_ad_to_display(self, banner_ad_request):
        try:
            ad_data = retrieve_adglare_ad(banner_ad_request.banner_url, banner_ad_request.language_id, banner_ad_request.rotation_settings)
            return ad_data
        except Exception as exception:
            self.LogInfo('Failed retrieving banner ad due to: %s' % getattr(exception, 'msg', str(exception)))

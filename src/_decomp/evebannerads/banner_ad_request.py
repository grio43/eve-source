#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evebannerads\banner_ad_request.py


class BannerAdRequest(object):

    def __init__(self, banner_owner, load_ad_method, banner_url, language_id, rotation_settings = None, failure_callback = None):
        self.banner_owner = banner_owner
        self.load_ad = load_ad_method
        self.banner_url = banner_url
        self.language_id = language_id
        self.rotation_settings = rotation_settings
        self.failure_callback = failure_callback
        self.paused = False
        self.received_data = None

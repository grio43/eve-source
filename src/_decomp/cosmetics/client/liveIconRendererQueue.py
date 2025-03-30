#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\liveIconRendererQueue.py
import uthread2
import os
import blue
import trinity
from cosmetics.client.iconGenerator import IconGenerator
from evegraphics.settings import DEVICE_HIGH_END, DEVICE_MID_RANGE, DEVICE_LOW_END
from evegraphics.settings import GetDeviceClassification
from logging import getLogger
from liveIconCacheUtils import create_cache_directory
log = getLogger(__name__)
_DEVICE_SETTING_DELAY_MAPPING = {DEVICE_HIGH_END: 60,
 DEVICE_MID_RANGE: 110,
 DEVICE_LOW_END: 160}

class LiveIconRenderQueue(object):
    __instance__ = None
    __notifyevents__ = ['OnGraphicSettingsChanged']

    @staticmethod
    def get_instance():
        if LiveIconRenderQueue.__instance__ is None:
            LiveIconRenderQueue.__instance__ = LiveIconRenderQueue()
        return LiveIconRenderQueue.__instance__

    @staticmethod
    def get_artificial_delay():
        classification = GetDeviceClassification()
        delay = _DEVICE_SETTING_DELAY_MAPPING.get(classification, None)
        return delay or 100

    def __init__(self):
        self.queue = []
        self.queue_thread = None
        self._icon_generator = None
        self.skin_design = None
        sm.RegisterNotify(self)
        create_cache_directory()

    def OnGraphicSettingsChanged(self, *args):
        self._icon_generator = None

    def add_to_queue(self, function):
        log.info('LIVE ICONS - Add to queue')
        self.queue.insert(0, function)
        if not self.queue_thread:
            log.info('LIVE ICONS - Start queue')
            self.queue_thread = uthread2.start_tasklet(self.render_queue_thread)

    def remove_from_queue(self, function):
        log.info('LIVE ICONS - Remove from queue')
        if function in self.queue:
            self.queue.remove(function)

    def render_queue_thread(self):
        artificial_delay = self.get_artificial_delay()
        try:
            while len(self.queue) > 0:
                current_action = self.queue.pop()
                if callable(current_action):
                    current_action()
                blue.synchro.Sleep(artificial_delay)

        finally:
            self.queue = []
            self.queue_thread = None

    def get_icon_generator(self, width, height, skin_design, bg_texture_path):
        if not self._icon_generator:
            self._icon_generator = self._construct_icon_generator(width, height, skin_design, bg_texture_path)
        return self._icon_generator

    def _construct_icon_generator(self, width, height, skin_design, bg_texture_path):
        log.info('LIVE ICONS - Construct icon generator of {width}x{height}'.format(width=width, height=height))
        ss = 1
        if trinity.GetShaderModel() == 'SM_3_0_DEPTH':
            ss = 2
        w = width * ss
        h = height * ss
        return IconGenerator(width=w, height=h, skin_design=skin_design, bg_texture_path=bg_texture_path)

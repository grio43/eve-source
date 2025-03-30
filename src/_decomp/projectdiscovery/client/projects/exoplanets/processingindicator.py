#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\exoplanets\processingindicator.py
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from carbonui.uianimations import animations
from projectdiscovery.client.projects.exoplanets.ui.processingcontainer import ProcessingContainer
from projectdiscovery.client import const
import carbonui.const as uiconst

class ProcessingIndicator(ProcessingContainer):

    def ApplyAttributes(self, attributes):
        super(ProcessingIndicator, self).ApplyAttributes(attributes)
        self.pickState = uiconst.TR2_SPS_OFF
        self._prefix = ''
        self._percentage = 0.0
        self.setup_layout()

    def setup_layout(self):
        self._processing_label = EveCaptionSmall(name='ProcessingLabel', parent=self, text='%s%s%%' % (self._prefix, 0), align=uiconst.CENTER, idx=0)

    def process(self, prefix = '', duration = 1, time_offset = 0.0, expand = True, callback = None):

        def processing_callback():
            self.audio_service.SendUIEvent(const.Sounds.ProcessingStop)
            if expand:
                self.expand_screen(duration=0.7, callback=lambda : self.fade_out(callback=callback))
            elif callable(callback):
                callback()

        self._prefix = prefix
        self.reset_processing_screen()
        self.show(prefix, 0)
        animations.MorphScalar(self, 'percentage', 0.0, 100.0, duration, timeOffset=time_offset, callback=processing_callback)
        self.audio_service.SendUIEvent(const.Sounds.ProcessingPlay)

    def show(self, prefix = '', percentage = 0):
        self.opacity = 1
        self._prefix = prefix
        self.percentage = percentage

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, percentage):
        self._percentage = percentage
        self._processing_label.SetText('%s%s%%' % (self._prefix, round(percentage, 3)))

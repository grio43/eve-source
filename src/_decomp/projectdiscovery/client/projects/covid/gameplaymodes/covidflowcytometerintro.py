#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\projects\covid\gameplaymodes\covidflowcytometerintro.py
import carbonui.const as uiconst
from projectdiscovery.client.projects.covid.gameplaymodes.covidproject import CovidProject
from projectdiscovery.client.projects.covid.sounds import Sounds
from projectdiscovery.client.projects.covid.ui.intro.flowcytometer import FlowCytometer
NUMBER_OF_STEPS = 4

class CovidFlowCytometerIntro(CovidProject):

    def ApplyAttributes(self, attributes):
        self.go_to_transition = attributes.get('go_to_transition')
        self.window = attributes.get('window')
        self.audio = sm.GetService('audio')
        super(CovidFlowCytometerIntro, self).ApplyAttributes(attributes)

    def should_play_sample_sounds(self):
        return False

    def should_play_drawing_sounds(self):
        return False

    def setup_content(self):
        self.panels = self._add_panels()
        self.panel = None

    def _add_panels(self):
        panels = {}
        for step in xrange(0, NUMBER_OF_STEPS):
            panels[step] = FlowCytometer(name='flow_cytometer_step_%s' % step, parent=self.main_container, align=uiconst.CENTER, width=self.width, height=self.height, step=step, go_to_next=self.go_to_next, opacity=0.0, clipChildren=True)

        return panels

    def initialize(self):
        self.step = -1
        self.audio.SendUIEvent(Sounds.FLOW_CYTOMETER_LOOP)
        self.go_to_next()

    def Close(self):
        super(CovidFlowCytometerIntro, self).Close()
        self.audio.SendUIEvent(Sounds.FLOW_CYTOMETER_LOOP_STOP)

    def go_to_next(self):
        self.step += 1
        if self.step < NUMBER_OF_STEPS:
            self.go_to_next_flow_cytometer_step()
        else:
            self.go_to_transition()

    def go_to_next_flow_cytometer_step(self):
        if self.panel and not self.panel.destroyed:
            self.panel.Close()
        self.panel = self.panels[self.step]
        self.panel.show()

    def rescale_content(self):
        width, height = self.window.width, self.window.height
        self.SetSize(width, height)
        for panel in self.panels.values():
            panel.SetSize(width, height)

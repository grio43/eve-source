#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\sequence\studioSequencePage.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from cosmetics.client.shipSkinSequencingSvc import get_ship_skin_sequencing_svc
from eve.client.script.ui.cosmetics.ship.pages.sequence.sequenceBinderPanel import SequenceBinderPanel
from eve.client.script.ui.cosmetics.ship.pages.sequence.startSequencingPanel import StartSequencingPanel

class StudioSequencePage(Container):

    def __init__(self, **kw):
        super(StudioSequencePage, self).__init__(**kw)
        self.is_loaded = False

    def LoadPanel(self, animate = True):
        if not self.is_loaded:
            self.is_loaded = True
            self.construct_layout()
        self.state = uiconst.UI_PICKCHILDREN
        get_ship_skin_sequencing_svc().set_num_runs(1)
        self.sequence_binders_panel.load_panel()
        self.start_sequencing_panel.load_panel()
        animations.FadeTo(self, 0.0, 1.0, duration=0.6)

    def UnloadPanel(self, animate = True):
        self.Disable()
        get_ship_skin_sequencing_svc().set_num_runs(1)
        animations.FadeTo(self, self.opacity, 0.0, duration=0.2, callback=self.Hide)

    def construct_layout(self):
        self.sequence_binders_panel = SequenceBinderPanel(parent=self, align=uiconst.TOLEFT, padding=(32, 0, 0, 0))
        self.start_sequencing_panel = StartSequencingPanel(parent=self, align=uiconst.TORIGHT, padding=(0, 125, 32, 64))

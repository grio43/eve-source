#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rwinfopanelpiratetaskentry.py
import carbonui.const as uiconst
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
import localization
import logging
from eve.client.script.ui.shared.infoPanels.const.infoPanelTextureConst import POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH
from resourcewars.client.const import RW_PANEL_PIRATES_KILLED_LABEL
from resourcewars.common.const import RESOURCE_WARS_LOG_CHANNEL
logger = logging.getLogger(RESOURCE_WARS_LOG_CHANNEL)
PROGRESS_FRAME_CORNER_SIZE = 16
PROGRESS_FRAME_OFFSET = -14
PROGRESS_FRAME_PAD_RIGHT = 7

class RWInfoPanelPirateTaskEntry(Container):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 0
    default_padBottom = 4
    default_height = 23
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    tooltipPointer = uiconst.POINT_LEFT_2
    LABEL_PAD_LEFT = 10
    LABEL_PAD_TOP = 3
    COUNTER_PAD_RIGHT = 20
    COUNTER_PAD_TOP = 3
    ARROW_FRAME_COLOR = (1.0, 1.0, 1.0, 0.25)
    ARROW_BG_COLOR = (0.1, 0.1, 0.1, 0.45)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.progress = attributes.progress
        self.target = attributes.target
        self._construct_arrow_frame()
        labelText = self._generate_label_text()
        self.label = EveLabelMediumBold(name='rw_pirate_header_label', parent=self, text=labelText, align=uiconst.TOLEFT_NOPUSH, padLeft=self.LABEL_PAD_LEFT, padTop=self.LABEL_PAD_TOP)
        self.label.SetOrder(0)
        piratesKilled = sm.GetService('rwService').get_pirates_killed()
        self._create_counter(piratesKilled)

    def _generate_label_text(self):
        return localization.GetByLabel(RW_PANEL_PIRATES_KILLED_LABEL, current=self.progress, total=self.target)

    def _create_counter(self, piratesKilled):
        if hasattr(self, 'counter'):
            self.counter.Close()
        self.counter = EveLabelMediumBold(name='rw_pirate_counter_label', parent=self, text=FmtAmt(piratesKilled), align=uiconst.TORIGHT_NOPUSH, padRight=self.COUNTER_PAD_RIGHT, padTop=self.COUNTER_PAD_TOP)
        self.counter.SetOrder(1)

    def register_progress(self, progress):
        logger.debug('RWInfoPanelPirateTaskEntry Registering killed pirates %s %s', self.progress, progress)
        self.progress = progress
        self._create_counter(self.progress)

    def _construct_arrow_frame(self):
        self.progress_frame = Frame(name='arrow_frame', texturePath=POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, cornerSize=PROGRESS_FRAME_CORNER_SIZE, offset=PROGRESS_FRAME_OFFSET, parent=self, color=self.ARROW_FRAME_COLOR, align=uiconst.TOALL, padRight=PROGRESS_FRAME_PAD_RIGHT, blendMode=trinity.TR2_SBM_ADD)
        self.progress_bg = Frame(name='progress_bg', texturePath=POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH, cornerSize=PROGRESS_FRAME_CORNER_SIZE, offset=PROGRESS_FRAME_OFFSET, parent=self, color=self.ARROW_BG_COLOR, padRight=PROGRESS_FRAME_PAD_RIGHT)

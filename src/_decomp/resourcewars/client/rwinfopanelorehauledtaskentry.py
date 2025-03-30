#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\resourcewars\client\rwinfopanelorehauledtaskentry.py
from carbonui.uicore import uicore
import carbonui.const as uiconst
import trinity
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
import localization
from eve.client.script.ui.shared.infoPanels.const.infoPanelUIConst import PANELWIDTH, LEFTPAD
from eve.client.script.ui.shared.infoPanels.const.infoPanelTextureConst import POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH
from resourcewars.client.const import RW_PANEL_MAIN_PROGRESS_LABEL, RW_PANEL_HAULER_PROGRESS_LABEL
from resourcewars.client.rwinfopanelhaulertaskentry import HAULER_PROGRESS_COLOR
from resourcewars.common.const import HAULER_CAPACITY_UNLIMITED, HAULER_CAPACITY_UNLIMITED_STR
from seasons.client.challengetaskprogressbar import PROGRESS_FRAME_CORNER_SIZE, PROGRESS_FRAME_OFFSET, PROGRESS_FRAME_PAD_RIGHT, PROGRESS_BAR_CORNER_SIZE, PROGRESS_BAR_OFFSET, PROGRESS_BAR_PAD_RIGHT
INFO_PANEL_WIDTH = PANELWIDTH - LEFTPAD

class RWInfoPanelOreHauledTaskEntry(Container):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 0
    default_padBottom = 10
    default_height = 23
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    tooltipPointer = uiconst.POINT_LEFT_2
    LABEL_PAD_LEFT = 10
    LABEL_PAD_TOP = 3
    COUNTER_PAD_RIGHT = 20
    COUNTER_PAD_TOP = 3
    PROGRESS_BG_WIDTH = 7
    PROGRESS_BG_COLOR = (0.1, 0.1, 0.1, 0.45)
    PROGRESS_FRAME_OPACITY = 0.25

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.progress = attributes.progress
        self.target = attributes.target
        self._construct_progress_frame()
        labelText = self._generate_label_text()
        self.label = EveLabelMediumBold(name='rw_progress_header_label', parent=self, text=labelText, align=uiconst.TOLEFT_NOPUSH, padLeft=self.LABEL_PAD_LEFT, padTop=self.LABEL_PAD_TOP, state=uiconst.UI_NORMAL)
        self.label.hint = localization.GetByLabel('UI/ResourceWars/FillHaulersHint')
        self.label.SetOrder(0)
        self._update_counter()

    def _generate_label_text(self):
        return localization.GetByLabel(RW_PANEL_MAIN_PROGRESS_LABEL)

    def _generate_counter_label(self):
        if self.target == HAULER_CAPACITY_UNLIMITED:
            total = HAULER_CAPACITY_UNLIMITED_STR
        else:
            total = FmtAmt(self.target)
        return localization.GetByLabel(RW_PANEL_HAULER_PROGRESS_LABEL, current=FmtAmt(self.progress), total=total)

    def _update_counter(self):
        counterLabel = self._generate_counter_label()
        if hasattr(self, 'counter'):
            self.counter.Close()
        self.counter = EveLabelMediumBold(name='rw_progress_header_label', parent=self, text=counterLabel, align=uiconst.TORIGHT_NOPUSH, padRight=self.COUNTER_PAD_RIGHT, padTop=self.COUNTER_PAD_TOP)
        self.counter.SetOrder(0)

    def register_progress(self, progress):
        self.progress += progress
        self._update_counter()
        self.animate_progress()

    def animate_progress(self):
        if not self.progress:
            return
        self.progress_bar.Show()
        new_width = INFO_PANEL_WIDTH + 7 - INFO_PANEL_WIDTH * self.progress / self.target
        uicore.animations.StopAnimation(self.progress_bar, 'width')
        uicore.animations.MorphScalar(self.progress_bar, 'width', self.progress_bar.width, new_width, 1)

    def _construct_progress_frame(self):
        self.progress_frame = Frame(name='progress_bar_frame', texturePath=POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, cornerSize=PROGRESS_FRAME_CORNER_SIZE, offset=PROGRESS_FRAME_OFFSET, parent=self, align=uiconst.TOALL, padRight=PROGRESS_FRAME_PAD_RIGHT, blendMode=trinity.TR2_SBM_ADD, opacity=self.PROGRESS_FRAME_OPACITY)
        self.progress_frame_container = Container(name='progress_frame_container', parent=self, align=uiconst.TOLEFT, clipChildren=True)
        self.progress_bar_container = Container(name='progress_bar_container', parent=self.progress_frame_container, align=uiconst.TOLEFT)
        self.progress_bg = Frame(name='progress_bg', texturePath=POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH, cornerSize=PROGRESS_BAR_CORNER_SIZE, offset=PROGRESS_BAR_OFFSET, parent=self.progress_bar_container, color=self.PROGRESS_BG_COLOR, padRight=PROGRESS_BAR_PAD_RIGHT)
        self.progress_bar = Frame(name='progress_bar_fill', texturePath=POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH, cornerSize=PROGRESS_BAR_CORNER_SIZE, offset=PROGRESS_BAR_OFFSET, parent=self.progress_bar_container, color=HAULER_PROGRESS_COLOR, padRight=PROGRESS_BAR_PAD_RIGHT)
        self.progress_bar.SetOrder(0)
        self.progress_frame_container.width = INFO_PANEL_WIDTH
        self.progress_bg.width = self.PROGRESS_BG_WIDTH
        self.progress_bar_container.width = INFO_PANEL_WIDTH
        self.progress_bar.width = INFO_PANEL_WIDTH + self.PROGRESS_BG_WIDTH - INFO_PANEL_WIDTH * self.progress / self.target
        if not self.progress:
            self.progress_bar.Hide()

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\features\daily_goals\home_page_card.py
import carbonui
import eveicon
import eveui
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Align, TextColor, PickState, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uiconst import OutputMode
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gauge import Gauge
from jobboard.client import get_job_board_service
from jobboard.client.features.daily_goals.completion_convenience.ui.compact_button import CompactCompletionConvenienceButton
from jobboard.client.features.daily_goals.completion_convenience.util import can_pay_for_completion

class DailyGoalHomePageEntry(Container):
    default_state = uiconst.UI_NORMAL

    def __init__(self, job, **kw):
        self.cc_button = None
        super(DailyGoalHomePageEntry, self).__init__(**kw)
        self.job = job
        self.job.on_job_updated.connect(self.update)
        self._layout()

    def _layout(self):
        self.cc_cont = Container(name='cc_cont', parent=self, align=Align.TOPLEFT, width=24, height=24, left=4)
        self.construct_cc_button()
        self.icon_cont = Container(name='icon_cont', align=Align.TOLEFT, width=48, parent=self, pickState=PickState.OFF, padLeft=4)
        self.construct_icon_cont()
        self.main_cont = ContainerAutoSize(name='main_cont', parent=self, align=Align.VERTICALLY_CENTERED, pickState=PickState.OFF, padding=(8, 0, 16, 0))
        self.construct_main_cont()
        self.hover_bg = Frame(name='hover_bg', bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=12, color=eveColor.FOCUS_BLUE, opacity=0.0)
        self.update()

    def construct_cc_button(self):
        if not can_pay_for_completion(self.job):
            return
        self.cc_button = CompactCompletionConvenienceButton(parent=self.cc_cont, job=self.job)

    def construct_icon_cont(self):
        self.checkmark_icon = Sprite(name='checkmark_icon', parent=self.icon_cont, align=Align.CENTER, texturePath='res:/UI/Texture/classes/DungeonMessaging/Checkmark2x.png', color=eveColor.SUCCESS_GREEN, opacity=0.0, pos=(0, 0, 26, 18), outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.3)
        self.icon = Sprite(name='icon', parent=self.icon_cont, align=Align.CENTER, texturePath=self.job.career_icon, pos=(0, 0, 32, 32), outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=0.3)
        Sprite(name='icon_bg', parent=self.icon_cont, align=Align.CENTER, texturePath='res:/UI/Texture/classes/Opportunities/DailyGoals/icon_bg.png', color=eveColor.FOCUS_BLUE, pos=(0, 0, 48, 48))

    def construct_main_cont(self):
        self.progress_label = carbonui.TextDetail(name='progress_label', parent=self.main_cont, align=Align.TOTOP)
        self.gauge = Gauge(name='gauge', parent=ContainerAutoSize(name='gauge_cont', parent=self.main_cont, align=Align.TOTOP, padTop=4), align=Align.CENTERLEFT, gaugeHeight=2, width=80, backgroundColor=(0, 0, 0, 0.5))
        carbonui.TextBody(name='title_header', parent=ContainerAutoSize(parent=self.main_cont, align=uiconst.TOTOP, padTop=4), maxLines=1, text=self.job.title, bold=True, autoFadeSides=16, color=TextColor.HIGHLIGHT)

    def update(self):
        color = eveColor.SUCCESS_GREEN if self.job.is_completed else eveColor.AIR_TURQUOISE
        self.gauge.SetColor(color)
        self.gauge.SetValueTimed(self.job.progress_percentage, duration=0.7)
        self.progress_label.text = u'{} / {}'.format(self.job.current_progress, self.job.desired_progress)
        self.progress_label.color = eveColor.SUCCESS_GREEN if self.job.is_completed else TextColor.NORMAL
        self.icon.opacity = 0.1 if self.job.is_completed else 1.0
        self.checkmark_icon.opacity = 1.0 if self.job.is_completed else 0.0

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        get_job_board_service().open_job(self.job.job_id)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        animations.FadeTo(self.hover_bg, endVal=0.1, duration=0.1)
        if self.cc_button:
            self.cc_button.expand()

    def OnMouseExit(self, *args):
        animations.FadeOut(self.hover_bg, duration=0.1)
        if self.cc_button:
            self.cc_button.minimize()

    def GetMenu(self):
        return self.job.get_menu()

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\title_step.py
import math
import evetypes
import eveui
import uthread2
from carbonui import Align, TextColor, TextBody, TextDisplay, TextHeadline, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from characterdata.factions import get_faction_logo_flat
from eve.common.lib.appConst import factionTriglavian
from localization import GetByMessageID
from raffles.client.widget.sweep_effect import SweepEffect
from shipgroup import get_ship_group_name
from shipprogression.boarding_moment.ui.steps.base import _BoardingUIStepBase
from shipprogression.boarding_moment.ui.utils import roll_in, unscramble_triglavian

class TitleStep(_BoardingUIStepBase):
    MARGIN_LEFT = 325

    def __init__(self, **kwargs):
        self.sweep_effect = None
        self.faction_logo = None
        super(TitleStep, self).__init__(**kwargs)

    def _construct_layout(self):
        self.title_cont = Container(parent=self, align=Align.BOTTOMLEFT, height=120, width=600, top=self.MARGIN_TOP, left=self.MARGIN_LEFT)
        self._construct_type()
        self._construct_title()
        self._construct_tagline()
        self._construct_faction_logo()

    def _construct_faction_logo(self):
        faction_id = evetypes.GetFactionID(self.typeID)
        faction_logo = get_faction_logo_flat(faction_id)
        if not faction_logo:
            return
        icon_size = 512
        self.faction_logo_cont = Container(parent=self, align=Align.BOTTOMLEFT, height=icon_size, width=icon_size, top=self.MARGIN_TOP - icon_size / 4, left=self.MARGIN_LEFT - icon_size / 2.0)
        self.sweep_effect = TitleSweepEffect(parent=self.faction_logo_cont, align=Align.TOALL, texturePath=faction_logo.resolve(icon_size), duration=2.5, opacity=0.1, rotation=math.pi * 0.75, color=TextColor.DISABLED)
        self.faction_logo = Sprite(parent=self.faction_logo_cont, align=Align.TOALL, texturePath=faction_logo.resolve(icon_size), color=(1.0, 1.0, 1.0, 0.02))

    def _construct_type(self):
        self.type_cont = Container(parent=self.title_cont, align=Align.TOTOP, height=22)
        icon_container = Container(parent=self.type_cont, align=Align.TOLEFT, width=16)
        self.class_icon = Sprite(parent=icon_container, align=Align.CENTER, width=16, height=16, color=TextColor.SECONDARY, texturePath=sm.GetService('bracket').GetBracketIcon(self.typeID), opacity=0)
        self.class_label = TextBody(parent=self.type_cont, align=Align.TOLEFT, text=get_ship_group_name(self.typeID), color=TextColor.SECONDARY, top=3, padLeft=4, opacity=0)

    def _construct_title(self):
        self.name_container = ContainerAutoSize(name='nameCont', parent=self.title_cont, align=Align.TOTOP, padTop=6)
        name_string = evetypes.GetName(self.typeID)
        if evetypes.GetFactionID(self.typeID) == factionTriglavian:
            name_string = "<font file='Triglavian.ttf'>{name}</font>".format(name=name_string)
        self.name_label = TextDisplay(parent=self.name_container, align=Align.TOTOP, text=name_string, color=TextColor.HIGHLIGHT, opacity=0)

    def _construct_tagline(self):
        quote = evetypes.GetQuoteID(self.typeID)
        if quote:
            self.tagline = GetByMessageID(quote)
        else:
            self.tagline = ''
        self.tagline_cont = ContainerAutoSize(parent=self.title_cont, align=Align.TOTOP, padTop=16, padBottom=10, padRight=4, opacity=0)
        self.tagline_label = TextHeadline(parent=self.tagline_cont, align=Align.TOTOP, text='')

    def _update(self):
        name_fade_in_duration = 1
        name_fade_in_delay = 1.8
        initial_delay = name_fade_in_duration + name_fade_in_delay
        animations.FadeIn(self.name_label, duration=name_fade_in_duration, timeOffset=name_fade_in_delay)
        animations.FadeIn(self.class_icon, endVal=0.5, duration=0.6, timeOffset=initial_delay + 1, curveType=uiconst.ANIM_OVERSHOT5)
        animations.FadeIn(self.class_label, endVal=0.5, duration=1.4, timeOffset=initial_delay + 1.6)
        animations.FadeIn(self.tagline_cont, duration=0.2, timeOffset=initial_delay + 2.5)
        if self.tagline:
            uthread2.StartTasklet(roll_in, self.tagline_label, self.tagline, delay=initial_delay + 2.5, duration=1, onStart=self.on_start_typing_2, onEnd=self.on_stop_typing_2)
        if self.sweep_effect:
            self.sweep_effect.sweep_to(loops=1, endVal=(-0.25, 0), final_delay=1.4)
        if evetypes.GetFactionID(self.typeID) == factionTriglavian:
            uthread2.StartTasklet(unscramble_triglavian, self.name_label, evetypes.GetName(self.typeID), delay=initial_delay + 1, duration=0.5, onStart=self.on_start_typing_1, onEnd=self.on_stop_typing_1)


class TitleSweepEffect(SweepEffect):

    def sweep_to(self, loops = 0, endVal = (0, 0), final_delay = 0.0):
        eveui.fade_in(self, end_value=self._opacity, duration=0.05)
        if loops > 0:
            self._thread = uthread2.start_tasklet(self._loop_to, loops, endVal, final_delay)
        else:
            self._anim_to(endVal, delay=final_delay)

    def _loop_to(self, loops, endVal, final_delay = 0.0):
        for i in range(loops):
            self._anim()
            uthread2.sleep(self._duration)

        self._anim_to(endVal, delay=final_delay)

    def _anim_to(self, endVal, delay = 0.0):
        uicore.animations.SpSwoopBlink(self, startVal=(-1.2, 0.0), endVal=endVal, rotation=self._rotation, duration=self._duration, timeOffset=delay)

#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page\welcome.py
import math
from carbonui.uianimations import animations
import eveui
import uthread2
from raffles.client import texture
from raffles.client.localization import Text
from raffles.client.tutorial.effects import do_ding
from raffles.client.tutorial.page import Page

class WelcomePage(Page):

    def __init__(self):
        super(WelcomePage, self).__init__(caption=Text.tutorial_welcome_title(), text=Text.tutorial_welcome_text(), button_label=Text.tutorial_lets_go(), enter_animation=self._animate_enter, exit_animation=self._animate_exit)

    def _animate_enter(self, container):
        left_main = eveui.Sprite(name='logo_left_main', parent=container, align=eveui.Align.center, texturePath=texture.logo_left_main, width=96, height=96)
        star = eveui.Sprite(name='logo_star', parent=container, align=eveui.Align.center, texturePath=texture.logo_star, width=96, height=96)
        left_inner = eveui.Sprite(name='logo_left_inner', parent=container, align=eveui.Align.center, texturePath=texture.logo_left_inner, width=96, height=96)
        right_inner = eveui.Sprite(name='logo_right_inner', parent=container, align=eveui.Align.center, texturePath=texture.logo_right_inner, width=96, height=96)
        right_main = eveui.Sprite(name='logo_right_main', parent=container, align=eveui.Align.center, texturePath=texture.logo_right_main, width=96, height=96)
        animations.SpMaskIn(left_main, rotation=-math.pi / 2, duration=0.5, timeOffset=0.3)
        animations.SpMaskIn(left_inner, rotation=-math.pi / 2, duration=0.6, timeOffset=0.0)
        animations.SpMaskIn(right_main, rotation=math.pi / 2, duration=0.5, timeOffset=0.2)
        animations.SpMaskIn(right_inner, rotation=math.pi / 2, duration=0.6, timeOffset=0.0)
        animations.SpMaskIn(star, rotation=-math.pi / 2, duration=0.6, timeOffset=0.6, curveType=eveui.CurveType.overshot2)
        do_ding(parent=container, align=eveui.Align.center, pos=(-9, -24, 96, 96), offset=0.5)
        do_ding(parent=container, align=eveui.Align.center, pos=(-9, -24, 96, 96), offset=0.65)

    def _animate_exit(self, container):
        i = 0
        for child in container.children:
            if 'logo_' in child.name:
                eveui.animate(child, 'left', end_value=child.left - 10, duration=0.15, time_offset=i * 0.03, on_complete=child.Close)
                eveui.fade_out(child, duration=0.1, time_offset=i * 0.03)
                i += 1
            else:
                eveui.animate(child, 'left', end_value=-10, duration=0.2)
                eveui.fade_out(child, duration=child.opacity * 0.2, on_complete=child.Close)

        uthread2.sleep(0.2)

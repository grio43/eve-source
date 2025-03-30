#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\ui\objective_task_widget\target.py
import eveui
import eve.client.script.ui.eveColor as color
from carbonui import TextColor
from carbonui.primitives.gridcontainer import GridContainer
from .base import ObjectiveTaskWidget

class TargetHealthWidget(ObjectiveTaskWidget):
    BAR_COLOR = color.WHITE

    def update(self, **kwargs):
        if not self._objective_task:
            return
        super(TargetHealthWidget, self).update(**kwargs)
        shield, armor, hull = self._get_damage()
        self._hull.update(hull)
        self._armor.update(armor)
        self._shield.update(shield)

    def _get_damage(self):
        damage_state = self._objective_task.damage_state
        if damage_state:
            return (damage_state[0], damage_state[1], damage_state[2])
        else:
            return (0, 0, 0)

    def _layout(self):
        super(TargetHealthWidget, self)._layout()
        shield, armor, hull = self._get_damage()
        health_container = GridContainer(parent=self.content_container, align=eveui.Align.to_top, height=4, top=2, contentSpacing=(4, 4), columns=3)
        self._hull = HealthBar(bar_color=self.BAR_COLOR, damage=hull, parent=health_container)
        self._armor = HealthBar(bar_color=self.BAR_COLOR, damage=armor, parent=health_container)
        self._shield = HealthBar(bar_color=self.BAR_COLOR, damage=shield, parent=health_container)


class EnemyTargetWidget(TargetHealthWidget):
    BAR_COLOR = color.DANGER_RED


class FriendlyTargetWidget(TargetHealthWidget):
    BAR_COLOR = color.CRYO_BLUE


class HealthBar(eveui.Container):

    def __init__(self, bar_color, damage, *args, **kwargs):
        super(HealthBar, self).__init__(*args, **kwargs)
        self.health_bar = eveui.Line(parent=self, align=eveui.Align.to_left_prop, weight=4, width=damage or 0, color=bar_color, opacity=TextColor.NORMAL.opacity)
        eveui.Line(parent=self, align=eveui.Align.to_all, padTop=1, padBottom=1, color=(1, 1, 1), opacity=0.2)

    def update(self, damage):
        eveui.animate(self.health_bar, 'width', end_value=damage or 0, duration=1)
